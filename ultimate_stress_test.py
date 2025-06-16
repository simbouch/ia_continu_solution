#!/usr/bin/env python3
"""
Test de stress ultime pour le système IA Continu Solution
Tests de charge extrême, résilience et performance sous pression
"""

import time
import threading
import random
import json
import os
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics
import requests

class UltimateStressTest:
    """Tests de stress ultimes pour valider la robustesse du système"""
    
    def __init__(self):
        self.base_url = "http://localhost:9000"
        self.prefect_url = "http://localhost:4200"
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        self.results = []
        self.start_time = datetime.now()
        
    def log_metric(self, test_name: str, metric: str, value: float, unit: str = ""):
        """Enregistrer une métrique de performance"""
        self.results.append({
            "test": test_name,
            "metric": metric,
            "value": value,
            "unit": unit,
            "timestamp": datetime.now().isoformat()
        })
        print(f"📊 {test_name} - {metric}: {value:.2f}{unit}")

    def stress_test_concurrent_requests(self, max_concurrent: int = 50, duration_seconds: int = 30):
        """Test de charge avec requêtes concurrentes massives"""
        print(f"\n🔥 STRESS TEST: {max_concurrent} requêtes concurrentes pendant {duration_seconds}s")
        print("-" * 70)
        
        endpoints = ["/health", "/", "/status"]
        results = []
        errors = []
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        def make_request():
            endpoint = random.choice(endpoints)
            try:
                req_start = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                req_time = time.time() - req_start
                
                return {
                    "endpoint": endpoint,
                    "status_code": response.status_code,
                    "response_time": req_time,
                    "success": response.status_code < 400,
                    "timestamp": time.time()
                }
            except Exception as e:
                return {
                    "endpoint": endpoint,
                    "error": str(e),
                    "success": False,
                    "timestamp": time.time()
                }
        
        # Lancement des requêtes concurrentes
        with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            futures = []
            
            while time.time() < end_time:
                # Maintenir le nombre de requêtes concurrentes
                while len(futures) < max_concurrent and time.time() < end_time:
                    future = executor.submit(make_request)
                    futures.append(future)
                
                # Collecter les résultats terminés
                completed_futures = []
                for future in futures:
                    if future.done():
                        try:
                            result = future.result()
                            results.append(result)
                            if not result["success"]:
                                errors.append(result)
                        except Exception as e:
                            errors.append({"error": str(e), "success": False})
                        completed_futures.append(future)
                
                # Retirer les futures terminées
                for future in completed_futures:
                    futures.remove(future)
                
                time.sleep(0.01)  # Petite pause pour éviter la surcharge CPU
        
        # Attendre les dernières requêtes
        for future in futures:
            try:
                result = future.result(timeout=5)
                results.append(result)
                if not result["success"]:
                    errors.append(result)
            except Exception as e:
                errors.append({"error": str(e), "success": False})
        
        # Analyse des résultats
        total_requests = len(results)
        successful_requests = sum(1 for r in results if r.get("success", False))
        error_rate = (len(errors) / total_requests * 100) if total_requests > 0 else 100
        
        response_times = [r["response_time"] for r in results if "response_time" in r]
        if response_times:
            avg_response_time = statistics.mean(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
            max_response_time = max(response_times)
            min_response_time = min(response_times)
        else:
            avg_response_time = p95_response_time = max_response_time = min_response_time = 0
        
        requests_per_second = total_requests / duration_seconds
        
        # Enregistrer les métriques
        self.log_metric("Stress Concurrent", "Total Requests", total_requests)
        self.log_metric("Stress Concurrent", "Successful Requests", successful_requests)
        self.log_metric("Stress Concurrent", "Error Rate", error_rate, "%")
        self.log_metric("Stress Concurrent", "Requests/Second", requests_per_second, " req/s")
        self.log_metric("Stress Concurrent", "Avg Response Time", avg_response_time * 1000, "ms")
        self.log_metric("Stress Concurrent", "P95 Response Time", p95_response_time * 1000, "ms")
        self.log_metric("Stress Concurrent", "Max Response Time", max_response_time * 1000, "ms")
        
        print(f"\n📈 Résultats Stress Test:")
        print(f"   Total requêtes: {total_requests}")
        print(f"   Succès: {successful_requests}")
        print(f"   Taux d'erreur: {error_rate:.2f}%")
        print(f"   Req/sec: {requests_per_second:.2f}")
        print(f"   Temps réponse moyen: {avg_response_time*1000:.2f}ms")
        print(f"   P95: {p95_response_time*1000:.2f}ms")
        
        return {
            "success": error_rate < 5,  # Moins de 5% d'erreurs
            "metrics": {
                "total_requests": total_requests,
                "error_rate": error_rate,
                "avg_response_time_ms": avg_response_time * 1000,
                "requests_per_second": requests_per_second
            }
        }

    def stress_test_memory_leak(self, iterations: int = 100):
        """Test de fuite mémoire avec requêtes répétées"""
        print(f"\n🧠 MEMORY LEAK TEST: {iterations} itérations")
        print("-" * 70)
        
        import psutil
        process = psutil.Process()
        
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_samples = [initial_memory]
        
        for i in range(iterations):
            try:
                # Faire plusieurs requêtes
                for endpoint in ["/health", "/", "/status", "/docs"]:
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                
                # Échantillonner la mémoire tous les 10 itérations
                if i % 10 == 0:
                    current_memory = process.memory_info().rss / 1024 / 1024
                    memory_samples.append(current_memory)
                    print(f"   Itération {i}: {current_memory:.2f}MB")
                
            except Exception as e:
                print(f"   Erreur itération {i}: {e}")
        
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        memory_increase_percent = (memory_increase / initial_memory) * 100
        
        self.log_metric("Memory Leak", "Initial Memory", initial_memory, "MB")
        self.log_metric("Memory Leak", "Final Memory", final_memory, "MB")
        self.log_metric("Memory Leak", "Memory Increase", memory_increase, "MB")
        self.log_metric("Memory Leak", "Memory Increase", memory_increase_percent, "%")
        
        # Considérer comme succès si l'augmentation est < 50%
        success = memory_increase_percent < 50
        
        print(f"\n🧠 Résultats Memory Leak:")
        print(f"   Mémoire initiale: {initial_memory:.2f}MB")
        print(f"   Mémoire finale: {final_memory:.2f}MB")
        print(f"   Augmentation: {memory_increase:.2f}MB ({memory_increase_percent:.1f}%)")
        print(f"   Status: {'✅ OK' if success else '❌ FUITE DÉTECTÉE'}")
        
        return {"success": success, "memory_increase_percent": memory_increase_percent}

    def stress_test_discord_rate_limit(self, messages_count: int = 20):
        """Test des limites de taux Discord"""
        print(f"\n📱 DISCORD RATE LIMIT TEST: {messages_count} messages")
        print("-" * 70)
        
        if not self.webhook_url:
            print("❌ Discord webhook non configuré")
            return {"success": False, "reason": "No webhook"}
        
        successful_sends = 0
        rate_limited = 0
        errors = 0
        response_times = []
        
        for i in range(messages_count):
            try:
                start_time = time.time()
                
                data = {
                    "embeds": [{
                        "title": f"🧪 Test Rate Limit #{i+1}",
                        "description": f"Message de test {i+1}/{messages_count}",
                        "color": 3447003,
                        "fields": [{
                            "name": "Timestamp",
                            "value": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                            "inline": True
                        }]
                    }]
                }
                
                response = requests.post(self.webhook_url, json=data, timeout=10)
                response_time = time.time() - start_time
                response_times.append(response_time)
                
                if response.status_code == 204:
                    successful_sends += 1
                    print(f"   ✅ Message {i+1}: {response_time*1000:.0f}ms")
                elif response.status_code == 429:
                    rate_limited += 1
                    print(f"   ⚠️ Message {i+1}: Rate limited")
                else:
                    errors += 1
                    print(f"   ❌ Message {i+1}: Error {response.status_code}")
                
                # Délai pour éviter le rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                errors += 1
                print(f"   ❌ Message {i+1}: Exception {e}")
        
        success_rate = (successful_sends / messages_count) * 100
        avg_response_time = statistics.mean(response_times) if response_times else 0
        
        self.log_metric("Discord Rate Limit", "Messages Sent", successful_sends)
        self.log_metric("Discord Rate Limit", "Rate Limited", rate_limited)
        self.log_metric("Discord Rate Limit", "Errors", errors)
        self.log_metric("Discord Rate Limit", "Success Rate", success_rate, "%")
        self.log_metric("Discord Rate Limit", "Avg Response Time", avg_response_time * 1000, "ms")
        
        print(f"\n📱 Résultats Discord Rate Limit:")
        print(f"   Messages envoyés: {successful_sends}/{messages_count}")
        print(f"   Rate limited: {rate_limited}")
        print(f"   Erreurs: {errors}")
        print(f"   Taux de succès: {success_rate:.1f}%")
        
        return {
            "success": success_rate >= 80,  # Au moins 80% de succès
            "success_rate": success_rate
        }

    def stress_test_prefect_flow_spam(self, executions: int = 10):
        """Test de spam d'exécutions Prefect"""
        print(f"\n🔄 PREFECT FLOW SPAM TEST: {executions} exécutions")
        print("-" * 70)
        
        try:
            import sys
            sys.path.append('.')
            os.environ["PREFECT_API_URL"] = f"{self.prefect_url}/api"
            
            from flow import periodic_check
            
            successful_executions = 0
            failed_executions = 0
            execution_times = []
            
            for i in range(executions):
                try:
                    start_time = time.time()
                    result = periodic_check()
                    execution_time = time.time() - start_time
                    execution_times.append(execution_time)
                    
                    if result:
                        successful_executions += 1
                        print(f"   ✅ Exécution {i+1}: {execution_time:.2f}s")
                    else:
                        failed_executions += 1
                        print(f"   ❌ Exécution {i+1}: Échec")
                    
                    # Petit délai entre les exécutions
                    time.sleep(1)
                    
                except Exception as e:
                    failed_executions += 1
                    print(f"   ❌ Exécution {i+1}: Exception {e}")
            
            success_rate = (successful_executions / executions) * 100
            avg_execution_time = statistics.mean(execution_times) if execution_times else 0
            
            self.log_metric("Prefect Flow Spam", "Successful Executions", successful_executions)
            self.log_metric("Prefect Flow Spam", "Failed Executions", failed_executions)
            self.log_metric("Prefect Flow Spam", "Success Rate", success_rate, "%")
            self.log_metric("Prefect Flow Spam", "Avg Execution Time", avg_execution_time, "s")
            
            print(f"\n🔄 Résultats Prefect Flow Spam:")
            print(f"   Exécutions réussies: {successful_executions}/{executions}")
            print(f"   Taux de succès: {success_rate:.1f}%")
            print(f"   Temps moyen: {avg_execution_time:.2f}s")
            
            return {
                "success": success_rate >= 90,  # Au moins 90% de succès
                "success_rate": success_rate
            }
            
        except Exception as e:
            print(f"❌ Erreur import flow: {e}")
            return {"success": False, "reason": str(e)}

    def run_ultimate_stress_tests(self):
        """Exécuter tous les tests de stress ultimes"""
        print("🔥 TESTS DE STRESS ULTIMES - IA Continu Solution")
        print("=" * 80)
        print("Tests de charge extrême et résilience du système")
        print("=" * 80)
        
        test_results = {}
        
        # Test 1: Requêtes concurrentes massives
        test_results["concurrent"] = self.stress_test_concurrent_requests(
            max_concurrent=30, duration_seconds=20
        )
        
        # Test 2: Test de fuite mémoire
        test_results["memory_leak"] = self.stress_test_memory_leak(iterations=50)
        
        # Test 3: Rate limiting Discord
        test_results["discord_rate_limit"] = self.stress_test_discord_rate_limit(messages_count=10)
        
        # Test 4: Spam Prefect flows
        test_results["prefect_spam"] = self.stress_test_prefect_flow_spam(executions=5)
        
        # Générer le rapport final
        self.generate_ultimate_report(test_results)
        
        return test_results

    def generate_ultimate_report(self, test_results: dict):
        """Générer le rapport final des tests de stress"""
        print("\n" + "=" * 80)
        print("🏆 RAPPORT FINAL - TESTS DE STRESS ULTIMES")
        print("=" * 80)
        
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results.values() if result.get("success", False))
        
        print(f"📊 Résumé Global:")
        print(f"   Tests de stress: {total_tests}")
        print(f"   Tests réussis: {passed_tests}")
        print(f"   Taux de réussite: {(passed_tests/total_tests*100):.1f}%")
        
        print(f"\n🎯 Détails par Test:")
        for test_name, result in test_results.items():
            status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
            print(f"   {status} {test_name.replace('_', ' ').title()}")
            
            # Afficher les métriques clés
            if "metrics" in result:
                for key, value in result["metrics"].items():
                    print(f"      📈 {key}: {value}")
        
        # Recommandations
        print(f"\n💡 Recommandations:")
        if passed_tests == total_tests:
            print("   🎉 SYSTÈME ULTRA-ROBUSTE!")
            print("   ✅ Tous les tests de stress passent")
            print("   🚀 Prêt pour une charge de production élevée")
        else:
            print("   ⚠️ Améliorations nécessaires:")
            for test_name, result in test_results.items():
                if not result.get("success", False):
                    print(f"      • {test_name}: {result.get('reason', 'Performance insuffisante')}")
        
        # Sauvegarder les résultats
        report_data = {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "success_rate": round((passed_tests/total_tests*100), 2),
                "test_duration": (datetime.now() - self.start_time).total_seconds()
            },
            "test_results": test_results,
            "metrics": self.results,
            "generated_at": datetime.now().isoformat()
        }
        
        with open("ultimate_stress_test_results.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Rapport détaillé: ultimate_stress_test_results.json")
        
        # Score final
        if passed_tests == total_tests:
            print(f"\n🏆 SCORE FINAL: SYSTÈME ULTRA-PERFORMANT! 🏆")
        elif passed_tests >= total_tests * 0.75:
            print(f"\n🥈 SCORE FINAL: SYSTÈME ROBUSTE")
        else:
            print(f"\n🥉 SCORE FINAL: AMÉLIORATIONS NÉCESSAIRES")

def main():
    """Fonction principale pour les tests de stress ultimes"""
    print("🔥 Démarrage des tests de stress ultimes...")
    
    # Vérifier la configuration
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("⚠️ DISCORD_WEBHOOK_URL non configuré - certains tests seront limités")
    
    # Exécuter les tests
    stress_tester = UltimateStressTest()
    results = stress_tester.run_ultimate_stress_tests()
    
    return results

if __name__ == "__main__":
    main()
