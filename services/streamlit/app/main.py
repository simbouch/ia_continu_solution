#!/usr/bin/env python3
"""
Streamlit UI for IA Continu Solution
Interface utilisateur pour tester l'API avec authentification
"""

import os
import random

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="IA Continu Solution - Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Configuration API
API_BASE_URL = os.getenv("API_URL", "http://host.docker.internal:8000")


class APIClient:
    """Client pour interagir avec l'API"""

    def __init__(self, base_url: str, token: str | None = None):
        self.base_url = base_url
        self.token = token
        self.headers = {}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def health_check(self):
        """Vérifier la santé de l'API"""
        try:
            response = requests.get(
                f"{self.base_url}/health", headers=self.headers, timeout=5
            )
            return (
                response.status_code == 200,
                response.json() if response.status_code == 200 else None,
            )
        except Exception as e:
            return False, str(e)

    def predict(self, features):
        """Faire une prédiction"""
        try:
            payload = {"features": features}
            response = requests.post(
                f"{self.base_url}/predict",
                json=payload,
                headers=self.headers,
                timeout=10,
            )
            return (
                response.status_code == 200,
                response.json() if response.status_code == 200 else response.text,
            )
        except Exception as e:
            return False, str(e)

    def generate_dataset(self, samples=1000):
        """Générer un nouveau dataset"""
        try:
            payload = {"samples": samples}
            response = requests.post(
                f"{self.base_url}/generate",
                json=payload,
                headers=self.headers,
                timeout=30,
            )
            return (
                response.status_code == 200,
                response.json() if response.status_code == 200 else response.text,
            )
        except Exception as e:
            return False, str(e)

    # REMOVED: Retrain endpoints - handled by Prefect automation
    # def retrain_model(self):
    # def conditional_retrain(self, threshold=0.85, force=False):

    def get_model_info(self):
        """Obtenir les informations du modèle"""
        try:
            response = requests.get(
                f"{self.base_url}/model/info", headers=self.headers, timeout=5
            )
            return (
                response.status_code == 200,
                response.json() if response.status_code == 200 else response.text,
            )
        except Exception as e:
            return False, str(e)

    def list_datasets(self):
        """Lister les datasets"""
        try:
            response = requests.get(
                f"{self.base_url}/datasets/list", headers=self.headers, timeout=10
            )
            return (
                response.status_code == 200,
                response.json() if response.status_code == 200 else response.text,
            )
        except Exception as e:
            return False, str(e)


def authenticate():
    """Interface d'authentification"""
    st.sidebar.title("🔐 Authentification")

    # Vérifier si déjà authentifié
    if hasattr(st.session_state, "api_client") and st.session_state.api_client:
        is_healthy, health_data = st.session_state.api_client.health_check()
        if is_healthy:
            st.sidebar.success("✅ Déjà authentifié")
            if st.sidebar.button("🚪 Se déconnecter"):
                del st.session_state.api_client
                del st.session_state.token
                st.rerun()
            return True

    # Choix du mode d'authentification
    auth_mode = st.sidebar.radio(
        "Mode d'authentification", ["Username/Password", "Token JWT"]
    )

    if auth_mode == "Username/Password":
        username = st.sidebar.text_input("Nom d'utilisateur", value="testuser")
        password = st.sidebar.text_input(
            "Mot de passe", type="password", value="test123"
        )

        if st.sidebar.button("🔑 Se connecter"):
            if username and password:
                # Obtenir le token via l'API
                try:
                    login_data = {"username": username, "password": password}
                    response = requests.post(
                        f"{API_BASE_URL}/auth/login", json=login_data, timeout=10
                    )

                    if response.status_code == 200:
                        token_data = response.json()
                        token = token_data["access_token"]
                        st.session_state.token = token
                        st.session_state.api_client = APIClient(API_BASE_URL, token)
                        st.sidebar.success(f"✅ Connecté en tant que {username}")
                        st.rerun()
                    else:
                        st.sidebar.error("❌ Identifiants incorrects")
                        return False
                except Exception as e:
                    st.sidebar.error(f"❌ Erreur de connexion: {e}")
                    return False
            else:
                st.sidebar.warning("⚠️ Veuillez saisir vos identifiants")
                return False
    else:
        # Mode token JWT
        token = st.sidebar.text_input(
            "Token d'accès", type="password", help="Entrez votre token JWT"
        )

        if token:
            st.session_state.token = token
            st.session_state.api_client = APIClient(API_BASE_URL, token)

            # Tester la connexion
            is_healthy, health_data = st.session_state.api_client.health_check()
            if is_healthy:
                st.sidebar.success("✅ Authentifié et connecté à l'API")
                return True
            else:
                st.sidebar.error("❌ Erreur de connexion à l'API")
                st.sidebar.error(f"Détails: {health_data}")
                return False
        else:
            st.sidebar.warning("⚠️ Token requis pour accéder à l'API")
            return False

    return False


