#!/usr/bin/env python3
"""
Enhanced Monitoring Service - Day 4
Comprehensive monitoring with Discord integration for Uptime Kuma and system alerts
"""

from datetime import UTC, datetime
import logging
import os
from pathlib import Path
import time
from typing import Any

import requests

# Configuration
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
API_URL = os.getenv("API_URL", "http://api:8000")
MLFLOW_URL = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
PREFECT_URL = os.getenv("PREFECT_API_URL", "http://prefect-server:4200/api")
UPTIME_KUMA_URL = os.getenv("UPTIME_KUMA_URL", "http://uptime-kuma:3001")
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")
GRAFANA_URL = os.getenv("GRAFANA_URL", "http://grafana:3000")

MONITORING_INTERVAL = int(os.getenv("MONITORING_INTERVAL", "60"))  # 60 seconds

# Setup logging
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(logs_dir / "monitoring.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


class EnhancedMonitoringService:
    """Enhanced monitoring service with Discord integration"""

    def __init__(self):
        self.services = {
            "api": {"url": f"{API_URL}/health", "name": "FastAPI ML Service"},
            "mlflow": {"url": f"{MLFLOW_URL}/health", "name": "MLflow Tracking"},
            "prefect": {
                "url": f"{PREFECT_URL}/health",
                "name": "Prefect Orchestration",
            },
            "prometheus": {
                "url": f"{PROMETHEUS_URL}/-/healthy",
                "name": "Prometheus Metrics",
            },
            "grafana": {
                "url": f"{GRAFANA_URL}/api/health",
                "name": "Grafana Dashboards",
            },
            "uptime_kuma": {"url": f"{UPTIME_KUMA_URL}", "name": "Uptime Kuma Monitor"},
        }

        self.last_status = {}
        self.alert_history = []

    def send_discord_notification(
        self, message: str, status: str = "Info", title: str = "System Monitoring"
    ) -> bool:
        """Send Discord notification with enhanced formatting"""
        if not DISCORD_WEBHOOK_URL:
            logger.warning("Discord webhook not configured")
            return False

        # Color mapping
        color_map = {
            "Succès": 5814783,  # Green
            "Échec": 15158332,  # Red
            "Avertissement": 16776960,  # Yellow
            "Info": 3447003,  # Blue
            "Critical": 10038562,  # Dark Red
            "Recovery": 3066993,  # Dark Green
        }

        color = color_map.get(status, 3447003)

        data = {
            "embeds": [
                {
                    "title": title,
                    "description": message,
                    "color": color,
                    "fields": [
                        {"name": "Status", "value": status, "inline": True},
                        {
                            "name": "Timestamp",
                            "value": datetime.now(UTC).strftime(
                                "%Y-%m-%d %H:%M:%S UTC"
                            ),
                            "inline": True,
                        },
                        {
                            "name": "Service",
                            "value": "Enhanced Monitoring",
                            "inline": True,
                        },
                    ],
                    "footer": {
                        "text": "IA Continu Solution - Day 4 Professional Monitoring"
                    },
                }
            ]
        }

        try:
            response = requests.post(DISCORD_WEBHOOK_URL, json=data, timeout=10)
            if response.status_code == 204:
                logger.info(f"✅ Discord notification sent: {message}")
                return True
            else:
                logger.error(f"❌ Discord notification failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Discord notification error: {e}")
            return False

    def check_service_health(
        self, service_key: str, service_info: dict[str, str]
    ) -> dict[str, Any]:
        """Check health of a specific service"""
        try:
            response = requests.get(service_info["url"], timeout=10)
            is_healthy = response.status_code in [200, 201, 202]

            return {
                "service": service_key,
                "name": service_info["name"],
                "healthy": is_healthy,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "timestamp": datetime.now(UTC).isoformat(),
            }
        except Exception as e:
            return {
                "service": service_key,
                "name": service_info["name"],
                "healthy": False,
                "error": str(e),
                "response_time": None,
                "timestamp": datetime.now(UTC).isoformat(),
            }

    def check_all_services(self) -> dict[str, Any]:
        """Check health of all monitored services"""
        results = {}

        for service_key, service_info in self.services.items():
            results[service_key] = self.check_service_health(service_key, service_info)

        return results

    def detect_status_changes(
        self, current_status: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Detect status changes and generate alerts"""
        changes = []

        for service_key, current in current_status.items():
            previous = self.last_status.get(service_key, {})

            # Check for status change
            if previous.get("healthy") != current.get("healthy"):
                change_type = "recovery" if current.get("healthy") else "failure"

                changes.append(
                    {
                        "service": service_key,
                        "name": current.get("name", service_key),
                        "change_type": change_type,
                        "current_status": current,
                        "previous_status": previous,
                        "timestamp": current.get("timestamp"),
                    }
                )

        return changes

    def send_status_change_alerts(self, changes: list[dict[str, Any]]):
        """Send Discord alerts for status changes"""
        for change in changes:
            service_name = change["name"]
            change_type = change["change_type"]

            if change_type == "failure":
                message = "🚨 **Service Down Alert**\n\n"
                message += f"**Service:** {service_name}\n"
                message += "**Status:** ❌ Unhealthy\n"

                current = change["current_status"]
                if "error" in current:
                    message += f"**Error:** {current['error']}\n"
                elif "status_code" in current:
                    message += f"**Status Code:** {current['status_code']}\n"

                message += f"**Time:** {current.get('timestamp', 'N/A')}"

                self.send_discord_notification(message, "Critical", "🚨 Service Alert")

            elif change_type == "recovery":
                message = "✅ **Service Recovery**\n\n"
                message += f"**Service:** {service_name}\n"
                message += "**Status:** ✅ Healthy\n"

                current = change["current_status"]
                if current.get("response_time"):
                    message += f"**Response Time:** {current['response_time']:.3f}s\n"

                message += f"**Time:** {current.get('timestamp', 'N/A')}"

                self.send_discord_notification(
                    message, "Recovery", "✅ Service Recovery"
                )

    def generate_health_summary(self, status: dict[str, Any]) -> str:
        """Generate a comprehensive health summary"""
        healthy_count = sum(1 for s in status.values() if s.get("healthy", False))
        total_count = len(status)

        summary = "📊 **System Health Summary**\n\n"
        summary += (
            f"**Overall Status:** {healthy_count}/{total_count} services healthy\n\n"
        )

        for service_key, service_status in status.items():
            name = service_status.get("name", service_key)
            is_healthy = service_status.get("healthy", False)

            status_icon = "✅" if is_healthy else "❌"
            summary += f"• **{name}:** {status_icon}\n"

            if (
                is_healthy
                and "response_time" in service_status
                and service_status["response_time"]
            ):
                summary += f"  └─ Response: {service_status['response_time']:.3f}s\n"
            elif not is_healthy and "error" in service_status:
                summary += f"  └─ Error: {service_status['error'][:50]}...\n"

        return summary

    def run_monitoring_cycle(self):
        """Run a single monitoring cycle"""
        logger.info("🔍 Starting monitoring cycle...")

        # Check all services
        current_status = self.check_all_services()

        # Detect status changes
        changes = self.detect_status_changes(current_status)

        # Send alerts for status changes
        if changes:
            self.send_status_change_alerts(changes)

            # Log changes
            for change in changes:
                logger.info(
                    f"Status change detected: {change['name']} - {change['change_type']}"
                )

        # Update last status
        self.last_status = current_status

        # Log summary
        healthy_count = sum(
            1 for s in current_status.values() if s.get("healthy", False)
        )
        total_count = len(current_status)
        logger.info(
            f"Monitoring cycle complete: {healthy_count}/{total_count} services healthy"
        )

        # Send periodic summary (every 10 cycles = 10 minutes)
        if not hasattr(self, "cycle_count"):
            self.cycle_count = 0

        self.cycle_count += 1
        if self.cycle_count % 10 == 0:
            summary = self.generate_health_summary(current_status)
            self.send_discord_notification(summary, "Info", "📊 Periodic Health Report")

    def run(self):
        """Main monitoring loop"""
        logger.info("🚀 Enhanced Monitoring Service started")

        # Send startup notification
        self.send_discord_notification(
            "🚀 **Enhanced Monitoring Service Started**\n\n"
            f"• Monitoring Interval: {MONITORING_INTERVAL} seconds\n"
            f"• Services Monitored: {len(self.services)}\n"
            f"• Discord Notifications: Enabled\n"
            f"• Professional Architecture: Day 4",
            "Succès",
            "🎯 Monitoring Startup",
        )

        try:
            while True:
                self.run_monitoring_cycle()
                time.sleep(MONITORING_INTERVAL)

        except KeyboardInterrupt:
            logger.info("🛑 Monitoring service stopped by user")
            self.send_discord_notification(
                "🛑 **Monitoring Service Stopped**\n\nService manually stopped by administrator.",
                "Avertissement",
                "⚠️ Service Shutdown",
            )
        except Exception as e:
            logger.error(f"❌ Monitoring service error: {e}")
            self.send_discord_notification(
                f"❌ **Monitoring Service Error**\n\n**Error:** {e!s}",
                "Échec",
                "🚨 Service Error",
            )


if __name__ == "__main__":
    monitoring_service = EnhancedMonitoringService()
    monitoring_service.run()
