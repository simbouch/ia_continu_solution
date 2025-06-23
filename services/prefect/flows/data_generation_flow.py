"""
Data Generation Flow for IA Continu Solution
Automated data generation and processing workflow
"""

from datetime import datetime
import random

from prefect import flow, task
from prefect.logging import get_run_logger
import requests


@task(name="authenticate_api", retries=2, retry_delay_seconds=3)
def authenticate_api() -> str:
    """Authenticate with the API and return token"""
    logger = get_run_logger()

    try:
        response = requests.post(
            "http://host.docker.internal:8000/auth/login",
            json={"username": "admin", "password": "admin123"},
            timeout=10,
        )

        if response.status_code == 200:
            token = response.json()["access_token"]
            logger.info("✅ Successfully authenticated with API")
            return token
        else:
            raise Exception(f"Authentication failed: {response.status_code}")

    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise


@task(name="generate_training_data", retries=1)
def generate_training_data(token: str, samples: int = 300) -> dict[str, any]:
    """Generate training data"""
    logger = get_run_logger()

    try:
        headers = {"Authorization": f"Bearer {token}"}
        generation_id = random.randint(10000, 99999)

        logger.info(f"Generating {samples} training samples with ID {generation_id}")

        response = requests.post(
            "http://host.docker.internal:8000/generate",
            json={"samples": samples, "generation_id": generation_id},
            headers=headers,
            timeout=30,
        )

        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ Generated {result.get('samples_generated', 0)} samples")
            return {
                "status": "success",
                "samples_generated": result.get("samples_generated", 0),
                "generation_id": generation_id,
                "timestamp": datetime.now().isoformat(),
            }
        else:
            raise Exception(f"Generation failed: {response.text}")

    except Exception as e:
        logger.error(f"Data generation failed: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@task(name="validate_generated_data", retries=1)
def validate_generated_data(generation_result: dict[str, any]) -> dict[str, any]:
    """Validate the generated data quality"""
    logger = get_run_logger()

    if generation_result["status"] != "success":
        logger.error("Cannot validate data - generation failed")
        return {
            "status": "failed",
            "reason": "generation_failed",
            "timestamp": datetime.now().isoformat(),
        }

    samples_generated = generation_result.get("samples_generated", 0)

    # Simulate data validation
    validation_checks = {
        "sample_count_valid": samples_generated > 0,
        "data_format_valid": True,  # Simulate format check
        "no_duplicates": random.choice([True, True, False]),  # Mostly pass
        "feature_distribution_valid": random.choice(
            [True, True, True, False]
        ),  # Mostly pass
        "target_balance_valid": random.uniform(0.4, 0.6)
        < 0.55,  # Simulate balance check
    }

    all_checks_passed = all(validation_checks.values())

    logger.info(
        f"Data validation - Checks passed: {sum(validation_checks.values())}/{len(validation_checks)}"
    )

    if all_checks_passed:
        logger.info("✅ All data validation checks passed")
    else:
        logger.warning("⚠️ Some data validation checks failed")

    return {
        "status": "passed" if all_checks_passed else "failed",
        "checks": validation_checks,
        "samples_validated": samples_generated,
        "timestamp": datetime.now().isoformat(),
    }


@task(name="run_model_predictions", retries=1)
def run_model_predictions(token: str, num_predictions: int = 10) -> dict[str, any]:
    """Run model predictions on sample data"""
    logger = get_run_logger()

    try:
        headers = {"Authorization": f"Bearer {token}"}
        predictions = []

        logger.info(f"Running {num_predictions} model predictions")

        for i in range(num_predictions):
            # Generate random features
            features = [random.uniform(-3, 3), random.uniform(-3, 3)]

            response = requests.post(
                "http://host.docker.internal:8000/predict",
                json={"features": features},
                headers=headers,
                timeout=10,
            )

            if response.status_code == 200:
                pred_data = response.json()
                predictions.append(
                    {
                        "features": features,
                        "prediction": pred_data["prediction"],
                        "confidence": pred_data.get("confidence", 0.5),
                        "timestamp": datetime.now().isoformat(),
                    }
                )
            else:
                logger.warning(f"Prediction {i + 1} failed: {response.status_code}")

        success_rate = len(predictions) / num_predictions

        logger.info(
            f"✅ Completed {len(predictions)}/{num_predictions} predictions (success rate: {success_rate:.1%})"
        )

        return {
            "status": "success",
            "predictions_made": len(predictions),
            "success_rate": success_rate,
            "predictions": predictions,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Model predictions failed: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@task(name="calculate_performance_metrics", retries=1)
def calculate_performance_metrics(prediction_result: dict[str, any]) -> dict[str, any]:
    """Calculate performance metrics from predictions"""
    logger = get_run_logger()

    if prediction_result["status"] != "success":
        logger.error("Cannot calculate metrics - predictions failed")
        return {
            "status": "failed",
            "reason": "predictions_failed",
            "timestamp": datetime.now().isoformat(),
        }

    predictions = prediction_result.get("predictions", [])

    if not predictions:
        logger.error("No predictions to analyze")
        return {
            "status": "failed",
            "reason": "no_predictions",
            "timestamp": datetime.now().isoformat(),
        }

    # Calculate metrics
    confidences = [p["confidence"] for p in predictions]
    avg_confidence = sum(confidences) / len(confidences)
    min_confidence = min(confidences)
    max_confidence = max(confidences)

    # Count predictions by class
    class_counts = {}
    for pred in predictions:
        pred_class = pred["prediction"]
        class_counts[pred_class] = class_counts.get(pred_class, 0) + 1

    metrics = {
        "total_predictions": len(predictions),
        "average_confidence": avg_confidence,
        "min_confidence": min_confidence,
        "max_confidence": max_confidence,
        "class_distribution": class_counts,
        "timestamp": datetime.now().isoformat(),
    }

    logger.info(
        f"📊 Performance metrics calculated - Avg confidence: {avg_confidence:.3f}"
    )

    return {
        "status": "success",
        "metrics": metrics,
        "timestamp": datetime.now().isoformat(),
    }


@flow(name="data_generation_workflow", log_prints=True)
def data_generation_workflow(samples: int = 250):
    """Complete data generation and validation workflow"""
    logger = get_run_logger()

    logger.info(f"🚀 Starting data generation workflow for {samples} samples")

    # Step 1: Authenticate
    token = authenticate_api()

    # Step 2: Generate training data
    generation_result = generate_training_data(token, samples)

    # Step 3: Validate generated data
    validation_result = validate_generated_data(generation_result)

    # Step 4: Run model predictions
    prediction_result = run_model_predictions(token, num_predictions=15)

    # Step 5: Calculate performance metrics
    metrics_result = calculate_performance_metrics(prediction_result)

    # Compile workflow summary
    workflow_summary = {
        "workflow_id": f"data_gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "data_generation": generation_result,
        "data_validation": validation_result,
        "model_predictions": prediction_result,
        "performance_metrics": metrics_result,
        "overall_status": "success"
        if all(
            [
                generation_result.get("status") == "success",
                validation_result.get("status") == "passed",
                prediction_result.get("status") == "success",
                metrics_result.get("status") == "success",
            ]
        )
        else "partial_success",
    }

    logger.info(
        f"📊 Data generation workflow completed - Status: {workflow_summary['overall_status']}"
    )

    return workflow_summary


if __name__ == "__main__":
    # Run the flow
    result = data_generation_workflow()
    print(f"Workflow result: {result}")
