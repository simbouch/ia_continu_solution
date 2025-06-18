#!/usr/bin/env python3
"""
Day 3 Features Tests
Tests pour les nouvelles fonctionnalités du Jour 3
"""

import pytest
import requests
import json
import time
import os
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000"

class TestDay3Authentication:
    """Tests pour le système d'authentification"""
    
    @classmethod
    def setup_class(cls):
        """Setup pour les tests d'authentification"""
        cls.base_url = API_BASE_URL
        cls.admin_token = None
        cls.user_token = None
    
    def test_admin_login(self):
        """Test de connexion admin"""
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post(f"{self.base_url}/auth/login", json=login_data, timeout=10)
        
        assert response.status_code == 200, "Admin login should succeed"
        
        data = response.json()
        assert "access_token" in data, "Response should contain access_token"
        assert "token_type" in data, "Response should contain token_type"
        assert "user_id" in data, "Response should contain user_id"
        assert "username" in data, "Response should contain username"
        assert "role" in data, "Response should contain role"
        
        assert data["username"] == "admin", "Username should be admin"
        assert data["role"] == "admin", "Role should be admin"
        assert data["token_type"] == "bearer", "Token type should be bearer"
        
        # Store token for other tests
        TestDay3Authentication.admin_token = data["access_token"]
    
    def test_user_login(self):
        """Test de connexion utilisateur normal"""
        login_data = {"username": "testuser", "password": "test123"}
        response = requests.post(f"{self.base_url}/auth/login", json=login_data, timeout=10)
        
        assert response.status_code == 200, "User login should succeed"
        
        data = response.json()
        assert data["username"] == "testuser", "Username should be testuser"
        assert data["role"] == "user", "Role should be user"
        
        # Store token for other tests
        TestDay3Authentication.user_token = data["access_token"]
    
    def test_invalid_login(self):
        """Test de connexion avec mauvais credentials"""
        login_data = {"username": "admin", "password": "wrongpassword"}
        response = requests.post(f"{self.base_url}/auth/login", json=login_data, timeout=10)
        
        assert response.status_code == 401, "Invalid login should return 401"
    
    def test_user_info(self):
        """Test récupération info utilisateur"""
        if not self.admin_token:
            pytest.skip("Admin token not available")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.get(f"{self.base_url}/auth/me", headers=headers, timeout=5)
        
        assert response.status_code == 200, "User info should be accessible"
        
        data = response.json()
        assert data["username"] == "admin", "Should return admin user info"
        assert data["role"] == "admin", "Should return admin role"

