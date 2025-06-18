
# Configuration Uptime Kuma

## Acc�s
- URL: http://localhost:3001
- Utilisateur: admin (� cr�er au premier d�marrage)
- Mot de passe: (� d�finir au premier d�marrage)

## Monitors � cr�er manuellement

### 1. FastAPI Health
- **Type**: HTTP(s)
- **URL**: http://fastapi_app:8000/health
- **Nom**: FastAPI Health
- **Intervalle**: 60 secondes
- **Timeout**: 10 secondes
- **Mot-cl�**: "ok"
- **Description**: Monitor de l'API principale

### 2. FastAPI Metrics
- **Type**: HTTP(s)
- **URL**: http://fastapi_app:8000/metrics
- **Nom**: FastAPI Metrics
- **Intervalle**: 300 secondes
- **Timeout**: 15 secondes
- **Description**: Endpoint des m�triques Prometheus

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
- **Description**: Serveur de m�triques

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
2. Cr�er une nouvelle page
3. Titre: "IA Continu Solution Status"
4. Ajouter les monitors par groupes:
   - Core Services: FastAPI, Prefect, MLflow
   - Monitoring: Prometheus, Grafana
5. Publier la page

## Alertes recommand�es
- **Down**: Imm�diatement
- **Up**: Apr�s 1 minute de stabilit�
- **Maintenance**: Notification 15 minutes avant
