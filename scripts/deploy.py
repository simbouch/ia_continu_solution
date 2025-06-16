#!/usr/bin/env python3
"""
Deployment script for IA Continu Solution
Provides easy deployment and management commands
"""

import subprocess
import sys
import os
import time
import requests
from typing import List, Dict, Any

class DeploymentManager:
    """Manages deployment of IA Continu Solution"""
    
    def __init__(self):
        self.container_name = "ia_continu_app"
        self.image_name = "fastapi-app"
        self.port = 9000
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    
    def run_command(self, command: List[str], capture_output: bool = True) -> subprocess.CompletedProcess:
        """Run shell command and return result"""
        try:
            result = subprocess.run(
                command, 
                capture_output=capture_output, 
                text=True, 
                timeout=60
            )
            return result
        except subprocess.TimeoutExpired:
            print(f"❌ Command timed out: {' '.join(command)}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Command failed: {e}")
            sys.exit(1)
    
    def check_docker(self) -> bool:
        """Check if Docker is available"""
        result = self.run_command(["docker", "--version"])
        if result.returncode == 0:
            print("✅ Docker is available")
            return True
        else:
            print("❌ Docker is not available")
            return False
    
    def build_image(self) -> bool:
        """Build Docker image"""
        print("🔨 Building Docker image...")
        result = self.run_command(["docker", "build", "-t", self.image_name, "."], capture_output=False)
        
        if result.returncode == 0:
            print("✅ Docker image built successfully")
            return True
        else:
            print("❌ Failed to build Docker image")
            return False
    
    def stop_existing_container(self) -> bool:
        """Stop and remove existing container"""
        print("🛑 Stopping existing container...")
        
        # Check if container exists
        result = self.run_command(["docker", "ps", "-a", "--filter", f"name={self.container_name}", "--format", "{{.Names}}"])
        
        if self.container_name in result.stdout:
            # Stop container
            stop_result = self.run_command(["docker", "stop", self.container_name])
            if stop_result.returncode == 0:
                print("✅ Container stopped")
            
            # Remove container
            remove_result = self.run_command(["docker", "rm", self.container_name])
            if remove_result.returncode == 0:
                print("✅ Container removed")
                return True
            else:
                print("❌ Failed to remove container")
                return False
        else:
            print("ℹ️  No existing container found")
            return True
    
    def start_container(self) -> bool:
        """Start new container"""
        print("🚀 Starting new container...")
        
        command = [
            "docker", "run", "-d",
            "-p", f"{self.port}:8000",
            "--name", self.container_name
        ]
        
        # Add Discord webhook if available
        if self.webhook_url:
            command.extend(["-e", f"DISCORD_WEBHOOK_URL={self.webhook_url}"])
            print("📱 Discord notifications enabled")
        else:
            print("📱 Discord notifications disabled (no webhook URL)")
        
        command.append(self.image_name)
        
        result = self.run_command(command)
        
        if result.returncode == 0:
            print("✅ Container started successfully")
            return True
        else:
            print("❌ Failed to start container")
            print(f"Error: {result.stderr}")
            return False
    
    def wait_for_health(self, timeout: int = 60) -> bool:
        """Wait for application to be healthy"""
        print("⏳ Waiting for application to be healthy...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"http://localhost:{self.port}/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Application is healthy")
                    return True
            except requests.RequestException:
                pass
            
            time.sleep(2)
            print(".", end="", flush=True)
        
        print("\n❌ Application failed to become healthy")
        return False
    
    def test_deployment(self) -> bool:
        """Test the deployment"""
        print("🧪 Testing deployment...")
        
        tests = [
            ("Root endpoint", f"http://localhost:{self.port}/"),
            ("Health check", f"http://localhost:{self.port}/health"),
            ("Status endpoint", f"http://localhost:{self.port}/status")
        ]
        
        all_passed = True
        for test_name, url in tests:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    print(f"✅ {test_name}: PASS")
                else:
                    print(f"❌ {test_name}: FAIL (Status: {response.status_code})")
                    all_passed = False
            except requests.RequestException as e:
                print(f"❌ {test_name}: FAIL (Error: {e})")
                all_passed = False
        
        return all_passed
    
    def send_deployment_notification(self, success: bool) -> None:
        """Send deployment notification to Discord"""
        if not self.webhook_url:
            return
        
        status = "✅ SUCCESS" if success else "❌ FAILED"
        message = f"🚀 **Deployment {status}**\n\nIA Continu Solution has been {'successfully deployed' if success else 'deployment failed'}"
        
        data = {
            "embeds": [{
                "title": "🚀 IA Continu Solution - Deployment",
                "description": message,
                "color": 5814783 if success else 15158332,
                "fields": [{
                    "name": "Status",
                    "value": "Deployed" if success else "Failed",
                    "inline": True
                }, {
                    "name": "URL",
                    "value": f"http://localhost:{self.port}",
                    "inline": True
                }],
                "footer": {
                    "text": "IA Continu Solution - Deployment Manager"
                }
            }]
        }
        
        try:
            response = requests.post(self.webhook_url, json=data, timeout=10)
            if response.status_code == 204:
                print("📱 Deployment notification sent to Discord")
        except requests.RequestException:
            print("⚠️  Failed to send deployment notification")
    
    def deploy(self) -> bool:
        """Full deployment process"""
        print("🚀 IA Continu Solution - Deployment Manager")
        print("=" * 50)
        
        # Check prerequisites
        if not self.check_docker():
            return False
        
        # Build image
        if not self.build_image():
            return False
        
        # Stop existing container
        if not self.stop_existing_container():
            return False
        
        # Start new container
        if not self.start_container():
            return False
        
        # Wait for health
        if not self.wait_for_health():
            return False
        
        # Test deployment
        if not self.test_deployment():
            print("⚠️  Some tests failed, but deployment completed")
        
        print("\n" + "=" * 50)
        print("🎉 Deployment completed successfully!")
        print(f"📱 Application URL: http://localhost:{self.port}")
        print(f"📚 API Documentation: http://localhost:{self.port}/docs")
        print(f"🔍 Health Check: http://localhost:{self.port}/health")
        
        # Send notification
        self.send_deployment_notification(True)
        
        return True
    
    def status(self) -> None:
        """Show deployment status"""
        print("📊 IA Continu Solution - Status")
        print("=" * 40)
        
        # Check container status
        result = self.run_command(["docker", "ps", "--filter", f"name={self.container_name}", "--format", "{{.Status}}"])
        
        if result.stdout.strip():
            print(f"🐳 Container: {result.stdout.strip()}")
            
            # Check application health
            try:
                response = requests.get(f"http://localhost:{self.port}/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Application: Healthy")
                    health_data = response.json()
                    print(f"📊 Version: {health_data.get('version', 'Unknown')}")
                else:
                    print(f"⚠️  Application: Unhealthy (Status: {response.status_code})")
            except requests.RequestException:
                print("❌ Application: Unreachable")
        else:
            print("❌ Container: Not running")
        
        # Show URLs
        print(f"\n🔗 URLs:")
        print(f"   Application: http://localhost:{self.port}")
        print(f"   Documentation: http://localhost:{self.port}/docs")
        print(f"   Health: http://localhost:{self.port}/health")
    
    def logs(self) -> None:
        """Show container logs"""
        print("📋 Container Logs:")
        print("-" * 30)
        self.run_command(["docker", "logs", "--tail", "50", self.container_name], capture_output=False)
    
    def stop(self) -> None:
        """Stop the application"""
        print("🛑 Stopping IA Continu Solution...")
        if self.stop_existing_container():
            print("✅ Application stopped successfully")
        else:
            print("❌ Failed to stop application")

def main():
    """Main CLI interface"""
    manager = DeploymentManager()
    
    if len(sys.argv) < 2:
        print("Usage: python deploy.py [deploy|status|logs|stop]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "deploy":
        success = manager.deploy()
        sys.exit(0 if success else 1)
    elif command == "status":
        manager.status()
    elif command == "logs":
        manager.logs()
    elif command == "stop":
        manager.stop()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: deploy, status, logs, stop")
        sys.exit(1)

if __name__ == "__main__":
    main()
