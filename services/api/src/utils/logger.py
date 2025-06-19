#!/usr/bin/env python3
"""
Advanced Logging Service with Loguru
Système de journalisation avancé pour l'application IA Continu
"""

import sys
import os
from pathlib import Path
from loguru import logger
from datetime import datetime
import json
from typing import Dict, Any, Optional
import requests

class LoguruLogger:
    """Service de logging avancé avec Loguru"""
    
    def __init__(self, app_name: str = "ia_continu_solution"):
        self.app_name = app_name
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        
        # Configuration Discord pour les erreurs critiques
        self.discord_webhook = os.getenv("DISCORD_WEBHOOK_URL")
        
        # Supprimer le handler par défaut
        logger.remove()
        
        # Configurer les handlers
        self._setup_handlers()
        
        logger.info(f"Loguru logger initialized for {app_name}")
    
    def _setup_handlers(self):
        """Configurer les différents handlers de logging"""
        
        # 1. Console handler avec couleurs
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                   "<level>{message}</level>",
            level="INFO",
            colorize=True,
            backtrace=True,
            diagnose=True
        )
        
        # 2. Fichier général avec rotation
        logger.add(
            self.logs_dir / "app.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level="DEBUG",
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            backtrace=True,
            diagnose=True
        )
        
        # 3. Fichier des erreurs uniquement
        logger.add(
            self.logs_dir / "errors.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level="ERROR",
            rotation="5 MB",
            retention="60 days",
            compression="zip",
            backtrace=True,
            diagnose=True
        )
        
        # 4. Fichier API avec format JSON
        logger.add(
            self.logs_dir / "api.json",
            format=self._json_formatter,
            level="INFO",
            rotation="20 MB",
            retention="30 days",
            compression="zip",
            filter=lambda record: "api" in record["extra"]
        )
        
        # 5. Fichier ML avec format JSON
        logger.add(
            self.logs_dir / "ml.json",
            format=self._json_formatter,
            level="INFO",
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            filter=lambda record: "ml" in record["extra"]
        )
        
        # 6. Fichier monitoring
        logger.add(
            self.logs_dir / "monitoring.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
            level="INFO",
            rotation="5 MB",
            retention="15 days",
            filter=lambda record: "monitoring" in record["extra"]
        )
        
        # 7. Handler Discord pour erreurs critiques
        logger.add(
            self._discord_handler,
            level="CRITICAL",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
            backtrace=True,
            diagnose=True
        )
    
    def _json_formatter(self, record):
        """Formateur JSON pour les logs structurés"""
        log_entry = {
            "timestamp": record["time"].isoformat(),
            "level": record["level"].name,
            "logger": record["name"],
            "function": record["function"],
            "line": record["line"],
            "message": record["message"],
            "module": record["module"],
            "process": record["process"].id,
            "thread": record["thread"].id,
            "extra": record["extra"]
        }
        
        if record["exception"]:
            log_entry["exception"] = {
                "type": record["exception"].type.__name__,
                "value": str(record["exception"].value),
                "traceback": record["exception"].traceback
            }
        
        return json.dumps(log_entry, ensure_ascii=False) + "\n"
    
    def _discord_handler(self, message):
        """Handler pour envoyer les erreurs critiques à Discord"""
        if not self.discord_webhook:
            return
        
        try:
            record = message.record
            
            embed = {
                "embeds": [{
                    "title": "🚨 Erreur Critique - IA Continu Solution",
                    "description": f"```\n{record['message']}\n```",
                    "color": 15158332,  # Rouge
                    "fields": [
                        {
                            "name": "Niveau",
                            "value": record["level"].name,
                            "inline": True
                        },
                        {
                            "name": "Module",
                            "value": f"{record['name']}:{record['function']}:{record['line']}",
                            "inline": True
                        },
                        {
                            "name": "Timestamp",
                            "value": record["time"].strftime("%Y-%m-%d %H:%M:%S"),
                            "inline": True
                        }
                    ],
                    "footer": {
                        "text": f"Process: {record['process'].id} | Thread: {record['thread'].id}"
                    }
                }]
            }
            
            if record["exception"]:
                embed["embeds"][0]["fields"].append({
                    "name": "Exception",
                    "value": f"```\n{record['exception'].type.__name__}: {record['exception'].value}\n```",
                    "inline": False
                })
            
            response = requests.post(
                self.discord_webhook,
                json=embed,
                timeout=5
            )
            
            if response.status_code != 204:
                print(f"Failed to send Discord notification: {response.status_code}")
                
        except Exception as e:
            print(f"Error sending Discord notification: {e}")
    
    def get_logger(self, name: str = None):
        """Obtenir un logger avec un nom spécifique"""
        if name:
            return logger.bind(name=name)
        return logger
    
    def log_api_request(self, method: str, endpoint: str, status_code: int, 
                       duration: float, user_id: str = None):
        """Logger une requête API"""
        logger.bind(api=True).info(
            f"API Request: {method} {endpoint} -> {status_code} ({duration:.3f}s)",
            extra={
                "api": True,
                "method": method,
                "endpoint": endpoint,
                "status_code": status_code,
                "duration": duration,
                "user_id": user_id
            }
        )
    
    def log_ml_operation(self, operation: str, model_version: str, 
                        metrics: Dict[str, Any] = None):
        """Logger une opération ML"""
        logger.bind(ml=True).info(
            f"ML Operation: {operation} (model: {model_version})",
            extra={
                "ml": True,
                "operation": operation,
                "model_version": model_version,
                "metrics": metrics or {}
            }
        )
    
    def log_prediction(self, model_version: str, features: list, 
                      prediction: Any, confidence: float):
        """Logger une prédiction"""
        logger.bind(ml=True).info(
            f"Prediction made: {prediction} (confidence: {confidence:.3f})",
            extra={
                "ml": True,
                "operation": "prediction",
                "model_version": model_version,
                "features": features,
                "prediction": prediction,
                "confidence": confidence
            }
        )
    
    def log_training(self, model_version: str, samples_count: int, 
                    accuracy: float, duration: float):
        """Logger un entraînement"""
        logger.bind(ml=True).info(
            f"Model training completed: {model_version} "
            f"(accuracy: {accuracy:.3f}, samples: {samples_count}, duration: {duration:.2f}s)",
            extra={
                "ml": True,
                "operation": "training",
                "model_version": model_version,
                "samples_count": samples_count,
                "accuracy": accuracy,
                "duration": duration
            }
        )
    
    def log_drift_detection(self, trigger_value: float, threshold: float, 
                           action_taken: str):
        """Logger une détection de dérive"""
        logger.bind(ml=True).warning(
            f"Model drift detected: {trigger_value} < {threshold} -> {action_taken}",
            extra={
                "ml": True,
                "operation": "drift_detection",
                "trigger_value": trigger_value,
                "threshold": threshold,
                "action_taken": action_taken
            }
        )
    
    def log_monitoring_event(self, event_type: str, service: str, 
                           status: str, details: Dict[str, Any] = None):
        """Logger un événement de monitoring"""
        logger.bind(monitoring=True).info(
            f"Monitoring: {service} -> {status} ({event_type})",
            extra={
                "monitoring": True,
                "event_type": event_type,
                "service": service,
                "status": status,
                "details": details or {}
            }
        )
    
    def log_database_operation(self, operation: str, table: str, 
                             affected_rows: int = None):
        """Logger une opération base de données"""
        logger.bind(db=True).debug(
            f"Database: {operation} on {table}" + 
            (f" ({affected_rows} rows)" if affected_rows else ""),
            extra={
                "db": True,
                "operation": operation,
                "table": table,
                "affected_rows": affected_rows
            }
        )
    
    def log_system_event(self, event: str, details: Dict[str, Any] = None):
        """Logger un événement système"""
        logger.info(
            f"System: {event}",
            extra={
                "system": True,
                "event": event,
                "details": details or {}
            }
        )

# Instance globale
_logger_instance = None

def get_logger(name: str = None) -> LoguruLogger:
    """Obtenir l'instance globale du logger"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = LoguruLogger()
    return _logger_instance

def setup_logging(app_name: str = "ia_continu_solution"):
    """Initialiser le système de logging"""
    global _logger_instance
    _logger_instance = LoguruLogger(app_name)
    return _logger_instance
