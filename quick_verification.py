#!/usr/bin/env python3
"""
Quick verification that all systems are working
"""

import requests
import time

def quick_test():
    """Quick test of all endpoints"""
    print("🚀 QUICK SYSTEM VERIFICATION")
    print("=" * 30)
    
    base_url = "http://localhost:8000"
    
    tests = [
        ("Health", "GET", "/health", None),
        ("Predict", "POST", "/predict", {"features": [0.5, -0.3]}),
        ("Generate", "POST", "/generate", {"samples": 100}),
        ("Datasets", "GET", "/datasets/list", None),
        ("Model Info", "GET", "/model/info", None),
    ]
    
    passed = 0
    
    for name, method, endpoint, data in tests:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            else:
                response = requests.post(f"{base_url}{endpoint}", json=data, timeout=15)
            
            if response.status_code == 200:
                print(f"✅ {name}: OK")
                passed += 1
            else:
                print(f"❌ {name}: {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: {e}")
    
    # Test retrain separately
    print("\n🔄 Testing Retrain...")
    try:
        time.sleep(1)  # Wait for database
        retrain_response = requests.post(f"{base_url}/retrain", timeout=30)
        if retrain_response.status_code == 200:
            data = retrain_response.json()
            print(f"✅ Retrain: OK (accuracy: {data['accuracy']:.3f})")
            passed += 1
        else:
            print(f"❌ Retrain: {retrain_response.status_code}")
    except Exception as e:
        print(f"❌ Retrain: {e}")
    
    # Test other services
    print("\n📊 Testing Other Services...")
    
    services = [
        ("Prefect", "http://localhost:4200/api/health"),
        ("Uptime Kuma", "http://localhost:3001"),
    ]
    
    for name, url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: OK")
                passed += 1
            else:
                print(f"❌ {name}: {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: {e}")
    
    total = len(tests) + 1 + len(services)  # +1 for retrain
    success_rate = (passed / total) * 100
    
    print(f"\n📊 Result: {passed}/{total} tests passed ({success_rate:.1f}%)")
    
    if success_rate >= 85:
        print("🎉 SYSTEM IS WORKING EXCELLENTLY!")
    elif success_rate >= 70:
        print("✅ System is working well")
    else:
        print("⚠️ System needs attention")

if __name__ == "__main__":
    quick_test()
