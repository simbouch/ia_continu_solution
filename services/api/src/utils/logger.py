#!/usr/bin/env python3
"""
Advanced Logging Service with Loguru
Système de journalisation avancé pour l'application IA Continu
"""

import os
from pathlib import Path
import sys
from typing import Any

from loguru import logger


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
        """Configurer les différents handlers de logging - Simplified to fix recursion"""

        # 1. Console handler simple
        logger.add(
            sys.stdout,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level="INFO",
            colorize=False,  # Disable colorize to prevent recursion
            backtrace=False,  # Disable backtrace to prevent recursion
            diagnose=False,  # Disable diagnose to prevent recursion
        )

        # 2. Fichier général avec rotation - simplified
        logger.add(
            self.logs_dir / "app.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level="DEBUG",
            rotation="10 MB",
            retention="30 days",
            backtrace=False,
            diagnose=False,
        )

        # 3. Fichier des erreurs uniquement - simplified
        logger.add(
            self.logs_dir / "errors.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level="ERROR",
            rotation="5 MB",
            retention="60 days",
            backtrace=False,
            diagnose=False,
        )

    # Removed problematic JSON formatter and Discord handler to fix recursion issues

    def get_logger(self):
        """Obtenir un logger avec un nom spécifique"""
        return logger

    def log_api_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration: float,
        user_id: str = None,
    ):
        """Logger une requête API"""
        logger.bind(api=True).info(
            f"API Request: {method} {endpoint} -> {status_code} ({duration:.3f}s)",
            extra={
                "api": True,
                "method": method,
                "endpoint": endpoint,
                "status_code": status_code,
                "duration": duration,
                "user_id": user_id,
            },
        )

    def log_ml_operation(
        self, operation: str, model_version: str, metrics: dict[str, Any] = None
    ):
        """Logger une opération ML"""
        logger.bind(ml=True).info(
            f"ML Operation: {operation} (model: {model_version})",
            extra={
                "ml": True,
                "operation": operation,
                "model_version": model_version,
                "metrics": metrics or {},
            },
        )

    def log_prediction(
        self, model_version: str, features: list, prediction: Any, confidence: float
    ):
        """Logger une prédiction"""
        logger.bind(ml=True).info(
            f"Prediction made: {prediction} (confidence: {confidence:.3f})",
            extra={
                "ml": True,
                "operation": "prediction",
                "model_version": model_version,
                "features": features,
                "prediction": prediction,
                "confidence": confidence,
            },
        )

    def log_training(
        self, model_version: str, samples_count: int, accuracy: float, duration: float
    ):
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
                "duration": duration,
            },
        )

    def log_drift_detection(
        self, trigger_value: float, threshold: float, action_taken: str
    ):
        """Logger une détection de dérive"""
        logger.bind(ml=True).warning(
            f"Model drift detected: {trigger_value} < {threshold} -> {action_taken}",
            extra={
                "ml": True,
                "operation": "drift_detection",
                "trigger_value": trigger_value,
                "threshold": threshold,
                "action_taken": action_taken,
            },
        )

    def log_monitoring_event(
        self, event_type: str, service: str, status: str, details: dict[str, Any] = None
    ):
        """Logger un événement de monitoring"""
        logger.bind(monitoring=True).info(
            f"Monitoring: {service} -> {status} ({event_type})",
            extra={
                "monitoring": True,
                "event_type": event_type,
                "service": service,
                "status": status,
                "details": details or {},
            },
        )

    def log_database_operation(
        self, operation: str, table: str, affected_rows: int = None
    ):
        """Logger une opération base de données"""
        logger.bind(db=True).debug(
            f"Database: {operation} on {table}"
            + (f" ({affected_rows} rows)" if affected_rows else ""),
            extra={
                "db": True,
                "operation": operation,
                "table": table,
                "affected_rows": affected_rows,
            },
        )

    def log_system_event(self, event: str, details: dict[str, Any] = None):
        """Logger un événement système"""
        logger.info(
            f"System: {event}",
            extra={"system": True, "event": event, "details": details or {}},
        )


# Instance globale
_logger_instance = None


def get_logger() -> LoguruLogger:
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
