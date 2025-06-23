#!/usr/bin/env python3
"""
Generate monitoring activity for IA Continu Solution
Creates API calls, predictions, and data generation to populate dashboards
"""

from datetime import datetime
import random
import time

import requests


def get_auth_token():
    """Get authentication token"""
    try:
        response = requests.post(
            "http://localhost:8000/auth/login",
            json={"username": "admin", "password": "admin123"},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None


def make_predictions(token, count=10):
    """Generate multiple predictions"""
    headers = {"Authorization": f"Bearer {token}"}
    predictions = []

    print(f"🔮 Generating {count} predictions...")

    for i in range(count):
        try:
            features = [random.uniform(-3, 3), random.uniform(-3, 3)]
            response = requests.post(
                "http://localhost:8000/predict",
                json={"features": features},
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                pred_data = response.json()
                predictions.append(pred_data)
                print(f"  ✅ Prediction {i+1}: {pred_data['prediction']} (confidence: {pred_data['confidence']:.3f})")
            else:
                print(f"  ❌ Prediction {i+1} failed: {response.status_code}")

            time.sleep(0.5)  # Small delay between requests

        except Exception as e:
            print(f"  ❌ Prediction {i+1} error: {e}")

    return predictions


def generate_data(token, samples=200):
    """Generate training data"""
    headers = {"Authorization": f"Bearer {token}"}

    print(f"📊 Generating {samples} training samples...")

    try:
        generation_id = random.randint(10000, 99999)
        response = requests.post(
            "http://localhost:8000/generate",
            json={"samples": samples, "generation_id": generation_id},
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Generated {result.get('samples_created', 0)} samples with ID {generation_id}")
            return result
        else:
            print(f"  ❌ Data generation failed: {response.status_code}")
            return None

    except Exception as e:
        print(f"  ❌ Data generation error: {e}")
        return None


def check_services():
    """Check all service health"""
    services = [
        ("API", "http://localhost:8000/health"),
        ("MLflow", "http://localhost:5000"),
        ("Prefect", "http://localhost:4200/api/ready"),
        ("Streamlit", "http://localhost:8501"),
        ("Uptime Kuma", "http://localhost:3001"),
        ("Prometheus", "http://localhost:9090"),
        ("Grafana", "http://localhost:3000"),
    ]

    print("🏥 Checking service health...")

    for name, url in services:
        try:
            response = requests.get(url, timeout=5)
            status = "✅ UP" if response.status_code in [200, 404] else f"⚠️ {response.status_code}"
            print(f"  {name}: {status}")
        except Exception as e:
            print(f"  {name}: ❌ DOWN ({e})")


def check_metrics():
    """Check custom ML metrics"""
    print("📊 Checking ML metrics...")

    try:
        response = requests.get("http://localhost:8000/ml-metrics", timeout=10)
        if response.status_code == 200:
            print("  ✅ ML metrics endpoint working")
            # Print first few lines of metrics
            lines = response.text.split('\n')[:10]
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    print(f"    {line}")
        else:
            print(f"  ❌ ML metrics failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ ML metrics error: {e}")


def main():
    """Main function to generate monitoring activity"""
    print("🚀 Starting monitoring activity generation...")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Check services first
    check_services()
    print()

    # Get authentication token
    token = get_auth_token()
    if not token:
        print("❌ Cannot proceed without authentication token")
        return

    print("✅ Authentication successful")
    print()

    # Generate predictions
    predictions = make_predictions(token, count=15)
    print(f"📈 Generated {len(predictions)} predictions")
    print()

    # Generate training data
    data_result = generate_data(token, samples=300)
    if data_result:
        print("📊 Data generation successful")
    print()

    # Check ML metrics
    check_metrics()
    print()

    # Generate some more predictions with different patterns
    print("🔄 Generating additional prediction patterns...")

    # High confidence predictions
    for _i in range(5):
        features = [random.uniform(1, 3), random.uniform(1, 3)]  # Likely positive
        try:
            response = requests.post(
                "http://localhost:8000/predict",
                json={"features": features},
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            if response.status_code == 200:
                pred = response.json()
                print(f"  High confidence: {pred['prediction']} ({pred['confidence']:.3f})")
        except:
            pass
        time.sleep(0.3)

    # Low confidence predictions
    for _i in range(5):
        features = [random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)]  # Near boundary
        try:
            response = requests.post(
                "http://localhost:8000/predict",
                json={"features": features},
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            if response.status_code == 200:
                pred = response.json()
                print(f"  Low confidence: {pred['prediction']} ({pred['confidence']:.3f})")
        except:
            pass
        time.sleep(0.3)

    print()
    print("🎉 Monitoring activity generation completed!")
    print("📊 Check the following dashboards:")
    print("  • Prefect UI: http://localhost:4200")
    print("  • Prometheus: http://localhost:9090")
    print("  • Grafana: http://localhost:3000")
    print("  • Uptime Kuma: http://localhost:3001")
    print("  • Streamlit: http://localhost:8501")


if __name__ == "__main__":
    main()
