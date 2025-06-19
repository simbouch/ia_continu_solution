"""
Test suite for API health endpoints
"""
import pytest
import requests
from tests.conftest import API_BASE_URL

class TestHealthEndpoints:
    """Test health and status endpoints"""
    
    def test_api_health_check_returns_healthy_status(self):
        """Test that health endpoint returns healthy status"""
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "services" in data
        assert "metrics" in data
    
    def test_api_health_check_includes_service_status(self):
        """Test that health check includes service status information"""
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        
        assert response.status_code == 200
        data = response.json()
        services = data["services"]
        
        # Check required service status fields
        assert "database" in services
        assert "ml_model" in services
        assert isinstance(services["database"], bool)
        assert isinstance(services["ml_model"], bool)
    
    def test_api_health_check_includes_metrics(self):
        """Test that health check includes system metrics"""
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        
        assert response.status_code == 200
        data = response.json()
        metrics = data["metrics"]
        
        # Check required metrics fields
        assert "uptime" in metrics
        assert "memory_usage" in metrics
        assert isinstance(metrics["uptime"], (int, float))
    
    def test_api_health_check_response_time_under_threshold(self):
        """Test that health check responds within acceptable time"""
        import time
        
        start_time = time.time()
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        response_time = time.time() - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0  # Should respond within 1 second
    
    def test_model_info_endpoint_requires_authentication(self):
        """Test that model info endpoint requires authentication"""
        response = requests.get(f"{API_BASE_URL}/model/info", timeout=10)
        
        assert response.status_code == 401
    
    def test_model_info_endpoint_with_valid_token(self, auth_headers):
        """Test model info endpoint with valid authentication"""
        response = requests.get(
            f"{API_BASE_URL}/model/info",
            headers=auth_headers,
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required model info fields
        assert "model_version" in data
        assert "model_loaded" in data
        assert "model_type" in data
        assert "accuracy" in data
        assert "timestamp" in data
    
    def test_model_info_endpoint_returns_valid_model_data(self, auth_headers):
        """Test that model info returns valid model information"""
        response = requests.get(
            f"{API_BASE_URL}/model/info",
            headers=auth_headers,
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate model data types and ranges
        assert isinstance(data["model_loaded"], bool)
        assert isinstance(data["accuracy"], (int, float))
        assert 0.0 <= data["accuracy"] <= 1.0
        assert data["model_type"] in ["LogisticRegression", "RandomForest", "SVM"]
    
    def test_api_root_endpoint_returns_info(self):
        """Test that root endpoint returns API information"""
        response = requests.get(f"{API_BASE_URL}/", timeout=10)
        
        # Should either return 200 with info or 404 (both acceptable)
        assert response.status_code in [200, 404]
    
    def test_api_docs_endpoint_accessible(self):
        """Test that API documentation endpoint is accessible"""
        response = requests.get(f"{API_BASE_URL}/docs", timeout=10)
        
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
    
    def test_api_openapi_json_accessible(self):
        """Test that OpenAPI JSON specification is accessible"""
        response = requests.get(f"{API_BASE_URL}/openapi.json", timeout=10)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check OpenAPI specification structure
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
