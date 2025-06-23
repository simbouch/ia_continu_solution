#!/usr/bin/env python3
"""
Metrics Generator for IA Continu Solution Template
Generates realistic metrics for Prometheus monitoring
"""

import time
import random
import requests
from datetime import datetime
import os

# Configuration
API_URL = os.getenv("API_URL", "http://api:8000")
PROMETHEUS_GATEWAY = os.getenv("PROMETHEUS_GATEWAY", "http://prometheus:9091")

def generate_api_metrics():
    """Generate API performance metrics"""
    try:
        # Make some API calls to generate real metrics
        token_response = requests.post(
            f"{API_URL}/auth/login",
            json={"username": "testuser", "password": "test123"},
            timeout=5
        )
        
        if token_response.status_code == 200:
            token = token_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Generate some predictions
            for i in range(random.randint(3, 8)):
                features = [random.uniform(-2, 2), random.uniform(-2, 2)]
                requests.post(
                    f"{API_URL}/predict",
                    json={"features": features},
                    headers=headers,
                    timeout=5
                )
                time.sleep(0.5)
            
            # Check health
            requests.get(f"{API_URL}/health", timeout=5)
            
            print(f"✅ Generated API metrics at {datetime.now()}")
            return True
            
    except Exception as e:
        print(f"❌ Error generating API metrics: {e}")
        return False

def generate_ml_metrics():
    """Generate ML-specific metrics"""
    try:
        # Simulate ML metrics
        metrics = {
            "model_accuracy": random.uniform(0.85, 0.98),
            "prediction_latency": random.uniform(10, 100),
            "drift_score": random.uniform(0.0, 0.8),
            "data_quality": random.uniform(0.80, 1.0),
            "training_samples": random.randint(800, 1200),
        }
        
        print(f"📊 ML Metrics: Accuracy={metrics['model_accuracy']:.3f}, "
              f"Latency={metrics['prediction_latency']:.1f}ms, "
              f"Drift={metrics['drift_score']:.3f}")
        
        return metrics
        
    except Exception as e:
        print(f"❌ Error generating ML metrics: {e}")
        return None

def generate_system_metrics():
    """Generate system performance metrics"""
    try:
        # Simulate system metrics
        metrics = {
            "cpu_usage": random.uniform(20, 80),
            "memory_usage": random.uniform(40, 85),
            "disk_usage": random.uniform(30, 70),
            "network_io": random.uniform(100, 1000),
            "active_connections": random.randint(5, 50),
        }
        
        print(f"🖥️ System Metrics: CPU={metrics['cpu_usage']:.1f}%, "
              f"Memory={metrics['memory_usage']:.1f}%, "
              f"Connections={metrics['active_connections']}")
        
        return metrics
        
    except Exception as e:
        print(f"❌ Error generating system metrics: {e}")
        return None

def check_service_health():
    """Check health of all services"""
    services = {
        "api": f"{API_URL}/health",
        "streamlit": "http://streamlit:8501/_stcore/health",
        "mlflow": "http://mlflow:5000/",
        "uptime_kuma": "http://uptime-kuma:3001/",
    }
    
    health_status = {}
    
    for service, url in services.items():
        try:
            response = requests.get(url, timeout=3)
            health_status[service] = 1 if response.status_code == 200 else 0
        except:
            health_status[service] = 0
    
    healthy_count = sum(health_status.values())
    total_count = len(health_status)
    
    print(f"🏥 Service Health: {healthy_count}/{total_count} services healthy")
    
    return health_status

def run_metrics_cycle():
    """Run one complete metrics generation cycle"""
    print(f"🔄 Running metrics generation cycle at {datetime.now()}")
    
    # Generate different types of metrics
    api_success = generate_api_metrics()
    ml_metrics = generate_ml_metrics()
    system_metrics = generate_system_metrics()
    service_health = check_service_health()
    
    # Log summary
    print(f"📈 Metrics cycle completed - API: {'✅' if api_success else '❌'}, "
          f"ML: {'✅' if ml_metrics else '❌'}, "
          f"System: {'✅' if system_metrics else '❌'}")
    
    return {
        "api_success": api_success,
        "ml_metrics": ml_metrics,
        "system_metrics": system_metrics,
        "service_health": service_health,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("📊 Starting Metrics Generator for IA Continu Solution Template")
    print("=" * 60)
    
    cycle_count = 0
    
    while True:
        try:
            result = run_metrics_cycle()
            cycle_count += 1
            
            # Log periodic summary
            if cycle_count % 10 == 0:
                print(f"\n📊 Metrics Summary - {cycle_count} cycles completed")
                print(f"⏱️ Running for {cycle_count * 60 // 60} minutes")
                print(f"🔄 Next summary in 10 cycles\n")
            
        except Exception as e:
            print(f"❌ Metrics generation error: {e}")
        
        print(f"⏳ Waiting 60 seconds... (Cycle #{cycle_count} completed)")
        time.sleep(60)  # Run every minute
