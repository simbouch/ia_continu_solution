#!/usr/bin/env python3
"""
Tests complets pour vérifier tous les éléments du Jour 1
Vérifie Docker Compose, Uptime Kuma, API, Notifications Discord, et Prefect
"""

import os
import subprocess
import requests
import time
import json
from typing import Dict, Any, List
from datetime import datetime

class Day1TestSuite:
    """Suite de tests pour valider tous les composants du Jour 1"""
    
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        self.base_url = "http://localhost:9000"  # Port utilisé dans le projet
        
    def log_result(self, test_name: str, success: bool, details: str = "", expected: str = "", actual: str = ""):
        """Enregistrer le résultat d'un test"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "expected": expected,
            "actual": actual,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name}")
        if details:
            print(f"      {details}")
        if not success and expected:
            print(f"      Attendu: {expected}")
            print(f"      Obtenu: {actual}")

    def run_command(self, command: List[str], timeout: int = 30) -> subprocess.CompletedProcess:
        """Exécuter une commande shell"""
        try:
            return subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return subprocess.CompletedProcess(command, 1, "", "Timeout")

    def test_docker_compose_structure(self):
        """Test 1: Vérifier la structure du docker-compose.yml"""
        print("\n🐳 Test 1: Structure Docker Compose")
        print("-" * 50)
        
        try:
            with open("docker-compose.yml", "r") as f:
                content = f.read()
            
            # Vérifier les services requis
            required_services = ["app", "uptime-kuma", "prefect-server", "prefect-worker"]
            for service in required_services:
                if service in content:
                    self.log_result(f"Service {service} présent", True)
                else:
                    self.log_result(f"Service {service} présent", False, f"Service {service} manquant")
            
            # Vérifier les ports
            port_checks = [
                ("9000:8000", "Port FastAPI"),
                ("3001:3001", "Port Uptime Kuma"),
                ("4200:4200", "Port Prefect")
            ]
            
            for port, description in port_checks:
                if port in content:
                    self.log_result(f"{description} configuré", True)
                else:
                    self.log_result(f"{description} configuré", False, f"Port {port} manquant")
            
            # Vérifier les volumes
            if "uptime-kuma-data" in content:
                self.log_result("Volume Uptime Kuma configuré", True)
            else:
                self.log_result("Volume Uptime Kuma configuré", False)
                
        except FileNotFoundError:
            self.log_result("Fichier docker-compose.yml", False, "Fichier non trouvé")

    def test_prefect_flow_structure(self):
        """Test 2: Vérifier la structure du flow.py"""
        print("\n🔄 Test 2: Structure Prefect Flow")
        print("-" * 50)
        
        try:
            with open("flow.py", "r") as f:
                content = f.read()
            
            # Vérifier les imports requis
            required_imports = [
                "from prefect import flow, task",
                "from prefect.logging import get_run_logger",
                "import random"
            ]
            
            for import_line in required_imports:
                if import_line in content:
                    self.log_result(f"Import présent: {import_line}", True)
                else:
                    self.log_result(f"Import présent: {import_line}", False)
            
            # Vérifier les fonctions/tâches requises
            required_elements = [
                ("@task", "Décorateur @task"),
                ("@flow", "Décorateur @flow"),
                ("check_random", "Fonction check_random"),
                ("periodic_check", "Fonction periodic_check"),
                ("retries=2", "Configuration retries"),
                ("retry_delay_seconds=1", "Configuration retry_delay"),
                ("random.random()", "Génération nombre aléatoire"),
                ("< 0.5", "Condition seuil 0.5"),
                ("serve(", "Configuration serve"),
                ("interval=30", "Intervalle 30 secondes")
            ]
            
            for element, description in required_elements:
                if element in content:
                    self.log_result(description, True)
                else:
                    self.log_result(description, False, f"Élément manquant: {element}")
                    
        except FileNotFoundError:
            self.log_result("Fichier flow.py", False, "Fichier non trouvé")

    def test_discord_notification_function(self):
        """Test 3: Vérifier la fonction de notification Discord"""
        print("\n📱 Test 3: Fonction Notification Discord")
        print("-" * 50)
        
        try:
            with open("flow.py", "r") as f:
                content = f.read()
            
            # Vérifier la fonction send_discord_embed selon les spécifications
            discord_checks = [
                ("def send_discord_embed(message)", "Fonction send_discord_embed"),
                ('"embeds":', "Structure embeds"),
                ('"title": "Résultats du pipeline"', "Titre pipeline"),
                ('"color": 5814783', "Couleur verte"),
                ('"Status"', "Champ Status"),
                ('"Succès"', "Valeur Succès"),
                ("requests.post", "Requête POST"),
                ("response.status_code != 204", "Vérification status 204")
            ]
            
            for check, description in discord_checks:
                if check in content:
                    self.log_result(description, True)
                else:
                    self.log_result(description, False, f"Élément manquant: {check}")
                    
        except FileNotFoundError:
            self.log_result("Vérification fonction Discord", False, "Fichier flow.py non trouvé")

    def test_dockerfile_prefect(self):
        """Test 4: Vérifier le Dockerfile.prefect"""
        print("\n🐳 Test 4: Dockerfile Prefect")
        print("-" * 50)
        
        try:
            with open("Dockerfile.prefect", "r") as f:
                content = f.read()
            
            dockerfile_checks = [
                ("FROM python:3.11-slim", "Image de base Python 3.11"),
                ("WORKDIR /app", "Répertoire de travail"),
                ("PYTHONIOENCODING=utf-8", "Encodage UTF-8"),
                ("COPY flow.py", "Copie du flow"),
                ("python flow.py", "Commande d'exécution")
            ]
            
            for check, description in dockerfile_checks:
                if check in content:
                    self.log_result(description, True)
                else:
                    self.log_result(description, False, f"Élément manquant: {check}")
                    
        except FileNotFoundError:
            self.log_result("Fichier Dockerfile.prefect", False, "Fichier non trouvé")

    def test_api_endpoints(self):
        """Test 5: Tester les endpoints de l'API"""
        print("\n🔗 Test 5: Endpoints API")
        print("-" * 50)
        
        # Vérifier si l'API est accessible
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.log_result("API accessible", True, f"Status: {response.status_code}")
                
                # Tester les autres endpoints
                endpoints = [
                    ("/", "Endpoint racine"),
                    ("/status", "Endpoint status"),
                    ("/docs", "Documentation API")
                ]
                
                for endpoint, description in endpoints:
                    try:
                        resp = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                        success = resp.status_code < 400
                        self.log_result(description, success, f"Status: {resp.status_code}")
                    except requests.RequestException as e:
                        self.log_result(description, False, f"Erreur: {e}")
            else:
                self.log_result("API accessible", False, f"Status: {response.status_code}")
                
        except requests.RequestException as e:
            self.log_result("API accessible", False, f"Erreur: {e}")

    def test_discord_webhook(self):
        """Test 6: Tester le webhook Discord"""
        print("\n📱 Test 6: Webhook Discord")
        print("-" * 50)
        
        if not self.webhook_url:
            self.log_result("Configuration webhook", False, "DISCORD_WEBHOOK_URL non configuré")
            return
        
        # Test de la fonction selon les spécifications
        test_message = "Test du pipeline - Jour 1"
        data = {"embeds": [{
            "title": "Résultats du pipeline",
            "description": test_message,
            "color": 5814783,
            "fields": [{
                "name": "Status",
                "value": "Succès",
                "inline": True
            }]
        }]}
        
        try:
            response = requests.post(self.webhook_url, json=data, timeout=10)
            if response.status_code == 204:
                self.log_result("Envoi notification Discord", True, "Message envoyé avec succès")
            else:
                self.log_result("Envoi notification Discord", False, f"Status: {response.status_code}")
        except requests.RequestException as e:
            self.log_result("Envoi notification Discord", False, f"Erreur: {e}")

    def test_docker_images_build(self):
        """Test 7: Vérifier que les images Docker peuvent être construites"""
        print("\n🔨 Test 7: Construction Images Docker")
        print("-" * 50)
        
        # Test construction image principale
        result = self.run_command(["docker", "build", "-t", "test-fastapi-app", "."])
        if result.returncode == 0:
            self.log_result("Construction image FastAPI", True)
        else:
            self.log_result("Construction image FastAPI", False, result.stderr)
        
        # Test construction image Prefect
        result = self.run_command(["docker", "build", "-f", "Dockerfile.prefect", "-t", "test-prefect-flow", "."])
        if result.returncode == 0:
            self.log_result("Construction image Prefect", True)
        else:
            self.log_result("Construction image Prefect", False, result.stderr)

    def test_environment_variables(self):
        """Test 8: Vérifier les variables d'environnement"""
        print("\n⚙️ Test 8: Variables d'Environnement")
        print("-" * 50)
        
        # Vérifier le fichier .env
        try:
            with open(".env", "r") as f:
                content = f.read()
            
            if "DISCORD_WEBHOOK_URL" in content:
                self.log_result("Variable DISCORD_WEBHOOK_URL dans .env", True)
            else:
                self.log_result("Variable DISCORD_WEBHOOK_URL dans .env", False)
                
        except FileNotFoundError:
            self.log_result("Fichier .env", False, "Fichier non trouvé")
        
        # Vérifier les variables d'environnement actuelles
        if os.getenv("DISCORD_WEBHOOK_URL"):
            self.log_result("DISCORD_WEBHOOK_URL configuré", True)
        else:
            self.log_result("DISCORD_WEBHOOK_URL configuré", False, "Variable non définie")

    def run_all_tests(self):
        """Exécuter tous les tests du Jour 1"""
        print("🧪 TESTS JOUR 1 - IA Continu Solution")
        print("=" * 60)
        print("Vérification de tous les éléments requis pour le Jour 1")
        print("=" * 60)
        
        # Exécuter tous les tests
        self.test_docker_compose_structure()
        self.test_prefect_flow_structure()
        self.test_discord_notification_function()
        self.test_dockerfile_prefect()
        self.test_api_endpoints()
        self.test_discord_webhook()
        self.test_docker_images_build()
        self.test_environment_variables()
        
        # Générer le rapport
        self.generate_report()

    def generate_report(self):
        """Générer le rapport final"""
        print("\n" + "=" * 60)
        print("📊 RAPPORT FINAL - JOUR 1")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total des tests: {total_tests}")
        print(f"Tests réussis: {passed_tests}")
        print(f"Tests échoués: {failed_tests}")
        print(f"Taux de réussite: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Tests échoués:")
            for result in self.results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        # Éléments manquants critiques
        critical_missing = []
        for result in self.results:
            if not result["success"] and any(keyword in result["test"].lower() for keyword in ["docker-compose", "flow.py", "check_random", "discord"]):
                critical_missing.append(result["test"])
        
        if critical_missing:
            print(f"\n🚨 Éléments critiques manquants:")
            for item in critical_missing:
                print(f"   • {item}")
        
        print(f"\n🎯 Statut global: {'✅ JOUR 1 COMPLET' if failed_tests == 0 else '⚠️ ÉLÉMENTS MANQUANTS'}")
        
        # Sauvegarder les résultats
        with open("test_results_day1.json", "w") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n📄 Résultats détaillés sauvegardés: test_results_day1.json")

def main():
    """Fonction principale"""
    print("Démarrage des tests Jour 1...")
    
    # Vérifier si Discord webhook est configuré
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("⚠️  DISCORD_WEBHOOK_URL non configuré")
        print("   Pour activer les tests Discord:")
        print("   $env:DISCORD_WEBHOOK_URL=\"votre_webhook_url\"")
        print()
    
    # Exécuter les tests
    test_suite = Day1TestSuite()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main()
