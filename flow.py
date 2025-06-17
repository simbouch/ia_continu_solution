import os
import random
import requests
from prefect import flow, task
from prefect.logging import get_run_logger
from datetime import datetime

from utilities import send_discord_embed
from sklearn.linear_model import LinearRegression
from sklearn.metrics import accuracy_score
import joblib
import mlflow
from mlflow.exceptions import MlflowException

# Set environment variables for Prefect
# PYTHONIOENCODING: évite les UnicodeDecodeError sous Windows
# PREFECT_API_URL: indique au SDK où se trouve l'API Prefect
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("PREFECT_API_URL", "http://127.0.0.1:4200/api")


@task
def check_accuracy():
    logger = get_run_logger()

    # Charger le modèle sauvegardé
    try:
        model = joblib.load("model.pkl")
    except FileNotFoundError:
        logger.warning("Aucun modèle local trouvé.")
        send_discord_embed(f"🚨 Aucun modèle local trouvé. - Training nécessaire")
        
        return {"status": "no_model"}

    data = get_last_dataset()
    if not data:
        logger.warning("Pas de données disponibles.")
        send_discord_embed(f"🚨 Pas de données disponibles. - Impossible d'entrainer")
        
        return {"status": "no_data"}

    X = [[row.feature1, row.feature2] for row in data]
    Y = [row.target for row in data]

    if not X or not Y:
        return {"status": "no_data"}

    # Prédiction et accuracy
    Y_pred = model.predict(X)
    current_accuracy = accuracy_score(Y, Y_pred)

    # Lire dernière accuracy de MLflow
    client = mlflow.tracking.MlflowClient()
    runs = client.search_runs(experiment_ids=["0"], order_by=["start_time DESC"], max_results=1)

    if not runs or "accuracy" not in runs[0].data.metrics:
        logger.warning("Pas d'ancienne métrique d'accuracy trouvée.")
        send_discord_embed(f"🚨 Pas d'ancienne métrique d'accuracy trouvée. - Training nécessaire")
        return {"status": "no_previous_accuracy"}

    previous_accuracy = runs[0].data.metrics["accuracy"]

    logger.info(f"Accuracy actuelle: {current_accuracy:.3f} — Précédente: {previous_accuracy:.3f}")

    if current_accuracy < previous_accuracy:
        logger.warning(f"Dérive détectée ! Accuracy {accuracy:.3f} < dernière accuracy {last_accuracy} - seuil {threshold}")
        send_discord_embed(f"🚨 Dérive du modèle détectée! Accuracy actuelle: {accuracy:.3f}, dernière accuracy: {last_accuracy} - Retraining nécessaire")
        return {"status": "drift", "accuracy": current_accuracy}
    else:
        logger.info(f"Modèle OK ! Accuracy {accuracy:.3f} >= dernière accuracy {last_accuracy} - seuil {threshold}")
        send_discord_embed(f"✅ Modèle performant! Accuracy: {accuracy:.3f}")
        return {"status": "ok", "accuracy": current_accuracy}
    


@task(retries=2, retry_delay_seconds=1)
def check_random():
    """
    Génère un nombre aléatoire et déclenche un retrain si < 0.5
    Le tirage aléatoire joue le rôle d'un test de performance :
    un résultat < 0.5 symbolise la dérive d'un modèle qu'il faut ré-entraîner.
    """
    logger = get_run_logger()

    # Générer un nombre aléatoire entre 0 et 1
    random_value = random.random()
    logger.info(f"Valeur aléatoire générée: {random_value:.3f}")

    if random_value < 0.5:
        # Symbolise la dérive du modèle - déclenche un échec + retries
        logger.warning(f"Dérive détectée! Valeur: {random_value:.3f} < 0.5")
        send_discord_embed(f"🚨 Dérive du modèle détectée! Valeur: {random_value:.3f} - Retraining nécessaire")
        raise ValueError(f"Model drift detected: {random_value:.3f} < 0.5 - Initiating retrain")
    else:
        # Modèle OK
        logger.info(f"Modèle OK! Valeur: {random_value:.3f} >= 0.5")
        send_discord_embed(f"✅ Modèle performant! Valeur: {random_value:.3f}")
        return {"status": "ok", "value": random_value}




def save_last_model_mlflow_to_joblib():
    model = mlflow.sklearn.load_model("models:/my_model/latest")
    joblib.dump(model, "model.pkl")


@task
def train_model():
    model=LinearRegression()
    data=get_last_dataset(db)
    X=[[X.feature1,X.feature2] for X in data]
    Y=[X.target for X in data]
    with mlflow.start_run():
        model.fit(X,Y)
        Y_pred=model.predict(X)
        accuracy=accuracy_score(Y,Y_pred)
        mlflow.sklearn.log_model(model, "model")
        mlflow.log_metrics({"accuracy": accuracy})

    message = f"📈 Nouveau modèle entraîné — Accuracy : {accuracy:.3f}"
    logger.info(message)
    send_discord_embed(message, "Succès")
    
    save_last_model_mlflow_to_joblib()

@flow
def periodic_check():
    logger = get_run_logger()
    logger.info("💡 Lancement de la vérification périodique...")

    check_future = check_accuracy.submit()
    result = check_future.result()  # attend le résultat

    if result["status"] in {"no_model", "no_previous_accuracy", "drift"}:
        logger.warning(f"⚠️ Entraînement nécessaire : {result['status']}")
        train_model.submit()
    elif result["status"] == "ok":
        logger.info(f"✅ Modèle performant (accuracy: {result['accuracy']:.3f})")
    else:
        logger.warning(f"❌ État inattendu ou données manquantes : {result['status']}")


if __name__ == "__main__":
    # Planifier l'exécution toutes les 30 secondes
    # Le bloc if __name__ == "__main__": sert à lancer le scheduler et le worker intégrés
    # lorsque vous exécutez directement le fichier ; il est ignoré si le module est importé ailleurs.
    periodic_check.serve(
        name="random-check-every-30s",
        interval=30,
        description="Pipeline random-check qui s'exécute toutes les 30 secondes"
    )
