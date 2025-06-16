import os
import random
import requests
from prefect import flow, task
from prefect.logging import get_run_logger
from datetime import datetime

# Set environment variables for Prefect
# PYTHONIOENCODING: évite les UnicodeDecodeError sous Windows
# PREFECT_API_URL: indique au SDK où se trouve l'API Prefect
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
#os.environ.setdefault("PREFECT_API_URL", "http://127.0.0.1:4200/api")

def send_discord_embed(message):
    """Envoyer un message à un canal Discord via un Webhook."""
    DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

    if not DISCORD_WEBHOOK_URL:
        print("Discord webhook URL not configured")
        return

    data = {"embeds": [{
        "title": "Résultats du pipeline",
        "description": message,
        "color": 5814783,
        "fields": [{
            "name": "Status",
            "value": "Succès",
            "inline": True
        }]
    }]}

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data, timeout=30)
        if response.status_code != 204:
            print(f"Erreur lors de l'envoi de l'embed : {response.status_code}")
        else:
            print("Embed envoyé avec succès !")
    except requests.RequestException as e:
        print(f"Erreur de connexion Discord : {e}")

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

@flow
def periodic_check():
    """
    Pipeline Prefect qui s'exécute toutes les 30 secondes :
    génère un nombre aléatoire et, s'il est inférieur à 0.5,
    déclenche un retrain (échec + retries) ; sinon, affiche ok.
    """
    logger = get_run_logger()
    logger.info("Démarrage du pipeline de vérification périodique...")

    # Exécuter la vérification aléatoire
    result = check_random()

    logger.info("Pipeline de vérification terminé avec succès")
    return result

if __name__ == "__main__":
    # Planifier l'exécution toutes les 30 secondes
    # Le bloc if __name__ == "__main__": sert à lancer le scheduler et le worker intégrés
    # lorsque vous exécutez directement le fichier ; il est ignoré si le module est importé ailleurs.
    periodic_check.serve(
        name="random-check-every-30s",
        interval=30,
        description="Pipeline random-check qui s'exécute toutes les 30 secondes"
    )
