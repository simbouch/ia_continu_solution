#!/usr/bin/env python3
"""
Prefect Flow - Drift Check Pipeline
Runs every 30 seconds, check accuracy, triggers retrain if < 0.5
"""

import os
import time
import requests
import logging
from pathlib import Path
from prefect import flow, task
from prefect.logging import get_run_logger
from datetime import datetime
from sklearn.linear_model import LinearRegression
from sklearn.metrics import accuracy_score
import joblib
import mlflow
from mlflow.exceptions import MlflowException
import sqlite3
from collections import namedtuple

import os; print("CWD:", os.getcwd(), "FILES:", os.listdir())

from utils.utilities import send_discord_embed

# Configure logging for Prefect flow
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Setup file logging
file_handler = logging.FileHandler(logs_dir / "prefect_flow.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Add file handler to root logger
logging.getLogger().addHandler(file_handler)

# Set environment variables


# Set environment variables for Prefect
# PYTHONIOENCODING: évite les UnicodeDecodeError sous Windows
# PREFECT_API_URL: indique au SDK où se trouve l'API Prefect
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("PREFECT_API_URL", "http://prefect-server:4200/api")
os.environ["MLFLOW_TRACKING_URI"] = "http://mlflow-server:5000"
DATABASE_PATH = "data/ia_continu_solution.db"
PATH_MODEL="/app/models/"


@task(retries=2, retry_delay_seconds=10, name="Check model accuracy")
def check_accuracy():
    logger = get_run_logger()

    # Charger le modèle sauvegardé
    try:
        model = joblib.load(PATH_MODEL + "model.pkl")
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

    threshold = 0.05

    if current_accuracy < previous_accuracy:
        logger.warning(f"Dérive détectée ! Accuracy {current_accuracy:.3f} < dernière accuracy {previous_accuracy} - seuil {threshold}")
        send_discord_embed(f"🚨 Dérive du modèle détectée! Accuracy actuelle: {current_accuracy:.3f}, dernière accuracy: {previous_accuracy} - Retraining nécessaire")
        return {"status": "drift", "accuracy": current_accuracy}
    else:
        logger.info(f"Modèle OK ! Accuracy {current_accuracy:.3f} >= dernière accuracy {previous_accuracy} - seuil {threshold}")
        send_discord_embed(f"✅ Modèle performant! Accuracy: {current_accuracy:.3f}")
        return {"status": "ok", "accuracy": current_accuracy}
    

def save_last_model_mlflow_to_joblib():
    model = mlflow.sklearn.load_model("models:/my_model/latest")
    joblib.dump(model, PATH_MODEL + "model.pkl")


def get_last_dataset(db_path: str = DATABASE_PATH, table_name: str = "dataset_samples"):
    """
    Récupère le dernier batch (max generation_id) et retourne la liste de DataRow.

    Args:
        db_path (str): chemin vers la base SQLite.
        table_name (str): nom de la table.

    Returns:
        List[DataRow]: liste des lignes du dernier batch.
    """
    DataRow = namedtuple("DataRow", ["feature1", "feature2", "target"])
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Récupérer la valeur max generation_id
    cursor.execute(f"SELECT MAX(generation_id) FROM {table_name}")
    max_generation_id = cursor.fetchone()[0]

    if max_generation_id is None:
        # Pas de données en base
        conn.close()
        return []

    # Récupérer les données du dernier batch
    cursor.execute(f"""
        SELECT feature1, feature2, target 
        FROM {table_name} 
        WHERE generation_id = ?
    """, (max_generation_id,))

    rows = cursor.fetchall()
    conn.close()

    # Transformer en liste de DataRow
    dataset = [DataRow(*row) for row in rows]
    return dataset


@task(retries=2, retry_delay_seconds=10, name="Train model")
def train_model():
    logger = get_run_logger()
    logger.info("Entraînement du modèle")
    model=LinearRegression()
    data=get_last_dataset()
    X=[[X.feature1,X.feature2] for X in data]
    Y=[X.target for X in data]
    with mlflow.start_run():
        model.fit(X,Y)
        Y_pred=model.predict(X)
        accuracy=accuracy_score(Y,Y_pred)
        mlflow.sklearn.log_model(model, "model")
        mlflow.log_metrics({"accuracy": accuracy})

        run_id = run.info.run_id
        model_uri = f"runs:/{run_id}/model"
        mlflow.register_model(model_uri, "my_model")

    message = f"📈 Nouveau modèle entraîné — Accuracy : {accuracy:.3f}"
    logger.info(message)
    send_discord_embed(message, "Succès")
    
    save_last_model_mlflow_to_joblib()


@flow
def periodic_check():
    """Main flow that runs periodic checks"""
    
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

    logger.info(f"Periodic check completed: " + result['status'])
    return result

if __name__ == "__main__":
    # Wait for services to be ready
    print("Waiting for services to be ready...")
    time.sleep(30)
    
    # Send startup notification
    send_discord_embed("Pipeline de vérification démarrée")
    
    # Start the flow with 30-second intervals
    periodic_check.serve(
        name="drift-check-every-30s",
        interval=30
    )
