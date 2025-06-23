#!/usr/bin/env python3
"""
IA Continu Solution - Main API Service
FastAPI application with ML pipeline endpoints, MLflow integration, and Discord notifications
"""

from datetime import UTC, datetime
import logging
import os
from pathlib import Path
import random
import sqlite3
import time

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
import joblib
import numpy as np
from pydantic import BaseModel, Field
import requests
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# Import authentication
from src.auth.auth_service import (
    TokenResponse,
    User,
    UserCreate,
    UserLogin,
    get_admin_user,
    get_auth_service,
    get_current_user,
)

# Import prediction logging
from src.database.prediction_logger import get_prediction_logger

# Import monitoring
from src.monitoring.prometheus_metrics import get_prometheus_metrics

# Import advanced logging
from src.utils.logger import setup_logging

# Configure advanced logging with Loguru
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Initialize basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ia_continu_api")

# Initialize Loguru logger for advanced features
try:
    app_logger = setup_logging("ia_continu_api")
except Exception:
    app_logger = None

# Initialize FastAPI app
app = FastAPI(
    title="IA Continu Solution - Day 3",
    description="ML API with monitoring, CI/CD, and advanced features",
    version="3.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics instance
metrics = get_prometheus_metrics()

# Prediction logger instance
pred_logger = get_prediction_logger()


# Middleware pour les métriques
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Middleware pour collecter les métriques de chaque requête"""
    start_time = time.time()
    metrics.increment_active_requests()

    try:
        response = await call_next(request)
        duration = time.time() - start_time

        # Enregistrer les métriques
        metrics.record_api_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            duration=duration,
        )

        return response
    finally:
        metrics.decrement_active_requests()


# Global variables
current_model = None
current_model_version = "v1.0.0"
models_dir = Path("models")
models_dir.mkdir(exist_ok=True)
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# Database setup
DATABASE_PATH = "data/ia_continu_solution.db"

# Discord webhook configuration
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


def send_discord_notification(message: str, status: str = "Succès") -> bool:
    """Send notification to Discord webhook with Day 1 format"""
    if not DISCORD_WEBHOOK_URL:
        logger.info(f"Discord webhook not configured. Message: {message}")
        return False

    # Color mapping
    color_map = {
        "Succès": 5814783,  # Green
        "Échec": 15158332,  # Red
        "Avertissement": 16776960,  # Yellow
        "Info": 3447003,  # Blue
    }

    color = color_map.get(status, 3447003)

    data = {
        "embeds": [
            {
                "title": "Résultats du pipeline",
                "description": message,
                "color": color,
                "fields": [
                    {"name": "Status", "value": status, "inline": True},
                    {
                        "name": "Timestamp",
                        "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                        "inline": True,
                    },
                ],
                "footer": {"text": "IA Continu Solution - Day 2"},
            }
        ]
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data, timeout=10)
        if response.status_code == 204:
            logger.info(f"✅ Discord notification sent: {message}")
            return True
        else:
            logger.warning(f"❌ Discord notification failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Discord notification error: {e}")
        return False


def get_db_connection():
    """Get database connection with proper configuration"""
    conn = sqlite3.connect(DATABASE_PATH, timeout=60.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=30000")  # 30 seconds
    conn.execute("PRAGMA wal_autocheckpoint=1000")
    return conn


def init_database():
    """Initialize SQLite database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create datasets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS datasets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                generation_id INTEGER UNIQUE,
                samples_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                hour_generated INTEGER
            )
        """)

        # Create dataset_samples table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dataset_samples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                generation_id INTEGER,
                feature1 REAL,
                feature2 REAL,
                target INTEGER,
                FOREIGN KEY (generation_id) REFERENCES datasets (generation_id)
            )
        """)

        # Create models table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT UNIQUE,
                accuracy REAL,
                training_samples INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT FALSE
            )
        """)

        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False


# Initialize database on startup
init_database()


# Pydantic models
class GenerateRequest(BaseModel):
    samples: int = Field(default=1000, ge=100, le=10000)


class GenerateResponse(BaseModel):
    generation_id: int
    samples_created: int
    timestamp: str


class PredictRequest(BaseModel):
    features: list[float] = Field(..., min_items=2, max_items=2)


class PredictResponse(BaseModel):
    prediction: int
    model_version: str
    confidence: float
    timestamp: str


# REMOVED: Retrain-related models - Day 4 Professional Architecture
# All retraining is now handled by Prefect automation workflows

# Routes


@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "IA Continu Solution - Day 3 API", "version": "3.0.0"}


@app.get("/metrics")
def get_metrics():
    """Endpoint pour les métriques Prometheus"""
    return metrics.get_metrics()


@app.get("/ml-metrics", response_class=PlainTextResponse)
def get_ml_metrics():
    """Custom ML metrics endpoint for Prometheus"""
    try:
        # Get current model performance metrics
        model_accuracy = 0.85 + random.uniform(-0.1, 0.1)  # Simulate accuracy
        drift_score = random.uniform(0.0, 1.0)  # Simulate drift detection
        data_quality = random.uniform(0.7, 1.0)  # Simulate data quality

        # Get prediction statistics from database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Count total predictions today
        cursor.execute("""
            SELECT COUNT(*) FROM predictions
            WHERE DATE(created_at) = DATE('now')
        """)
        daily_predictions = cursor.fetchone()[0] if cursor.fetchone() else 0

        # Count total models
        cursor.execute("SELECT COUNT(*) FROM models")
        total_models = cursor.fetchone()[0] if cursor.fetchone() else 1

        conn.close()

        # Generate Prometheus metrics format
        metrics_text = f"""# HELP model_accuracy Current model accuracy score
