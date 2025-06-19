"""
Test configuration and fixtures for IA Continu Solution
"""
import pytest
import requests
import os
from typing import Dict, Any

# Test configuration
API_BASE_URL = "http://localhost:8000"
STREAMLIT_URL = "http://localhost:8501"
MLFLOW_URL = "http://localhost:5000"
PREFECT_URL = "http://localhost:4200"
UPTIME_KUMA_URL = "http://localhost:3001"

# Default test credentials
TEST_USER = {
    "username": "testuser",
    "password": "test123"
}

ADMIN_USER = {
    "username": "admin", 
    "password": "admin123"
}

@pytest.fixture(scope="session")
def api_base_url():
    """Base URL for API endpoints"""
    return API_BASE_URL

@pytest.fixture(scope="session")
def test_user_credentials():
    """Test user credentials"""
    return TEST_USER

@pytest.fixture(scope="session")
def admin_user_credentials():
    """Admin user credentials"""
    return ADMIN_USER

@pytest.fixture(scope="session")
def auth_token():
    """Get authentication token for test user"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json=TEST_USER,
            timeout=10
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            pytest.skip(f"Cannot get auth token: {response.status_code}")
    except Exception as e:
        pytest.skip(f"Cannot connect to API for auth: {e}")

@pytest.fixture(scope="session")
def admin_auth_token():
    """Get authentication token for admin user"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json=ADMIN_USER,
            timeout=10
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            pytest.skip(f"Cannot get admin auth token: {response.status_code}")
    except Exception as e:
        pytest.skip(f"Cannot connect to API for admin auth: {e}")

@pytest.fixture
def auth_headers(auth_token):
    """Headers with authentication token"""
    return {"Authorization": f"Bearer {auth_token}"}

@pytest.fixture
def admin_auth_headers(admin_auth_token):
    """Headers with admin authentication token"""
    return {"Authorization": f"Bearer {admin_auth_token}"}

@pytest.fixture
def sample_prediction_data():
    """Sample data for prediction testing"""
    return {"features": [0.5, 0.5]}

@pytest.fixture
def sample_generation_data():
    """Sample data for data generation testing"""
    return {"samples": 100}

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "api: mark test as API test"
    )
    config.addinivalue_line(
        "markers", "auth: mark test as authentication test"
    )
    config.addinivalue_line(
        "markers", "ml: mark test as ML functionality test"
    )
    config.addinivalue_line(
        "markers", "monitoring: mark test as monitoring test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on file location"""
    for item in items:
        # Add markers based on test file location
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "api" in str(item.fspath):
            item.add_marker(pytest.mark.api)
        elif "auth" in str(item.fspath):
            item.add_marker(pytest.mark.auth)
        elif "ml" in str(item.fspath):
            item.add_marker(pytest.mark.ml)
        elif "monitoring" in str(item.fspath):
            item.add_marker(pytest.mark.monitoring)
