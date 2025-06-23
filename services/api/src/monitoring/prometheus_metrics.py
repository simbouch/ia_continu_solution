#!/usr/bin/env python3
"""
Prometheus Metrics Service
Collecte et expose les métriques pour le monitoring
"""

import logging

from fastapi import Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
)
from prometheus_client.core import CollectorRegistry
import psutil

logger = logging.getLogger(__name__)


class PrometheusMetrics:
    """Service de métriques Prometheus pour l'application IA Continu"""

    def __init__(self):
        # Registry personnalisé pour éviter les conflits
        self.registry = CollectorRegistry()

        # Métriques API
        self.api_requests_total = Counter(
            "api_requests_total",
            "Total number of API requests",
            ["method", "endpoint", "status_code"],
            registry=self.registry,
        )

        self.api_request_duration = Histogram(
            "api_request_duration_seconds",
            "API request duration in seconds",
            ["method", "endpoint"],
            registry=self.registry,
        )

        self.api_active_requests = Gauge(
            "api_active_requests",
            "Number of active API requests",
            registry=self.registry,
        )

        # Métriques ML
        self.ml_predictions_total = Counter(
            "ml_predictions_total",
            "Total number of ML predictions",
            ["model_version"],
            registry=self.registry,
        )

        self.ml_model_accuracy = Gauge(
            "ml_model_accuracy",
            "Current model accuracy",
            ["model_version"],
            registry=self.registry,
        )

        self.ml_training_duration = Histogram(
            "ml_training_duration_seconds",
            "Model training duration in seconds",
            registry=self.registry,
        )

        self.ml_retrains_total = Counter(
            "ml_retrains_total",
            "Total number of model retrains",
            ["trigger_reason"],
            registry=self.registry,
        )

        # Métriques système
        self.system_cpu_usage = Gauge(
            "system_cpu_usage_percent",
            "System CPU usage percentage",
            registry=self.registry,
        )

        self.system_memory_usage = Gauge(
            "system_memory_usage_bytes",
            "System memory usage in bytes",
            registry=self.registry,
        )

        self.system_disk_usage = Gauge(
            "system_disk_usage_bytes",
            "System disk usage in bytes",
            ["path"],
            registry=self.registry,
        )

        # Métriques base de données
        self.db_operations_total = Counter(
            "db_operations_total",
            "Total database operations",
            ["operation", "table"],
            registry=self.registry,
        )

        self.db_connection_pool_size = Gauge(
            "db_connection_pool_size",
            "Database connection pool size",
            registry=self.registry,
        )

        # Métriques business
        self.dataset_samples_generated = Counter(
            "dataset_samples_generated_total",
            "Total dataset samples generated",
            registry=self.registry,
        )

        self.model_drift_detected = Counter(
            "model_drift_detected_total",
            "Total model drift detections",
            registry=self.registry,
        )

        # Info sur l'application
        self.app_info = Info(
            "app_info", "Application information", registry=self.registry
        )

        # Initialiser les infos de l'app
        self.app_info.info(
            {
                "version": "2.0.0",
                "name": "ia_continu_solution",
                "environment": "production",
            }
        )

        logger.info("Prometheus metrics initialized")

    def record_api_request(
        self, method: str, endpoint: str, status_code: int, duration: float
    ):
        """Enregistrer une requête API"""
        self.api_requests_total.labels(
            method=method, endpoint=endpoint, status_code=str(status_code)
        ).inc()

        self.api_request_duration.labels(method=method, endpoint=endpoint).observe(
            duration
        )

    def increment_active_requests(self):
        """Incrémenter le nombre de requêtes actives"""
        self.api_active_requests.inc()

    def decrement_active_requests(self):
        """Décrémenter le nombre de requêtes actives"""
        self.api_active_requests.dec()

    def record_prediction(self, model_version: str):
        """Enregistrer une prédiction"""
        self.ml_predictions_total.labels(model_version=model_version).inc()

    def update_model_accuracy(self, model_version: str, accuracy: float):
        """Mettre à jour la précision du modèle"""
        self.ml_model_accuracy.labels(model_version=model_version).set(accuracy)

    def record_training(self, duration: float):
        """Enregistrer un entraînement"""
        self.ml_training_duration.observe(duration)

    def record_retrain(self, trigger_reason: str):
        """Enregistrer un réentraînement"""
        self.ml_retrains_total.labels(trigger_reason=trigger_reason).inc()

    def record_drift_detection(self):
        """Enregistrer une détection de dérive"""
        self.model_drift_detected.inc()

    def record_dataset_generation(self, samples_count: int):
        """Enregistrer la génération de dataset"""
        self.dataset_samples_generated.inc(samples_count)

    def record_db_operation(self, operation: str, table: str):
        """Enregistrer une opération base de données"""
        self.db_operations_total.labels(operation=operation, table=table).inc()

    def update_system_metrics(self):
        """Mettre à jour les métriques système"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            self.system_cpu_usage.set(cpu_percent)

            # Mémoire
            memory = psutil.virtual_memory()
            self.system_memory_usage.set(memory.used)

            # Disque
            disk = psutil.disk_usage("/")
            self.system_disk_usage.labels(path="/").set(disk.used)

        except Exception as e:
            logger.error(f"Failed to update system metrics: {e}")

    def get_metrics(self) -> Response:
        """Retourner les métriques au format Prometheus"""
        # Mettre à jour les métriques système avant de les exposer
        self.update_system_metrics()

        # Générer les métriques
        metrics_data = generate_latest(self.registry)

        return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)


# Instance globale
prometheus_metrics = PrometheusMetrics()


def get_prometheus_metrics() -> PrometheusMetrics:
    """Obtenir l'instance des métriques Prometheus"""
    return prometheus_metrics