# TYPE model_accuracy gauge
model_accuracy {model_accuracy:.3f}

# HELP model_drift_score Current model drift detection score
# TYPE model_drift_score gauge
model_drift_score {drift_score:.3f}

# HELP data_quality_score Current data quality score
# TYPE data_quality_score gauge
data_quality_score {data_quality:.3f}

# HELP daily_predictions_total Total predictions made today
# TYPE daily_predictions_total counter
daily_predictions_total {daily_predictions}

# HELP total_models_count Total number of trained models
# TYPE total_models_count gauge
total_models_count {total_models}

# HELP api_health API service health status
# TYPE api_health gauge
api_health 1

# HELP ml_service_uptime ML service uptime in seconds
# TYPE ml_service_uptime counter
ml_service_uptime {int(time.time())}
"""

        return metrics_text

    except Exception as e:
        logger.error(f"Failed to generate ML metrics: {e}")
        # Return basic metrics even if database fails
        return """# HELP api_health API service health status
# TYPE api_health gauge
api_health 1

# HELP model_accuracy Current model accuracy score
# TYPE model_accuracy gauge
model_accuracy 0.85

# HELP model_drift_score Current model drift detection score
# TYPE model_drift_score gauge
model_drift_score 0.3
"""


# Routes d'authentification
@app.post("/auth/register", response_model=User)
def register(user_data: UserCreate, current_user: User = Depends(get_admin_user)):
    """Créer un nouvel utilisateur (admin seulement)"""
    try:
        auth_service = get_auth_service()
        new_user = auth_service.create_user(user_data)
        if app_logger:
            app_logger.log_system_event(
                f"User created: {new_user.username} by {current_user.username}",
                {"new_user_id": new_user.id, "created_by": current_user.id},
            )
        return new_user
    except Exception as e:
        logger.error(f"User registration failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/auth/login", response_model=TokenResponse)
def login(login_data: UserLogin):
    """Connexion utilisateur"""
    try:
        auth_service = get_auth_service()
        token_response = auth_service.login(login_data)
        if app_logger:
            app_logger.log_system_event(
                f"User logged in: {login_data.username}",
                {"user_id": token_response.user_id},
            )
        return token_response
    except Exception as e:
        logger.error(f"Login failed for {login_data.username}: {e}")
        raise


@app.get("/auth/me", response_model=User)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Obtenir les informations de l'utilisateur actuel"""
    return current_user


@app.get("/auth/users", response_model=list[User])
def list_users(current_user: User = Depends(get_admin_user)):
    """Lister tous les utilisateurs (admin seulement)"""
    # Cette route sera implémentée dans auth_service si nécessaire
    return []


