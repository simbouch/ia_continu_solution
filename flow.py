import os
import random
import requests
from prefect import flow, task
from prefect.logging import get_run_logger
from datetime import datetime

# Set environment variables for Prefect
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("PREFECT_API_URL", "http://127.0.0.1:4200/api")

def send_discord_notification(message: str, status: str = "Info") -> None:
    """Send notification to Discord webhook."""
    DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
    
    if not DISCORD_WEBHOOK_URL:
        print("Discord webhook URL not configured")
        return
    
    color_map = {
        "Succès": 5814783,  # Green
        "Erreur": 15158332,  # Red
        "Avertissement": 16776960,  # Yellow
        "Info": 3447003  # Blue
    }
    
    data = {
        "embeds": [{
            "title": "Pipeline de Surveillance IA",
            "description": message,
            "color": color_map.get(status, 3447003),
            "fields": [{
                "name": "Status",
                "value": status,
                "inline": True
            }, {
                "name": "Timestamp",
                "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "inline": True
            }],
            "footer": {
                "text": "Prefect Flow - Model Monitoring"
            }
        }]
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data, timeout=10)
        if response.status_code != 204:
            print(f"Erreur lors de l'envoi de l'embed : {response.status_code}")
        else:
            print("Notification Discord envoyée avec succès !")
    except requests.RequestException as e:
        print(f"Erreur de connexion Discord : {e}")

@task(retries=2, retry_delay_seconds=1)
def check_model_performance():
    """Simulate model drift detection with random number generation"""
    logger = get_run_logger()
    
    # Simulate model performance metrics
    accuracy = random.uniform(0.7, 0.95)
    drift_score = random.uniform(0.0, 1.0)
    
    logger.info(f"Model accuracy: {accuracy:.3f}")
    logger.info(f"Drift score: {drift_score:.3f}")
    
    # Define thresholds
    accuracy_threshold = 0.85
    drift_threshold = 0.7
    
    if accuracy < accuracy_threshold:
        message = f"⚠️ Model accuracy ({accuracy:.3f}) below threshold ({accuracy_threshold})"
        logger.warning(message)
        send_discord_notification(message, "Avertissement")
        return {"status": "warning", "accuracy": accuracy, "drift_score": drift_score}
    
    if drift_score > drift_threshold:
        message = f"🚨 Model drift detected! Drift score: {drift_score:.3f} (threshold: {drift_threshold})"
        logger.error(message)
        send_discord_notification(message, "Erreur")
        raise ValueError("Model drift detected, initiating retraining...")
    
    message = f"✅ Model performing well - Accuracy: {accuracy:.3f}, Drift: {drift_score:.3f}"
    logger.info(message)
    send_discord_notification(message, "Succès")
    
    return {"status": "healthy", "accuracy": accuracy, "drift_score": drift_score}

@task
def check_api_health():
    """Check if the FastAPI application is healthy"""
    logger = get_run_logger()
    
    try:
        # Try to reach the health endpoint
        api_url = os.getenv("API_URL", "http://fastapi_app:8000")
        response = requests.get(f"{api_url}/health", timeout=5)
        
        if response.status_code == 200:
            logger.info("API health check passed")
            return {"api_status": "healthy"}
        else:
            logger.warning(f"API health check failed with status: {response.status_code}")
            return {"api_status": "unhealthy", "status_code": response.status_code}
            
    except requests.RequestException as e:
        logger.error(f"API health check failed: {e}")
        send_discord_notification(f"🔴 API Health Check Failed: {str(e)}", "Erreur")
        return {"api_status": "unreachable", "error": str(e)}

@task
def log_metrics(model_metrics: dict, api_metrics: dict):
    """Log all collected metrics"""
    logger = get_run_logger()
    
    logger.info("=== Monitoring Summary ===")
    logger.info(f"Model Status: {model_metrics.get('status', 'unknown')}")
    logger.info(f"API Status: {api_metrics.get('api_status', 'unknown')}")
    
    if 'accuracy' in model_metrics:
        logger.info(f"Model Accuracy: {model_metrics['accuracy']:.3f}")
    if 'drift_score' in model_metrics:
        logger.info(f"Drift Score: {model_metrics['drift_score']:.3f}")
    
    return {"timestamp": datetime.now().isoformat(), "model": model_metrics, "api": api_metrics}

@flow(log_prints=True)
def periodic_monitoring_flow():
    """Flow that performs periodic model performance and API health checks"""
    logger = get_run_logger()
    logger.info("Starting periodic monitoring flow...")
    
    # Run parallel checks
    model_metrics = check_model_performance()
    api_metrics = check_api_health()
    
    # Log combined metrics
    summary = log_metrics(model_metrics, api_metrics)
    
    logger.info("Monitoring flow completed successfully")
    return summary

if __name__ == "__main__":
    # Run the flow as a deployment that executes every 30 seconds
    periodic_monitoring_flow.serve(
        name="model-monitoring-every-30s",
        interval=30,
        description="Monitors model performance and API health every 30 seconds"
    )
