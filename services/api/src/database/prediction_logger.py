#!/usr/bin/env python3
"""
Prediction Logger Service
Service pour enregistrer l'historique des prédictions et métriques
"""

import json
import sqlite3
from typing import Any


class PredictionLogger:
    """Service pour enregistrer les prédictions et métriques"""

    def __init__(self, db_path: str = "data/ia_continu_solution.db"):
        self.db_path = db_path
        self.ensure_tables()

    def ensure_tables(self):
        """Créer les tables de logging si elles n'existent pas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Table des logs de prédictions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prediction_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                model_version TEXT NOT NULL,
                feature1 REAL NOT NULL,
                feature2 REAL NOT NULL,
                prediction INTEGER NOT NULL,
                confidence REAL NOT NULL,
                response_time_ms REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        # Table des logs d'entraînement
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_training_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_version TEXT NOT NULL,
                trigger_reason TEXT NOT NULL,
                training_samples INTEGER NOT NULL,
                accuracy_before REAL,
                accuracy_after REAL NOT NULL,
                training_duration_seconds REAL NOT NULL,
                mlflow_run_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Table des logs système
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,
                component TEXT NOT NULL,
                event_type TEXT NOT NULL,
                message TEXT NOT NULL,
                details TEXT,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        # Table des métriques de monitoring
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monitoring_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_type TEXT NOT NULL,
                labels TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Table des détections de dérive
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS drift_detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_version TEXT NOT NULL,
                detection_method TEXT NOT NULL,
                trigger_value REAL NOT NULL,
                threshold REAL NOT NULL,
                action_taken TEXT NOT NULL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def log_prediction(
        self,
        user_id: int | None,
        model_version: str,
        feature1: float,
        feature2: float,
        prediction: int,
        confidence: float,
        response_time_ms: float | None = None,
    ):
        """Enregistrer une prédiction"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO prediction_logs
            (user_id, model_version, feature1, feature2, prediction, confidence, response_time_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                user_id,
                model_version,
                feature1,
                feature2,
                prediction,
                confidence,
                response_time_ms,
            ),
        )

        conn.commit()
        conn.close()

    def log_training(
        self,
        model_version: str,
        trigger_reason: str,
        training_samples: int,
        accuracy_before: float,
        accuracy_after: float,
        training_duration: float,
        mlflow_run_id: str | None = None,
    ):
        """Enregistrer un entraînement"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO model_training_logs
            (model_version, trigger_reason, training_samples, accuracy_before,
             accuracy_after, training_duration_seconds, mlflow_run_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                model_version,
                trigger_reason,
                training_samples,
                accuracy_before,
                accuracy_after,
                training_duration,
                mlflow_run_id,
            ),
        )

        conn.commit()
        conn.close()

    def log_system_event(
        self,
        level: str,
        component: str,
        event_type: str,
        message: str,
        details: dict[str, Any] | None = None,
        user_id: int | None = None,
    ):
        """Enregistrer un événement système"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        details_json = json.dumps(details) if details else None

        cursor.execute(
            """
            INSERT INTO system_logs
            (level, component, event_type, message, details, user_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (level, component, event_type, message, details_json, user_id),
        )

        conn.commit()
        conn.close()

    def log_monitoring_metric(
        self,
        metric_name: str,
        metric_value: float,
        metric_type: str,
        labels: dict[str, str] | None = None,
    ):
        """Enregistrer une métrique de monitoring"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        labels_json = json.dumps(labels) if labels else None

        cursor.execute(
            """
            INSERT INTO monitoring_metrics
            (metric_name, metric_value, metric_type, labels)
            VALUES (?, ?, ?, ?)
        """,
            (metric_name, metric_value, metric_type, labels_json),
        )

        conn.commit()
        conn.close()

    def log_drift_detection(
        self,
        model_version: str,
        detection_method: str,
        trigger_value: float,
        threshold: float,
        action_taken: str,
        details: dict[str, Any] | None = None,
    ):
        """Enregistrer une détection de dérive"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        details_json = json.dumps(details) if details else None

        cursor.execute(
            """
            INSERT INTO drift_detections
            (model_version, detection_method, trigger_value, threshold, action_taken, details)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                model_version,
                detection_method,
                trigger_value,
                threshold,
                action_taken,
                details_json,
            ),
        )

        conn.commit()
        conn.close()

    def get_prediction_history(
        self, limit: int = 100, user_id: int | None = None
    ) -> list[dict]:
        """Récupérer l'historique des prédictions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if user_id:
            cursor.execute(
                """
                SELECT id, user_id, model_version, feature1, feature2,
                       prediction, confidence, response_time_ms, created_at
                FROM prediction_logs
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """,
                (user_id, limit),
            )
        else:
            cursor.execute(
                """
                SELECT id, user_id, model_version, feature1, feature2,
                       prediction, confidence, response_time_ms, created_at
                FROM prediction_logs
                ORDER BY created_at DESC
                LIMIT ?
            """,
                (limit,),
            )

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "id": row[0],
                "user_id": row[1],
                "model_version": row[2],
                "feature1": row[3],
                "feature2": row[4],
                "prediction": row[5],
                "confidence": row[6],
                "response_time_ms": row[7],
                "created_at": row[8],
            }
            for row in rows
        ]

    def get_training_history(self, limit: int = 50) -> list[dict]:
        """Récupérer l'historique des entraînements"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, model_version, trigger_reason, training_samples,
                   accuracy_before, accuracy_after, training_duration_seconds,
                   mlflow_run_id, created_at
            FROM model_training_logs
            ORDER BY created_at DESC
            LIMIT ?
        """,
            (limit,),
        )

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "id": row[0],
                "model_version": row[1],
                "trigger_reason": row[2],
                "training_samples": row[3],
                "accuracy_before": row[4],
                "accuracy_after": row[5],
                "training_duration_seconds": row[6],
                "mlflow_run_id": row[7],
                "created_at": row[8],
            }
            for row in rows
        ]

    def get_drift_detections(self, limit: int = 50) -> list[dict]:
        """Récupérer l'historique des détections de dérive"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, model_version, detection_method, trigger_value,
                   threshold, action_taken, details, created_at
            FROM drift_detections
            ORDER BY created_at DESC
            LIMIT ?
        """,
            (limit,),
        )

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "id": row[0],
                "model_version": row[1],
                "detection_method": row[2],
                "trigger_value": row[3],
                "threshold": row[4],
                "action_taken": row[5],
                "details": json.loads(row[6]) if row[6] else None,
                "created_at": row[7],
            }
            for row in rows
        ]

    def get_system_logs(
        self, limit: int = 100, level: str | None = None, component: str | None = None
    ) -> list[dict]:
        """Récupérer les logs système"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT id, level, component, event_type, message, details, user_id, created_at
            FROM system_logs
        """
        params = []

        conditions = []
        if level:
            conditions.append("level = ?")
            params.append(level)
        if component:
            conditions.append("component = ?")
            params.append(component)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "id": row[0],
                "level": row[1],
                "component": row[2],
                "event_type": row[3],
                "message": row[4],
                "details": json.loads(row[5]) if row[5] else None,
                "user_id": row[6],
                "created_at": row[7],
            }
            for row in rows
        ]

    def get_prediction_stats(self) -> dict[str, Any]:
        """Obtenir des statistiques sur les prédictions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Nombre total de prédictions
        cursor.execute("SELECT COUNT(*) FROM prediction_logs")
        total_predictions = cursor.fetchone()[0]

        # Prédictions par modèle
        cursor.execute("""
            SELECT model_version, COUNT(*)
            FROM prediction_logs
            GROUP BY model_version
            ORDER BY COUNT(*) DESC
        """)
        predictions_by_model = dict(cursor.fetchall())

        # Confiance moyenne
        cursor.execute("SELECT AVG(confidence) FROM prediction_logs")
        avg_confidence = cursor.fetchone()[0] or 0

        # Temps de réponse moyen
        cursor.execute(
            "SELECT AVG(response_time_ms) FROM prediction_logs WHERE response_time_ms IS NOT NULL"
        )
        avg_response_time = cursor.fetchone()[0] or 0

        conn.close()

        return {
            "total_predictions": total_predictions,
            "predictions_by_model": predictions_by_model,
            "average_confidence": round(avg_confidence, 3),
            "average_response_time_ms": round(avg_response_time, 2),
        }


# Instance globale
prediction_logger = PredictionLogger()


def get_prediction_logger() -> PredictionLogger:
    """Obtenir l'instance du logger de prédictions"""
    return prediction_logger