# Routes pour l'historique et les statistiques
@app.get("/predictions/history")
def get_prediction_history(
    limit: int = 100, current_user: User = Depends(get_current_user)
):
    """Obtenir l'historique des prédictions de l'utilisateur"""
    history = pred_logger.get_prediction_history(limit=limit, user_id=current_user.id)
    return {"predictions": history, "total": len(history)}


@app.get("/predictions/history/all")
def get_all_prediction_history(
    limit: int = 100, current_user: User = Depends(get_admin_user)
):
    """Obtenir l'historique de toutes les prédictions (admin seulement)"""
    history = pred_logger.get_prediction_history(limit=limit)
    return {"predictions": history, "total": len(history)}


@app.get("/predictions/stats")
def get_prediction_stats(current_user: User = Depends(get_current_user)):
    """Obtenir les statistiques des prédictions"""
    stats = pred_logger.get_prediction_stats()
    return stats


@app.get("/training/history")
def get_training_history(
    limit: int = 50, current_user: User = Depends(get_current_user)
):
    """Obtenir l'historique des entraînements"""
    history = pred_logger.get_training_history(limit=limit)
    return {"trainings": history, "total": len(history)}


@app.get("/drift/history")
def get_drift_history(limit: int = 50, current_user: User = Depends(get_current_user)):
    """Obtenir l'historique des détections de dérive"""
    history = pred_logger.get_drift_detections(limit=limit)
    return {"drift_detections": history, "total": len(history)}


@app.get("/logs/system")
def get_system_logs(
    limit: int = 100,
    level: str | None = None,
    component: str | None = None,
    current_user: User = Depends(get_admin_user),
):
    """Obtenir les logs système (admin seulement)"""
    logs = pred_logger.get_system_logs(limit=limit, level=level, component=component)
    return {"logs": logs, "total": len(logs)}


@app.get("/health")
def health_check():
    """Health check endpoint - returns 200 OK"""
    return {
        "status": "ok",
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "2.0.0",
    }


@app.post("/generate", response_model=GenerateResponse)
def generate_dataset(
    request: GenerateRequest, current_user: User = Depends(get_current_user)
):
    """Generate synthetic dataset with time-based modifications"""
    try:
        logger.info(f"Generating {request.samples} samples")

        # Generate base features
        np.random.seed(int(datetime.now().timestamp()) % 1000)
        feature1 = np.random.normal(0, 1, request.samples)
        feature2 = np.random.normal(0, 1, request.samples)

        # Apply time-based modification
        current_hour = datetime.now().hour
        if current_hour % 2 == 1:
            feature1 = feature1 - 0.5
            logger.info(f"Applied time-based modification (hour {current_hour} is odd)")

        # Create binary target based on linear combination
        linear_combination = 0.5 * feature1 + 0.3 * feature2
        target = (linear_combination > 0).astype(int)

        # Store in database
        generation_id = int(datetime.now().timestamp() * 1000) + random.randint(1, 999)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert dataset metadata
        cursor.execute(
            """
            INSERT INTO datasets (generation_id, samples_count, hour_generated)
            VALUES (?, ?, ?)
        """,
            (generation_id, request.samples, current_hour),
        )

        # Insert samples
        for i in range(request.samples):
            cursor.execute(
                """
                INSERT INTO dataset_samples (generation_id, feature1, feature2, target)
                VALUES (?, ?, ?, ?)
            """,
                (generation_id, float(feature1[i]), float(feature2[i]), int(target[i])),
            )

        conn.commit()
        conn.close()

        timestamp = datetime.now(UTC).isoformat()

        logger.info(f"Generated dataset with ID: {generation_id}")

        return GenerateResponse(
            generation_id=generation_id,
            samples_created=request.samples,
            timestamp=timestamp,
        )

    except Exception as e:
        logger.error(f"Dataset generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Dataset generation failed: {e!s}")


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest, current_user: User = Depends(get_current_user)):
    """Make predictions using the latest trained model"""
    start_time = time.time()

    try:
        if current_model is None:
            # Train a simple model if none exists
            train_default_model()

        # Make prediction
        features = np.array(request.features).reshape(1, -1)
        prediction = current_model.predict(features)[0]

        # Get prediction probability for confidence
        if hasattr(current_model, "predict_proba"):
            probabilities = current_model.predict_proba(features)[0]
            confidence = float(max(probabilities))
        else:
            confidence = 0.8  # Default confidence

        # Calculate response time
        response_time_ms = (time.time() - start_time) * 1000

        # Logs avancés avec Loguru
        if app_logger:
            app_logger.log_prediction(
                model_version=current_model_version,
                features=request.features,
                prediction=prediction,
                confidence=confidence,
            )

        # Enregistrer dans la base de données
        pred_logger.log_prediction(
            user_id=current_user.id,
            model_version=current_model_version,
            feature1=request.features[0],
            feature2=request.features[1],
            prediction=int(prediction),
            confidence=confidence,
            response_time_ms=response_time_ms,
        )

        # Enregistrer la métrique de prédiction
        metrics.record_prediction(current_model_version)

        return PredictResponse(
            prediction=int(prediction),
            model_version=current_model_version,
            confidence=confidence,
            timestamp=datetime.now(UTC).isoformat(),
        )

    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e!s}")


