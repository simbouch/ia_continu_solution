#!/usr/bin/env python3
"""
IA Continu Solution - Main API Service
FastAPI application with ML pipeline endpoints, MLflow integration, and Discord notifications
"""

from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import sqlite3
import joblib
import mlflow
import mlflow.sklearn
from datetime import datetime, timezone
import os
import requests
import time
from pathlib import Path
from contextlib import asynccontextmanager

# Import monitoring
from src.monitoring.prometheus_metrics import get_prometheus_metrics

# Import advanced logging
from src.utils.logger import get_logger, setup_logging

# Import authentication
from src.auth.auth_service import (
    get_auth_service, get_current_user, get_admin_user,
    UserCreate, UserLogin, TokenResponse, User
)

# Import prediction logging
from src.database.prediction_logger import get_prediction_logger

# Configure advanced logging with Loguru
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Initialize Loguru logger
app_logger = setup_logging("ia_continu_api")
logger = app_logger.get_logger("api")

# Initialize FastAPI app
app = FastAPI(
    title="IA Continu Solution - Day 3",
    description="ML API with monitoring, CI/CD, and advanced features",
    version="3.0.0"
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
            duration=duration
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
        "Succès": 5814783,    # Green
        "Échec": 15158332,    # Red
        "Avertissement": 16776960,  # Yellow
        "Info": 3447003       # Blue
    }
    
    color = color_map.get(status, 3447003)
    
    data = {
        "embeds": [{
            "title": "Résultats du pipeline",
            "description": message,
            "color": color,
            "fields": [{
                "name": "Status",
                "value": status,
                "inline": True
            }, {
                "name": "Timestamp",
                "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "inline": True
            }],
            "footer": {
                "text": "IA Continu Solution - Day 2"
            }
        }]
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
    features: List[float] = Field(..., min_items=2, max_items=2)

class PredictResponse(BaseModel):
    prediction: int
    model_version: str
    confidence: float
    timestamp: str

class RetrainResponse(BaseModel):
    status: str
    model_version: str
    training_samples: int
    accuracy: float
    timestamp: str

class ConditionalRetrainRequest(BaseModel):
    accuracy_threshold: float = Field(default=0.85, ge=0.0, le=1.0)
    force_retrain: bool = Field(default=False)

class ConditionalRetrainResponse(BaseModel):
    status: str
    action_taken: str
    current_accuracy: float
    threshold: float
    model_version: str
    retrain_triggered: bool
    timestamp: str
    details: str

# Routes

@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "IA Continu Solution - Day 3 API", "version": "3.0.0"}

@app.get("/metrics")
def get_metrics():
    """Endpoint pour les métriques Prometheus"""
    return metrics.get_metrics()

