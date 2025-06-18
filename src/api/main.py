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
from datetime import datetime, timezone
import os
import logging
import requests
from pathlib import Path

# Configure logging
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configure logging with both file and console handlers
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / "api.log"),
        logging.StreamHandler()
    ]
)
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
