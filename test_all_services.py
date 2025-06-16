#!/usr/bin/env python3
"""
Test complet de tous les services du Jour 1
Vérifie FastAPI, Prefect UI, et les notifications Discord
"""

import requests
import time
from datetime import datetime

def test_fastapi():
    """Test FastAPI application"""
    print("🔍 Testing FastAPI Application...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:9000/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ FastAPI Health: OK")
            print(f"   📊 Response: {response.json()}")
            
            # Test other endpoints
            endpoints = [
                ("/", "Root endpoint"),
                ("/status", "Status endpoint"),
                ("/docs", "API Documentation")
            ]
            
            for endpoint, description in endpoints:
                try:
                    resp = requests.get(f"http://localhost:9000{endpoint}", timeout=5)
                    if resp.status_code < 400:
                        print(f"   ✅ {description}: OK (Status: {resp.status_code})")
                    else:
                        print(f"   ⚠️  {description}: Warning (Status: {resp.status_code})")
                except Exception as e:
                    print(f"   ❌ {description}: Failed ({e})")
            
            return True
        else:
            print(f"   ❌ FastAPI Health: Failed (Status: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"   ❌ FastAPI: Unreachable ({e})")
        return False

def test_prefect():
    """Test Prefect Server"""
    print("\n🔄 Testing Prefect Server...")
    
    try:
        # Test API health
        response = requests.get("http://localhost:4200/api/health", timeout=10)
        if response.status_code == 200:
            print("   ✅ Prefect API: OK")
            
            # Test UI access
            try:
                ui_response = requests.get("http://localhost:4200", timeout=5)
                if ui_response.status_code == 200:
                    print("   ✅ Prefect UI: Accessible")
                else:
                    print(f"   ⚠️  Prefect UI: Warning (Status: {ui_response.status_code})")
            except Exception as e:
                print(f"   ❌ Prefect UI: Failed ({e})")
            
            return True
        else:
            print(f"   ❌ Prefect API: Failed (Status: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"   ❌ Prefect: Unreachable ({e})")
        return False

def test_discord():
    """Test Discord webhook"""
    print("\n📱 Testing Discord Notifications...")
    
    import os
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    
    if not webhook_url:
        print("   ⚠️  Discord webhook not configured")
        return False
    
    try:
        # Test simple message
        data = {
            "content": f"🧪 **Test Message** - All services verification at {datetime.now().strftime('%H:%M:%S')}"
        }
        
        response = requests.post(webhook_url, json=data, timeout=10)
        if response.status_code == 204:
            print("   ✅ Discord Simple Message: Sent")
            
            # Test embed message
            embed_data = {
                "embeds": [{
                    "title": "🧪 Service Test - IA Continu Solution",
                    "description": "Testing all services for Jour 1 completion",
                    "color": 3447003,
                    "fields": [{
                        "name": "Test Type",
                        "value": "Complete Service Verification",
                        "inline": True
                    }, {
                        "name": "Timestamp",
                        "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "inline": True
                    }],
                    "footer": {
                        "text": "IA Continu Solution - Jour 1"
                    }
                }]
            }
            
            embed_response = requests.post(webhook_url, json=embed_data, timeout=10)
            if embed_response.status_code == 204:
                print("   ✅ Discord Embed Message: Sent")
                return True
            else:
                print(f"   ⚠️  Discord Embed: Warning (Status: {embed_response.status_code})")
                return False
        else:
            print(f"   ❌ Discord: Failed (Status: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"   ❌ Discord: Error ({e})")
        return False

def test_uptime_monitoring():
    """Test uptime monitoring functionality"""
    print("\n🔍 Testing Uptime Monitoring...")
    
    try:
        # Test our simple uptime monitor
        from simple_uptime_monitor import SimpleUptimeMonitor
        
        monitor = SimpleUptimeMonitor()
        status = monitor.check_api_health()
        
        if status["status"] == "up":
            print("   ✅ Uptime Monitor: Working")
            print(f"   📊 Response Time: {status.get('response_time', 0):.2f}ms")
            return True
        else:
            print(f"   ❌ Uptime Monitor: API Down ({status.get('error', 'Unknown')})")
            return False
            
    except Exception as e:
        print(f"   ❌ Uptime Monitor: Error ({e})")
        return False

def main():
    """Main test function"""
    print("🧪 COMPLETE SERVICE VERIFICATION - JOUR 1")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Run all tests
    results = {
        "FastAPI": test_fastapi(),
        "Prefect": test_prefect(),
        "Discord": test_discord(),
        "Uptime Monitor": test_uptime_monitoring()
    }
    
    # Generate summary
    print("\n" + "=" * 60)
    print("📊 SERVICE VERIFICATION SUMMARY")
    print("=" * 60)
    
    total_services = len(results)
    working_services = sum(results.values())
    success_rate = (working_services / total_services * 100) if total_services > 0 else 0
    
    for service, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {service}: {'WORKING' if status else 'FAILED'}")
    
    print(f"\n📈 Overall Status: {working_services}/{total_services} services working ({success_rate:.1f}%)")
    
    # Service URLs
    print(f"\n🔗 Service URLs:")
    print(f"   📱 FastAPI Application: http://localhost:9000")
    print(f"   📚 API Documentation: http://localhost:9000/docs")
    print(f"   🔄 Prefect UI: http://localhost:4200")
    print(f"   📊 Prefect Dashboard: http://localhost:4200")
    
    # Recommendations
    if working_services == total_services:
        print(f"\n🎉 ALL SERVICES WORKING! Jour 1 is complete and ready.")
        print(f"   You can now access:")
        print(f"   • FastAPI at http://localhost:9000")
        print(f"   • Prefect UI at http://localhost:4200")
        print(f"   • Discord notifications are functional")
    else:
        print(f"\n⚠️  Some services need attention:")
        for service, status in results.items():
            if not status:
                print(f"   • {service}: Needs troubleshooting")
    
    print(f"\n📄 Next steps:")
    print(f"   1. Open browser tabs for working services")
    print(f"   2. Configure Uptime Kuma monitoring (when network allows)")
    print(f"   3. Test Prefect flow execution")
    print(f"   4. Verify Discord notifications in your channel")

if __name__ == "__main__":
    main()
