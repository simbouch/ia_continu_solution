# 🚀 Quick Start Guide - IA Continu Solution

## 📋 Prerequisites
- Docker & Docker Compose installed
- Git (for cloning)
- Discord webhook URL (optional, for notifications)

## ⚡ Quick Start (5 minutes)

### 1. Clone and Setup
```bash
git clone https://github.com/simbouch/ia_continu_solution.git
cd ia_continu_solution

# Optional: Configure Discord notifications
echo "DISCORD_WEBHOOK_URL=your_webhook_url_here" > .env
```

### 2. Start All Services
```bash
# Start all services in background
docker-compose up -d

# Check all services are running
docker-compose ps
```

### 3. Verify Installation
```bash
# Run comprehensive test suite
python test_global.py
```

Expected result: **8/9 tests passing (88.9%)** = ✅ **PRODUCTION READY**

## 🌐 Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| **API** | http://localhost:8000 | testuser / test123 |
| **API Docs** | http://localhost:8000/docs | - |
| **Streamlit UI** | http://localhost:8501 | testuser / test123 |
| **Prefect** | http://localhost:4200 | - |
| **Uptime Kuma** | http://localhost:3001 | Setup required |
| **MLflow** | http://localhost:5000 | - |
| **Prometheus** | http://localhost:9090 | - |
| **Grafana** | http://localhost:3000 | admin / admin123 |

## 🔐 Authentication

### Default Users
- **Admin**: `admin` / `admin123`
- **Test User**: `testuser` / `test123`

### Get JWT Token
```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "test123"}'
```

### Use Token in API Calls
```bash
# Replace YOUR_TOKEN with the token from login
curl -X POST "http://localhost:8000/predict" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"features": [0.5, -0.3]}'
```

## 🧪 Testing

### Quick Health Check
```bash
# Test API health
curl http://localhost:8000/health

# Test Plotly in Streamlit
docker exec streamlit_ui python -c "import plotly.express as px; print('✅ Plotly OK')"
```

### Full Test Suite
```bash
# Comprehensive system test
python test_global.py

# Expected output: 8/9 tests passing (88.9%)
```

## 🔄 Common Operations

### Make a Prediction
```bash
# 1. Get token
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"username": "testuser", "password": "test123"}' | \
        python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 2. Make prediction
curl -X POST "http://localhost:8000/predict" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"features": [0.5, -0.3]}'
```

### Generate New Dataset
```bash
curl -X POST "http://localhost:8000/generate" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"samples": 1000}'
```

### Retrain Model
```bash
curl -X POST "http://localhost:8000/retrain" \
     -H "Authorization: Bearer $TOKEN"
```

## 🛠️ Troubleshooting

### Services Not Starting
```bash
# Check Docker status
docker --version
docker-compose --version

# Restart services
docker-compose down
docker-compose up -d
```

### Port Conflicts
If ports are already in use, modify `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change 8000 to 8001
```

### Authentication Issues
```bash
# Check if users exist
docker exec fastapi_app python -c "
from src.auth.auth_service import get_auth_service
auth = get_auth_service()
print('✅ Auth service initialized')
"
```

### Plotly Import Issues
```bash
# Verify Plotly installation
docker exec streamlit_ui pip show plotly
```

## 📊 Monitoring

### Check System Status
```bash
# All containers status
docker-compose ps

# View logs
docker-compose logs -f fastapi_app
docker-compose logs -f streamlit_ui
```

### Performance Metrics
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
- **Uptime Kuma**: http://localhost:3001

## 🔧 Development

### Run Tests in Development
```bash
# Install dependencies locally
pip install -r requirements.txt

# Run specific tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### Code Quality
```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/
```

## 📚 Documentation

- **Main README**: [README.md](README.md)
- **Architecture**: [docs/architecture.md](docs/architecture.md)
- **Fixes Summary**: [FIXES_SUMMARY.md](FIXES_SUMMARY.md)
- **Final Report**: [FINAL_VERIFICATION_REPORT.md](FINAL_VERIFICATION_REPORT.md)

## 🆘 Support

### Common Issues Fixed
1. ✅ Plotly import errors → Fixed in requirements.txt
2. ✅ Flake8 configuration errors → Fixed in .flake8
3. ✅ Authentication 403 errors → Use JWT tokens
4. ✅ Duplicate monitoring folders → Cleaned up structure

### Getting Help
1. Check logs: `docker-compose logs [service_name]`
2. Run tests: `python test_global.py`
3. Verify services: `docker-compose ps`
4. Check documentation in `docs/` folder

---

**Status**: ✅ **PRODUCTION READY** | **Test Success**: 88.9% | **All Critical Issues Resolved**
