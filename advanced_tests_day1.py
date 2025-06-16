#!/usr/bin/env python3
"""
Tests avancés et sophistiqués pour le Jour 1
Tests complets avec validation fonctionnelle, performance et intégration
"""

import os
import subprocess
import requests
import time
import json
import threading
import socket
import psutil
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import concurrent.futures
import tempfile
import yaml

class AdvancedDay1TestSuite:
    """Suite de tests avancés pour valider tous les aspects du Jour 1"""
    
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        self.base_url = "http://localhost:9000"
        self.prefect_url = "http://localhost:4200"
        self.performance_metrics = {}
        self.start_time = datetime.now()
        
    def log_result(self, test_name: str, success: bool, details: str = "", 
                   performance: Dict[str, Any] = None, severity: str = "normal"):
        """Enregistrer le résultat d'un test avec métriques de performance"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "severity": severity,
            "performance": performance or {},
            "timestamp": datetime.now().isoformat(),
            "duration": (datetime.now() - self.start_time).total_seconds()
        }
        self.results.append(result)
        
        # Icônes selon la sévérité
        icons = {
            "critical": "🚨",
            "high": "⚠️",
            "normal": "✅" if success else "❌",
            "low": "ℹ️"
        }
        
        status = f"{icons.get(severity, '✅' if success else '❌')} {'PASS' if success else 'FAIL'}"
        print(f"{status} | {test_name}")
        if details:
            print(f"      {details}")
        if performance:
            for key, value in performance.items():
                print(f"      📊 {key}: {value}")

    def check_port_availability(self, host: str, port: int, timeout: int = 3) -> bool:
        """Vérifier si un port est disponible"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def measure_response_time(self, url: str, timeout: int = 5) -> Dict[str, Any]:
        """Mesurer le temps de réponse d'une URL"""
        try:
            start_time = time.time()
            response = requests.get(url, timeout=timeout)
            end_time = time.time()
            
            return {
                "response_time_ms": round((end_time - start_time) * 1000, 2),
                "status_code": response.status_code,
                "success": response.status_code < 400,
                "content_length": len(response.content)
            }
        except requests.RequestException as e:
            return {
                "response_time_ms": None,
                "status_code": None,
                "success": False,
                "error": str(e)
            }

    def test_infrastructure_health(self):
        """Test 1: Santé complète de l'infrastructure"""
        print("\n🏗️ Test 1: Santé Infrastructure Complète")
        print("-" * 60)
        
        # Test des ports critiques
        critical_ports = [
            (9000, "FastAPI Application"),
            (4200, "Prefect Server")
        ]
        
        for port, service in critical_ports:
            available = self.check_port_availability("localhost", port)
            self.log_result(
                f"Port {port} ({service}) disponible",
                available,
                f"Port {'ouvert' if available else 'fermé'}",
                severity="critical" if not available else "normal"
            )
        
        # Test de la mémoire système
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        self.log_result(
            "Utilisation mémoire système",
            memory_usage < 90,
            f"Mémoire utilisée: {memory_usage:.1f}%",
            {"memory_percent": memory_usage, "available_gb": round(memory.available / (1024**3), 2)},
            severity="high" if memory_usage > 80 else "normal"
        )
        
        # Test des processus Docker
        try:
            result = subprocess.run(["docker", "ps", "--format", "json"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                containers = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        containers.append(json.loads(line))
                
                running_containers = len(containers)
                self.log_result(
                    "Containers Docker actifs",
                    running_containers >= 2,
                    f"{running_containers} containers en cours d'exécution",
                    {"container_count": running_containers}
                )
            else:
                self.log_result("Containers Docker actifs", False, "Erreur Docker", severity="critical")
        except Exception as e:
            self.log_result("Containers Docker actifs", False, f"Erreur: {e}", severity="critical")

    def test_api_performance_stress(self):
        """Test 2: Tests de performance et stress de l'API"""
        print("\n🚀 Test 2: Performance et Stress API")
        print("-" * 60)
        
        # Test de charge concurrent
        def make_request(endpoint):
            return self.measure_response_time(f"{self.base_url}{endpoint}")
        
        endpoints = ["/health", "/", "/status", "/docs"]
        concurrent_requests = 10
        
        for endpoint in endpoints:
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
                futures = [executor.submit(make_request, endpoint) for _ in range(concurrent_requests)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            successful_requests = sum(1 for r in results if r["success"])
            avg_response_time = sum(r["response_time_ms"] for r in results if r["response_time_ms"]) / len(results)
            
            success_rate = (successful_requests / concurrent_requests) * 100
            performance_ok = avg_response_time < 1000 and success_rate >= 95
            
            self.log_result(
                f"Stress test {endpoint}",
                performance_ok,
                f"Taux de succès: {success_rate:.1f}%",
                {
                    "avg_response_time_ms": round(avg_response_time, 2),
                    "success_rate_percent": success_rate,
                    "concurrent_requests": concurrent_requests
                },
                severity="high" if not performance_ok else "normal"
            )

    def test_prefect_integration_deep(self):
        """Test 3: Intégration Prefect approfondie"""
        print("\n🔄 Test 3: Intégration Prefect Approfondie")
        print("-" * 60)
        
        # Test de l'API Prefect
        prefect_metrics = self.measure_response_time(f"{self.prefect_url}/api/health")
        self.log_result(
            "API Prefect accessible",
            prefect_metrics["success"],
            f"Status: {prefect_metrics.get('status_code', 'N/A')}",
            prefect_metrics
        )
        
        # Test du dashboard Prefect
        dashboard_metrics = self.measure_response_time(self.prefect_url)
        self.log_result(
            "Dashboard Prefect accessible",
            dashboard_metrics["success"],
            f"Status: {dashboard_metrics.get('status_code', 'N/A')}",
            dashboard_metrics
        )
        
        # Test d'exécution de flow (si possible)
        try:
            # Importer et exécuter le flow
            import sys
            sys.path.append('.')
            
            # Configuration de l'environnement
            os.environ["PREFECT_API_URL"] = f"{self.prefect_url}/api"
            
            from flow import periodic_check
            
            start_time = time.time()
            result = periodic_check()
            execution_time = time.time() - start_time
            
            self.log_result(
                "Exécution flow Prefect",
                result is not None,
                f"Flow exécuté avec succès",
                {
                    "execution_time_s": round(execution_time, 2),
                    "result": str(result)[:100] if result else None
                }
            )
            
        except Exception as e:
            self.log_result(
                "Exécution flow Prefect",
                False,
                f"Erreur: {str(e)[:100]}",
                severity="high"
            )

    def test_discord_notification_advanced(self):
        """Test 4: Tests avancés des notifications Discord"""
        print("\n📱 Test 4: Notifications Discord Avancées")
        print("-" * 60)
        
        if not self.webhook_url:
            self.log_result(
                "Configuration Discord",
                False,
                "DISCORD_WEBHOOK_URL non configuré",
                severity="high"
            )
            return
        
        # Test de différents types de messages
        test_messages = [
            {
                "name": "Message simple",
                "data": {"content": "🧪 Test message simple - IA Continu Solution"}
            },
            {
                "name": "Embed basique",
                "data": {
                    "embeds": [{
                        "title": "Résultats du pipeline",
                        "description": "Test embed basique",
                        "color": 5814783,
                        "fields": [{
                            "name": "Status",
                            "value": "Succès",
                            "inline": True
                        }]
                    }]
                }
            },
            {
                "name": "Embed complexe",
                "data": {
                    "embeds": [{
                        "title": "🧪 Test Avancé - IA Continu Solution",
                        "description": "Test de notification complexe",
                        "color": 3447003,
                        "fields": [
                            {"name": "Type", "value": "Test Automatisé", "inline": True},
                            {"name": "Timestamp", "value": datetime.now().strftime("%H:%M:%S"), "inline": True},
                            {"name": "Status", "value": "✅ Succès", "inline": True}
                        ],
                        "footer": {"text": "Tests Jour 1"},
                        "timestamp": datetime.now().isoformat()
                    }]
                }
            }
        ]
        
        for test_msg in test_messages:
            try:
                start_time = time.time()
                response = requests.post(self.webhook_url, json=test_msg["data"], timeout=10)
                response_time = time.time() - start_time
                
                success = response.status_code == 204
                self.log_result(
                    f"Discord {test_msg['name']}",
                    success,
                    f"Status: {response.status_code}",
                    {"response_time_ms": round(response_time * 1000, 2)}
                )
                
                # Délai entre les messages pour éviter le rate limiting
                time.sleep(1)
                
            except Exception as e:
                self.log_result(
                    f"Discord {test_msg['name']}",
                    False,
                    f"Erreur: {e}",
                    severity="high"
                )

    def test_file_structure_comprehensive(self):
        """Test 5: Structure de fichiers complète"""
        print("\n📁 Test 5: Structure de Fichiers Complète")
        print("-" * 60)
        
        # Fichiers critiques requis
        critical_files = [
            ("docker-compose.yml", "Configuration Docker Compose"),
            ("Dockerfile", "Dockerfile principal"),
            ("main.py", "Application FastAPI"),
            ("flow.py", "Flow Prefect"),
            ("requirements.txt", "Dépendances Python")
        ]
        
        for filename, description in critical_files:
            exists = os.path.exists(filename)
            if exists:
                size = os.path.getsize(filename)
                self.log_result(
                    f"Fichier {filename}",
                    True,
                    description,
                    {"file_size_bytes": size}
                )
            else:
                self.log_result(
                    f"Fichier {filename}",
                    False,
                    f"{description} - Fichier manquant",
                    severity="critical"
                )
        
        # Vérification du contenu Docker Compose
        if os.path.exists("docker-compose.yml"):
            try:
                with open("docker-compose.yml", "r") as f:
                    compose_content = yaml.safe_load(f)
                
                services = compose_content.get("services", {})
                required_services = ["app"]
                
                for service in required_services:
                    if service in services:
                        self.log_result(f"Service {service} dans compose", True)
                    else:
                        self.log_result(f"Service {service} dans compose", False, severity="high")
                        
            except Exception as e:
                self.log_result("Parsing Docker Compose", False, f"Erreur: {e}", severity="high")

    def test_security_basic(self):
        """Test 6: Tests de sécurité de base"""
        print("\n🔒 Test 6: Sécurité de Base")
        print("-" * 60)
        
        # Test des headers de sécurité
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            headers = response.headers
            
            security_headers = [
                ("X-Content-Type-Options", "Protection MIME"),
                ("X-Frame-Options", "Protection Clickjacking"),
                ("X-XSS-Protection", "Protection XSS")
            ]
            
            for header, description in security_headers:
                present = header in headers
                self.log_result(
                    f"Header {header}",
                    present,
                    f"{description} {'présent' if present else 'manquant'}",
                    severity="low"
                )
                
        except Exception as e:
            self.log_result("Test headers sécurité", False, f"Erreur: {e}")
        
        # Test des variables d'environnement sensibles
        sensitive_vars = ["DISCORD_WEBHOOK_URL", "PREFECT_API_URL"]
        for var in sensitive_vars:
            value = os.getenv(var)
            configured = value is not None and len(value) > 0
            self.log_result(
                f"Variable {var}",
                configured,
                f"{'Configurée' if configured else 'Non configurée'}",
                severity="high" if var == "DISCORD_WEBHOOK_URL" else "normal"
            )

    def run_all_advanced_tests(self):
        """Exécuter tous les tests avancés"""
        print("🧪 TESTS AVANCÉS JOUR 1 - IA Continu Solution")
        print("=" * 70)
        print("Tests sophistiqués avec métriques de performance et sécurité")
        print("=" * 70)
        
        # Configuration de l'environnement Discord si nécessaire
        if not self.webhook_url:
            print("⚠️  DISCORD_WEBHOOK_URL non configuré")
            print("   Pour activer les tests Discord complets:")
            print("   $env:DISCORD_WEBHOOK_URL=\"votre_webhook_url\"")
            print()
        
        # Exécuter tous les tests
        test_methods = [
            self.test_infrastructure_health,
            self.test_api_performance_stress,
            self.test_prefect_integration_deep,
            self.test_discord_notification_advanced,
            self.test_file_structure_comprehensive,
            self.test_security_basic
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log_result(
                    f"Erreur test {test_method.__name__}",
                    False,
                    f"Exception: {e}",
                    severity="critical"
                )
        
        # Générer le rapport avancé
        self.generate_advanced_report()

    def generate_advanced_report(self):
        """Générer un rapport avancé avec métriques"""
        print("\n" + "=" * 70)
        print("📊 RAPPORT AVANCÉ - JOUR 1")
        print("=" * 70)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        
        # Calcul par sévérité
        severity_counts = {}
        for result in self.results:
            severity = result.get("severity", "normal")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Métriques de performance
        response_times = [r["performance"].get("response_time_ms") 
                         for r in self.results 
                         if r["performance"].get("response_time_ms")]
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        print(f"📈 Métriques Globales:")
        print(f"   Total des tests: {total_tests}")
        print(f"   Tests réussis: {passed_tests}")
        print(f"   Tests échoués: {failed_tests}")
        print(f"   Taux de réussite: {(passed_tests/total_tests*100):.1f}%")
        print(f"   Temps de réponse moyen: {avg_response_time:.2f}ms")
        
        print(f"\n🎯 Répartition par Sévérité:")
        for severity, count in severity_counts.items():
            print(f"   {severity.capitalize()}: {count} tests")
        
        # Tests critiques échoués
        critical_failures = [r for r in self.results 
                           if not r["success"] and r.get("severity") == "critical"]
        
        if critical_failures:
            print(f"\n🚨 ÉCHECS CRITIQUES ({len(critical_failures)}):")
            for failure in critical_failures:
                print(f"   • {failure['test']}: {failure['details']}")
        
        # Recommandations
        print(f"\n💡 Recommandations:")
        if failed_tests == 0:
            print("   ✅ Tous les tests passent - Système prêt pour la production")
        else:
            print(f"   ⚠️  {failed_tests} tests à corriger avant mise en production")
            if critical_failures:
                print("   🚨 Corriger en priorité les échecs critiques")
        
        # Sauvegarde des résultats détaillés
        report_data = {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": round((passed_tests/total_tests*100), 2),
                "avg_response_time_ms": round(avg_response_time, 2),
                "test_duration_s": (datetime.now() - self.start_time).total_seconds()
            },
            "results": self.results,
            "generated_at": datetime.now().isoformat()
        }
        
        with open("advanced_test_results_day1.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Rapport détaillé: advanced_test_results_day1.json")
        print(f"🎯 Statut final: {'🎉 JOUR 1 COMPLET' if failed_tests == 0 else '⚠️ CORRECTIONS NÉCESSAIRES'}")

def main():
    """Fonction principale pour les tests avancés"""
    print("🚀 Démarrage des tests avancés Jour 1...")
    
    # Exécuter les tests avancés
    test_suite = AdvancedDay1TestSuite()
    test_suite.run_all_advanced_tests()

if __name__ == "__main__":
    main()