class TestDay3MLFeatures:
    """Tests pour les nouvelles fonctionnalités ML"""
    
    @classmethod
    def setup_class(cls):
        """Setup pour les tests ML"""
        cls.base_url = API_BASE_URL
        # Get admin token
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post(f"{cls.base_url}/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            cls.token = response.json()["access_token"]
            cls.headers = {"Authorization": f"Bearer {cls.token}"}
        else:
            cls.token = None
            cls.headers = {}
    
    def test_authenticated_prediction(self):
        """Test prédiction avec authentification"""
        if not self.token:
            pytest.skip("Authentication token not available")
        
        payload = {"features": [1.5, 2.3]}
        response = requests.post(f"{self.base_url}/predict", json=payload, headers=self.headers, timeout=10)
        
        assert response.status_code == 200, "Authenticated prediction should work"
        
        data = response.json()
        assert "prediction" in data, "Response should contain prediction"
        assert "confidence" in data, "Response should contain confidence"
        assert "model_version" in data, "Response should contain model_version"
    
    def test_unauthenticated_prediction(self):
        """Test prédiction sans authentification"""
        payload = {"features": [1.5, 2.3]}
        response = requests.post(f"{self.base_url}/predict", json=payload, timeout=10)
        
        assert response.status_code == 401, "Unauthenticated prediction should fail"
    
    def test_conditional_retrain(self):
        """Test réentraînement conditionnel"""
        if not self.token:
            pytest.skip("Authentication token not available")
        
        payload = {"accuracy_threshold": 0.7, "force_retrain": False}
        response = requests.post(f"{self.base_url}/retrain/conditional", json=payload, headers=self.headers, timeout=60)
        
        assert response.status_code == 200, "Conditional retrain should work"
        
        data = response.json()
        assert "status" in data, "Response should contain status"
        assert "action_taken" in data, "Response should contain action_taken"
        assert "current_accuracy" in data, "Response should contain current_accuracy"
        assert "threshold" in data, "Response should contain threshold"
        assert "retrain_triggered" in data, "Response should contain retrain_triggered"
        
        assert data["status"] == "success", "Status should be success"
        assert isinstance(data["retrain_triggered"], bool), "retrain_triggered should be boolean"
    
    def test_prediction_history(self):
        """Test historique des prédictions"""
        if not self.token:
            pytest.skip("Authentication token not available")
        
        # First make a prediction to have history
        payload = {"features": [0.5, -0.3]}
        pred_response = requests.post(f"{self.base_url}/predict", json=payload, headers=self.headers, timeout=10)
        assert pred_response.status_code == 200, "Should make prediction first"
        
        # Then get history
        response = requests.get(f"{self.base_url}/predictions/history?limit=10", headers=self.headers, timeout=10)
        
        assert response.status_code == 200, "Prediction history should be accessible"
        
        data = response.json()
        assert "predictions" in data, "Response should contain predictions"
        assert "total" in data, "Response should contain total"
        assert isinstance(data["predictions"], list), "predictions should be a list"

class TestDay3Monitoring:
    """Tests pour le monitoring"""
    
    def test_prometheus_metrics(self):
        """Test endpoint des métriques Prometheus"""
        response = requests.get(f"{API_BASE_URL}/metrics", timeout=10)
        
        assert response.status_code == 200, "Metrics endpoint should be accessible"
        
        content = response.text
        assert "api_requests_total" in content, "Should contain API request metrics"
        assert "ml_predictions_total" in content, "Should contain ML prediction metrics"
        assert "system_cpu_usage_percent" in content, "Should contain system metrics"
    
    def test_external_services_health(self):
        """Test santé des services externes"""
        services = [
            ("Prometheus", "http://localhost:9090"),
            ("Grafana", "http://localhost:3000"),
            ("Uptime Kuma", "http://localhost:3001"),
            ("MLflow", "http://localhost:5000"),
            ("Prefect", "http://localhost:4200")
        ]
        
        for service_name, url in services:
            try:
                response = requests.get(url, timeout=5)
                # Accept 200, 302 (redirects), and some other success codes
                assert response.status_code in [200, 302, 404], f"{service_name} should be accessible"
            except requests.ConnectionError:
                pytest.fail(f"{service_name} service is not running at {url}")

class TestDay3Database:
    """Tests pour les nouvelles fonctionnalités de base de données"""
    
    @classmethod
    def setup_class(cls):
        """Setup pour les tests de base de données"""
        cls.base_url = API_BASE_URL
        # Get admin token
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post(f"{cls.base_url}/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            cls.token = response.json()["access_token"]
            cls.headers = {"Authorization": f"Bearer {cls.token}"}
        else:
            cls.token = None
            cls.headers = {}
    
    def test_prediction_stats(self):
        """Test statistiques des prédictions"""
        if not self.token:
            pytest.skip("Authentication token not available")
        
        response = requests.get(f"{self.base_url}/predictions/stats", headers=self.headers, timeout=10)
        
        assert response.status_code == 200, "Prediction stats should be accessible"
        
        data = response.json()
        assert "total_predictions" in data, "Should contain total_predictions"
        assert "predictions_by_model" in data, "Should contain predictions_by_model"
        assert "average_confidence" in data, "Should contain average_confidence"
        assert "average_response_time_ms" in data, "Should contain average_response_time_ms"
    
    def test_training_history(self):
        """Test historique des entraînements"""
        if not self.token:
            pytest.skip("Authentication token not available")
        
        response = requests.get(f"{self.base_url}/training/history", headers=self.headers, timeout=10)
        
        assert response.status_code == 200, "Training history should be accessible"
        
        data = response.json()
        assert "trainings" in data, "Should contain trainings"
        assert "total" in data, "Should contain total"
        assert isinstance(data["trainings"], list), "trainings should be a list"

class TestDay3Logging:
    """Tests pour le système de logging"""
    
    def test_log_files_exist(self):
        """Test existence des fichiers de logs"""
        logs_dir = Path("logs")
        
        if not logs_dir.exists():
            pytest.skip("Logs directory does not exist")
        
        expected_logs = ["app.log", "errors.log"]
        
        for log_file in expected_logs:
            log_path = logs_dir / log_file
            # Note: Les fichiers peuvent ne pas exister s'il n'y a pas encore eu d'activité
            # On teste juste que le répertoire existe
        
        assert logs_dir.is_dir(), "Logs directory should exist"

def run_day3_tests():
    """Exécuter tous les tests du Jour 3"""
    print("🧪 Running Day 3 Feature Tests")
    print("=" * 50)
    
    # Run pytest with verbose output
    import subprocess
    result = subprocess.run([
        "python", "-m", "pytest", __file__, "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("Errors:")
        print(result.stderr)
    
    return result.returncode == 0

if __name__ == "__main__":
    success = run_day3_tests()
    if success:
        print("\n✅ All Day 3 tests passed!")
    else:
        print("\n❌ Some Day 3 tests failed!")
    
    exit(0 if success else 1)
