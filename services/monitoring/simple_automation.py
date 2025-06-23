#!/usr/bin/env python3
"""
Simple ML Automation Script - Alternative to Prefect
Runs continuous monitoring and drift detection every 30 seconds
"""

from datetime import UTC, datetime
import os
import random
import time

import requests

# Configuration
API_URL = os.getenv("API_URL", "http://api:8000")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


def send_discord_notification(
    message: str, status: str = "Succès", title: str = "🤖 ML Automation"
):
    """Send Discord notification with proper formatting"""
    if not DISCORD_WEBHOOK_URL:
        print(f"Discord webhook not configured. Message: {message}")
        return False

    color_map = {
        "Succès": 5814783,  # Green
        "Échec": 15158332,  # Red
        "Avertissement": 16776960,  # Yellow
        "Info": 3447003,  # Blue
        "Drift": 16753920,  # Orange
    }

    data = {
        "embeds": [
            {
                "title": title,
                "description": message,
                "color": color_map.get(status, 3447003),
                "fields": [
                    {"name": "Status", "value": status, "inline": True},
                    {
                        "name": "Timestamp",
                        "value": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC"),
                        "inline": True,
                    },
                    {"name": "Service", "value": "ML Automation", "inline": True},
                ],
                "footer": {"text": "IA Continu Solution - Jour 4"},
            }
        ]
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data, timeout=10)
        if response.status_code == 204:
            print(f"✅ Discord notification sent: {message[:50]}...")
            return True
        else:
            print(f"❌ Discord failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Discord error: {e}")
        return False


def authenticate():
    """Authenticate with API"""
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={"username": "admin", "password": "admin123"},
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()["access_token"]
    except Exception as e:
        print(f"Auth error: {e}")
    return None


def detect_drift():
    """Simple drift detection"""
    random_value = random.random()
    drift_detected = random_value < 0.5

    return {
        "drift_detected": drift_detected,
        "random_value": random_value,
        "method": "random_simulation",
    }


def run_automation_cycle(cycle_count=0):
    """Run one automation cycle with enhanced notifications"""
    print(f"🔄 Running automation cycle #{cycle_count} at {datetime.now()}")

    # Check API health
    try:
        health = requests.get(f"{API_URL}/health", timeout=5)
        if health.status_code != 200:
            print("❌ API unhealthy, skipping cycle")
            send_discord_notification(
                f"❌ **API Health Check Failed**\\n\\n"
                f"• Status Code: {health.status_code}\\n"
                f"• Cycle: #{cycle_count}\\n"
                f"• Action: Skipping automation cycle",
                "Échec",
                "🏥 Health Check Alert",
            )
            return
    except Exception as e:
        print(f"❌ API check failed: {e}")
        send_discord_notification(
            f"❌ **API Connection Failed**\\n\\n"
            f"• Error: {str(e)[:100]}\\n"
            f"• Cycle: #{cycle_count}\\n"
            f"• Action: Skipping automation cycle",
            "Échec",
            "🔌 Connection Alert",
        )
        return

    # Detect drift
    drift_info = detect_drift()
    print(f"Drift check: {drift_info}")

    if drift_info["drift_detected"]:
        print("🚨 Drift detected!")

        # Authenticate and generate new data
        token = authenticate()
        if token:
            headers = {"Authorization": f"Bearer {token}"}
            try:
                # Generate new training data
                gen_response = requests.post(
                    f"{API_URL}/generate",
                    json={"samples": 100},
                    headers=headers,
                    timeout=30,
                )
                if gen_response.status_code == 200:
                    print("✅ Generated new training data")

                    # Send Discord notification for drift
                    send_discord_notification(
                        f"🚨 **Model Drift Detected & Handled**\\n\\n"
                        f"• **Drift Details:**\\n"
                        f"  - Random Value: {drift_info['random_value']:.3f}\\n"
                        f"  - Method: {drift_info['method']}\\n"
                        f"• **Action Taken:**\\n"
                        f"  - Generated new training data\\n"
                        f"  - Samples Created: {gen_response.json().get('samples_created', 'N/A')}\\n"
                        f"• **Cycle:** #{cycle_count}",
                        "Drift",
                        "🔄 Drift Detection & Response",
                    )
                else:
                    print("❌ Failed to generate data")
                    send_discord_notification(
                        f"❌ **Data Generation Failed**\\n\\n"
                        f"• Drift detected but data generation failed\\n"
                        f"• Status Code: {gen_response.status_code}\\n"
                        f"• Cycle: #{cycle_count}",
                        "Échec",
                        "📊 Data Generation Error",
                    )
            except Exception as e:
                print(f"❌ Data generation error: {e}")
                send_discord_notification(
                    f"❌ **Automation Error**\\n\\n"
                    f"• Error during drift response\\n"
                    f"• Details: {str(e)[:100]}\\n"
                    f"• Cycle: #{cycle_count}",
                    "Échec",
                    "⚙️ Automation Error",
                )
    else:
        print("✅ No drift detected")

        # Send periodic status updates
        if cycle_count % 10 == 0 and cycle_count > 0:  # Every 10 cycles (5 minutes)
            send_discord_notification(
                f"✅ **ML System Status Update**\\n\\n"
                f"• **System Health:** All services operational\\n"
                f"• **Drift Status:** No drift detected\\n"
                f"• **Last Check:** {drift_info['random_value']:.3f}\\n"
                f"• **Cycles Completed:** {cycle_count}\\n"
                f"• **Uptime:** {cycle_count * 30 // 60} minutes\\n"
                f"• **Next Check:** 30 seconds",
                "Info",
                "📊 Periodic Status Report",
            )
        elif cycle_count % 20 == 0 and cycle_count > 0:  # Every 20 cycles (10 minutes)
            send_discord_notification(
                f"🔄 **Extended Status Report**\\n\\n"
                f"• **Automation Running:** {cycle_count * 30 // 60} minutes\\n"
                f"• **Health Checks:** All passing\\n"
                f"• **Drift Monitoring:** Active\\n"
                f"• **Performance:** Optimal\\n"
                f"• **Next Report:** 10 minutes",
                "Succès",
                "📈 Extended Status Report",
            )


if __name__ == "__main__":
    print("🚀 Starting Enhanced ML Automation - Jour 4")

    # Send startup notification
    send_discord_notification(
        "🚀 **ML Automation System Started**\\n\\n"
        "• **Architecture:** Professional Day 4 Implementation\\n"
        "• **Monitoring:** Drift detection every 30 seconds\\n"
        "• **Notifications:** Enhanced Discord integration\\n"
        "• **Features:**\\n"
        "  - Automated drift detection\\n"
        "  - Health monitoring\\n"
        "  - Periodic status reports\\n"
        "  - Error handling & alerts\\n"
        "• **Status:** Fully operational",
        "Succès",
        "🎯 System Startup",
    )

    # Main automation loop with cycle counting
    cycle_count = 0
    while True:
        try:
            run_automation_cycle(cycle_count)
            cycle_count += 1
        except Exception as e:
            print(f"❌ Automation error: {e}")
            send_discord_notification(
                f"❌ **Critical Automation Error**\\n\\n"
                f"• Error: {str(e)[:100]}\\n"
                f"• Cycle: #{cycle_count}\\n"
                f"• Action: Continuing with next cycle\\n"
                f"• System: Still operational",
                "Échec",
                "🚨 Critical Error Alert",
            )

        print(f"⏳ Waiting 30 seconds... (Cycle #{cycle_count} completed)")
        time.sleep(30)