def main_dashboard():
    """Dashboard principal"""
    st.title("🤖 IA Continu Solution - Day 4 Dashboard")
    st.markdown(
        "🚀 **Day 4 Implementation** - Interface complète de gestion et monitoring du pipeline ML"
    )

    # Vérifier la santé de l'API
    is_healthy, health_data = st.session_state.api_client.health_check()

    if is_healthy:
        st.success(
            f"✅ API Status: {health_data.get('status', 'OK')} - Version: {health_data.get('version', 'N/A')}"
        )
    else:
        st.error(f"❌ API non disponible: {health_data}")
        return

    # Tabs pour organiser les fonctionnalités
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["🎯 Prédictions", "🔄 Modèle", "📊 Datasets", "📈 Monitoring", "⚙️ Admin"]
    )

    with tab1:
        prediction_interface()

    with tab2:
        model_management()

    with tab3:
        dataset_management()

    with tab4:
        monitoring_dashboard()

    with tab5:
        admin_interface()


def prediction_interface():
    """Interface de prédiction"""
    st.header("🎯 Interface de Prédiction")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Paramètres d'entrée")
        feature1 = st.number_input("Feature 1", value=0.5, step=0.1, format="%.2f")
        feature2 = st.number_input("Feature 2", value=0.5, step=0.1, format="%.2f")

        if st.button("🚀 Faire une prédiction", type="primary"):
            with st.spinner("Prédiction en cours..."):
                success, result = st.session_state.api_client.predict(
                    [feature1, feature2]
                )

                if success:
                    st.success("✅ Prédiction réussie!")

                    # Afficher les résultats
                    col_pred, col_conf = st.columns(2)
                    with col_pred:
                        st.metric("Prédiction", result["prediction"])
                    with col_conf:
                        st.metric("Confiance", f"{result['confidence']:.3f}")

                    st.json(result)
                else:
                    st.error(f"❌ Erreur de prédiction: {result}")

    with col2:
        st.subheader("Prédictions en lot")

        # Interface pour prédictions multiples
        num_predictions = st.number_input(
            "Nombre de prédictions", min_value=1, max_value=100, value=10
        )

        if st.button("🎲 Générer prédictions aléatoires"):
            predictions_data = []

            progress_bar = st.progress(0)
            for i in range(num_predictions):
                f1 = random.uniform(-2, 2)
                f2 = random.uniform(-2, 2)

                success, result = st.session_state.api_client.predict([f1, f2])
                if success:
                    predictions_data.append(
                        {
                            "Feature1": f1,
                            "Feature2": f2,
                            "Prediction": result["prediction"],
                            "Confidence": result["confidence"],
                        }
                    )

                progress_bar.progress((i + 1) / num_predictions)

            if predictions_data:
                df = pd.DataFrame(predictions_data)
                st.dataframe(df)

                # Graphique des prédictions
                fig = px.scatter(
                    df,
                    x="Feature1",
                    y="Feature2",
                    color="Prediction",
                    size="Confidence",
                    title="Visualisation des prédictions",
                )
                st.plotly_chart(fig, use_container_width=True)


def model_management():
    """Interface de gestion du modèle"""
    st.header("🔄 Gestion du Modèle")

    # Informations du modèle actuel
    success, model_info = st.session_state.api_client.get_model_info()

    if success:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Version", model_info.get("model_version", "N/A"))
        with col2:
            st.metric("Type", model_info.get("model_type", "N/A"))
        with col3:
            status = (
                "✅ Chargé"
                if model_info.get("model_loaded", False)
                else "❌ Non chargé"
            )
            st.metric("Status", status)

    st.subheader("Actions sur le modèle")

    st.info("🤖 **Retraining is now automated via Prefect workflows**")
    st.markdown("""
    The model retraining is handled automatically by Prefect workflows that run every 30 seconds.
    These workflows:
    - Monitor model performance
    - Detect data drift
    - Automatically retrain when needed
    - Send Discord notifications

    **Prefect Dashboard**: [http://localhost:4200](http://localhost:4200)
    """)


