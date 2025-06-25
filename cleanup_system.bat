@echo off
echo 🧹 IA Continu Solution - System Cleanup Script
echo ================================================
echo.

echo 📊 Current system status:
echo - Docker cleanup: COMPLETED (11.85GB freed)
echo - Python packages: READY FOR CLEANUP
echo - Project data: READY FOR CLEANUP
echo.

echo ⚠️  WARNING: This will remove Python packages and project data
echo Press any key to continue or Ctrl+C to cancel...
pause

echo.
echo 🐍 Removing Python packages...
echo ================================

echo Removing ML and Data Science packages...
pip uninstall -y numpy pandas scikit-learn mlflow plotly geopandas

echo Removing Web Framework packages...
pip uninstall -y fastapi uvicorn streamlit streamlit-date-picker streamlit_folium streamlit-lottie

echo Removing Workflow packages...
pip uninstall -y prefect

echo Removing Testing packages...
pip uninstall -y pytest pytest-asyncio pytest-fastapi

echo Removing Authentication packages...
pip uninstall -y python-jose PyJWT passlib bcrypt

echo Removing Database packages...
pip uninstall -y sqlalchemy alembic

echo Removing Monitoring packages...
pip uninstall -y prometheus-client prometheus-fastapi-instrumentator

echo Removing Development tools...
pip uninstall -y ruff black

echo.
echo 🧹 Cleaning Python cache...
echo ===========================
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul
del /s /q *.pyo 2>nul
pip cache purge

echo.
echo 📁 Cleaning project data directories...
echo ======================================
if exist "logs" (
    echo Removing logs directory...
    rd /s /q logs
)

if exist "mlruns" (
    echo Removing MLflow runs directory...
    rd /s /q mlruns
)

if exist "models" (
    echo Removing models directory...
    rd /s /q models
)

if exist "prometheus_data" (
    echo Removing Prometheus data...
    rd /s /q prometheus_data
)

if exist "grafana_data" (
    echo Removing Grafana data...
    rd /s /q grafana_data
)

if exist "uptime_kuma_data" (
    echo Removing Uptime Kuma data...
    rd /s /q uptime_kuma_data
)

if exist ".pytest_cache" (
    echo Removing pytest cache...
    rd /s /q .pytest_cache
)

if exist "installed_packages.txt" (
    echo Removing temporary files...
    del installed_packages.txt
)

echo.
echo 💻 Running Windows system cleanup...
echo ===================================
echo Clearing temporary files...
del /q/f/s "%TEMP%\*" 2>nul

echo.
echo ✅ CLEANUP COMPLETED!
echo ====================
echo.
echo 📊 Summary:
echo - Docker: 11.85GB freed
echo - Python packages: Removed major ML/web packages
echo - Project data: Cleaned
echo - System temp files: Cleared
echo.
echo 🚀 Your laptop is now optimized for the next project!
echo.
echo 💡 To reinstall this project later:
echo    git clone [repository]
echo    pip install -r requirements.txt
echo    docker-compose up -d
echo.
pause
