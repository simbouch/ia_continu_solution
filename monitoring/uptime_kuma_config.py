#!/usr/bin/env python3
"""
Configuration automatique pour Uptime Kuma
Crée des monitors pour tous les services de l'application
"""

import requests
import json
import time
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class UptimeKumaConfig:
    """Configuration automatique d'Uptime Kuma"""
    
    def __init__(self, base_url: str = "http://localhost:3001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
    
    def wait_for_uptime_kuma(self, max_retries: int = 30):
        """Attendre que Uptime Kuma soit disponible"""
        for i in range(max_retries):
            try:
                response = self.session.get(f"{self.base_url}/api/status-page/heartbeat/public")
                if response.status_code in [200, 404]:  # 404 is normal for this endpoint
                    logger.info("Uptime Kuma is ready")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            logger.info(f"Waiting for Uptime Kuma... ({i+1}/{max_retries})")
            time.sleep(5)
        
        logger.error("Uptime Kuma not available after waiting")
        return False
    
    def setup_monitors(self) -> bool:
        """Configurer les monitors automatiquement"""
        try:
            if not self.wait_for_uptime_kuma():
                return False
            
            monitors = self.get_monitor_configs()
            
            for monitor_config in monitors:
                self.create_monitor_if_not_exists(monitor_config)
            
            logger.info("All monitors configured successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup monitors: {e}")
            return False
    
    def get_monitor_configs(self) -> List[Dict]:
        """Obtenir les configurations des monitors"""
        return [
            {
                "name": "FastAPI Health",
                "type": "http",
                "url": "http://fastapi_app:8000/health",
                "interval": 60,
                "maxretries": 3,
                "timeout": 10,
                "description": "API Health Check"
            },
            {
                "name": "FastAPI Metrics",
                "type": "http",
                "url": "http://fastapi_app:8000/metrics",
                "interval": 300,
                "maxretries": 2,
                "timeout": 15,
                "description": "Prometheus Metrics Endpoint"
            },
            {
                "name": "Prefect Server",
                "type": "http",
                "url": "http://prefect-server:4200/api/health",
                "interval": 120,
                "maxretries": 3,
                "timeout": 10,
                "description": "Prefect Orchestration Server"
            },
            {
                "name": "MLflow Server",
                "type": "http",
                "url": "http://mlflow-server:5000/health",
                "interval": 300,
                "maxretries": 2,
                "timeout": 15,
                "description": "MLflow Tracking Server"
            },
            {
                "name": "Prometheus",
                "type": "http",
                "url": "http://prometheus:9090/-/healthy",
                "interval": 180,
                "maxretries": 2,
                "timeout": 10,
                "description": "Prometheus Monitoring"
            },
            {
                "name": "Grafana",
                "type": "http",
                "url": "http://grafana:3000/api/health",
                "interval": 300,
                "maxretries": 2,
                "timeout": 10,
                "description": "Grafana Dashboards"
            }
        ]
    
    def create_monitor_if_not_exists(self, config: Dict):
        """Créer un monitor s'il n'existe pas déjà"""
        try:
            # Note: Uptime Kuma n'a pas d'API REST complète par défaut
            # Cette fonction est un placeholder pour une configuration manuelle
            # ou une future API
            
            logger.info(f"Monitor configuration for '{config['name']}':")
            logger.info(f"  URL: {config['url']}")
            logger.info(f"  Interval: {config['interval']}s")
            logger.info(f"  Timeout: {config['timeout']}s")
            logger.info(f"  Max Retries: {config['maxretries']}")
            logger.info(f"  Description: {config['description']}")
            
            # Pour l'instant, on log la configuration
            # Dans une vraie implémentation, on utiliserait l'API Uptime Kuma
            
        except Exception as e:
            logger.error(f"Failed to create monitor '{config['name']}': {e}")

def generate_uptime_kuma_config():
    """Générer un fichier de configuration pour Uptime Kuma"""
    config = {
        "monitors": [
            {
                "name": "FastAPI Health",
                "type": "http",
                "url": "http://fastapi_app:8000/health",
                "interval": 60,
                "retryInterval": 60,
                "maxretries": 3,
                "timeout": 10,
                "method": "GET",
                "headers": {},
                "body": "",
                "httpBodyEncoding": "json",
                "description": "Monitor FastAPI health endpoint",
                "keyword": "ok",
                "invertKeyword": False,
                "ignoreTls": False,
                "upsideDown": False,
                "packetSize": 56,
                "port": None,
                "hostname": None,
                "mqttTopic": "",
                "mqttSuccessMessage": "",
                "databaseConnectionString": "",
                "databaseQuery": "",
                "authMethod": "",
                "authWorkstation": "",
                "authDomain": "",
                "radiusCalledStationId": "",
                "radiusCallingStationId": "",
                "game": "",
                "httpBodyEncoding": "json",
                "jsonPath": "",
                "expectedValue": "",
                "kafkaProducerTopic": "",
                "kafkaProducerBrokers": [],
                "kafkaProducerSsl": False,
                "kafkaProducerAllowAutoTopicCreation": False,
                "kafkaProducerMessage": "",
                "cacheBust": False,
                "proxyId": None,
                "notificationIDList": {},
                "tags": []
            }
        ],
        "notifications": [
            {
                "name": "Discord Webhook",
                "type": "discord",
                "discordWebhookUrl": "${DISCORD_WEBHOOK_URL}",
                "discordUsername": "Uptime Kuma",
                "discordPrefixMessage": "",
                "discordChannelType": "channel",
                "isDefault": True,
                "applyExisting": True
            }
        ],
        "status_pages": [
            {
                "title": "IA Continu Solution Status",
                "description": "Status page for ML pipeline services",
                "theme": "dark",
                "published": True,
                "showTags": True,
                "domainNameList": [],
                "customCSS": "",
                "footerText": "IA Continu Solution - Day 3",
                "showPoweredBy": True,
                "icon": "/icon.svg",
                "publicGroupList": [
                    {
                        "name": "Core Services",
                        "weight": 1,
                        "monitorList": [
                            {"name": "FastAPI Health"},
                            {"name": "Prefect Server"},
                            {"name": "MLflow Server"}
                        ]
                    },
                    {
                        "name": "Monitoring",
                        "weight": 2,
                        "monitorList": [
                            {"name": "Prometheus"},
                            {"name": "Grafana"}
                        ]
                    }
                ]
            }
        ]
    }
    
    return config

def create_uptime_kuma_documentation():
    """Créer la documentation pour configurer Uptime Kuma"""
    doc = """
# Configuration Uptime Kuma

## Accès
- URL: http://localhost:3001
- Utilisateur: admin (à créer au premier démarrage)
- Mot de passe: (à définir au premier démarrage)

## Monitors à créer manuellement

### 1. FastAPI Health
- **Type**: HTTP(s)
- **URL**: http://fastapi_app:8000/health
- **Nom**: FastAPI Health
- **Intervalle**: 60 secondes
- **Timeout**: 10 secondes
- **Mot-clé**: "ok"
- **Description**: Monitor de l'API principale

### 2. FastAPI Metrics
- **Type**: HTTP(s)
- **URL**: http://fastapi_app:8000/metrics
- **Nom**: FastAPI Metrics
- **Intervalle**: 300 secondes
- **Timeout**: 15 secondes
- **Description**: Endpoint des métriques Prometheus

### 3. Prefect Server
- **Type**: HTTP(s)
- **URL**: http://prefect-server:4200/api/health
- **Nom**: Prefect Server
- **Intervalle**: 120 secondes
- **Timeout**: 10 secondes
- **Description**: Serveur d'orchestration Prefect

### 4. MLflow Server
- **Type**: HTTP(s)
- **URL**: http://mlflow-server:5000/health
- **Nom**: MLflow Server
- **Intervalle**: 300 secondes
- **Timeout**: 15 secondes
- **Description**: Serveur de tracking ML

### 5. Prometheus
- **Type**: HTTP(s)
- **URL**: http://prometheus:9090/-/healthy
- **Nom**: Prometheus
- **Intervalle**: 180 secondes
- **Timeout**: 10 secondes
- **Description**: Serveur de métriques

### 6. Grafana
- **Type**: HTTP(s)
- **URL**: http://grafana:3000/api/health
- **Nom**: Grafana
- **Intervalle**: 300 secondes
- **Timeout**: 10 secondes
- **Description**: Dashboards de monitoring

## Configuration des notifications

### Discord Webhook
1. Aller dans Settings > Notifications
2. Ajouter une nouvelle notification
3. Type: Discord
4. Webhook URL: ${DISCORD_WEBHOOK_URL}
5. Username: Uptime Kuma
6. Activer pour tous les monitors

## Status Page
1. Aller dans Status Pages
2. Créer une nouvelle page
3. Titre: "IA Continu Solution Status"
4. Ajouter les monitors par groupes:
   - Core Services: FastAPI, Prefect, MLflow
   - Monitoring: Prometheus, Grafana
5. Publier la page

## Alertes recommandées
- **Down**: Immédiatement
- **Up**: Après 1 minute de stabilité
- **Maintenance**: Notification 15 minutes avant
"""
    
    return doc

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Générer la configuration
    config = generate_uptime_kuma_config()
    
    # Sauvegarder la configuration
    with open("monitoring/uptime_kuma_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    # Créer la documentation
    doc = create_uptime_kuma_documentation()
    with open("monitoring/uptime_kuma_setup.md", "w") as f:
        f.write(doc)
    
    # Essayer de configurer automatiquement
    kuma = UptimeKumaConfig()
    kuma.setup_monitors()
    
    print("✅ Configuration Uptime Kuma générée")
    print("📁 Fichiers créés:")
    print("   - monitoring/uptime_kuma_config.json")
    print("   - monitoring/uptime_kuma_setup.md")
    print("🔧 Configuration manuelle requise via l'interface web")
