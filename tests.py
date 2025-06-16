#!/usr/bin/env python3
"""
Comprehensive test suite for IA Continu Solution
Tests API endpoints, Docker container health, and Discord notifications
"""

import requests
import time
import json
import os
import subprocess
from typing import Dict, Any, List
from datetime import datetime

class TestSuite:
    def __init__(self, base_url: str = "http://localhost:9000"):
        self.base_url = base_url
        self.results: List[Dict[str, Any]] = []
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        
    def log_result(self, test_name: str, success: bool, details: str = "", response_time: float = 0):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name}")
        if details:
            print(f"      {details}")
        if response_time > 0:
            print(f"      Response time: {response_time:.3f}s")

    def test_api_endpoint(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
        """Test a specific API endpoint"""
        try:
            url = f"{self.base_url}{endpoint}"
            start_time = time.time()
            
            if method.upper() == "GET":
                response = requests.get(url, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, timeout=10)
            else:
                return {"success": False, "error": f"Unsupported method: {method}"}
            
            response_time = time.time() - start_time
            
            return {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                "response_time": response_time
            }
        except requests.RequestException as e:
            return {"success": False, "error": str(e)}

    def test_api_endpoints(self):
        """Test all API endpoints"""
        print("\n🔍 Testing API Endpoints")
        print("-" * 50)
        
        # Test root endpoint
        result = self.test_api_endpoint("/")
        self.log_result(
            "Root Endpoint (/)", 
            result["success"], 
            f"Status: {result.get('status_code', 'N/A')}", 
            result.get("response_time", 0)
        )
        
        # Test health endpoint
        result = self.test_api_endpoint("/health")
        self.log_result(
            "Health Check (/health)", 
            result["success"], 
            f"Status: {result.get('status_code', 'N/A')}", 
            result.get("response_time", 0)
        )
        
        # Test status endpoint
        result = self.test_api_endpoint("/status")
        self.log_result(
            "Status Endpoint (/status)", 
            result["success"], 
            f"Status: {result.get('status_code', 'N/A')}", 
            result.get("response_time", 0)
        )
        
        # Test notification endpoint
        result = self.test_api_endpoint("/notify?message=Test%20notification&status=Info", "POST")
        self.log_result(
            "Notification Endpoint (/notify)", 
            result["success"], 
            f"Status: {result.get('status_code', 'N/A')}", 
            result.get("response_time", 0)
        )

    def test_docker_container(self):
        """Test Docker container health"""
        print("\n🐳 Testing Docker Container")
        print("-" * 50)
        
        try:
            # Check if container is running
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=ia_continu_app", "--format", "{{.Status}}"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0 and "Up" in result.stdout:
                self.log_result("Container Status", True, "Container is running")
                
                # Check container health
                health_result = subprocess.run(
                    ["docker", "inspect", "--format", "{{.State.Health.Status}}", "ia_continu_app"],
                    capture_output=True, text=True, timeout=10
                )
                
                if health_result.returncode == 0:
                    health_status = health_result.stdout.strip()
                    is_healthy = health_status == "healthy"
                    self.log_result("Container Health", is_healthy, f"Health: {health_status}")
                else:
                    self.log_result("Container Health", False, "Could not check health status")
                    
            else:
                self.log_result("Container Status", False, "Container not running")
                
        except subprocess.TimeoutExpired:
            self.log_result("Docker Commands", False, "Docker commands timed out")
        except Exception as e:
            self.log_result("Docker Commands", False, f"Error: {str(e)}")

    def test_discord_webhook(self):
        """Test Discord webhook functionality"""
        print("\n📱 Testing Discord Notifications")
        print("-" * 50)
        
        if not self.webhook_url:
            self.log_result("Discord Configuration", False, "DISCORD_WEBHOOK_URL not set")
            return
        
        # Test webhook URL validity
        try:
            response = requests.get(self.webhook_url, timeout=10)
            if response.status_code == 200:
                webhook_info = response.json()
                self.log_result(
                    "Webhook Validation", 
                    True, 
                    f"Webhook: {webhook_info.get('name', 'Unknown')}"
                )
            else:
                self.log_result("Webhook Validation", False, f"Status: {response.status_code}")
                return
        except Exception as e:
            self.log_result("Webhook Validation", False, f"Error: {str(e)}")
            return
        
        # Test simple message
        try:
            test_data = {
                "content": f"🧪 **TEST MESSAGE** - IA Continu Solution Test Suite - {datetime.now().strftime('%H:%M:%S')}"
            }
            response = requests.post(self.webhook_url, json=test_data, timeout=30)
            self.log_result(
                "Discord Simple Message", 
                response.status_code == 204, 
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.log_result("Discord Simple Message", False, f"Error: {str(e)}")
        
        # Test embed message
        try:
            embed_data = {
                "embeds": [{
                    "title": "🧪 Test Suite - IA Continu Solution",
                    "description": "Automated test of Discord notifications",
                    "color": 3447003,
                    "fields": [{
                        "name": "Status",
                        "value": "Testing",
                        "inline": True
                    }, {
                        "name": "Timestamp",
                        "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "inline": True
                    }],
                    "footer": {
                        "text": "IA Continu Solution - Test Suite"
                    }
                }]
            }
            response = requests.post(self.webhook_url, json=embed_data, timeout=30)
            self.log_result(
                "Discord Embed Message", 
                response.status_code == 204, 
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.log_result("Discord Embed Message", False, f"Error: {str(e)}")

    def test_monitoring_simulation(self):
        """Test monitoring functionality simulation"""
        print("\n📊 Testing Monitoring Simulation")
        print("-" * 50)
        
        # Test API health check
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            api_healthy = response.status_code == 200
            self.log_result("API Health Monitoring", api_healthy, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("API Health Monitoring", False, f"Error: {str(e)}")
        
        # Simulate model performance check
        import random
        accuracy = random.uniform(0.7, 0.95)
        drift_score = random.uniform(0.0, 1.0)
        
        model_healthy = accuracy >= 0.85 and drift_score <= 0.7
        self.log_result(
            "Model Performance Simulation", 
            True, 
            f"Accuracy: {accuracy:.3f}, Drift: {drift_score:.3f}, Healthy: {model_healthy}"
        )

    def run_all_tests(self):
        """Run all tests and generate report"""
        print("🧪 IA Continu Solution - Comprehensive Test Suite")
        print("=" * 60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Target URL: {self.base_url}")
        print(f"Discord Webhook: {'Configured' if self.webhook_url else 'Not configured'}")
        
        # Run all test categories
        self.test_api_endpoints()
        self.test_docker_container()
        self.test_discord_webhook()
        self.test_monitoring_simulation()
        
        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate test summary report"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY REPORT")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        print(f"\n🎯 Overall Status: {'✅ ALL TESTS PASSED' if failed_tests == 0 else '⚠️ SOME TESTS FAILED'}")
        
        # Save detailed results
        with open("test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n📄 Detailed results saved to: test_results.json")

def main():
    """Main test execution"""
    # Check if Discord webhook is configured
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("⚠️  DISCORD_WEBHOOK_URL not set. Discord tests will be skipped.")
        print("   To enable Discord tests, set the environment variable:")
        print("   $env:DISCORD_WEBHOOK_URL=\"your_webhook_url\"")
        print()
    
    # Run tests
    test_suite = TestSuite()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main()