def dataset_management():
    """Interface de gestion des datasets"""
    st.header("📊 Gestion des Datasets")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Générer nouveau dataset")
        samples = st.number_input(
            "Nombre d'échantillons",
            min_value=100,
            max_value=10000,
            value=1000,
            step=100,
        )

        if st.button("📊 Générer dataset"):
            with st.spinner("Génération en cours..."):
                success, result = st.session_state.api_client.generate_dataset(samples)

                if success:
                    st.success("✅ Dataset généré avec succès!")
                    st.json(result)
                else:
                    st.error(f"❌ Erreur de génération: {result}")

    with col2:
        st.subheader("Datasets existants")

        if st.button("🔄 Actualiser la liste"):
            success, datasets = st.session_state.api_client.list_datasets()

            if success and datasets.get("datasets"):
                df = pd.DataFrame(datasets["datasets"])
                st.dataframe(df)

                # Graphique de l'évolution
                if len(df) > 1:
                    fig = px.line(
                        df,
                        x="created_at",
                        y="samples_count",
                        title="Évolution du nombre d'échantillons",
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Aucun dataset trouvé")


def monitoring_dashboard():
    """Dashboard de monitoring"""
    st.header("📈 Monitoring - Day 4")

    # Check service status in real-time
    st.subheader("🔍 Service Status Check")

    services = {
        "🔬 MLflow": "http://localhost:5000/",
        "📡 Uptime Kuma": "http://localhost:3001/",
        "⚡ Prefect": "http://localhost:4200/api/ready",
        "🔍 Prometheus": "http://localhost:9090/",
        "📊 Grafana": "http://localhost:3000/",
    }

    if st.button("🔄 Check Service Status"):
        cols = st.columns(len(services))
        for i, (name, url) in enumerate(services.items()):
            with cols[i]:
                try:
                    response = requests.get(url, timeout=3)
                    if response.status_code == 200:
                        st.success(f"{name}\n✅ Online")
                    else:
                        st.error(f"{name}\n❌ Error {response.status_code}")
                except Exception:
                    st.error(f"{name}\n❌ Offline")

    st.markdown("""
    ### 🔗 Monitoring Services

    #### ✅ Working Services:
    - 🔬 **MLflow**: [http://localhost:5000](http://localhost:5000) - ML Experiment Tracking
    - 📡 **Uptime Kuma**: [http://localhost:3001](http://localhost:3001) - Service Monitoring

    #### ⚠️ Additional Services (Optional):
    - ⚡ **Prefect**: [http://localhost:4200](http://localhost:4200) - Workflow Orchestration
    - 🔍 **Prometheus**: [http://localhost:9090](http://localhost:9090) - Metrics Collection
    - 📊 **Grafana**: [http://localhost:3000](http://localhost:3000) - Dashboards (admin/admin123)
    """)

    # Métriques en temps réel (simulation)
    if st.button("📊 Actualiser les métriques"):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("API Requests", "1,234", "12%")
        with col2:
            st.metric("Model Accuracy", "0.923", "0.05")
        with col3:
            st.metric("Uptime", "99.9%", "0.1%")
        with col4:
            st.metric("Response Time", "45ms", "-5ms")


def admin_interface():
    """Interface d'administration"""
    st.header("⚙️ Administration")

    st.warning("🚨 Zone d'administration - Utilisez avec précaution")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Configuration API")
        st.text_input("URL de base", value=API_BASE_URL, disabled=True)
        st.text_input("Token actuel", value="***", type="password", disabled=True)

    with col2:
        st.subheader("Actions système")

        if st.button("🔄 Redémarrer les services", type="secondary"):
            st.warning("Cette action redémarrerait tous les services Docker")

        if st.button("🗑️ Nettoyer les logs", type="secondary"):
            st.warning("Cette action supprimerait les anciens fichiers de logs")

    # Logs en temps réel (simulation)
    st.subheader("📝 Logs récents")
    if st.button("🔄 Actualiser les logs"):
        logs = [
            "2024-01-01 12:00:00 - INFO - API started successfully",
            "2024-01-01 12:01:00 - INFO - Model loaded: v20240101_120000",
            "2024-01-01 12:02:00 - INFO - Prediction made: confidence 0.85",
            "2024-01-01 12:03:00 - WARNING - Model drift detected",
            "2024-01-01 12:04:00 - INFO - Retraining triggered",
        ]

        for log in logs:
            st.text(log)


def main():
    """Fonction principale"""
    st.sidebar.image(
        "https://via.placeholder.com/200x100/1f77b4/white?text=IA+Continu", width=200
    )

    # Authentification
    if not authenticate():
        st.warning("🔐 Veuillez vous authentifier pour accéder au dashboard")
        st.markdown("""
        ### 🔑 Connexion Requise - Day 4 Implementation

        Pour accéder au dashboard IA Continu Solution, veuillez vous connecter avec vos identifiants :

        #### Comptes de test disponibles :
        - **Utilisateur standard** : `testuser` / `test123`
        - **Administrateur** : `admin` / `admin123`

        Utilisez le mode "Username/Password" dans la barre latérale pour vous connecter.

        ---
        **Day 4 Features:**
        - ✅ Authentication sécurisée
        - ✅ Interface ML complète
        - ✅ Monitoring intégré
        - ✅ Pipeline automatisé
        """)
        return

    # Dashboard principal
    main_dashboard()

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**IA Continu Solution v4.0 - Day 4**")
    st.sidebar.markdown("🚀 Production Ready - ML Pipeline & Monitoring")


if __name__ == "__main__":
    main()
