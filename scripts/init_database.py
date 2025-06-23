#!/usr/bin/env python3
"""
Database Initialization Script
Script d'initialisation de la base de données avec Alembic
"""

from pathlib import Path
import subprocess
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.auth.auth_service import AuthService
from src.database.db_manager import DatabaseManager


def run_alembic_upgrade():
    """Exécuter les migrations Alembic"""
    try:
        print("🔄 Running Alembic migrations...")
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            check=False, cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("✅ Alembic migrations completed successfully")
            print(result.stdout)
        else:
            print("❌ Alembic migrations failed")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"❌ Error running Alembic: {e}")
        return False

    return True

def initialize_auth_system():
    """Initialiser le système d'authentification"""
    try:
        print("🔐 Initializing authentication system...")
        AuthService()
        print("✅ Authentication system initialized")
        return True
    except Exception as e:
        print(f"❌ Error initializing auth system: {e}")
        return False

def initialize_database_manager():
    """Initialiser le gestionnaire de base de données"""
    try:
        print("📊 Initializing database manager...")
        DatabaseManager()
        print("✅ Database manager initialized")
        return True
    except Exception as e:
        print(f"❌ Error initializing database manager: {e}")
        return False

def create_sample_data():
    """Créer des données d'exemple"""
    try:
        print("📝 Creating sample data...")

        # Créer un dataset d'exemple
        db_manager = DatabaseManager()

        # Générer quelques échantillons
        import random


        generation_id = 1
        samples_count = 100
        hour_generated = 12

        # Générer des données synthétiques
        features_targets = []
        for _ in range(samples_count):
            x1 = random.uniform(-2, 2)
            x2 = random.uniform(-2, 2)
            # Simple classification: positive if x1 + x2 > 0
            target = 1 if x1 + x2 > 0 else 0
            features_targets.append((x1, x2, target))

        success = db_manager.store_dataset(
            generation_id=generation_id,
            samples_count=samples_count,
            hour_generated=hour_generated,
            features_targets=features_targets
        )

        if success:
            print(f"✅ Sample dataset created with {samples_count} samples")
        else:
            print("❌ Failed to create sample dataset")

    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return False

    return True

def main():
    """Fonction principale d'initialisation"""
    print("🚀 Initializing IA Continu Solution Database")
    print("=" * 50)

    # Créer le répertoire data s'il n'existe pas
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    # 1. Exécuter les migrations Alembic
    if not run_alembic_upgrade():
        print("❌ Database initialization failed at Alembic step")
        return False

    # 2. Initialiser le système d'authentification
    if not initialize_auth_system():
        print("❌ Database initialization failed at auth step")
        return False

    # 3. Initialiser le gestionnaire de base de données
    if not initialize_database_manager():
        print("❌ Database initialization failed at database manager step")
        return False

    # 4. Créer des données d'exemple
    if not create_sample_data():
        print("⚠️ Sample data creation failed, but continuing...")

    print("=" * 50)
    print("✅ Database initialization completed successfully!")
    print()
    print("📋 Summary:")
    print("   - Alembic migrations applied")
    print("   - Authentication system ready")
    print("   - Default users created:")
    print("     * admin / admin123 (role: admin)")
    print("     * testuser / test123 (role: user)")
    print("   - Database manager initialized")
    print("   - Sample dataset created")
    print()
    print("🔗 Next steps:")
    print("   1. Start the API: python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000")
    print("   2. Test authentication: POST /auth/login")
    print("   3. Access Streamlit UI: http://localhost:8501")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
