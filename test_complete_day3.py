#!/usr/bin/env python3
"""
Complete Day 3 System Tests
Tests complets pour toutes les fonctionnalités du Jour 3
"""

import requests
import json
import time
import sys
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000"
STREAMLIT_URL = "http://localhost:8501"
PROMETHEUS_URL = "http://localhost:9090"
GRAFANA_URL = "http://localhost:3000"
UPTIME_KUMA_URL = "http://localhost:3001"
MLFLOW_URL = "http://localhost:5000"
PREFECT_URL = "http://localhost:4200"

class Day3SystemTester:
    """Testeur complet du système Jour 3"""
    
    def __init__(self):
        self.token = None
        self.session = requests.Session()
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Enregistrer un résultat de test"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def test_api_health(self):
        """Test 1: Vérifier la santé de l'API"""
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Version: {data.get('version', 'N/A')}"
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        
        self.log_test("API Health Check", success, details)
        return success
    
    def test_authentication(self):
        """Test 2: Système d'authentification"""
        try:
            # Test login avec utilisateur admin
            login_data = {"username": "admin", "password": "admin123"}
            response = requests.post(f"{API_BASE_URL}/auth/login", json=login_data, timeout=10)
            
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data["access_token"]
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                details = f"Token obtained for user: {token_data.get('username')}"
                success = True
            else:
                success = False
                details = f"Login failed: {response.status_code} - {response.text}"
        
        except Exception as e:
            success = False
            details = f"Auth error: {str(e)}"
        
        self.log_test("Authentication System", success, details)
        return success
    
    def test_user_info(self):
        """Test 3: Informations utilisateur"""
        if not self.token:
            self.log_test("User Info", False, "No token available")
            return False
        
        try:
            response = self.session.get(f"{API_BASE_URL}/auth/me", timeout=5)
            success = response.status_code == 200
            if success:
                user_data = response.json()
                details = f"User: {user_data.get('username')}, Role: {user_data.get('role')}"
            else:
                details = f"Failed: {response.status_code}"
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        
        self.log_test("User Info Retrieval", success, details)
        return success
    
    def test_prediction(self):
        """Test 4: Prédiction ML"""
        if not self.token:
            self.log_test("ML Prediction", False, "No token available")
            return False
        
        try:
            prediction_data = {"features": [1.5, 2.3]}
            response = self.session.post(f"{API_BASE_URL}/predict", json=prediction_data, timeout=10)
            
            success = response.status_code == 200
            if success:
                result = response.json()
                details = f"Prediction: {result.get('prediction')}, Confidence: {result.get('confidence'):.3f}"
            else:
                details = f"Failed: {response.status_code} - {response.text}"
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        
        self.log_test("ML Prediction", success, details)
        return success
    
    def test_conditional_retrain(self):
        """Test 5: Réentraînement conditionnel"""
        if not self.token:
            self.log_test("Conditional Retrain", False, "No token available")
            return False
        
        try:
            retrain_data = {"accuracy_threshold": 0.7, "force_retrain": False}
            response = self.session.post(f"{API_BASE_URL}/retrain/conditional", json=retrain_data, timeout=60)
            
            success = response.status_code == 200
            if success:
                result = response.json()
                details = f"Action: {result.get('action_taken')}, Triggered: {result.get('retrain_triggered')}"
            else:
                details = f"Failed: {response.status_code} - {response.text}"
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        
        self.log_test("Conditional Retrain", success, details)
        return success
    
    def test_prediction_history(self):
        """Test 6: Historique des prédictions"""
        if not self.token:
            self.log_test("Prediction History", False, "No token available")
            return False
        
        try:
            response = self.session.get(f"{API_BASE_URL}/predictions/history?limit=10", timeout=10)
            
            success = response.status_code == 200
            if success:
                result = response.json()
                count = len(result.get('predictions', []))
                details = f"Retrieved {count} prediction records"
            else:
                details = f"Failed: {response.status_code}"
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        
        self.log_test("Prediction History", success, details)
        return success
    
    def test_metrics_endpoint(self):
        """Test 7: Endpoint des métriques Prometheus"""
        try:
            response = requests.get(f"{API_BASE_URL}/metrics", timeout=10)
            success = response.status_code == 200 and "api_requests_total" in response.text
            details = f"Status: {response.status_code}, Contains metrics: {'api_requests_total' in response.text}"
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        
        self.log_test("Prometheus Metrics", success, details)
        return success
    
    def test_external_services(self):
        """Test 8: Services externes"""
        services = [
            ("Streamlit UI", STREAMLIT_URL),
            ("Prometheus", PROMETHEUS_URL),
            ("Grafana", GRAFANA_URL),
            ("Uptime Kuma", UPTIME_KUMA_URL),
            ("MLflow", MLFLOW_URL),
            ("Prefect", PREFECT_URL)
        ]
        
        all_success = True
        for service_name, url in services:
            try:
                response = requests.get(url, timeout=5)
                success = response.status_code in [200, 302]  # 302 for redirects
                details = f"Status: {response.status_code}"
            except Exception as e:
                success = False
                details = f"Connection error: {str(e)}"
            
            self.log_test(f"{service_name} Service", success, details)
            if not success:
                all_success = False
        
        return all_success
    
    def test_database_operations(self):
        """Test 9: Opérations base de données"""
        try:
            # Test de génération de dataset
            if not self.token:
                self.log_test("Database Operations", False, "No token available")
                return False
            
            generate_data = {"samples": 100}
            response = self.session.post(f"{API_BASE_URL}/generate", json=generate_data, timeout=30)
            
            success = response.status_code == 200
            if success:
                result = response.json()
                details = f"Generated {result.get('samples_count', 0)} samples"
            else:
                details = f"Failed: {response.status_code}"
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        
        self.log_test("Database Operations", success, details)
        return success
    
    def test_logging_system(self):
        """Test 10: Système de logging"""
        try:
            # Vérifier que les fichiers de logs existent
            logs_dir = Path("logs")
            log_files = ["app.log", "errors.log", "api.json", "ml.json"]
            
            existing_logs = []
            for log_file in log_files:
                if (logs_dir / log_file).exists():
                    existing_logs.append(log_file)
            
            success = len(existing_logs) > 0
            details = f"Found log files: {', '.join(existing_logs)}" if existing_logs else "No log files found"
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        
        self.log_test("Logging System", success, details)
        return success
    
    def run_all_tests(self):
        """Exécuter tous les tests"""
        print("🚀 Starting Day 3 Complete System Tests")
        print("=" * 50)
        
        # Tests séquentiels
        tests = [
            self.test_api_health,
            self.test_authentication,
            self.test_user_info,
            self.test_prediction,
            self.test_conditional_retrain,
            self.test_prediction_history,
            self.test_metrics_endpoint,
            self.test_database_operations,
            self.test_logging_system,
            self.test_external_services
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            time.sleep(1)  # Pause entre les tests
        
        print("=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Day 3 system is fully functional.")
        else:
            print(f"⚠️  {total - passed} tests failed. Check the details above.")
        
        return passed == total
    
    def generate_test_report(self):
        """Générer un rapport de test"""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_tests": len(self.test_results),
            "passed_tests": sum(1 for r in self.test_results if r["success"]),
            "failed_tests": sum(1 for r in self.test_results if not r["success"]),
            "results": self.test_results
        }
        
        with open("test_report_day3.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Test report saved to: test_report_day3.json")

def main():
    """Fonction principale"""
    tester = Day3SystemTester()
    
    print("⚠️  Make sure all Docker services are running:")
    print("   docker-compose up -d")
    print()
    
    input("Press Enter to start tests...")
    
    success = tester.run_all_tests()
    tester.generate_test_report()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
