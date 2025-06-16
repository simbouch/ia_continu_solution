#!/usr/bin/env python3
"""
Monitoring utilities for IA Continu Solution
Provides model performance monitoring and API health checks with Discord notifications
"""

import os
import random
import requests
from datetime import datetime
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModelMonitor:
    """Model performance monitoring with drift detection"""
    
    def __init__(self, accuracy_threshold: float = 0.85, drift_threshold: float = 0.7):
        self.accuracy_threshold = accuracy_threshold
        self.drift_threshold = drift_threshold
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    
    def send_discord_notification(self, message: str, status: str = "Info") -> bool:
        """Send notification to Discord webhook"""
        if not self.webhook_url:
            logger.warning("Discord webhook URL not configured")
            return False
        
        color_map = {
            "Succès": 5814783,    # Green
            "Erreur": 15158332,   # Red
            "Avertissement": 16776960,  # Yellow
            "Info": 3447003       # Blue
        }
        
        data = {
            "embeds": [{
                "title": "🤖 IA Continu Solution - Monitoring Alert",
                "description": message,
                "color": color_map.get(status, 3447003),
                "fields": [{
                    "name": "Status",
                    "value": status,
                    "inline": True
                }, {
                    "name": "Timestamp",
                    "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "inline": True
                }],
                "footer": {
                    "text": "IA Continu Solution - Model Monitor"
                }
            }]
        }
        
        try:
            response = requests.post(self.webhook_url, json=data, timeout=30)
            if response.status_code == 204:
                logger.info("Discord notification sent successfully")
                return True
            else:
                logger.error(f"Discord notification failed: {response.status_code}")
                return False
        except requests.RequestException as e:
            logger.error(f"Discord notification error: {e}")
            return False
    
    def check_model_performance(self) -> dict:
        """Simulate model performance check with random metrics"""
        # Simulate model metrics
        accuracy = random.uniform(0.7, 0.95)
        drift_score = random.uniform(0.0, 1.0)
        
        logger.info(f"Model metrics - Accuracy: {accuracy:.3f}, Drift: {drift_score:.3f}")
        
        # Evaluate performance
        if accuracy < self.accuracy_threshold:
            message = f"⚠️ Model accuracy ({accuracy:.3f}) below threshold ({self.accuracy_threshold})"
            logger.warning(message)
            self.send_discord_notification(message, "Avertissement")
            return {"status": "warning", "accuracy": accuracy, "drift_score": drift_score}
        
        if drift_score > self.drift_threshold:
            message = f"🚨 Model drift detected! Score: {drift_score:.3f} (threshold: {self.drift_threshold})"
            logger.error(message)
            self.send_discord_notification(message, "Erreur")
            return {"status": "error", "accuracy": accuracy, "drift_score": drift_score}
        
        message = f"✅ Model performing well - Accuracy: {accuracy:.3f}, Drift: {drift_score:.3f}"
        logger.info(message)
        self.send_discord_notification(message, "Succès")
        return {"status": "healthy", "accuracy": accuracy, "drift_score": drift_score}

class APIHealthMonitor:
    """API health monitoring"""
    
    def __init__(self, api_url: str = "http://localhost:9000"):
        self.api_url = api_url
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    
    def send_discord_notification(self, message: str, status: str = "Info") -> bool:
        """Send notification to Discord webhook"""
        if not self.webhook_url:
            logger.warning("Discord webhook URL not configured")
            return False
        
        data = {"content": f"🔍 **API Monitor**: {message}"}
        
        try:
            response = requests.post(self.webhook_url, json=data, timeout=30)
            return response.status_code == 204
        except requests.RequestException as e:
            logger.error(f"Discord notification error: {e}")
            return False
    
    def check_api_health(self) -> dict:
        """Check API health status"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            
            if response.status_code == 200:
                logger.info("API health check passed")
                return {"api_status": "healthy", "response_time": response.elapsed.total_seconds()}
            else:
                message = f"API health check failed: Status {response.status_code}"
                logger.warning(message)
                self.send_discord_notification(message, "Avertissement")
                return {"api_status": "unhealthy", "status_code": response.status_code}
                
        except requests.RequestException as e:
            message = f"API unreachable: {str(e)}"
            logger.error(message)
            self.send_discord_notification(message, "Erreur")
            return {"api_status": "unreachable", "error": str(e)}

class MonitoringService:
    """Combined monitoring service"""
    
    def __init__(self, api_url: str = "http://localhost:9000"):
        self.model_monitor = ModelMonitor()
        self.api_monitor = APIHealthMonitor(api_url)
    
    def run_monitoring_cycle(self) -> dict:
        """Run one complete monitoring cycle"""
        logger.info("Starting monitoring cycle")
        
        # Check model performance
        model_metrics = self.model_monitor.check_model_performance()
        
        # Check API health
        api_metrics = self.api_monitor.check_api_health()
        
        # Combine results
        results = {
            "timestamp": datetime.now().isoformat(),
            "model": model_metrics,
            "api": api_metrics
        }
        
        logger.info("Monitoring cycle completed")
        return results
    
    def run_continuous_monitoring(self, interval: int = 30, cycles: int = None):
        """Run continuous monitoring"""
        logger.info(f"Starting continuous monitoring (interval: {interval}s)")
        
        cycle_count = 0
        try:
            while cycles is None or cycle_count < cycles:
                cycle_count += 1
                logger.info(f"Monitoring cycle #{cycle_count}")
                
                results = self.run_monitoring_cycle()
                
                # Log summary
                logger.info(f"Cycle #{cycle_count} - Model: {results['model']['status']}, API: {results['api']['api_status']}")
                
                if cycles is None or cycle_count < cycles:
                    logger.info(f"Waiting {interval} seconds until next cycle...")
                    time.sleep(interval)
                    
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")

def main():
    """Main monitoring execution"""
    print("🔄 IA Continu Solution - Monitoring Service")
    print("=" * 50)
    
    # Check configuration
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if webhook_url:
        print("📱 Discord notifications: ENABLED")
    else:
        print("📱 Discord notifications: DISABLED (no webhook URL)")
        print("   Set DISCORD_WEBHOOK_URL environment variable to enable")
    
    # Initialize monitoring service
    monitor = MonitoringService()
    
    print("\nChoose monitoring mode:")
    print("1. Single cycle")
    print("2. Continuous monitoring (30s intervals)")
    print("3. Demo mode (3 cycles with 10s intervals)")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            print("\n🔍 Running single monitoring cycle...")
            results = monitor.run_monitoring_cycle()
            print(f"\n📊 Results:")
            print(f"   Model Status: {results['model']['status']}")
            print(f"   API Status: {results['api']['api_status']}")
            
        elif choice == "2":
            print("\n🔄 Starting continuous monitoring...")
            print("   Press Ctrl+C to stop")
            monitor.run_continuous_monitoring()
            
        elif choice == "3":
            print("\n🎭 Running demo mode (3 cycles)...")
            monitor.run_continuous_monitoring(interval=10, cycles=3)
            
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Monitoring stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
