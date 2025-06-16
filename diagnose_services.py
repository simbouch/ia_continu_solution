#!/usr/bin/env python3
"""
Script de diagnostic pour identifier les problèmes de connectivité
"""

import requests
import time
import socket
from datetime import datetime

def check_port_open(host, port):
    """Vérifier si un port est ouvert"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def test_prefect_connectivity():
    """Test détaillé de la connectivité Prefect"""
    print("🔍 Diagnostic Prefect Server")
    print("-" * 40)
    
    # Test 1: Port ouvert
    port_open = check_port_open('localhost', 4200)
    print(f"Port 4200 ouvert: {'✅' if port_open else '❌'}")
    
    if not port_open:
        print("❌ Le port 4200 n'est pas accessible")
        return False
    
    # Test 2: Accès HTTP de base
    try:
        response = requests.get("http://localhost:4200", timeout=5)
        print(f"HTTP localhost:4200: ✅ Status {response.status_code}")
    except Exception as e:
        print(f"HTTP localhost:4200: ❌ {e}")
        return False
    
    # Test 3: API Health
    api_urls = [
        "http://localhost:4200/api/health",
        "http://127.0.0.1:4200/api/health",
        "http://0.0.0.0:4200/api/health"
    ]
    
    for url in api_urls:
        try:
            response = requests.get(url, timeout=5)
            print(f"API {url}: ✅ Status {response.status_code}")
            return True
        except Exception as e:
            print(f"API {url}: ❌ {e}")
    
    return False

def test_fastapi_connectivity():
    """Test détaillé de la connectivité FastAPI"""
    print("\n🚀 Diagnostic FastAPI")
    print("-" * 40)
    
    # Test port
    port_open = check_port_open('localhost', 9000)
    print(f"Port 9000 ouvert: {'✅' if port_open else '❌'}")
    
    if not port_open:
        print("❌ Le port 9000 n'est pas accessible")
        return False
    
    # Test endpoints
    endpoints = [
        "http://localhost:9000/health",
        "http://localhost:9000/",
        "http://localhost:9000/docs"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=5)
            print(f"{endpoint}: ✅ Status {response.status_code}")
        except Exception as e:
            print(f"{endpoint}: ❌ {e}")
    
    return True

def test_docker_containers():
    """Vérifier l'état des containers Docker"""
    print("\n🐳 Diagnostic Docker Containers")
    print("-" * 40)
    
    import subprocess
    
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if result.returncode == 0:
            print("Containers actifs:")
            lines = result.stdout.split('\n')
            for line in lines[1:]:  # Skip header
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        container_name = parts[-1]
                        status = ' '.join(parts[4:-1])
                        print(f"  • {container_name}: {status}")
        else:
            print("❌ Erreur Docker:", result.stderr)
    except Exception as e:
        print(f"❌ Erreur Docker: {e}")

def fix_prefect_config():
    """Essayer de corriger la configuration Prefect"""
    print("\n🔧 Tentative de correction Prefect")
    print("-" * 40)
    
    import subprocess
    import os
    
    # Arrêter et redémarrer Prefect avec une meilleure configuration
    try:
        print("Arrêt du container Prefect...")
        subprocess.run(['docker', 'stop', 'prefect-server'], capture_output=True)
        subprocess.run(['docker', 'rm', 'prefect-server'], capture_output=True)
        
        print("Redémarrage avec nouvelle configuration...")
        cmd = [
            'docker', 'run', '-d',
            '-p', '4200:4200',
            '--name', 'prefect-server',
            '-e', 'PREFECT_SERVER_API_HOST=0.0.0.0',
            '-e', 'PREFECT_UI_URL=http://localhost:4200',
            'prefecthq/prefect:3-latest',
            'prefect', 'server', 'start', '--host', '0.0.0.0', '--port', '4200'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Container Prefect redémarré")
            print("⏳ Attente du démarrage (30 secondes)...")
            time.sleep(30)
            return True
        else:
            print(f"❌ Erreur redémarrage: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def run_comprehensive_test():
    """Test complet avec tentative de correction"""
    print("🧪 DIAGNOSTIC COMPLET DES SERVICES")
    print("=" * 50)
    print(f"Heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Test Docker
    test_docker_containers()
    
    # Test FastAPI
    fastapi_ok = test_fastapi_connectivity()
    
    # Test Prefect
    prefect_ok = test_prefect_connectivity()
    
    # Si Prefect ne fonctionne pas, essayer de le corriger
    if not prefect_ok:
        print("\n🔧 Prefect ne fonctionne pas, tentative de correction...")
        if fix_prefect_config():
            print("\n🔄 Nouveau test après correction...")
            time.sleep(5)
            prefect_ok = test_prefect_connectivity()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DU DIAGNOSTIC")
    print("=" * 50)
    print(f"FastAPI: {'✅ OK' if fastapi_ok else '❌ PROBLÈME'}")
    print(f"Prefect: {'✅ OK' if prefect_ok else '❌ PROBLÈME'}")
    
    if fastapi_ok and prefect_ok:
        print("\n🎉 TOUS LES SERVICES FONCTIONNENT!")
        print("URLs accessibles:")
        print("  • FastAPI: http://localhost:9000")
        print("  • Prefect: http://localhost:4200")
    else:
        print("\n⚠️ PROBLÈMES DÉTECTÉS:")
        if not fastapi_ok:
            print("  • FastAPI: Vérifier le container fastapi_app")
        if not prefect_ok:
            print("  • Prefect: Problème de configuration réseau")
    
    return fastapi_ok and prefect_ok

if __name__ == "__main__":
    run_comprehensive_test()
