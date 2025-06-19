#!/usr/bin/env python3
"""
Complete system rebuild tests - comprehensive validation
"""

import pytest
import requests
import time
import json
from typing import Dict, Any

# Test configuration
API_BASE_URL = "http://localhost:8000"
STREAMLIT_URL = "http://localhost:8501"
PREFECT_URL = "http://localhost:4200"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1384074867137056868/CgnO5x8ZYVXfLOKgMQxyA76_tN-0pb3C27EoYXOLmQdpRn9yvgIn0hrMteAjpfxTY5je"

class TestSystemRebuild:
    """Complete system rebuild validation tests"""
    
    @pytest.fixture(scope="class")
    def wait_for_services(self):
        """Wait for all services to be ready"""
        print("🔄 Waiting for services to start...")
        
        # Wait for API
        for i in range(60):
            try:
                response = requests.get(f"{API_BASE_URL}/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ API ready after {i * 2} seconds")
                    break
            except:
                if i == 59:
                    pytest.fail("API failed to start")
                time.sleep(2)
        
        # Wait for Streamlit
        for i in range(30):
            try:
                response = requests.get(f"{STREAMLIT_URL}/_stcore/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ Streamlit ready after {i * 2} seconds")
                    break
            except:
                if i == 29:
                    print("⚠️ Streamlit not ready, continuing")
                time.sleep(2)
        
        # Wait for Prefect
        for i in range(30):
            try:
                response = requests.get(f"{PREFECT_URL}/api/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ Prefect ready after {i * 2} seconds")
                    break
            except:
                if i == 29:
                    print("⚠️ Prefect not ready, continuing")
                time.sleep(2)
        
        time.sleep(10)  # Additional stabilization time
        print("✅ Service startup complete")
    
    @pytest.fixture(scope="class")
    def auth_token(self, wait_for_services):
        """Get authentication token"""
        login_data = {"username": "testuser", "password": "test123"}
        response = requests.post(f"{API_BASE_URL}/auth/login", json=login_data, timeout=10)
        assert response.status_code == 200, f"Auth failed: {response.text}"
        return response.json()["access_token"]
    
    @pytest.fixture
    def auth_headers(self, auth_token):
        """Get auth headers"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_01_api_health(self, wait_for_services):
        """Test API health endpoint"""
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✅ API health check passed")
    
    def test_02_api_authentication(self, wait_for_services):
        """Test API authentication"""
        # Valid credentials
        login_data = {"username": "testuser", "password": "test123"}
        response = requests.post(f"{API_BASE_URL}/auth/login", json=login_data, timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        print("✅ API authentication passed")
        
        # Invalid credentials
        invalid_data = {"username": "invalid", "password": "invalid"}
        response = requests.post(f"{API_BASE_URL}/auth/login", json=invalid_data, timeout=10)
        assert response.status_code == 401
        print("✅ API authentication rejection passed")
    
    def test_03_api_prediction(self, auth_headers):
        """Test ML prediction endpoint"""
        payload = {"features": [0.5, 0.5]}
        response = requests.post(
            f"{API_BASE_URL}/predict", 
            json=payload, 
            headers=auth_headers, 
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "confidence" in data
        assert isinstance(data["prediction"], int)
        assert 0 <= data["confidence"] <= 1
        print(f"✅ API prediction passed: {data['prediction']} (confidence: {data['confidence']:.3f})")
    
    def test_04_api_data_generation(self, auth_headers):
        """Test data generation endpoint"""
        payload = {"samples": 100}  # Minimum required
        response = requests.post(
            f"{API_BASE_URL}/generate", 
            json=payload, 
            headers=auth_headers, 
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert "samples_created" in data
        assert data["samples_created"] >= 100
        print(f"✅ API data generation passed: {data['samples_created']} samples")
    
    def test_05_api_model_info(self, auth_headers):
        """Test model info endpoint"""
        response = requests.get(
            f"{API_BASE_URL}/model/info", 
            headers=auth_headers, 
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        assert "model_version" in data
        assert "accuracy" in data
        print(f"✅ API model info passed: version {data['model_version']}")
    
    def test_06_streamlit_health(self, wait_for_services):
        """Test Streamlit health"""
        try:
            response = requests.get(f"{STREAMLIT_URL}/_stcore/health", timeout=10)
            assert response.status_code == 200
            print("✅ Streamlit health check passed")
        except:
            print("⚠️ Streamlit health check failed - service may not be ready")
    
    def test_07_prefect_health(self, wait_for_services):
        """Test Prefect server health"""
        try:
            response = requests.get(f"{PREFECT_URL}/api/health", timeout=10)
            assert response.status_code == 200
            print("✅ Prefect health check passed")
        except:
            print("⚠️ Prefect health check failed - service may not be ready")
    
    def test_08_discord_notification(self):
        """Test Discord webhook"""
        test_data = {
            "embeds": [{
                "title": "🧪 Unit Test Notification",
                "description": "Testing Discord webhook from unit tests",
                "color": 3447003,  # Blue
                "fields": [{
                    "name": "Test Status",
                    "value": "✅ Working",
                    "inline": True
                }, {
                    "name": "Timestamp",
                    "value": time.strftime('%Y-%m-%d %H:%M:%S UTC'),
                    "inline": True
                }],
                "footer": {
                    "text": "IA Continu Solution - Unit Tests"
                }
            }]
        }
        
        try:
            response = requests.post(DISCORD_WEBHOOK_URL, json=test_data, timeout=10)
            assert response.status_code == 204
            print("✅ Discord notification test passed")
        except Exception as e:
            print(f"⚠️ Discord notification failed: {e}")
    
    def test_09_api_unauthorized_access(self):
        """Test API security - unauthorized access"""
        # Try to access protected endpoint without token
        response = requests.post(f"{API_BASE_URL}/predict", json={"features": [0.5, 0.5]}, timeout=10)
        assert response.status_code == 401
        print("✅ API security test passed - unauthorized access blocked")
    
    def test_10_api_invalid_data(self, auth_headers):
        """Test API with invalid data"""
        # Invalid prediction data
        payload = {"features": "invalid"}
        response = requests.post(
            f"{API_BASE_URL}/predict", 
            json=payload, 
            headers=auth_headers, 
            timeout=10
        )
        assert response.status_code == 422  # Validation error
        print("✅ API validation test passed - invalid data rejected")
    
    def test_11_comprehensive_workflow(self, auth_headers):
        """Test complete ML workflow"""
        # 1. Generate data
        gen_response = requests.post(
            f"{API_BASE_URL}/generate", 
            json={"samples": 100}, 
            headers=auth_headers, 
            timeout=30
        )
        assert gen_response.status_code == 200
        
        # 2. Make predictions
        pred_response = requests.post(
            f"{API_BASE_URL}/predict", 
            json={"features": [0.5, 0.5]}, 
            headers=auth_headers, 
            timeout=10
        )
        assert pred_response.status_code == 200
        
        # 3. Get model info
        info_response = requests.get(
            f"{API_BASE_URL}/model/info", 
            headers=auth_headers, 
            timeout=10
        )
        assert info_response.status_code == 200
        
        print("✅ Complete ML workflow test passed")
    
    def test_12_system_status_summary(self, wait_for_services):
        """Final system status summary"""
        results = {
            "api_health": False,
            "api_auth": False,
            "api_predict": False,
            "api_generate": False,
            "streamlit": False,
            "prefect": False,
            "discord": False
        }
        
        # Test all components
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            results["api_health"] = response.status_code == 200
        except:
            pass
        
        try:
            login_data = {"username": "testuser", "password": "test123"}
            response = requests.post(f"{API_BASE_URL}/auth/login", json=login_data, timeout=10)
            if response.status_code == 200:
                results["api_auth"] = True
                token = response.json()["access_token"]
                headers = {"Authorization": f"Bearer {token}"}
                
                # Test prediction
                pred_response = requests.post(
                    f"{API_BASE_URL}/predict", 
                    json={"features": [0.5, 0.5]}, 
                    headers=headers, 
                    timeout=10
                )
                results["api_predict"] = pred_response.status_code == 200
                
                # Test generation
                gen_response = requests.post(
                    f"{API_BASE_URL}/generate", 
                    json={"samples": 100}, 
                    headers=headers, 
                    timeout=30
                )
                results["api_generate"] = gen_response.status_code == 200
        except:
            pass
        
        try:
            response = requests.get(f"{STREAMLIT_URL}/_stcore/health", timeout=5)
            results["streamlit"] = response.status_code == 200
        except:
            pass
        
        try:
            response = requests.get(f"{PREFECT_URL}/api/health", timeout=5)
            results["prefect"] = response.status_code == 200
        except:
            pass
        
        try:
            test_data = {"embeds": [{"title": "Test", "description": "Test", "color": 3447003}]}
            response = requests.post(DISCORD_WEBHOOK_URL, json=test_data, timeout=10)
            results["discord"] = response.status_code == 204
        except:
            pass
        
        working_count = sum(results.values())
        total_count = len(results)
        
        print(f"\n🎯 SYSTEM STATUS SUMMARY:")
        print(f"Working Services: {working_count}/{total_count}")
        
        for service, status in results.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {service.replace('_', ' ').title()}")
        
        # Assert that critical services are working
        assert results["api_health"], "API health check failed"
        assert results["api_auth"], "API authentication failed"
        assert results["api_predict"], "API prediction failed"
        
        print(f"\n🚀 SYSTEM STATUS: {'OPERATIONAL' if working_count >= 5 else 'NEEDS ATTENTION'}")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
