# IA Continu Solution 🤖

## 🎯 Objectif

Solution complète de Machine Learning en continu avec monitoring, API REST, et pipeline automatisé. Ce projet implémente un système intelligent de détection de dérive de modèle avec réentraînement automatique, monitoring en temps réel, et notifications Discord.

## 🏗️ Architecture

```
ia_continu_solution/
├── src/
│   ├── api/                 # API FastAPI
│   │   └── main.py         # Endpoints REST
│   ├── database/           # Gestion base de données
│   │   └── db_manager.py   # SQLite + ORM
│   ├── mlflow_service/     # MLflow integration
│   │   └── mlflow_manager.py
│   ├── monitoring/         # Monitoring & notifications
│   │   └── discord_notifier.py
│   └── utils/              # Utilitaires
├── config/                 # Configuration centralisée
│   └── settings.py
├── docs/                   # Documentation
├── tests/                  # Tests unitaires
├── data/                   # Base de données SQLite
├── models/                 # Modèles ML sauvegardés
├── logs/                   # Fichiers de logs
├── docker-compose.yml      # Orchestration services
└── flow.py                 # Pipeline Prefect
```

## 🚀 Services Déployés

- **FastAPI** (Port 8000) : API REST pour ML
- **Prefect Server** (Port 4200) : Orchestration workflows
- **Uptime Kuma** (Port 3001) : Monitoring uptime
- **MLflow** (Port 5000) : Tracking expériences ML
- **Pipeline Prefect** : Vérifications toutes les 30s

## 📡 Endpoints API

### 🔍 Health Check
```http
GET /health
```
Vérification de l'état de l'API.

**Réponse :**
```json
{
  "status": "ok",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "2.0.0"
}
```

### 🎯 Prédiction
```http
POST /predict
```
Effectue une prédiction avec le modèle actuel.

**Body :**
```json
{
  "features": [1.5, 2.3]
}
```

**Réponse :**
```json
{
  "prediction": 1,
  "model_version": "v1.0.0",
  "confidence": 0.85,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 🔄 Réentraînement
```http
POST /retrain
```
Lance le réentraînement du modèle avec nouvelles données.

**Réponse :**
```json
{
  "status": "success",
  "model_version": "v1.1.0",
  "training_samples": 1000,
  "accuracy": 0.92,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 📊 Génération de données
```http
POST /generate
```
Génère un nouveau dataset pour l'entraînement.

**Body :**
```json
{
  "samples": 1000
}
```

## 🐳 Lancement avec Docker

### Prérequis
- Docker & Docker Compose
- Variable d'environnement `DISCORD_WEBHOOK_URL`

### Démarrage rapide
```bash
# Cloner le repository
git clone https://github.com/simbouch/ia_continu_solution.git
cd ia_continu_solution

# Configurer Discord webhook
echo "DISCORD_WEBHOOK_URL=your_webhook_url" > .env

# Lancer tous les services
docker-compose up -d

# Vérifier les services
docker-compose ps
```

### Accès aux services
- **API** : http://localhost:8000
- **Prefect UI** : http://localhost:4200
- **Uptime Kuma** : http://localhost:3001
- **MLflow** : http://localhost:5000

## 🧪 Tests

```bash
# Tests unitaires
python -m pytest tests/ -v

# Test complet du système
python test_global.py

# Test API spécifique
python tests/test_api.py
```

## 📊 Monitoring

### Pipeline Automatique
- **Fréquence** : Toutes les 30 secondes
- **Logique** : Génère nombre aléatoire
- **Seuil** : Si < 0.5 → Réentraînement automatique
- **Notifications** : Discord embeds

### Uptime Kuma
- Surveillance continue de l'API
- Alertes en cas de panne
- Dashboard de disponibilité

## 🔧 Configuration

### Variables d'environnement
```bash
# Discord
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# API
API_HOST=0.0.0.0
API_PORT=9000

# MLflow
MLFLOW_TRACKING_URI=http://localhost:5000

# Logging
LOG_LEVEL=INFO
```

### Base de données
- **Type** : SQLite
- **Localisation** : `data/ia_continu_solution.db`
- **Tables** : datasets, dataset_samples, models

## 🔄 Workflow ML

1. **Génération de données** → Dataset synthétique
2. **Entraînement** → Modèle LogisticRegression
3. **Évaluation** → Métriques de performance
4. **Logging MLflow** → Tracking expériences
5. **Sauvegarde** → Modèle + métadonnées
6. **Monitoring** → Surveillance continue
7. **Réentraînement** → Si dérive détectée

## 📈 Métriques Suivies

- **Accuracy** : Précision du modèle
- **Training samples** : Nombre d'échantillons
- **Model version** : Versioning automatique
- **Response time** : Temps de réponse API
- **Uptime** : Disponibilité services

## 🚨 Notifications Discord

Format des notifications :
```json
{
  "title": "Résultats du pipeline",
  "description": "Message détaillé",
  "fields": [{
    "name": "Status",
    "value": "Succès" | "Échec"
  }]
}
```

## 🛠️ Développement

### Structure du code
- **FastAPI** : API REST moderne
- **SQLAlchemy** : ORM pour base de données
- **Prefect** : Orchestration workflows
- **MLflow** : Tracking ML
- **Docker** : Containerisation
- **Pytest** : Tests automatisés

### Ajout de nouvelles fonctionnalités
1. Modifier `src/api/main.py` pour nouveaux endpoints
2. Mettre à jour `src/database/db_manager.py` pour nouveaux modèles
3. Ajouter tests dans `tests/`
4. Documenter dans `docs/`

## 📚 Documentation

- `docs/jour1-summary.md` : Résumé Jour 1
- `docs/jour2-summary.md` : Résumé Jour 2
- `docs/jour3-summary.md` : Résumé Jour 3

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature
3. Commit les changements
4. Push vers la branche
5. Ouvrir une Pull Request

## 📄 Licence

MIT License - voir fichier LICENSE

---

**Version** : 2.0.0  
**Dernière mise à jour** : Jour 3  
**Statut** : Production Ready 🚀
