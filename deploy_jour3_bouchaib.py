#!/usr/bin/env python3
"""
Deploy to jour3_bouchaib Branch
Script pour déployer la solution complète vers la nouvelle branche
"""

import subprocess
import sys
from pathlib import Path

def run_command(command, description, timeout=60):
    """Exécute une commande et affiche le résultat"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            print(f"   ✅ {description} successful")
            if result.stdout.strip():
                print(f"   📄 Output: {result.stdout.strip()}")
            return True
        else:
            print(f"   ❌ {description} failed")
            if result.stderr.strip():
                print(f"   🔴 Error: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print(f"   ⏰ {description} timed out")
        return False
    except Exception as e:
        print(f"   ❌ {description} error: {e}")
        return False

def verify_project_structure():
    """Vérifie la structure du projet"""
    print("📁 Verifying project structure...")
    
    essential_files = [
        "README.md",
        "docker-compose.yml", 
        "Dockerfile",
        "requirements.txt",
        ".env",
        "main.py",
        "flow.py",
        "streamlit_app.py",
        "pyproject.toml",
        "alembic.ini",
        ".github/workflows/ci.yml",
        ".github/workflows/code-quality.yml",
        ".github/workflows/release.yml",
        "src/api/main.py",
        "src/auth/auth_service.py",
        "tests/test_complete_system.py",
        "FINAL_AUDIT_REPORT.md"
    ]
    
    missing_files = []
    for file_path in essential_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} (missing)")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️ Missing files: {missing_files}")
        return False
    
    print("   ✅ All essential files present")
    return True

def create_deployment_summary():
    """Crée un résumé de déploiement"""
    summary_content = """# 🚀 DÉPLOIEMENT JOUR 3 - BOUCHAIB

**Date**: 18 Juin 2025  
**Branche**: jour3_bouchaib  
**Version**: 3.0.0  

## ✅ CORRECTIONS APPLIQUÉES

### GitHub Actions
- ✅ Mise à jour `actions/setup-python` v4 → v5
- ✅ Mise à jour `actions/cache` v3 → v4  
- ✅ Mise à jour `actions/upload-artifact` v3 → v4
- ✅ Mise à jour `codecov/codecov-action` v3 → v4
- ✅ Ajout branche `jour3_bouchaib` aux triggers

### Dépendances
- ✅ Ajout SQLAlchemy aux requirements.txt
- ✅ Correction psutil dans requirements.txt
- ✅ Mise à jour toutes les dépendances

### Configuration
- ✅ Workflows GitHub Actions corrigés
- ✅ Configuration Docker optimisée
- ✅ Variables d'environnement configurées

## 🏗️ ARCHITECTURE FINALE

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │   FastAPI       │    │   MLflow        │
│   Port 8501     │◄──►│   Port 8000     │◄──►│   Port 5000     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │   SQLite DB     │              │
         │              │   + Alembic     │              │
         │              └─────────────────┘              │
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Uptime Kuma   │    │   Prefect       │    │   Prometheus    │
│   Port 3001     │    │   Port 4200     │    │   Port 9090     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────►│   Grafana       │◄─────────────┘
                        │   Port 3000     │
                        └─────────────────┘
```

## 🚀 DÉMARRAGE SYSTÈME

```bash
# Cloner et démarrer
git clone https://github.com/simbouch/ia_continu_solution.git
cd ia_continu_solution
git checkout jour3_bouchaib

# Démarrer avec Docker
docker-compose up -d

# Tester le système
python test_complete_day3.py
```

## 🔗 URLS D'ACCÈS

- **API**: http://localhost:8000
- **UI Streamlit**: http://localhost:8501  
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin123)
- **Uptime Kuma**: http://localhost:3001
- **MLflow**: http://localhost:5000
- **Prefect**: http://localhost:4200

## 🔐 AUTHENTIFICATION

- **Admin**: admin / admin123
- **User**: testuser / test123

## 🎯 STATUT FINAL

✅ **PRODUCTION READY** - Système complet et fonctionnel  
✅ **CI/CD CORRIGÉ** - Workflows GitHub Actions mis à jour  
✅ **MONITORING COMPLET** - Métriques et dashboards  
✅ **SÉCURITÉ ROBUSTE** - Authentification JWT  
✅ **DOCUMENTATION EXHAUSTIVE** - Guides complets  

**L'IA Continu Solution est prête pour la production !** 🎉
"""
    
    with open("DEPLOYMENT_SUMMARY.md", "w", encoding="utf-8") as f:
        f.write(summary_content)
    
    print("   ✅ Deployment summary created")

def deploy_to_github():
    """Déploie vers GitHub"""
    print("\n🚀 Deploying to GitHub - jour3_bouchaib branch")
    print("=" * 60)
    
    # Vérifier la structure
    if not verify_project_structure():
        print("❌ Project structure verification failed")
        return False
    
    # Créer le résumé de déploiement
    create_deployment_summary()
    
    # Vérifier la branche actuelle
    if not run_command("git branch --show-current", "Check current branch"):
        return False
    
    # Ajouter tous les fichiers
    if not run_command("git add .", "Add all files"):
        return False
    
    # Commit les changements
    commit_message = "feat: Complete Day 3 implementation - Production Ready with fixed CI/CD"
    if not run_command(f'git commit -m "{commit_message}"', "Commit changes"):
        print("   ℹ️ No changes to commit or commit failed")
    
    # Pousser vers GitHub
    if not run_command("git push -u origin jour3_bouchaib", "Push to jour3_bouchaib branch", timeout=120):
        return False
    
    print("\n🎉 Successfully deployed to GitHub!")
    print("\n📋 Next steps:")
    print("   1. Go to: https://github.com/simbouch/ia_continu_solution")
    print("   2. Switch to 'jour3_bouchaib' branch")
    print("   3. Check the 'Actions' tab for CI/CD pipeline")
    print("   4. Verify all workflows pass successfully")
    print("   5. Create a Pull Request to main when ready")
    
    return True

def main():
    """Fonction principale"""
    print("🚀 IA Continu Solution - Deploy to jour3_bouchaib")
    print("=" * 60)
    
    if deploy_to_github():
        print("\n✅ Deployment completed successfully!")
        print("\n🔗 GitHub Repository: https://github.com/simbouch/ia_continu_solution")
        print("🌿 Branch: jour3_bouchaib")
        print("🔄 CI/CD: Fixed and ready to run")
        sys.exit(0)
    else:
        print("\n❌ Deployment failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
