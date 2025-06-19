#!/usr/bin/env python3
"""
Comprehensive test runner for IA Continu Solution
Runs all tests and provides detailed reporting
"""
import subprocess
import sys
import time
import requests
from pathlib import Path

# Test configuration
API_BASE_URL = "http://localhost:8000"
SERVICES_TO_CHECK = [
    ("API", "http://localhost:8000/health"),
    ("Streamlit", "http://localhost:8501"),
    ("MLflow", "http://localhost:5000"),
    ("Prefect", "http://localhost:4200"),
    ("Uptime Kuma", "http://localhost:3001"),
]

def check_service_availability():
    """Check if all required services are running"""
    print("🔍 Checking service availability...")
    
    available_services = []
    unavailable_services = []
    
    for service_name, service_url in SERVICES_TO_CHECK:
        try:
            response = requests.get(service_url, timeout=5)
            if response.status_code in [200, 201, 302]:
                available_services.append(service_name)
                print(f"  ✅ {service_name}: Available")
            else:
                unavailable_services.append(service_name)
                print(f"  ❌ {service_name}: HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            unavailable_services.append(service_name)
            print(f"  ❌ {service_name}: Connection failed - {e}")
    
    print(f"\n📊 Service Status: {len(available_services)}/{len(SERVICES_TO_CHECK)} available")
    
    if unavailable_services:
        print(f"⚠️  Unavailable services: {', '.join(unavailable_services)}")
        print("💡 Make sure all services are running with: docker-compose up -d")
        return False
    
    return True

def run_test_category(category_path, category_name):
    """Run tests for a specific category"""
    print(f"\n🧪 Running {category_name} tests...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            str(category_path),
            "-v",
            "--tb=short",
            "--color=yes"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        if result.returncode == 0:
            print(f"  ✅ {category_name} tests: PASSED")
            return True, result.stdout
        else:
            print(f"  ❌ {category_name} tests: FAILED")
            print(f"  Error output: {result.stderr}")
            return False, result.stdout
            
    except Exception as e:
        print(f"  ❌ {category_name} tests: ERROR - {e}")
        return False, str(e)

def run_all_tests():
    """Run all test categories"""
    print("🚀 Starting comprehensive test suite for IA Continu Solution")
    print("=" * 60)
    
    # Check service availability first
    if not check_service_availability():
        print("\n❌ Cannot run tests - services not available")
        return False
    
    # Wait a moment for services to stabilize
    print("\n⏳ Waiting for services to stabilize...")
    time.sleep(5)
    
    # Test categories to run
    test_categories = [
        ("tests/api/test_health_endpoints.py", "API Health"),
        ("tests/auth/test_authentication.py", "Authentication"),
        ("tests/api/test_prediction_endpoints.py", "ML Predictions"),
        ("tests/integration/test_end_to_end_workflow.py", "Integration"),
    ]
    
    results = []
    total_tests = len(test_categories)
    passed_tests = 0
    
    # Run each test category
    for test_path, test_name in test_categories:
        success, output = run_test_category(test_path, test_name)
        results.append((test_name, success, output))
        if success:
            passed_tests += 1
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, success, output in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:20} {status}")
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"\n🎯 Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 Test suite PASSED - System is ready for production!")
        return True
    else:
        print("⚠️  Test suite FAILED - Please check failed tests and fix issues")
        return False

def main():
    """Main test runner function"""
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test run interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test runner error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
