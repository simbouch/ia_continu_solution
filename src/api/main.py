#!/usr/bin/env python3
"""
IA Continu Solution - Main API Service
FastAPI application with ML pipeline endpoints, MLflow integration, and Discord notifications
"""

from fastapi import FastAPI, HTTPException
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
import logging
import requests
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="IA Continu Solution - Day 2",
    description="ML API with complete Day 2 functionality",
    version="2.0.0"
)

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

def init_database():
    """Initialize SQLite database"""
    try:
        conn = sqlite3.connect(DATABASE_PATH, timeout=30.0)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
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

# Routes

@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "IA Continu Solution - Day 2 API", "version": "2.0.0"}

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
        
        conn = sqlite3.connect(DATABASE_PATH, timeout=30.0)
        conn.execute("PRAGMA journal_mode=WAL")
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
def predict(request: PredictRequest):
    """Make predictions using the latest trained model"""
    global current_model, current_model_version
    
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
        
        logger.info(f"Prediction: {prediction}, Confidence: {confidence:.3f}")
        
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

        # Retrieve latest dataset from database
        conn = sqlite3.connect(DATABASE_PATH, timeout=30.0)
        conn.execute("PRAGMA journal_mode=WAL")
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
        conn = sqlite3.connect(DATABASE_PATH, timeout=30.0)
        conn.execute("PRAGMA journal_mode=WAL")
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

        logger.info(f"Model retrained successfully: {new_version}, Accuracy: {accuracy:.3f}")

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
    conn = sqlite3.connect(DATABASE_PATH, timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL")
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
