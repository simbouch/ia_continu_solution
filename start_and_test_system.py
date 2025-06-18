#!/usr/bin/env python3
"""
Start and Test Complete System
Script pour démarrer et tester l'ensemble du système Jour 3
"""

import subprocess
import time
import requests
import sys
import os
from pathlib import Path

def check_docker_compose():
    """Vérifier que Docker Compose est disponible"""
    try:
        result = subprocess.run(["docker-compose", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker Compose available: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker Compose not found")
            return False
    except FileNotFoundError:
        print("❌ Docker Compose not installed")
        return False

def initialize_database():
    """Initialiser la base de données"""
    print("🔄 Initializing database...")
    
    try:
        # Initialize auth tables
        result = subprocess.run(["python", "init_auth.py"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Auth tables initialized")
        else:
            print(f"❌ Auth initialization failed: {result.stderr}")
            return False
        
        # Initialize logging tables
        result = subprocess.run(["python", "init_logging.py"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Logging tables initialized")
        else:
            print(f"❌ Logging initialization failed: {result.stderr}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        return False

def start_docker_services():
    """Démarrer les services Docker"""
    print("🚀 Starting Docker services...")
    
    try:
        # Stop any existing services
        subprocess.run(["docker-compose", "down"], capture_output=True)
        
        # Start services
        result = subprocess.run(["docker-compose", "up", "-d"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker services started")
            return True
        else:
            print(f"❌ Failed to start Docker services: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Docker startup error: {e}")
        return False

def wait_for_services():
    """Attendre que les services soient prêts"""
    print("⏳ Waiting for services to be ready...")
    
    services = [
        ("FastAPI", "http://localhost:8000/health"),
        ("Streamlit", "http://localhost:8501"),
        ("Prometheus", "http://localhost:9090"),
        ("Grafana", "http://localhost:3000"),
        ("Uptime Kuma", "http://localhost:3001"),
        ("MLflow", "http://localhost:5000"),
        ("Prefect", "http://localhost:4200")
    ]
    
    max_wait = 120  # 2 minutes
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        all_ready = True
        
        for service_name, url in services:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code not in [200, 302]:
                    all_ready = False
                    break
            except:
                all_ready = False
                break
        
        if all_ready:
            print("✅ All services are ready!")
            return True
        
        print("⏳ Services still starting...")
        time.sleep(10)
    
    print("❌ Services did not start within timeout")
    return False

def run_tests():
    """Exécuter les tests"""
    print("🧪 Running comprehensive tests...")
    
    # Run Day 3 specific tests
    print("\n📋 Running Day 3 Feature Tests:")
    result1 = subprocess.run(["python", "tests/test_day3_features.py"], capture_output=True, text=True)
    
    if result1.returncode == 0:
        print("✅ Day 3 feature tests passed")
    else:
        print("❌ Day 3 feature tests failed")
        print(result1.stdout)
        print(result1.stderr)
    
    # Run complete system test
    print("\n📋 Running Complete System Test:")
    result2 = subprocess.run(["python", "test_complete_day3.py"], capture_output=True, text=True)
    
    if result2.returncode == 0:
        print("✅ Complete system tests passed")
    else:
        print("❌ Complete system tests failed")
        print(result2.stdout)
        print(result2.stderr)
    
    return result1.returncode == 0 and result2.returncode == 0

def show_service_urls():
    """Afficher les URLs des services"""
    print("\n🔗 Service URLs:")
    print("=" * 40)
    print("🌐 FastAPI API:      http://localhost:8000")
    print("🎨 Streamlit UI:     http://localhost:8501")
    print("📊 Prometheus:       http://localhost:9090")
    print("📈 Grafana:          http://localhost:3000 (admin/admin123)")
    print("📡 Uptime Kuma:      http://localhost:3001")
    print("🔬 MLflow:           http://localhost:5000")
    print("⚡ Prefect:          http://localhost:4200")
    print("=" * 40)

def show_authentication_info():
    """Afficher les informations d'authentification"""
    print("\n🔐 Authentication Info:")
    print("=" * 40)
    print("👤 Admin User:       admin / admin123")
    print("👤 Test User:        testuser / test123")
    print("🔑 Use these credentials to login via:")
    print("   - Streamlit UI")
    print("   - Direct API calls to /auth/login")
    print("=" * 40)

def check_environment():
    """Vérifier l'environnement"""
    print("🔍 Checking environment...")
    
    # Check if .env file exists
    if not Path(".env").exists():
        print("⚠️  .env file not found, creating default...")
        with open(".env", "w") as f:
            f.write("DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_here\n")
        print("✅ Default .env file created")
    
    # Check required directories
    for dir_name in ["data", "models", "logs"]:
        Path(dir_name).mkdir(exist_ok=True)
    
    print("✅ Environment check completed")

def main():
    """Fonction principale"""
    print("🚀 IA Continu Solution - Day 3 Complete System Startup")
    print("=" * 60)
    
    # 1. Check environment
    check_environment()
    
    # 2. Check Docker Compose
    if not check_docker_compose():
        print("❌ Docker Compose is required. Please install Docker Desktop.")
        return False
    
    # 3. Initialize database
    if not initialize_database():
        print("❌ Database initialization failed")
        return False
    
    # 4. Start Docker services
    if not start_docker_services():
        print("❌ Failed to start Docker services")
        return False
    
    # 5. Wait for services
    if not wait_for_services():
        print("❌ Services failed to start properly")
        return False
    
    # 6. Show service information
    show_service_urls()
    show_authentication_info()
    
    # 7. Ask user if they want to run tests
    print("\n🧪 Would you like to run the test suite? (y/n): ", end="")
    try:
        choice = input().lower().strip()
        if choice in ['y', 'yes']:
            success = run_tests()
            if success:
                print("\n🎉 All tests passed! System is fully functional.")
            else:
                print("\n⚠️  Some tests failed. Check the output above.")
        else:
            print("\n✅ System started successfully. You can run tests manually later.")
    except KeyboardInterrupt:
        print("\n\n✅ System started successfully.")
    
    print("\n📚 Next Steps:")
    print("1. Open Streamlit UI: http://localhost:8501")
    print("2. Login with admin/admin123 or testuser/test123")
    print("3. Test the ML prediction interface")
    print("4. Check monitoring dashboards")
    print("5. Run manual tests: python test_complete_day3.py")
    
    print("\n🛑 To stop all services: docker-compose down")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 Startup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
