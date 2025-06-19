#!/usr/bin/env python3
"""
SQLAlchemy Models for IA Continu Solution
Modèles de base de données pour Alembic migrations
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class Dataset(Base):
    """Table des datasets générés"""
    __tablename__ = "datasets"
    
    generation_id = Column(Integer, primary_key=True)
    samples_count = Column(Integer, nullable=False)
    hour_generated = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relation avec les échantillons
    samples = relationship("DatasetSample", back_populates="dataset")

class DatasetSample(Base):
    """Table des échantillons de données"""
    __tablename__ = "dataset_samples"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    generation_id = Column(Integer, ForeignKey("datasets.generation_id"), nullable=False)
    feature1 = Column(Float, nullable=False)
    feature2 = Column(Float, nullable=False)
    target = Column(Integer, nullable=False)
    
    # Relation avec le dataset
    dataset = relationship("Dataset", back_populates="samples")

class Model(Base):
    """Table des modèles ML"""
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(String(100), unique=True, nullable=False)
    accuracy = Column(Float, nullable=False)
    training_samples = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    is_active = Column(Boolean, default=False)

class User(Base):
    """Table des utilisateurs"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    salt = Column(String(64), nullable=False)
    role = Column(String(20), default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime)
    login_count = Column(Integer, default=0)
    
    # Relations
    tokens = relationship("Token", back_populates="user")
    login_sessions = relationship("LoginSession", back_populates="user")
    predictions = relationship("PredictionLog", back_populates="user")

class Token(Base):
    """Table des tokens JWT"""
    __tablename__ = "tokens"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_hash = Column(String(64), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relation avec l'utilisateur
    user = relationship("User", back_populates="tokens")

class LoginSession(Base):
    """Table des sessions de login"""
    __tablename__ = "login_sessions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(Text)
    login_time = Column(DateTime, server_default=func.now())
    success = Column(Boolean, nullable=False)
    failure_reason = Column(String(200))
    
    # Relation avec l'utilisateur
    user = relationship("User", back_populates="login_sessions")

class PredictionLog(Base):
    """Table des logs de prédictions"""
    __tablename__ = "prediction_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    model_version = Column(String(100), nullable=False)
    feature1 = Column(Float, nullable=False)
    feature2 = Column(Float, nullable=False)
    prediction = Column(Integer, nullable=False)
    confidence = Column(Float, nullable=False)
    response_time_ms = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relation avec l'utilisateur
    user = relationship("User", back_populates="predictions")

class ModelTrainingLog(Base):
    """Table des logs d'entraînement"""
    __tablename__ = "model_training_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_version = Column(String(100), nullable=False)
    trigger_reason = Column(String(50), nullable=False)  # manual, drift_detected, scheduled
    training_samples = Column(Integer, nullable=False)
    accuracy_before = Column(Float)
    accuracy_after = Column(Float, nullable=False)
    training_duration_seconds = Column(Float, nullable=False)
    mlflow_run_id = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())

class SystemLog(Base):
    """Table des logs système"""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(String(10), nullable=False)  # INFO, WARNING, ERROR, CRITICAL
    component = Column(String(50), nullable=False)  # api, ml, monitoring, auth
    event_type = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    details = Column(Text)  # JSON details
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())

class MonitoringMetric(Base):
    """Table des métriques de monitoring"""
    __tablename__ = "monitoring_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_type = Column(String(20), nullable=False)  # counter, gauge, histogram
    labels = Column(Text)  # JSON labels
    timestamp = Column(DateTime, server_default=func.now())

class DriftDetection(Base):
    """Table des détections de dérive"""
    __tablename__ = "drift_detections"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_version = Column(String(100), nullable=False)
    detection_method = Column(String(50), nullable=False)  # random_check, performance_threshold
    trigger_value = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    action_taken = Column(String(50), nullable=False)  # retrain_triggered, no_action
    details = Column(Text)  # JSON details
    created_at = Column(DateTime, server_default=func.now())