# Routes d'authentification
@app.post("/auth/register", response_model=User)
def register(user_data: UserCreate, current_user: User = Depends(get_admin_user)):
    """Créer un nouvel utilisateur (admin seulement)"""
    try:
        auth_service = get_auth_service()
        new_user = auth_service.create_user(user_data)
        app_logger.log_system_event(
            f"User created: {new_user.username} by {current_user.username}",
            {"new_user_id": new_user.id, "created_by": current_user.id}
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
        app_logger.log_system_event(
            f"User logged in: {login_data.username}",
            {"user_id": token_response.user_id}
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
def get_prediction_history(limit: int = 100, current_user: User = Depends(get_current_user)):
    """Obtenir l'historique des prédictions de l'utilisateur"""
    history = pred_logger.get_prediction_history(limit=limit, user_id=current_user.id)
    return {"predictions": history, "total": len(history)}

@app.get("/predictions/history/all")
def get_all_prediction_history(limit: int = 100, current_user: User = Depends(get_admin_user)):
    """Obtenir l'historique de toutes les prédictions (admin seulement)"""
    history = pred_logger.get_prediction_history(limit=limit)
    return {"predictions": history, "total": len(history)}

@app.get("/predictions/stats")
def get_prediction_stats(current_user: User = Depends(get_current_user)):
    """Obtenir les statistiques des prédictions"""
    stats = pred_logger.get_prediction_stats()
    return stats

@app.get("/training/history")
def get_training_history(limit: int = 50, current_user: User = Depends(get_current_user)):
    """Obtenir l'historique des entraînements"""
    history = pred_logger.get_training_history(limit=limit)
    return {"trainings": history, "total": len(history)}

@app.get("/drift/history")
def get_drift_history(limit: int = 50, current_user: User = Depends(get_current_user)):
    """Obtenir l'historique des détections de dérive"""
    history = pred_logger.get_drift_detections(limit=limit)
    return {"drift_detections": history, "total": len(history)}

@app.get("/logs/system")
def get_system_logs(limit: int = 100, level: str = None, component: str = None,
                   current_user: User = Depends(get_admin_user)):
    """Obtenir les logs système (admin seulement)"""
    logs = pred_logger.get_system_logs(limit=limit, level=level, component=component)
    return {"logs": logs, "total": len(logs)}

@app.get("/health")
def health_check():
    """Health check endpoint - returns 200 OK"""
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "2.0.0"
    }

@app.post("/generate", response_model=GenerateResponse)
def generate_dataset(request: GenerateRequest):
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
        generation_id = int(datetime.now().timestamp())
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert dataset metadata
        cursor.execute("""
            INSERT INTO datasets (generation_id, samples_count, hour_generated)
            VALUES (?, ?, ?)
        """, (generation_id, request.samples, current_hour))
        
        # Insert samples
        for i in range(request.samples):
            cursor.execute("""
                INSERT INTO dataset_samples (generation_id, feature1, feature2, target)
                VALUES (?, ?, ?, ?)
            """, (generation_id, float(feature1[i]), float(feature2[i]), int(target[i])))
        
        conn.commit()
        conn.close()
        
        timestamp = datetime.now(timezone.utc).isoformat()
        
        logger.info(f"Generated dataset with ID: {generation_id}")
        
        return GenerateResponse(
            generation_id=generation_id,
            samples_created=request.samples,
            timestamp=timestamp
        )
        
    except Exception as e:
        logger.error(f"Dataset generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Dataset generation failed: {str(e)}")

@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest, current_user: User = Depends(get_current_user)):
    """Make predictions using the latest trained model"""
    global current_model, current_model_version

    start_time = time.time()

    try:
        if current_model is None:
            # Train a simple model if none exists
            train_default_model()

        # Make prediction
        features = np.array(request.features).reshape(1, -1)
        prediction = current_model.predict(features)[0]

        # Get prediction probability for confidence
        if hasattr(current_model, 'predict_proba'):
            probabilities = current_model.predict_proba(features)[0]
            confidence = float(max(probabilities))
        else:
            confidence = 0.8  # Default confidence

        # Calculate response time
        response_time_ms = (time.time() - start_time) * 1000

        # Logs avancés avec Loguru
        app_logger.log_prediction(
            model_version=current_model_version,
            features=request.features,
            prediction=prediction,
            confidence=confidence
        )

        # Enregistrer dans la base de données
        pred_logger.log_prediction(
            user_id=current_user.id,
            model_version=current_model_version,
            feature1=request.features[0],
            feature2=request.features[1],
            prediction=int(prediction),
            confidence=confidence,
            response_time_ms=response_time_ms
        )

        # Enregistrer la métrique de prédiction
        metrics.record_prediction(current_model_version)

        return PredictResponse(
            prediction=int(prediction),
            model_version=current_model_version,
            confidence=confidence,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

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
    current_model_version = f"default_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Save model
    model_path = models_dir / f"model_{current_model_version}.joblib"
    joblib.dump(model, model_path)
    
    logger.info(f"Default model trained and saved: {current_model_version}")

@app.post("/retrain", response_model=RetrainResponse)
def retrain_model():
    """Retrain model with latest dataset from database"""
    global current_model, current_model_version

    try:
        logger.info("Starting model retraining")
        start_time = time.time()

        # Retrieve latest dataset from database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get latest generation_id
        cursor.execute("SELECT generation_id FROM datasets ORDER BY created_at DESC LIMIT 1")
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=400, detail="No dataset found for training")

        generation_id = result[0]

        # Get samples for this generation
        cursor.execute("""
            SELECT feature1, feature2, target
            FROM dataset_samples
            WHERE generation_id = ?
        """, (generation_id,))

        samples = cursor.fetchall()
        conn.close()

        if len(samples) < 10:
            raise HTTPException(status_code=400, detail="Insufficient training data")

        # Prepare training data
        X = np.array([[s[0], s[1]] for s in samples])
        y = np.array([s[2] for s in samples])

        # Train logistic regression model
        model = LogisticRegression(
            C=1.0,
            solver='liblinear',
            max_iter=1000,
            random_state=42
        )
        model.fit(X, y)

        # Calculate metrics
        y_pred = model.predict(X)
        accuracy = accuracy_score(y, y_pred)

        # Try MLflow logging (optional - don't block if it fails)
        try:
            # Quick test if MLflow is available
            import requests
            mlflow_url = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
            test_response = requests.get(f"{mlflow_url}/health", timeout=2)

            if test_response.status_code == 200:
                mlflow.set_tracking_uri(mlflow_url)
                mlflow.set_experiment("ia_continu_solution")

                with mlflow.start_run(run_name=f"retrain_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
                    # Log hyperparameters to MLflow
                    mlflow.log_params({
                        "C": 1.0,
                        "solver": "liblinear",
                        "max_iter": 1000,
                        "training_samples": len(samples)
                    })

                    # Log metrics to MLflow
                    mlflow.log_metrics({
                        "accuracy": accuracy,
                        "training_samples": len(samples)
                    })

                    # Log model to MLflow
                    mlflow.sklearn.log_model(
                        model,
                        "model",
                        registered_model_name="ia_continu_logistic_regression"
                    )
                    logger.info("MLflow logging completed successfully")
            else:
                logger.warning("MLflow server not available, skipping MLflow logging")
        except Exception as e:
            logger.warning(f"MLflow logging failed (continuing without it): {e}")

        # Create new model version
        new_version = f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Save model locally
        model_path = models_dir / f"model_{new_version}.joblib"
        joblib.dump(model, model_path)

        # Update database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Set all models as inactive
        cursor.execute("UPDATE models SET is_active = FALSE")

        # Insert new model
        cursor.execute("""
            INSERT INTO models (version, accuracy, training_samples, is_active)
            VALUES (?, ?, ?, TRUE)
        """, (new_version, accuracy, len(samples)))

        conn.commit()
        conn.close()

        # Update global model
        current_model = model
        current_model_version = new_version

        # Enregistrer les métriques d'entraînement
        training_duration = time.time() - start_time
        metrics.record_training(training_duration)
        metrics.record_retrain("manual_trigger")
        metrics.update_model_accuracy(new_version, accuracy)

        # Logs avancés avec Loguru
        app_logger.log_training(
            model_version=new_version,
            samples_count=len(samples),
            accuracy=accuracy,
            duration=training_duration
        )
        app_logger.log_ml_operation(
            operation="retrain",
            model_version=new_version,
            metrics={"accuracy": accuracy, "samples": len(samples)}
        )

        # Send Discord notification for successful retraining
        message = f"✅ Model Retraining Successful\nVersion: {new_version}\nAccuracy: {accuracy:.3f}\nTraining Samples: {len(samples)}"
        send_discord_notification(message, "Succès")

        return RetrainResponse(
            status="success",
            model_version=new_version,
            training_samples=len(samples),
            accuracy=accuracy,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    except Exception as e:
        logger.error(f"Model retraining failed: {e}")

        # Send Discord notification for failed retraining
        message = f"🔴 Model Retraining Failed\nError: {str(e)}"
        send_discord_notification(message, "Échec")

        raise HTTPException(status_code=500, detail=f"Model retraining failed: {str(e)}")

@app.post("/retrain/conditional", response_model=ConditionalRetrainResponse)
def conditional_retrain(request: ConditionalRetrainRequest):
    """Réentraînement conditionnel basé sur les performances du modèle"""
    global current_model, current_model_version

    try:
        logger.info(f"Starting conditional retrain evaluation (threshold: {request.accuracy_threshold})")

        # Vérifier si un modèle existe
        if current_model is None:
            logger.warning("No model loaded, forcing retrain")
            # Pas de modèle, on force le réentraînement
            retrain_response = retrain_model()
            return ConditionalRetrainResponse(
                status="success",
                action_taken="forced_retrain_no_model",
                current_accuracy=retrain_response.accuracy,
                threshold=request.accuracy_threshold,
                model_version=retrain_response.model_version,
                retrain_triggered=True,
                timestamp=datetime.now(timezone.utc).isoformat(),
                details="No model was loaded, forced retraining"
            )

        # Évaluer les performances du modèle actuel
        current_accuracy = evaluate_current_model_performance()

        logger.info(f"Current model accuracy: {current_accuracy:.3f}, Threshold: {request.accuracy_threshold}")

        # Décider si le réentraînement est nécessaire
        needs_retrain = (current_accuracy < request.accuracy_threshold) or request.force_retrain

        if needs_retrain:
            reason = "performance_below_threshold" if current_accuracy < request.accuracy_threshold else "forced_retrain"
            logger.warning(f"Retraining triggered: {reason}")

            # Enregistrer la détection de dérive
            if current_accuracy < request.accuracy_threshold:
                app_logger.log_drift_detection(
                    trigger_value=current_accuracy,
                    threshold=request.accuracy_threshold,
                    action_taken="retrain_triggered"
                )
                metrics.record_drift_detection()

            # Déclencher le réentraînement
            retrain_response = retrain_model()

            return ConditionalRetrainResponse(
                status="success",
                action_taken=reason,
                current_accuracy=current_accuracy,
                threshold=request.accuracy_threshold,
                model_version=retrain_response.model_version,
                retrain_triggered=True,
                timestamp=datetime.now(timezone.utc).isoformat(),
                details=f"Model retrained due to {reason}. New accuracy: {retrain_response.accuracy:.3f}"
            )
        else:
            logger.info("Model performance is acceptable, no retraining needed")

            return ConditionalRetrainResponse(
                status="success",
                action_taken="no_action_needed",
                current_accuracy=current_accuracy,
                threshold=request.accuracy_threshold,
                model_version=current_model_version,
                retrain_triggered=False,
                timestamp=datetime.now(timezone.utc).isoformat(),
                details=f"Model performance ({current_accuracy:.3f}) is above threshold ({request.accuracy_threshold})"
            )

    except Exception as e:
        logger.error(f"Conditional retrain evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Conditional retrain failed: {str(e)}")

def evaluate_current_model_performance() -> float:
    """Évaluer les performances du modèle actuel sur un échantillon de test"""
    global current_model

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
            logger.warning("Not enough test data for evaluation, returning default accuracy")
            return 0.8  # Valeur par défaut conservatrice

        # Préparer les données de test
        X_test = np.array([[s[0], s[1]] for s in test_samples])
        y_test = np.array([s[2] for s in test_samples])

        # Faire des prédictions
        y_pred = current_model.predict(X_test)

        # Calculer l'accuracy
        accuracy = accuracy_score(y_test, y_pred)

        logger.info(f"Model evaluation completed: {accuracy:.3f} accuracy on {len(test_samples)} samples")

        return accuracy

    except Exception as e:
        logger.error(f"Model evaluation failed: {e}")
        return 0.5  # Valeur par défaut très conservatrice en cas d'erreur

@app.get("/model/info")
def get_model_info():
    """Get current model information"""
    global current_model, current_model_version

    return {
        "model_version": current_model_version,
        "model_loaded": current_model is not None,
        "model_type": "LogisticRegression" if current_model else None,
        "timestamp": datetime.now(timezone.utc).isoformat()
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
        datasets.append({
            "generation_id": row[0],
            "samples_count": row[1],
            "created_at": row[2],
            "hour_generated": row[3]
        })

    conn.close()

    return {
        "datasets": datasets,
        "total_datasets": len(datasets)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
