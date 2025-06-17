#!/usr/bin/env python3
"""
Prefect Flow - Random Check Pipeline
Runs every 30 seconds, generates random number, triggers retrain if < 0.5
"""

import os
import random
import time
import requests
from prefect import flow, task
from prefect.logging import get_run_logger

# Set environment variables
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("PREFECT_API_URL", "http://prefect-server:4200/api")

# Configuration
API_URL = os.getenv("API_URL", "http://fastapi_app:8000")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_discord_embed(message, status="Succès"):
    """Send message to Discord via Webhook."""
    if not DISCORD_WEBHOOK_URL:
        print("Discord webhook not configured")
        return
    
    color = 5814783 if status == "Succès" else 15158332  # Green or Red
    
    data = {
        "embeds": [{
            "title": "Résultats du pipeline",
            "description": message,
            "color": color,
            "fields": [{
                "name": "Status",
                "value": status,
                "inline": True
            }]
        }]
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data, timeout=10)
        if response.status_code != 204:
            print(f"Erreur lors de l'envoi de l'embed : {response.status_code}")
        else:
            print("Embed envoyé avec succès !")
    except Exception as e:
        print(f"Erreur Discord: {e}")

@task(retries=2, retry_delay_seconds=1)
def check_random():
    """Generate random number and check if retrain is needed"""
    logger = get_run_logger()
    
    # Generate random number
    random_value = random.random()
    logger.info(f"Generated random value: {random_value}")
    
    if random_value < 0.5:
        logger.warning(f"Random value {random_value} < 0.5 - Model drift detected! Triggering retrain...")
        
        # Trigger retrain
        try:
            response = requests.post(f"{API_URL}/retrain", timeout=60)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Retrain successful: {data}")
                send_discord_embed(f"Retrain déclenché avec succès. Nouvelle précision: {data.get('accuracy', 'N/A')}")
                return {"status": "retrain_success", "random_value": random_value, "retrain_data": data}
            else:
                logger.error(f"Retrain failed with status {response.status_code}")
                send_discord_embed(f"Échec du retrain. Code: {response.status_code}", "Échec")
                raise Exception(f"Retrain failed: {response.status_code}")
        except Exception as e:
            logger.error(f"Retrain error: {e}")
            send_discord_embed(f"Erreur lors du retrain: {str(e)}", "Échec")
            raise
    else:
        logger.info(f"Random value {random_value} >= 0.5 - Model is OK")
        return {"status": "ok", "random_value": random_value}

@task
def health_check():
    """Check API health"""
    logger = get_run_logger()
    
    try:
        response = requests.get(f"{API_URL}/health", timeout=10)
        if response.status_code == 200:
            logger.info("API health check passed")
            return True
        else:
            logger.warning(f"API health check failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"API health check error: {e}")
        return False

@flow
def periodic_check():
    """Main flow that runs periodic checks"""
    logger = get_run_logger()
    
    logger.info("Starting periodic check flow")
    
    # Check API health first
    is_healthy = health_check()
    
    if not is_healthy:
        logger.error("API is not healthy, skipping random check")
        send_discord_embed("API non disponible lors du check périodique", "Échec")
        return {"status": "api_unhealthy"}
    
    # Perform random check
    result = check_random()
    
    logger.info(f"Periodic check completed: {result}")
    return result

if __name__ == "__main__":
    # Wait for services to be ready
    print("Waiting for services to be ready...")
    time.sleep(30)
    
    # Send startup notification
    send_discord_embed("Pipeline de vérification aléatoire démarré")
    
    # Start the flow with 30-second intervals
    periodic_check.serve(
        name="random-check-every-30s",
        interval=30
    )
