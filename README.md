# 🤖 IA Continu Solution - Enterprise ML Template

[![CI/CD Pipeline](https://img.shields.io/badge/CI%2FCD-Ruff%20%2B%20Pytest-green.svg)](https://github.com/simbouch/ia_continu_solution)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://github.com/simbouch/ia_continu_solution)
[![Template Ready](https://img.shields.io/badge/Template-Production%20Ready-orange.svg)](https://github.com/simbouch/ia_continu_solution)
[![Enterprise Grade](https://img.shields.io/badge/Quality-Enterprise-purple.svg)](https://github.com/simbouch/ia_continu_solution)

## 👨‍💻 Author

**KHRIBECH Bouchaib**
🌐 Website: [https://khribech-b.vercel.app/](https://khribech-b.vercel.app/)
📧 Contact: [simplonbouchaib@gmail.com](mailto:simplonbouchaib@gmail.com)

## 🎯 Overview

**IA Continu Solution** is a production-ready ML template with complete automation, advanced monitoring, and Discord integration. Built with modern microservices architecture and designed for immediate deployment and reuse across multiple projects.

### **🏆 Complete Enterprise Template**
This template provides a comprehensive foundation for ML projects with professional architecture, automated CI/CD, and complete monitoring stack. Perfect as a base for your professional ML projects.

### **🚀 Key Features**
- 🏗️ **Professional Microservices**: 5 independent services with dedicated containers
- 🤖 **Full ML Automation**: 30-second automated pipeline with drift detection
- 📊 **Comprehensive Monitoring**: Multi-service health checks and real-time alerting
- 🔔 **Discord Integration**: Rich notifications for all operations and alerts
- 🔐 **Enterprise Security**: JWT authentication with role-based access control
- 📈 **MLflow Integration**: Complete experiment tracking and model management
- 🎨 **Modern UI**: Professional Streamlit dashboard with interactive features
- 📚 **Complete Documentation**: Comprehensive guides and API reference

---

## ⚡ Quick Start (5 Minutes)

### **1. Prerequisites**
- Docker 20.10+ with Docker Compose
- 8GB+ RAM (16GB recommended)
- Git for cloning

### **2. Deploy**
```bash
# Clone repository
git clone https://github.com/simbouch/ia_continu_solution.git
cd ia_continu_solution

# Configure environment
cp .env.example .env
# Edit .env with your Discord webhook URL (optional)

# Deploy all services
docker-compose up -d

# Verify deployment
docker-compose ps
```

### **3. Access Services**
- **🎨 Streamlit UI**: http://localhost:8501 (Login: `testuser`/`test123`)
- **📚 API Documentation**: http://localhost:8000/docs
- **📈 MLflow Tracking**: http://localhost:5000
- **🔄 Prefect Dashboard**: http://localhost:4200
- **📊 Monitoring**: http://localhost:3001

### **4. Validate**
```bash
# Run comprehensive tests
python tests/run_all_tests.py
# Expected: All tests passing (100% success rate)
```

---

## 🏗️ Architecture Overview

### **Microservices Structure**
```
services/
├── api/          # FastAPI ML Service (Port 8000)
├── mlflow/       # MLflow Tracking (Port 5000)
├── prefect/      # Workflow Orchestration (Port 4200)
├── monitoring/   # System Health Monitoring (Port 9000)
└── streamlit/    # User Interface (Port 8501)
```

### **Service Responsibilities**

| Service | Purpose | Port | Key Features |
|---------|---------|------|--------------|
| **API** | ML Operations & Auth | 8000 | JWT auth, predictions, data generation |
| **MLflow** | Model Tracking | 5000 | Experiment tracking, model registry |
| **Prefect** | Workflow Orchestration | 4200 | Automated ML pipeline, drift detection |
| **Monitoring** | System Health | 9000 | Discord notifications, health checks |
| **Streamlit** | User Interface | 8501 | Interactive dashboard, visualizations |

### **External Services**
- **Uptime Kuma**: System monitoring dashboard (Port 3001)
- **Prometheus**: Metrics collection (Port 9090)
- **Grafana**: Advanced dashboards (Port 3000)

---

## 🤖 Automation Features

### **ML Pipeline Automation**
- **🔍 Drift Detection**: Hybrid detection using multiple methods
- **🔄 Automated Retraining**: Triggered when drift is detected
- **📊 Model Versioning**: Automatic versioning with MLflow
- **📈 Data Generation**: Fresh training data when needed
- **⏱️ 30-Second Intervals**: Continuous monitoring and automation

### **Monitoring Automation**
- **💓 Health Checks**: All services monitored continuously
- **🚨 Alert Generation**: Immediate notifications on issues
- **🔄 Recovery Tracking**: Automatic recovery detection
- **📊 Performance Monitoring**: Response time and availability tracking

---

## 🔔 Discord Integration

### **Notification Types**
- **🤖 ML Operations**: Drift detection, retraining status, model updates
- **💓 System Health**: Service availability, performance alerts
- **⚙️ Operational Status**: Pipeline startup/shutdown, configuration changes
- **🚨 Error Alerts**: System errors and recovery notifications

### **Setup Discord Webhook**
1. Create webhook in your Discord server
2. Copy webhook URL
3. Add to `.env` file: `DISCORD_WEBHOOK_URL=your_webhook_url`
4. Restart services to apply

---

## 🔐 Authentication

### **Default Users**
| Username | Password | Role | Access |
|----------|----------|------|--------|
| `admin` | `admin123` | Administrator | Full access |
| `testuser` | `test123` | Standard User | Predictions, basic features |

### **API Authentication**
```bash
# Get JWT token
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "test123"}'

# Use token for API calls
curl -X POST "http://localhost:8000/predict" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"features": [0.5, 0.5]}'
```

---

## 📊 Monitoring & Observability

### **Health Monitoring**
- **API Health**: Real-time endpoint monitoring
- **Service Availability**: Multi-service health checks
- **Performance Metrics**: Response times and throughput
- **Error Tracking**: Comprehensive error logging and alerting

### **ML Monitoring**
- **Model Performance**: Accuracy and prediction quality tracking
- **Drift Detection**: Automated data and model drift monitoring
- **Training Metrics**: Complete training history and performance
- **Prediction Logging**: Full audit trail of all predictions

---

## 🛠️ Template Customization

### **Easy Customization Points**
1. **ML Models**: Replace LogisticRegression with your models in `services/api/src/ml/`
2. **Data Sources**: Modify data generation and ingestion in `services/api/src/data/`
3. **UI Components**: Customize Streamlit interface in `services/streamlit/app/`
4. **Monitoring**: Add custom metrics and alerts in `services/monitoring/`
5. **Workflows**: Extend Prefect automation flows in `services/prefect/flows/`

### **Configuration Files**
- `docker-compose.yml`: Service orchestration
- `.env`: Environment variables and secrets
- `services/*/Dockerfile`: Individual service configurations
- `services/prefect/flows/`: Automation workflow definitions

---

## 📚 Complete Documentation

### **📖 Guides Complets**
- **[Guide Installation](docs/setup-guide.md)**: Instructions complètes déploiement et configuration
- **[Documentation API](docs/api-documentation.md)**: Référence API complète avec exemples
- **[Guide Dépannage](docs/troubleshooting-guide.md)**: Problèmes courants et solutions

### **📋 Template Documentation**
- **[Setup Guide](docs/setup-guide.md)**: Complete deployment and configuration instructions
- **[API Documentation](docs/api-documentation.md)**: Complete API reference with examples
- **[Troubleshooting Guide](docs/troubleshooting-guide.md)**: Common issues and solutions

---

## 🎯 Use Cases & Applications

### **Perfect For**
- **🎓 Educational Projects**: Learning modern ML architecture and DevOps
- **🏢 Enterprise Templates**: Reusable ML project foundation
- **🔬 Proof of Concepts**: Rapid ML solution prototyping
- **🎯 Capstone Projects**: Academic and professional demonstrations
- **🚀 Production Deployments**: Enterprise-grade ML systems

### **Industries**
- **💻 Technology**: Software development and AI companies
- **💰 Finance**: Risk modeling and fraud detection
- **🏥 Healthcare**: Diagnostic and predictive modeling
- **🛒 Retail**: Recommendation systems and demand forecasting
- **🏭 Manufacturing**: Quality control and predictive maintenance

---

## 📈 Success Metrics

### **Template Quality**
- ✅ **100% Service Separation**: All services properly modularized
- ✅ **100% Automation**: Manual operations eliminated
- ✅ **100% Monitoring Coverage**: Comprehensive health checks
- ✅ **Enterprise Grade**: Professional architecture and practices

### **Performance Benchmarks**
- **API Response Time**: < 100ms for predictions
- **Model Accuracy**: > 95% on test datasets
- **System Uptime**: > 99% availability target
- **Automation Reliability**: 30-second consistent intervals

---

## 🤝 Contributing & Support

### **How to Contribute**
1. **Fork** the repository
2. **Create** a feature branch
3. **Implement** your enhancement
4. **Test** thoroughly
5. **Submit** a pull request

### **Getting Help**
- **📚 Documentation**: Check the comprehensive guides in `docs/`
- **🔧 Troubleshooting**: Follow the troubleshooting guide
- **📊 Monitoring**: Use built-in monitoring dashboards
- **🧪 Testing**: Run `python test_global.py` for validation

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**🎯 Template Status**: ✅ **PRODUCTION READY**  
**🏗️ Quality**: ✅ **ENTERPRISE GRADE**  
**📚 Documentation**: ✅ **COMPREHENSIVE**  
**🚀 Support**: ✅ **COMMUNITY DRIVEN**

---

## 🙏 Acknowledgments

This project was developed as part of the **Simplon Formation** program, demonstrating enterprise-grade ML architecture and DevOps practices.

**Author**: KHRIBECH Bouchaib
**Portfolio**: [https://khribech-b.vercel.app/](https://khribech-b.vercel.app/)
**Formation**: Simplon - Intelligence Artificielle Continue

---

*Built with ❤️ for the ML community. Ready to power your next ML project!*
