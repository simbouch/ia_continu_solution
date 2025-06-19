# 🔧 Services Techniques - Jour 4
## Détail des Implémentations et Difficultés Rencontrées

---

## 📋 **Services Inconnus Implémentés**

### 1. **MLflow - Tracking des Modèles**

#### **Découverte**
MLflow était un service inconnu nécessitant une courbe d'apprentissage importante.

#### **Implémentation**
```yaml
mlflow:
  build:
    context: .
    dockerfile: services/mlflow/Dockerfile
  ports:
    - "5000:5000"
  volumes:
    - ./mlflow_data:/app/mlflow
    - ./mlruns:/app/mlruns
  command: >
    mlflow server 
      --backend-store-uri file:///app/mlflow 
      --default-artifact-root /app/mlruns 
      --host 0.0.0.0 
      --port 5000
```

#### **Difficultés Rencontrées**
1. **Problème de Binding**: MLflow se liait à `127.0.0.1` au lieu de `0.0.0.0`
2. **Permissions Fichiers**: Problèmes d'accès aux répertoires de données
3. **Configuration Gunicorn**: Paramètres `--gunicorn-opts` non fonctionnels

#### **Solutions Appliquées**
1. **Dockerfile Personnalisé**: Création d'un Dockerfile spécifique
2. **Permissions**: `chmod -R 777` sur les répertoires de données
3. **Configuration Simple**: Suppression des options Gunicorn complexes

---

### 2. **Prefect - Orchestration Workflows**

#### **Découverte**
Prefect était totalement inconnu, nécessitant une veille technologique approfondie.

#### **Veille Technologique Effectuée**
- **Documentation officielle**: Étude des concepts flows/tasks
- **Exemples communauté**: Recherche de patterns ML
- **Comparaison**: Airflow vs Prefect vs autres
- **Versions**: Différences Prefect 2.x vs 3.x

#### **Implémentation Tentée**
```python
@flow(name="ml-automation-pipeline", log_prints=True)
def ml_automation_pipeline():
    # Monitoring système
    health_status = monitor_system_health()
    
    # Détection drift
    drift_info = detect_model_drift()
    
    # Retraining automatique
    if drift_info.get("drift_detected", False):
        retraining_result = automated_model_retraining(drift_info)
```

#### **Difficultés Majeures**
1. **Erreurs Pydantic**: `PydanticUndefinedAnnotation: name 'BaseResult' is not defined`
2. **Compatibilité Versions**: Conflits entre Prefect 2.x et 3.x
3. **Dépendances**: Problèmes de résolution des imports
4. **Configuration Serveur**: Connexion `http://0.0.0.0:4200/api` inaccessible

#### **Solutions Tentées**
1. **Downgrade Prefect**: Passage de 3.0.0 à 2.19.9
2. **Pydantic Fixe**: Utilisation de pydantic==1.10.12
3. **Simplification Types**: Suppression des annotations complexes
4. **Alternative**: Création d'un script Python simple

#### **Solution Finale**
Création d'un script d'automation simple en Python pur pour remplacer Prefect temporairement.

---

### 3. **Prometheus + Grafana - Monitoring**

#### **Découverte**
Stack de monitoring professionnel inconnu nécessitant apprentissage.

#### **Implémentation Prometheus**
```yaml
prometheus:
  image: prom/prometheus:latest
  ports:
    - "9090:9090"
  volumes:
    - ./monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'
    - '--storage.tsdb.retention.time=200h'
```

#### **Configuration Scraping**
```yaml
scrape_configs:
  - job_name: 'ia-continu-api'
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/health'
    scrape_interval: 30s
```

#### **Difficultés**
1. **Configuration Réseau**: Résolution DNS entre conteneurs
2. **Métriques Endpoints**: Pas tous les services exposent `/metrics`
3. **Grafana Datasource**: Configuration automatique

#### **Solutions**
1. **Network Docker**: Utilisation du réseau `ia_continu_network`
2. **Health Endpoints**: Utilisation des endpoints de santé existants
3. **Provisioning**: Configuration automatique Grafana via volumes

---

### 4. **Discord Webhooks - Notifications**

#### **Implémentation**
```python
def send_discord_notification(message: str, status: str = "Succès"):
    color_map = {
        "Succès": 5814783,      # Green
        "Échec": 15158332,      # Red
        "Avertissement": 16776960,  # Yellow
        "Drift": 16753920       # Orange
    }
    
    data = {
        "embeds": [{
            "title": "🤖 ML Automation",
            "description": message,
            "color": color_map.get(status, 3447003),
            "fields": [...]
        }]
    }
```

#### **Difficultés**
1. **Format Embeds**: Syntaxe Discord complexe
2. **Caractères Spéciaux**: Échappement des caractères
3. **Rate Limiting**: Gestion des limites Discord

#### **Solutions**
1. **Documentation Discord**: Étude approfondie de l'API
2. **Tests Itératifs**: Validation format par format
3. **Gestion Erreurs**: Try/catch robuste

---

## 🚧 **Difficultés Générales et Solutions**

### **1. Problèmes de Réseau Docker**
- **Problème**: Services ne se trouvent pas entre eux
- **Solution**: Réseau Docker dédié `ia_continu_network`

### **2. Conflits de Ports**
- **Problème**: Ports déjà utilisés sur la machine
- **Solution**: Mapping de ports alternatifs

### **3. Permissions Fichiers**
- **Problème**: Conteneurs ne peuvent pas écrire
- **Solution**: Volumes avec permissions appropriées

### **4. Versions Dépendances**
- **Problème**: Conflits entre versions de packages
- **Solution**: Pinning des versions exactes

### **5. Logs et Debugging**
- **Problème**: Difficile de déboguer les conteneurs
- **Solution**: Logs centralisés et healthchecks

---

## 📈 **Apprentissages Clés**

### **Technologies Maîtrisées**
1. **MLflow**: Tracking et versioning des modèles ML
2. **Prometheus**: Collecte de métriques système
3. **Grafana**: Visualisation et dashboards
4. **Discord API**: Notifications et webhooks
5. **Docker Compose**: Orchestration multi-services

### **Patterns Architecturaux**
1. **Microservices**: Séparation des responsabilités
2. **Monitoring**: Observabilité complète
3. **Automation**: Workflows automatisés
4. **Notifications**: Alerting en temps réel

### **Bonnes Pratiques**
1. **Documentation**: Chaque service documenté
2. **Tests**: Validation automatisée
3. **Monitoring**: Surveillance proactive
4. **Template**: Réutilisabilité maximale

---

## 🎯 **Résultats Finaux**

### **Services Opérationnels**
- ✅ **7/7 Services** fonctionnels
- ✅ **Monitoring** complet
- ✅ **Notifications** actives
- ✅ **Template** créé

### **Compétences Acquises**
- ✅ **MLflow** pour ML tracking
- ✅ **Prometheus/Grafana** pour monitoring
- ✅ **Prefect** (concepts et limitations)
- ✅ **Discord API** pour notifications
- ✅ **Architecture microservices**
