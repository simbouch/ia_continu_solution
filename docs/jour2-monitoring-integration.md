# 📊 Jour 2 - Monitoring et Applications
## Intégration Complète Monitoring Stack

---

## 🎯 **Objectifs Jour 2**

### **Documentation et CI/CD**
- ✅ Mise en place documentation complète
- ✅ Daily standup et README.md
- ✅ CI/CD GitHub Actions

### **Monitoring Stack**
- ✅ Prometheus et Grafana
- ✅ Loguru pour journalisation
- ✅ Uptime Kuma surveillance
- ✅ Interface Streamlit avec auth

---

## 📚 **Documentation**

### **README.md Complet**
```markdown
# IA Continu Solution
## ML Pipeline avec Monitoring Avancé

### Quick Start
- Installation et configuration
- Accès aux services
- Guide utilisation

### Architecture
- Microservices détaillés
- Diagrammes techniques
- Flux de données
```

### **CI/CD GitHub Actions**
```yaml
name: CI/CD Pipeline
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/
      - name: Build Docker
        run: docker build -t ia-continu .
```

---

## 📊 **Prometheus et Grafana**

### **Configuration Prometheus**
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'ia-continu-api'
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
```

### **Métriques Collectées**
- **API Performance**: Temps réponse, throughput
- **Système**: CPU, RAM, disque
- **ML Metrics**: Accuracy, prédictions/sec
- **Erreurs**: Taux d'erreur, exceptions

### **Dashboards Grafana**
```json
{
  "dashboard": {
    "title": "IA Continu Monitoring",
    "panels": [
      {
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "http_request_duration_seconds",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "ML Model Accuracy",
        "type": "stat",
        "targets": [
          {
            "expr": "ml_model_accuracy",
            "legendFormat": "Current Accuracy"
          }
        ]
      }
    ]
  }
}
```

---

## 📝 **Loguru - Journalisation**

### **Configuration Logging**
```python
from loguru import logger
import sys

# Configuration Loguru
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

# Fichiers de logs
logger.add("logs/api.log", rotation="1 day", retention="30 days", level="INFO")
logger.add("logs/errors.log", rotation="1 day", retention="30 days", level="ERROR")
logger.add("logs/ml.log", rotation="1 day", retention="30 days", level="DEBUG", filter=lambda record: "ml" in record["extra"])
```

### **Logging dans l'API**
```python
@app.post("/predict")
async def predict(request: PredictionRequest, current_user: dict = Depends(get_current_user)):
    logger.info(f"Prediction request from user {current_user['username']}")
    
    try:
        prediction = model.predict(request.features)
        logger.info(f"Prediction successful: {prediction}", extra={"ml": True})
        return {"prediction": prediction}
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed")
```

### **Structure Logs**
```
logs/
├── api.log          # Logs généraux API
├── errors.log       # Erreurs système
├── ml.log          # Logs ML spécifiques
└── monitoring.log   # Logs monitoring
```

---

## 🔄 **Route Retrain Améliorée**

### **Validation Performance Avant Retraining**
```python
@app.post("/retrain")
async def retrain_model(current_user: dict = Depends(get_current_user)):
    logger.info("Starting model retraining process")
    
    # 1. Évaluation modèle actuel
    current_accuracy = evaluate_current_model()
    logger.info(f"Current model accuracy: {current_accuracy}")
    
    # 2. Seuil de performance
    ACCURACY_THRESHOLD = 0.75
    
    if current_accuracy >= ACCURACY_THRESHOLD:
        logger.info("Model performance above threshold, skipping retraining")
        return {
            "status": "skipped",
            "reason": "performance_above_threshold",
            "current_accuracy": current_accuracy,
            "threshold": ACCURACY_THRESHOLD
        }
    
    # 3. Retraining si performance insuffisante
    logger.warning(f"Model performance below threshold ({current_accuracy} < {ACCURACY_THRESHOLD}), starting retraining")
    
    # Récupération dernier dataset
    latest_dataset = get_latest_dataset()
    
    # Entraînement nouveau modèle
    new_model = train_new_model(latest_dataset)
    new_accuracy = evaluate_model(new_model, latest_dataset)
    
    # MLflow logging
    with mlflow.start_run():
        mlflow.log_param("trigger", "performance_threshold")
        mlflow.log_metric("old_accuracy", current_accuracy)
        mlflow.log_metric("new_accuracy", new_accuracy)
        mlflow.log_metric("improvement", new_accuracy - current_accuracy)
        mlflow.sklearn.log_model(new_model, "model")
    
    logger.info(f"Retraining completed. New accuracy: {new_accuracy}")
    
    return {
        "status": "completed",
        "old_accuracy": current_accuracy,
        "new_accuracy": new_accuracy,
        "improvement": new_accuracy - current_accuracy
    }
