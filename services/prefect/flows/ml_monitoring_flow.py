"""
ML Monitoring Flow for IA Continu Solution
Automated monitoring and drift detection workflow
"""

from datetime import datetime
import random
import time

from prefect import flow, task
from prefect.logging import get_run_logger
import requests


@task(name="check_api_health", retries=2, retry_delay_seconds=5)
def check_api_health() -> dict[str, any]:
    """Check API service health"""
    logger = get_run_logger()

    try:
        response = requests.get("http://host.docker.internal:8000/health", timeout=10)
        health_data = response.json()

        logger.info(f"API Health Status: {health_data.get('status', 'unknown')}")
        return {
            "status": "healthy" if response.status_code == 200 else "unhealthy",
            "response_time": health_data.get("response_time", 0),
            "timestamp": datetime.now().isoformat(),
            "details": health_data,
        }
    except Exception as e:
        logger.error(f"API health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@task(name="simulate_model_drift_check", retries=1)
def simulate_model_drift_check() -> dict[str, any]:
    """Simulate model drift detection"""
    logger = get_run_logger()

    # Simulate drift detection with random values
    drift_score = random.uniform(0.0, 1.0)
    drift_threshold = 0.7

    has_drift = drift_score > drift_threshold

    logger.info(
        f"Model drift check - Score: {drift_score:.3f}, Threshold: {drift_threshold}"
    )

    if has_drift:
        logger.warning(f"⚠️ Model drift detected! Score: {drift_score:.3f}")
    else:
        logger.info(f"✅ No model drift detected. Score: {drift_score:.3f}")

    return {
        "drift_score": drift_score,
        "threshold": drift_threshold,
        "has_drift": has_drift,
        "timestamp": datetime.now().isoformat(),
        "status": "drift_detected" if has_drift else "stable",
    }


@task(name="check_data_quality", retries=1)
def check_data_quality() -> dict[str, any]:
    """Check data quality metrics"""
    logger = get_run_logger()

    # Simulate data quality checks
    metrics = {
        "completeness": random.uniform(0.85, 1.0),
        "accuracy": random.uniform(0.80, 0.98),
        "consistency": random.uniform(0.90, 1.0),
        "timeliness": random.uniform(0.75, 1.0),
    }

    # Calculate overall quality score
    quality_score = sum(metrics.values()) / len(metrics)
    quality_threshold = 0.85

    is_quality_good = quality_score >= quality_threshold

    logger.info(f"Data quality score: {quality_score:.3f}")

    return {
        "metrics": metrics,
        "overall_score": quality_score,
        "threshold": quality_threshold,
        "is_good": is_quality_good,
        "timestamp": datetime.now().isoformat(),
        "status": "good" if is_quality_good else "poor",
    }


@task(name="generate_ml_predictions", retries=1)
def generate_ml_predictions() -> dict[str, any]:
    """Generate some ML predictions for monitoring"""
    logger = get_run_logger()

    try:
        # Login to get token
        login_response = requests.post(
            "http://host.docker.internal:8000/auth/login",
            json={"username": "admin", "password": "admin123"},
            timeout=10,
        )

        if login_response.status_code != 200:
            raise Exception("Failed to authenticate")

        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Generate some predictions
        predictions = []
        for _i in range(5):
            features = [random.uniform(-2, 2), random.uniform(-2, 2)]
            pred_response = requests.post(
                "http://host.docker.internal:8000/predict",
                json={"features": features},
                headers=headers,
                timeout=10,
            )

            if pred_response.status_code == 200:
                pred_data = pred_response.json()
                predictions.append(
                    {
                        "features": features,
                        "prediction": pred_data["prediction"],
                        "confidence": pred_data.get("confidence", 0.5),
                    }
                )

        logger.info(f"Generated {len(predictions)} predictions")

        return {
            "predictions_count": len(predictions),
            "predictions": predictions,
            "timestamp": datetime.now().isoformat(),
            "status": "success",
        }

    except Exception as e:
        logger.error(f"Failed to generate predictions: {e}")
        return {
            "predictions_count": 0,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "status": "failed",
        }


@task(name="send_discord_notification")
def send_discord_notification(alert_data: dict[str, any]) -> bool:
    """Send Discord notification for alerts"""
    logger = get_run_logger()

    try:
        # This would normally use the Discord webhook
        # For demo purposes, we'll just log the notification
        logger.info(f"📢 Discord notification sent: {alert_data}")

        # Simulate notification success
        time.sleep(1)
        return True

    except Exception as e:
        logger.error(f"Failed to send Discord notification: {e}")
        return False


@flow(name="ml_monitoring_workflow", log_prints=True)
def ml_monitoring_workflow():
    """Main ML monitoring workflow"""
    logger = get_run_logger()

    logger.info("🚀 Starting ML monitoring workflow")

    # Check API health
    api_health = check_api_health()

    # Check for model drift
    drift_result = simulate_model_drift_check()

    # Check data quality
    quality_result = check_data_quality()

    # Generate some predictions for monitoring
    prediction_result = generate_ml_predictions()

    # Determine if alerts are needed
    alerts = []

    if api_health["status"] == "unhealthy":
        alerts.append(
            {
                "type": "api_health",
                "severity": "critical",
                "message": "API service is unhealthy",
                "details": api_health,
            }
        )

    if drift_result["has_drift"]:
        alerts.append(
            {
                "type": "model_drift",
                "severity": "warning",
                "message": f"Model drift detected (score: {drift_result['drift_score']:.3f})",
                "details": drift_result,
            }
        )

    if not quality_result["is_good"]:
        alerts.append(
            {
                "type": "data_quality",
                "severity": "warning",
                "message": f"Data quality below threshold (score: {quality_result['overall_score']:.3f})",
                "details": quality_result,
            }
        )

    # Send notifications for alerts
    if alerts:
        logger.warning(f"⚠️ {len(alerts)} alert(s) detected")
        for alert in alerts:
            send_discord_notification(alert)
    else:
        logger.info("✅ All systems healthy - no alerts")

    # Return summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "api_health": api_health,
        "drift_check": drift_result,
        "data_quality": quality_result,
        "predictions": prediction_result,
        "alerts_count": len(alerts),
        "alerts": alerts,
        "status": "healthy" if not alerts else "alerts_present",
    }

    logger.info(f"📊 Monitoring workflow completed - Status: {summary['status']}")

    return summary


if __name__ == "__main__":
    # Run the flow
    result = ml_monitoring_workflow()
    print(f"Workflow result: {result}")
