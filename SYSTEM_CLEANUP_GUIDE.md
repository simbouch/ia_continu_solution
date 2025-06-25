# 🧹 System Cleanup Guide - IA Continu Solution

## 📋 Overview
This guide provides comprehensive cleanup instructions to optimize laptop performance after completing the IA Continu Solution project.

## 🐳 Docker Cleanup (✅ COMPLETED)
- **Containers Stopped**: All IA Continu Solution containers
- **Images Removed**: All project-specific Docker images
- **Volumes Deleted**: All project data volumes
- **Networks Cleaned**: Project networks removed
- **Space Freed**: **11.85GB** of disk space recovered

## 🐍 Python Dependencies Cleanup

### Project-Specific Dependencies
The following packages were installed specifically for this project:

#### Core ML & Data Science
```bash
# Large ML packages that can be uninstalled if not needed elsewhere
pip uninstall numpy pandas scikit-learn
pip uninstall mlflow
pip uninstall plotly altair
```

#### Web Framework & API
```bash
# FastAPI and related packages
pip uninstall fastapi uvicorn
pip uninstall streamlit
pip uninstall prometheus-client prometheus-fastapi-instrumentator
```

#### Workflow & Orchestration
```bash
# Prefect workflow engine
pip uninstall prefect
```

#### Authentication & Security
```bash
# JWT and authentication packages
pip uninstall python-jose PyJWT passlib bcrypt
```

#### Database & Storage
```bash
# Database packages
pip uninstall sqlalchemy alembic
```

#### Development & Testing
```bash
# Testing and development tools
pip uninstall pytest pytest-asyncio
pip uninstall ruff black
```

### Complete Project Cleanup Command
```bash
# Uninstall all project dependencies at once
pip uninstall -y fastapi uvicorn streamlit prefect mlflow numpy pandas scikit-learn plotly sqlalchemy pytest ruff python-jose PyJWT passlib bcrypt prometheus-client requests pydantic loguru python-dotenv joblib psutil
```

## 📁 File System Cleanup

### Temporary Files & Caches
```bash
# Python cache cleanup
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete

# Pip cache cleanup
pip cache purge

# Remove pytest cache
rm -rf .pytest_cache/
```

### Project Data Directories
The following directories contain project data and can be cleaned:

#### Large Data Directories
- `./mlruns/` - MLflow experiment data
- `./models/` - Trained ML models
- `./logs/` - Application logs
- `./prometheus_data/` - Prometheus metrics data
- `./grafana_data/` - Grafana dashboard data
- `./uptime_kuma_data/` - Monitoring data

#### Cleanup Commands
```bash
# Remove large data directories (CAUTION: This removes all project data)
rm -rf mlruns/ models/ logs/ prometheus_data/ grafana_data/ uptime_kuma_data/

# Or selectively clean logs only
rm -rf logs/*.log
```

## 💻 System Performance Optimization

### 1. Disk Space Analysis
```bash
# Check disk usage
du -sh * | sort -hr

# Find large files
find . -type f -size +100M -exec ls -lh {} \;
```

### 2. Memory Optimization
- **Close unnecessary applications**
- **Restart Python IDE/editors** to free memory
- **Clear browser cache** if using web interfaces

### 3. Python Environment Cleanup
```bash
# Create a fresh virtual environment for future projects
python -m venv clean_env
source clean_env/bin/activate  # Linux/Mac
# or
clean_env\Scripts\activate     # Windows

# Install only essential packages
pip install --upgrade pip
```

## 🔧 Recommended System Maintenance

### Windows-Specific Cleanup
```cmd
# Disk Cleanup
cleanmgr /sagerun:1

# Clear temp files
del /q/f/s %TEMP%\*

# Clear Windows Update cache
net stop wuauserv
rd /s /q C:\Windows\SoftwareDistribution\Download
net start wuauserv
```

### General Maintenance
1. **Restart your computer** to clear memory
2. **Run disk defragmentation** (Windows) or **verify disk** (Mac)
3. **Update system drivers**
4. **Check for system updates**

## 📊 Expected Performance Improvements

### Disk Space Recovery
- **Docker Images**: ~11.85GB freed
- **Python Packages**: ~2-3GB potential savings
- **Project Data**: ~1-2GB (if cleaned)
- **Total Potential**: **~15GB** disk space recovery

### Memory Benefits
- **Reduced RAM usage** from fewer installed packages
- **Faster Python startup** with fewer dependencies
- **Improved system responsiveness**

## ⚠️ Important Notes

### What to Keep
- **Git repository** - Keep the project code for reference
- **Documentation** - All docs in `docs/` folder
- **Configuration files** - docker-compose.yml, .env templates

### What's Safe to Remove
- **Docker containers/images** - Can be rebuilt from code
- **Python packages** - Can be reinstalled when needed
- **Log files** - Historical data not needed for future use
- **Model files** - Can be retrained if needed

## 🚀 Future Project Setup

If you need to run this project again:

```bash
# Quick setup from clean state
git clone <repository>
cd ia_continu_solution

# Install dependencies
pip install -r requirements.txt

# Deploy with Docker
docker-compose up -d
```

## 📞 Support

If you encounter issues during cleanup:
1. **Check running processes** before removing packages
2. **Create backups** of important data
3. **Test system stability** after major cleanups
4. **Restart system** if performance doesn't improve

---

**🎯 Cleanup Status**: Ready for next project!  
**💾 Space Freed**: ~15GB potential  
**⚡ Performance**: Optimized for development
