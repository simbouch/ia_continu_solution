#!/usr/bin/env python3
"""
Simple Uptime Monitor - Alternative to Uptime Kuma
Monitors the FastAPI application and sends Discord notifications
"""

import requests
import time
import os
from datetime import datetime
from typing import Dict, Any

class SimpleUptimeMonitor:
    """Simple uptime monitoring for FastAPI application"""
    
    def __init__(self, api_url: str = "http://localhost:9000", check_interval: int = 30):
        self.api_url = api_url
        self.check_interval = check_interval
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        self.last_status = None
        self.downtime_start = None
        self.uptime_start = datetime.now()
        
    def send_discord_notification(self, message: str, status: str = "Info", color: int = 3447003):
        """Send notification to Discord webhook"""
        if not self.webhook_url:
            print("Discord webhook URL not configured")
            return False
        
        data = {
            "embeds": [{
                "title": "🔍 Uptime Monitor - IA Continu Solution",
                "description": message,
                "color": color,
                "fields": [{
                    "name": "Status",
                    "value": status,
                    "inline": True
                }, {
                    "name": "Timestamp",
                    "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "inline": True
                }, {
                    "name": "API URL",
                    "value": self.api_url,
                    "inline": True
                }],
                "footer": {
                    "text": "Simple Uptime Monitor"
                }
            }]
        }
        
        try:
            response = requests.post(self.webhook_url, json=data, timeout=10)
            if response.status_code == 204:
                print(f"✅ Discord notification sent: {status}")
                return True
            else:
                print(f"❌ Discord notification failed: {response.status_code}")
                return False
        except requests.RequestException as e:
            print(f"❌ Discord notification error: {e}")
            return False
    
    def check_api_health(self) -> Dict[str, Any]:
        """Check API health and return status"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_url}/health", timeout=5)
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            if response.status_code == 200:
                return {
                    "status": "up",
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "down",
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "timestamp": datetime.now().isoformat(),
                    "error": f"HTTP {response.status_code}"
                }
        except requests.RequestException as e:
            return {
                "status": "down",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def handle_status_change(self, current_status: Dict[str, Any]):
        """Handle status changes and send notifications"""
        current_state = current_status["status"]
        
        if self.last_status is None:
            # First check
            if current_state == "up":
                message = f"🟢 **API is UP** - Initial check successful"
                self.send_discord_notification(message, "Online", 5814783)  # Green
            else:
                message = f"🔴 **API is DOWN** - Initial check failed: {current_status.get('error', 'Unknown error')}"
                self.send_discord_notification(message, "Offline", 15158332)  # Red
                self.downtime_start = datetime.now()
        
        elif self.last_status["status"] != current_state:
            # Status changed
            if current_state == "up":
                # API came back online
                if self.downtime_start:
                    downtime_duration = datetime.now() - self.downtime_start
                    message = f"🟢 **API RECOVERED** - Back online after {downtime_duration}"
                else:
                    message = f"🟢 **API is UP** - Service restored"
                
                self.send_discord_notification(message, "Recovered", 5814783)  # Green
                self.downtime_start = None
                
            else:
                # API went down
                message = f"🔴 **API DOWN** - Service unavailable: {current_status.get('error', 'Unknown error')}"
                self.send_discord_notification(message, "Down", 15158332)  # Red
                self.downtime_start = datetime.now()
    
    def print_status(self, status: Dict[str, Any]):
        """Print current status to console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if status["status"] == "up":
            response_time = status.get("response_time", 0)
            print(f"[{timestamp}] ✅ API UP - Response time: {response_time:.2f}ms")
        else:
            error = status.get("error", "Unknown error")
            print(f"[{timestamp}] ❌ API DOWN - Error: {error}")
    
    def run_monitoring(self, duration_minutes: int = None):
        """Run continuous monitoring"""
        print("🔍 Simple Uptime Monitor Started")
        print(f"📊 Monitoring: {self.api_url}")
        print(f"⏱️  Check interval: {self.check_interval} seconds")
        print(f"📱 Discord notifications: {'Enabled' if self.webhook_url else 'Disabled'}")
        print("-" * 60)
        
        start_time = datetime.now()
        check_count = 0
        
        try:
            while True:
                check_count += 1
                current_status = self.check_api_health()
                
                # Handle status changes and notifications
                self.handle_status_change(current_status)
                
                # Print status
                self.print_status(current_status)
                
                # Update last status
                self.last_status = current_status
                
                # Check if we should stop (for demo mode)
                if duration_minutes:
                    elapsed = (datetime.now() - start_time).total_seconds() / 60
                    if elapsed >= duration_minutes:
                        print(f"\n⏹️  Monitoring completed after {duration_minutes} minutes")
                        break
                
                # Wait for next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print(f"\n⏹️  Monitoring stopped by user after {check_count} checks")
        except Exception as e:
            print(f"\n❌ Monitoring error: {e}")
        
        # Send final summary
        if self.webhook_url:
            uptime_duration = datetime.now() - self.uptime_start
            summary = f"📊 **Monitoring Summary**\nChecks performed: {check_count}\nMonitoring duration: {uptime_duration}\nLast status: {self.last_status['status'] if self.last_status else 'Unknown'}"
            self.send_discord_notification(summary, "Summary", 3447003)  # Blue

def main():
    """Main function"""
    print("🔍 Simple Uptime Monitor for IA Continu Solution")
    print("=" * 60)
    
    # Check if Discord webhook is configured
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("⚠️  DISCORD_WEBHOOK_URL not configured")
        print("   Set environment variable to enable notifications:")
        print("   $env:DISCORD_WEBHOOK_URL=\"your_webhook_url\"")
        print()
    
    # Initialize monitor
    monitor = SimpleUptimeMonitor()
    
    print("Choose monitoring mode:")
    print("1. Continuous monitoring (30s intervals)")
    print("2. Demo mode (5 minutes)")
    print("3. Quick test (3 checks)")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            print("\n🔄 Starting continuous monitoring...")
            print("   Press Ctrl+C to stop")
            monitor.run_monitoring()
            
        elif choice == "2":
            print("\n🎭 Running demo mode (5 minutes)...")
            monitor.run_monitoring(duration_minutes=5)
            
        elif choice == "3":
            print("\n🧪 Running quick test (3 checks)...")
            for i in range(3):
                status = monitor.check_api_health()
                monitor.handle_status_change(status)
                monitor.print_status(status)
                monitor.last_status = status
                if i < 2:
                    time.sleep(5)
            
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Monitoring stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