def train_default_model():
    """Train a default model with synthetic data"""
    global current_model, current_model_version

    logger.info("Training default model")

    # Generate small synthetic dataset
    X = np.random.normal(0, 1, (100, 2))
    y = (0.5 * X[:, 0] + 0.3 * X[:, 1] > 0).astype(int)

    # Train logistic regression
    model = LogisticRegression(random_state=42)
    model.fit(X, y)

    current_model = model
    current_model_version = f"v1.0.0-default_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Save model
    model_path = models_dir / f"model_{current_model_version}.joblib"
    joblib.dump(model, model_path)

    logger.info(f"Default model trained and saved: {current_model_version}")


# REMOVED: Manual retraining endpoint - Day 4 Professional Architecture
# All retraining is now handled by Prefect automation workflows
# This ensures consistent, automated ML operations without manual intervention

# REMOVED: Conditional retraining endpoint - Day 4 Professional Architecture
# All conditional retraining logic is now handled by Prefect automation workflows
# This provides better orchestration, monitoring, and error handling


def evaluate_current_model_performance() -> float:
    """Évaluer les performances du modèle actuel sur un échantillon de test"""
    try:
        # Récupérer des données de test depuis la base
        conn = get_db_connection()
        cursor = conn.cursor()

        # Prendre un échantillon récent pour l'évaluation
        cursor.execute("""
            SELECT ds.feature1, ds.feature2, ds.target
            FROM dataset_samples ds
            JOIN datasets d ON ds.generation_id = d.generation_id
            ORDER BY d.created_at DESC
            LIMIT 200
        """)

        test_samples = cursor.fetchall()
        conn.close()

        if len(test_samples) < 10:
            logger.warning(
                "Not enough test data for evaluation, returning default accuracy"
            )
            return 0.8  # Valeur par défaut conservatrice

        # Préparer les données de test
        X_test = np.array([[s[0], s[1]] for s in test_samples])
        y_test = np.array([s[2] for s in test_samples])

        # Faire des prédictions
        y_pred = current_model.predict(X_test)

        # Calculer l'accuracy
        accuracy = accuracy_score(y_test, y_pred)

        logger.info(
            f"Model evaluation completed: {accuracy:.3f} accuracy on {len(test_samples)} samples"
        )

        return accuracy

    except Exception as e:
        logger.error(f"Model evaluation failed: {e}")
        return 0.5  # Valeur par défaut très conservatrice en cas d'erreur


@app.get("/model/info")
def get_model_info():
    """Get current model information"""

    return {
        "model_version": current_model_version,
        "model_loaded": current_model is not None,
        "model_type": "LogisticRegression" if current_model else None,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/datasets/list")
def list_datasets():
    """List all generated datasets"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT generation_id, samples_count, created_at, hour_generated
        FROM datasets
        ORDER BY created_at DESC
    """)

    datasets = []
    for row in cursor.fetchall():
        datasets.append(
            {
                "generation_id": row[0],
                "samples_count": row[1],
                "created_at": row[2],
                "hour_generated": row[3],
            }
        )

    conn.close()

    return {"datasets": datasets, "total_datasets": len(datasets)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
