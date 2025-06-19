#!/usr/bin/env python3
"""
System Test for IA Continu Solution
Tests all components that should be working
"""

import requests
import json
import time
import sys
from pathlib import Path

def test_api_health():
    """Test API health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API Health: OK")
            return True
        else:
            print(f"❌ API Health: Failed ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ API Health: Error - {e}")
        return False

def test_api_authentication():
    """Test API authentication"""
    try:
        login_data = {"username": "testuser", "password": "test123"}
        response = requests.post("http://localhost:8000/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("✅ API Authentication: OK")
            return token
        else:
            print(f"❌ API Authentication: Failed ({response.status_code})")
            return None
    except Exception as e:
        print(f"❌ API Authentication: Error - {e}")
        return None

def test_api_prediction(token):
    """Test API prediction endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"features": [0.5, 0.5]}
        response = requests.post("http://localhost:8000/predict", json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API Prediction: OK (prediction: {result['prediction']}, confidence: {result['confidence']:.3f})")
            return True
        else:
            print(f"❌ API Prediction: Failed ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ API Prediction: Error - {e}")
        return False

def test_api_data_generation(token):
    """Test API data generation endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"samples": 100}
        response = requests.post("http://localhost:8000/generate", json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API Data Generation: OK (generated {result['samples_created']} samples)")
            return True
        else:
            print(f"❌ API Data Generation: Failed ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ API Data Generation: Error - {e}")
        return False

def test_streamlit():
    """Test Streamlit interface"""
    try:
        response = requests.get("http://localhost:8501/_stcore/health", timeout=5)
        if response.status_code == 200:
            print("✅ Streamlit Interface: OK")
            return True
        else:
            print(f"❌ Streamlit Interface: Failed ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Streamlit Interface: Error - {e}")
        return False

def test_mlflow():
    """Test MLflow service"""
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        if response.status_code == 200:
            print("✅ MLflow Service: OK")
            return True
        else:
            print(f"❌ MLflow Service: Failed ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ MLflow Service: Error - {e}")
        return False

def test_prefect():
    """Test Prefect service"""
    try:
        response = requests.get("http://localhost:4200/api/ready", timeout=5)
        if response.status_code == 200:
            print("✅ Prefect Service: OK")
            return True
        else:
            print(f"❌ Prefect Service: Failed ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Prefect Service: Error - {e}")
        return False

def test_uptime_kuma():
    """Test Uptime Kuma service"""
    try:
        response = requests.get("http://localhost:3001/", timeout=5)
        if response.status_code == 200:
            print("✅ Uptime Kuma: OK")
            return True
        else:
            print(f"❌ Uptime Kuma: Failed ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Uptime Kuma: Error - {e}")
        return False

def main():
    """Run comprehensive system test"""
    print("🚀 IA Continu Solution - System Test")
    print("=" * 50)
    
    results = {}
    
    # Test API components
    print("\n📡 Testing API Components...")
    results['api_health'] = test_api_health()
    
    if results['api_health']:
        token = test_api_authentication()
        if token:
            results['api_auth'] = True
            results['api_prediction'] = test_api_prediction(token)
            results['api_generation'] = test_api_data_generation(token)
        else:
            results['api_auth'] = False
            results['api_prediction'] = False
            results['api_generation'] = False
    else:
        results['api_auth'] = False
        results['api_prediction'] = False
        results['api_generation'] = False
    
    # Test UI components
    print("\n🎨 Testing UI Components...")
    results['streamlit'] = test_streamlit()
    
    # Test ML components
    print("\n🤖 Testing ML Components...")
    results['mlflow'] = test_mlflow()
    
    # Test orchestration components
    print("\n🔄 Testing Orchestration Components...")
    results['prefect'] = test_prefect()
    
    # Test monitoring components
    print("\n📊 Testing Monitoring Components...")
    results['uptime_kuma'] = test_uptime_kuma()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! System is fully operational.")
        return 0
    elif passed_tests >= total_tests * 0.7:
        print("⚠️  Most tests passed. System is mostly operational.")
        return 0
    else:
        print("❌ Many tests failed. System needs attention.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
