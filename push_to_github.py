#!/usr/bin/env python3
"""
Push to GitHub Script
Script pour pousser correctement le code vers GitHub avec les workflows
"""

import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Exécute une commande et affiche le résultat"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
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

def push_to_github():
    """Pousse le code vers GitHub"""
    
    print("🚀 Pushing IA Continu Solution to GitHub")
    print("=" * 50)
    
    # Vérifier que nous sommes dans un repo git
    if not Path(".git").exists():
        print("❌ Not in a git repository")
        return False
    
    # Vérifier les fichiers critiques
    critical_files = [
        ".github/workflows/ci.yml",
        "src/api/main.py",
        "docker-compose.yml",
        "requirements.txt",
        "README.md"
    ]
    
    print("\n📁 Checking critical files...")
    missing_files = []
    for file_path in critical_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} (missing)")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing critical files: {missing_files}")
        return False
    
    # Vérifier la branche actuelle
    print("\n🌿 Checking current branch...")
    if not run_command("git branch --show-current", "Get current branch"):
        return False
    
    # Ajouter tous les fichiers
    print("\n📦 Adding files to git...")
    if not run_command("git add .", "Add all files"):
        return False
    
    # Vérifier le statut
    print("\n📊 Checking git status...")
    if not run_command("git status --porcelain", "Check git status"):
        return False
    
    # Commit les changements
    print("\n💾 Committing changes...")
    commit_message = "feat: Complete Day 3 implementation with monitoring, auth, and CI/CD"
    if not run_command(f'git commit -m "{commit_message}"', "Commit changes"):
        print("   ℹ️ No changes to commit or commit failed")
    
    # Pousser vers GitHub
    print("\n🚀 Pushing to GitHub...")
    if not run_command("git push origin jour2", "Push to jour2 branch"):
        # Essayer de créer la branche si elle n'existe pas
        print("   🔄 Trying to create and push new branch...")
        if not run_command("git push -u origin jour2", "Create and push jour2 branch"):
            return False
    
    # Vérifier que le push a fonctionné
    print("\n🔍 Verifying push...")
    if not run_command("git log --oneline -1", "Check latest commit"):
        return False
    
    print("\n🎉 Successfully pushed to GitHub!")
    print("\n📋 Next steps:")
    print("   1. Go to: https://github.com/simbouch/ia_continu_solution")
    print("   2. Switch to 'jour2' branch")
    print("   3. Check the 'Actions' tab for CI/CD pipeline")
    print("   4. Create a Pull Request to main if needed")
    
    return True

def check_github_actions():
    """Vérifie si GitHub Actions fonctionne"""
    print("\n🔍 Checking GitHub Actions setup...")
    
    # Vérifier la structure des workflows
    workflows_dir = Path(".github/workflows")
    if not workflows_dir.exists():
        print("   ❌ .github/workflows directory missing")
        return False
    
    workflow_files = list(workflows_dir.glob("*.yml"))
    if not workflow_files:
        print("   ❌ No workflow files found")
        return False
    
    print(f"   ✅ Found {len(workflow_files)} workflow files:")
    for workflow in workflow_files:
        print(f"      - {workflow.name}")
    
    # Vérifier le contenu du workflow principal
    ci_workflow = workflows_dir / "ci.yml"
    if ci_workflow.exists():
        content = ci_workflow.read_text()
        if "on:" in content and "push:" in content:
            print("   ✅ CI workflow properly configured")
            return True
        else:
            print("   ❌ CI workflow missing triggers")
            return False
    else:
        print("   ❌ ci.yml workflow missing")
        return False

if __name__ == "__main__":
    print("🔧 GitHub Push and CI/CD Setup")
    print("=" * 50)
    
    # Vérifier GitHub Actions
    if not check_github_actions():
        print("\n❌ GitHub Actions setup issues detected")
        sys.exit(1)
    
    # Pousser vers GitHub
    if push_to_github():
        print("\n✅ All done! Check GitHub for CI/CD pipeline.")
        sys.exit(0)
    else:
        print("\n❌ Push to GitHub failed")
        sys.exit(1)
