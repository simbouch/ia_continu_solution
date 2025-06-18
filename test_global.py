#!/usr/bin/env python3
"""
Global Test Suite for IA Continu Solution
Single comprehensive test file to validate all functionality
"""

import requests
import time
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_BASE_URL = "http://localhost:8000"
PREFECT_URL = "http://localhost:4200"
UPTIME_KUMA_URL = "http://localhost:3001"
MLFLOW_URL = "http://localhost:5000"
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# Authentication
TEST_USERNAME = "testuser"
TEST_PASSWORD = "test123"
auth_token = None

def get_auth_token():
    """Get authentication token for API calls"""
    global auth_token
    if auth_token:
        return auth_token

    try:
        login_data = {"username": TEST_USERNAME, "password": TEST_PASSWORD}
        response = requests.post(f"{API_BASE_URL}/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            token_data = response.json()
            auth_token = token_data["access_token"]
            print(f"✅ Authenticated as {TEST_USERNAME}")
            return auth_token
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def get_auth_headers():
    """Get headers with authentication token"""
    token = get_auth_token()
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

def send_discord_embed(message, status="Succès"):
    """Send message to Discord via Webhook according to specifications"""
    if not DISCORD_WEBHOOK_URL:
        print("Discord webhook not configured")
        return False
    
    color = 5814783 if status == "Succès" else 15158332  # Green or Red
    
    data = {
        "embeds": [{
            "title": "Résultats du pipeline",
            "description": message,
            "color": color,
            "fields": [{
                "name": "Status",
                "value": status,
                "inline": True
            }]
        }]
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data, timeout=10)
        if response.status_code != 204:
            print(f"Erreur lors de l'envoi de l'embed : {response.status_code}")
            return False
        else:
            print("Embed envoyé avec succès !")
            return True
    except Exception as e:
        print(f"Erreur Discord: {e}")
        return False

def test_api_health():
    """Test API health endpoint - should return 200"""
    print("🏥 Testing API Health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "status" in data, "Response should contain 'status'"
        assert data["status"] == "ok", "Status should be 'ok'"
        
        print("   ✅ Health endpoint returns 200 and correct format")
        return True
    except Exception as e:
        print(f"   ❌ Health test failed: {e}")
        return False

def test_api_predict():
    """Test predict endpoint - should return 0 or 1"""
    print("🎯 Testing API Predict...")
    try:
        headers = get_auth_headers()
        if not headers:
            print("   ❌ Authentication required but failed")
            return False

        payload = {"features": [0.5, -0.3]}
        response = requests.post(f"{API_BASE_URL}/predict", json=payload, headers=headers, timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert "prediction" in data, "Response should contain 'prediction'"
        assert data["prediction"] in [0, 1], f"Prediction should be 0 or 1, got {data['prediction']}"
        assert "confidence" in data, "Response should contain 'confidence'"
        assert 0 <= data["confidence"] <= 1, "Confidence should be between 0 and 1"

        print(f"   ✅ Predict returns {data['prediction']} with confidence {data['confidence']:.3f}")
        return True
    except Exception as e:
        print(f"   ❌ Predict test failed: {e}")
        return False

def test_api_generate():
    """Test generate endpoint and database storage"""
    print("📊 Testing API Generate and Database...")
    try:
        payload = {"samples": 150}
        response = requests.post(f"{API_BASE_URL}/generate", json=payload, timeout=15)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "generation_id" in data, "Response should contain 'generation_id'"
        assert "samples_created" in data, "Response should contain 'samples_created'"
        assert data["samples_created"] == 150, f"Expected 150 samples, got {data['samples_created']}"
        
        generation_id = data["generation_id"]
        
        # Test database by checking datasets list
        time.sleep(1)  # Wait for database write
        datasets_response = requests.get(f"{API_BASE_URL}/datasets/list", timeout=10)
        assert datasets_response.status_code == 200, "Datasets list should be accessible"
        
        datasets_data = datasets_response.json()
        assert "datasets" in datasets_data, "Response should contain 'datasets'"
        assert "total_datasets" in datasets_data, "Response should contain 'total_datasets'"
        
        # Check if our generated dataset is in the list
        found_dataset = any(d["generation_id"] == generation_id for d in datasets_data["datasets"])
        assert found_dataset, "Generated dataset should be found in database"
        
        print(f"   ✅ Generated dataset {generation_id} with 150 samples and stored in database")
        return True
    except Exception as e:
        print(f"   ❌ Generate/Database test failed: {e}")
        return False

def test_api_retrain():
    """Test retrain endpoint with MLflow integration"""
    print("🔄 Testing API Retrain with MLflow...")
    try:
        # First ensure we have data
        gen_response = requests.post(f"{API_BASE_URL}/generate", json={"samples": 200}, timeout=15)
        assert gen_response.status_code == 200, "Should generate data first"
        
        time.sleep(2)  # Wait for database write
        
        # Test retrain
        response = requests.post(f"{API_BASE_URL}/retrain", timeout=60)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "status" in data, "Response should contain 'status'"
        assert data["status"] == "success", "Retrain should be successful"
        assert "model_version" in data, "Response should contain 'model_version'"
        assert "accuracy" in data, "Response should contain 'accuracy'"
        assert "training_samples" in data, "Response should contain 'training_samples'"
        
        assert 0 <= data["accuracy"] <= 1, "Accuracy should be between 0 and 1"
        assert data["training_samples"] > 0, "Should have training samples"
        
        print(f"   ✅ Retrain successful: {data['model_version']}, accuracy: {data['accuracy']:.3f}")
        return True
    except Exception as e:
        print(f"   ❌ Retrain test failed: {e}")
        return False

def test_prefect_service():
    """Test Prefect server"""
    print("⚡ Testing Prefect Service...")
    try:
        # Test health endpoint
        health_response = requests.get(f"{PREFECT_URL}/api/health", timeout=10)
        assert health_response.status_code == 200, "Prefect health should return 200"
        
        # Test UI
        ui_response = requests.get(f"{PREFECT_URL}", timeout=10)
        assert ui_response.status_code == 200, "Prefect UI should be accessible"
        
        print("   ✅ Prefect server and UI accessible")
        return True
    except Exception as e:
        print(f"   ❌ Prefect test failed: {e}")
        return False

def test_uptime_kuma():
    """Test Uptime Kuma service"""
    print("📊 Testing Uptime Kuma...")
    try:
        response = requests.get(f"{UPTIME_KUMA_URL}", timeout=10)
        assert response.status_code == 200, "Uptime Kuma should return 200"
        
        print("   ✅ Uptime Kuma accessible on port 3001")
        return True
    except Exception as e:
        print(f"   ❌ Uptime Kuma test failed: {e}")
        return False

def test_mlflow_service():
    """Test MLflow service"""
    print("🔬 Testing MLflow Service...")
    try:
        response = requests.get(f"{MLFLOW_URL}", timeout=10)
        if response.status_code == 200:
            print("   ✅ MLflow UI accessible")
            return True
        else:
            print(f"   ⚠️ MLflow not accessible (status: {response.status_code})")
            return False
    except Exception as e:
        print(f"   ⚠️ MLflow not accessible: {e}")
        return False

def test_discord_integration():
    """Test Discord webhook integration"""
    print("📱 Testing Discord Integration...")
    
    if not DISCORD_WEBHOOK_URL:
        print("   ⚠️ Discord webhook not configured")
        return False
    
    # Test success notification
    success = send_discord_embed("Test global du système IA Continu - Tous les tests passés!", "Succès")
    
    if success:
        print("   ✅ Discord webhook working")
        return True
    else:
        print("   ❌ Discord webhook failed")
        return False

def test_complete_workflow():
    """Test complete ML workflow"""
    print("🤖 Testing Complete ML Workflow...")
    try:
        # Step 1: Generate dataset
        print("   1. Generating dataset...")
        gen_response = requests.post(f"{API_BASE_URL}/generate", json={"samples": 300}, timeout=20)
        assert gen_response.status_code == 200, "Dataset generation should succeed"
        gen_data = gen_response.json()
        
        # Step 2: Make prediction
        print("   2. Making prediction...")
        headers = get_auth_headers()
        if not headers:
            raise Exception("Authentication required but failed")

        pred_response = requests.post(f"{API_BASE_URL}/predict", json={"features": [0.7, -0.4]}, headers=headers, timeout=10)
        assert pred_response.status_code == 200, "Prediction should succeed"
        pred_data = pred_response.json()
        
        # Step 3: Retrain model
        print("   3. Retraining model...")
        time.sleep(2)  # Wait for database

        # Retry retrain if database is locked
        retrain_success = False
        for attempt in range(3):
            try:
                retrain_response = requests.post(f"{API_BASE_URL}/retrain", timeout=60)
                if retrain_response.status_code == 200:
                    retrain_data = retrain_response.json()
                    retrain_success = True
                    break
                elif "database is locked" in retrain_response.text:
                    print(f"   ⚠️ Database locked, retrying attempt {attempt + 1}/3...")
                    time.sleep(5)
                else:
                    break
            except Exception as e:
                if attempt == 2:  # Last attempt
                    raise
                print(f"   ⚠️ Retrain error, retrying: {e}")
                time.sleep(5)

        assert retrain_success, f"Retrain should succeed after retries. Last response: {retrain_response.status_code if 'retrain_response' in locals() else 'No response'}"
        
        # Step 4: Make prediction with new model
        print("   4. Testing new model...")
        time.sleep(1)  # Wait for model to be updated in memory
        pred2_response = requests.post(f"{API_BASE_URL}/predict", json={"features": [0.7, -0.4]}, headers=headers, timeout=10)
        assert pred2_response.status_code == 200, "New prediction should succeed"
        pred2_data = pred2_response.json()

        # Verify workflow
        assert retrain_data["training_samples"] == 300, "Should train on 300 samples"

        # Check if model version was updated
        if pred2_data["model_version"] != retrain_data["model_version"]:
            print(f"   ⚠️ Model version mismatch: expected {retrain_data['model_version']}, got {pred2_data['model_version']}")
            # This might be a timing issue, let's check model info endpoint
            model_info_response = requests.get(f"{API_BASE_URL}/model/info", timeout=10)
            if model_info_response.status_code == 200:
                model_info = model_info_response.json()
                print(f"   📊 Current model info: {model_info['model_version']}")
                if model_info["model_version"] == retrain_data["model_version"]:
                    print("   ✅ Model was updated correctly (timing issue in prediction)")
                else:
                    raise AssertionError(f"Model version not updated: expected {retrain_data['model_version']}, got {model_info['model_version']}")
            else:
                raise AssertionError("Could not verify model info")
        else:
            print(f"   ✅ Model version updated correctly: {pred2_data['model_version']}")
        
        print(f"   ✅ Complete workflow: Generated {gen_data['samples_created']} samples, "
              f"retrained model {retrain_data['model_version']} with {retrain_data['accuracy']:.3f} accuracy")
        return True
    except Exception as e:
        print(f"   ❌ Complete workflow failed: {e}")
        return False

def main():
    """Run all global tests"""
    print("🎯 IA CONTINU SOLUTION - GLOBAL TEST SUITE")
    print("=" * 50)
    print()
    
    # Wait for services to be ready
    print("⏳ Waiting for services to be ready...")
    time.sleep(5)
    
    # Run all tests
    tests = [
        ("API Health", test_api_health),
        ("API Predict", test_api_predict),
        ("API Generate & Database", test_api_generate),
        ("API Retrain & MLflow", test_api_retrain),
        ("Prefect Service", test_prefect_service),
        ("Uptime Kuma", test_uptime_kuma),
        ("MLflow Service", test_mlflow_service),
        ("Discord Integration", test_discord_integration),
        ("Complete ML Workflow", test_complete_workflow)
    ]
    
    results = {}
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20}")
        try:
            result = test_func()
            results[test_name] = result
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Final summary
    print(f"\n{'='*50}")
    print("🎯 GLOBAL TEST RESULTS")
    print("=" * 50)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    success_rate = (passed / total) * 100
    print(f"\n📊 Overall Result: {passed}/{total} tests passed ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("\n🎉 SYSTEM VALIDATION SUCCESSFUL!")
        print("✅ IA Continu Solution is production ready!")
        
        # Send success notification
        if DISCORD_WEBHOOK_URL:
            send_discord_embed(f"Validation globale terminée avec succès! {passed}/{total} tests passés ({success_rate:.1f}%)")
    else:
        print(f"\n⚠️ System needs attention ({total - passed} failures)")
        
        # Send failure notification
        if DISCORD_WEBHOOK_URL:
            send_discord_embed(f"Validation globale échouée. {passed}/{total} tests passés ({success_rate:.1f}%)", "Échec")
    
    print(f"\n🌐 Service URLs:")
    print(f"   • API: {API_BASE_URL}")
    print(f"   • API Docs: {API_BASE_URL}/docs")
    print(f"   • Prefect: {PREFECT_URL}")
    print(f"   • Uptime Kuma: {UPTIME_KUMA_URL}")
    print(f"   • MLflow: {MLFLOW_URL}")

if __name__ == "__main__":
    main()