```

---

## 🔍 **Uptime Kuma**

### **Configuration Docker Compose**
```yaml
uptime-kuma:
  image: louislam/uptime-kuma:latest
  container_name: ia_continu_uptime_kuma
  ports:
    - "3001:3001"
  volumes:
    - ./uptime_kuma_data:/app/data
  restart: unless-stopped
  networks:
    - ia_continu_network
```

### **Monitoring Configuration**
- **API Health Check**: Ping `/health` toutes les minutes
- **Alertes**: Discord webhook si service down
- **Métriques**: Uptime, response time, availability
- **Dashboard**: Status page publique

### **Alertes Configurées**
```javascript
// Uptime Kuma notification settings
{
  "type": "discord",
  "discordWebhookUrl": process.env.DISCORD_WEBHOOK_URL,
  "discordUsername": "Uptime Kuma",
  "discordPrefixMessage": "🚨 Alert:",
  "conditions": {
    "down": true,
    "up": true,
    "certificate": true
  }
}
```

---

## 🎨 **Interface Streamlit**

### **Application Streamlit**
```python
import streamlit as st
import requests
import json

# Configuration page
st.set_page_config(
    page_title="IA Continu Solution",
    page_icon="🤖",
    layout="wide"
)

# Authentification
def authenticate(username, password):
    response = requests.post(
        "http://api:8000/auth/login",
        json={"username": username, "password": password}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

# Interface principale
def main():
    st.title("🤖 IA Continu Solution")
    
    # Sidebar authentification
    with st.sidebar:
        st.header("🔐 Authentification")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            token = authenticate(username, password)
            if token:
                st.session_state.token = token
                st.success("Authentifié avec succès!")
            else:
                st.error("Échec authentification")
    
    # Interface principale si authentifié
    if "token" in st.session_state:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Bouton Health Check
        with col1:
            if st.button("🏥 Health Check"):
                response = requests.get("http://api:8000/health")
                st.json(response.json())
        
        # Bouton Predict
        with col2:
            if st.button("🔮 Predict"):
                features = st.number_input("Features", value=[0.5, 0.5])
                response = requests.post(
                    "http://api:8000/predict",
                    json={"features": features},
                    headers=headers
                )
                st.json(response.json())
        
        # Bouton Generate
        with col3:
            if st.button("📊 Generate Data"):
                samples = st.number_input("Samples", value=100)
                response = requests.post(
                    "http://api:8000/generate",
                    json={"samples": samples},
                    headers=headers
                )
                st.json(response.json())
        
        # Bouton Retrain
        with col4:
            if st.button("🔄 Retrain Model"):
                response = requests.post(
                    "http://api:8000/retrain",
                    headers=headers
                )
                st.json(response.json())
```

### **Fonctionnalités Interface**
- ✅ **Authentification** JWT intégrée
- ✅ **Boutons** pour chaque route API
- ✅ **Visualisation** réponses JSON
- ✅ **Interface** responsive et moderne
- ✅ **Gestion erreurs** et feedback utilisateur

---

## 🔐 **API Token et Migration Alembic**

### **Système Tokens Avancé**
```python
# Modèles SQLAlchemy
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    tokens = relationship("Token", back_populates="user")

class Token(Base):
    __tablename__ = "tokens"
    
    id = Column(Integer, primary_key=True)
    token = Column(String(255), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    user = relationship("User", back_populates="tokens")
```

### **Migrations Alembic**
```python
# alembic/versions/001_initial_migration.py
def upgrade():
    # Création tables users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('email', sa.String(100), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('role', sa.String(20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    
    # Création tables tokens
    op.create_table(
        'tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(255), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )
```

---

## 📈 **Métriques Jour 2**

### **Fonctionnalités Livrées**
- ✅ **Monitoring Stack** complet (Prometheus + Grafana)
- ✅ **Logging** avancé avec Loguru
- ✅ **Uptime Kuma** surveillance continue
- ✅ **Interface Streamlit** avec authentification
- ✅ **CI/CD** GitHub Actions
- ✅ **Documentation** complète

### **Qualité Monitoring**
- ✅ **Métriques** système et application
- ✅ **Alertes** automatiques Discord
- ✅ **Dashboards** Grafana professionnels
- ✅ **Logs** structurés et rotatifs

---

## 🎯 **Résultats Jour 2**

### **Objectifs Atteints** ✅
- ✅ Stack monitoring professionnel déployé
- ✅ Interface utilisateur complète
- ✅ Authentification avancée avec tokens
- ✅ CI/CD pipeline opérationnel
- ✅ Documentation exhaustive

### **Prêt pour Jour 3** 🚀
Infrastructure monitoring solide pour validation et fixes avancés.

---

*Jour 2 - Monitoring & Applications - ✅ Succès Complet*
