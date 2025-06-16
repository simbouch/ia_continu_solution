# IA Continu Solution

A comprehensive AI monitoring solution with automated health checks, model drift detection, and real-time notifications.

## 🚀 Overview

This project provides a complete monitoring infrastructure for AI applications featuring:

- **FastAPI Application**: REST API with health endpoints and Discord notifications
- **Model Monitoring**: Automated drift detection and performance tracking
- **Docker Integration**: Containerized deployment for easy scaling
- **Real-time Notifications**: Discord webhook integration for instant alerts
- **Comprehensive Testing**: Full test suite for all components

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   Monitoring    │    │   Discord       │
│   Port: 9000    │    │   Service       │    │   Notifications │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Docker Container│
                    │ (Orchestration) │
                    └─────────────────┘
```

## ✨ Features

### 🤖 Automated Monitoring
- **Model Performance**: Accuracy and drift score tracking
- **API Health Checks**: Continuous endpoint monitoring
- **Real-time Alerts**: Instant Discord notifications
- **Configurable Thresholds**: Customizable alert levels

### 🔗 API Endpoints
- `GET /` - Application information
- `GET /health` - Health status check
- `GET /status` - Detailed system status
- `POST /notify` - Send custom notifications
- `GET /docs` - Interactive API documentation

### 📊 Alert Types
- 🟢 **Success**: System operating normally
- 🟡 **Warning**: Performance below threshold
- 🔴 **Error**: Critical issues detected
- 🔵 **Info**: General system information

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)
- Discord webhook URL (optional, for notifications)

### 1. Clone and Setup
```bash
git clone https://github.com/simbouch/ia_continu_solution.git
cd ia_continu_solution

# Configure environment
cp .env.example .env
# Edit .env with your Discord webhook URL
```

### 2. Start the Application
```bash
# Build and run with Docker
docker build -t fastapi-app .
docker run -d -p 9000:8000 --name ia_continu_app \
  -e DISCORD_WEBHOOK_URL="your_webhook_url" fastapi-app

# Or use docker-compose
docker-compose up -d
```

### 3. Verify Installation
```bash
# Run comprehensive tests
python tests.py

# Check application status
curl http://localhost:9000/health
```

### 4. Access Services
- **Application**: http://localhost:9000
- **API Documentation**: http://localhost:9000/docs
- **Health Check**: http://localhost:9000/health

## 📋 Project Structure

```
ia_continu_solution/
├── main.py              # FastAPI application
├── monitoring.py        # Monitoring utilities
├── tests.py            # Comprehensive test suite
├── flow.py             # Prefect workflow (optional)
├── Dockerfile          # Container configuration
├── docker-compose.yml  # Multi-service setup
├── requirements.txt    # Python dependencies
├── .env               # Environment configuration
└── README.md          # This documentation
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Discord Webhook (Required for notifications)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_TOKEN

# Application Settings
ENVIRONMENT=production
API_URL=http://fastapi_app:8000
PREFECT_API_URL=http://prefect-server:4200/api
```

### Discord Webhook Setup
1. Go to your Discord server settings
2. Navigate to Integrations → Webhooks
3. Create a new webhook
4. Copy the webhook URL
5. Set it in your `.env` file

## 🧪 Testing

### Run All Tests
```bash
# Set Discord webhook (optional)
export DISCORD_WEBHOOK_URL="your_webhook_url"

# Run comprehensive test suite
python tests.py
```

### Test Categories
- **API Endpoints**: All REST API functionality
- **Docker Container**: Container health and status
- **Discord Notifications**: Webhook functionality
- **Monitoring Simulation**: Model performance checks

## 📊 Monitoring

### Start Monitoring Service
```bash
# Set environment variables
export DISCORD_WEBHOOK_URL="your_webhook_url"

# Run monitoring
python monitoring.py
```

### Monitoring Options
1. **Single Cycle**: Run one monitoring check
2. **Continuous**: Monitor every 30 seconds
3. **Demo Mode**: 3 cycles with 10-second intervals

### Model Performance Thresholds
- **Accuracy Threshold**: 85% (configurable)
- **Drift Threshold**: 70% (configurable)
- **API Timeout**: 5 seconds

## 🐳 Docker Management

### Basic Commands
```bash
# Build image
docker build -t fastapi-app .

# Run container
docker run -d -p 9000:8000 --name ia_continu_app \
  -e DISCORD_WEBHOOK_URL="your_webhook_url" fastapi-app

# Check status
docker ps | grep ia_continu

# View logs
docker logs ia_continu_app

# Stop and remove
docker stop ia_continu_app
docker rm ia_continu_app
```

### Docker Compose
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f
```

## 🔍 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   netstat -ano | findstr :9000
   
   # Use different port
   docker run -d -p 9001:8000 --name ia_continu_app fastapi-app
   ```

2. **Discord Notifications Not Working**
   - Verify webhook URL is correct
   - Check container logs: `docker logs ia_continu_app`
   - Test webhook manually: `python tests.py`

3. **Container Won't Start**
   ```bash
   # Check Docker logs
   docker logs ia_continu_app
   
   # Rebuild image
   docker build --no-cache -t fastapi-app .
   ```

### Health Checks
```bash
# API Health
curl http://localhost:9000/health

# Container Health
docker inspect --format='{{.State.Health.Status}}' ia_continu_app

# Test Discord
python -c "import requests; print(requests.post('YOUR_WEBHOOK_URL', json={'content': 'test'}).status_code)"
```

## 🛠️ Development

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python main.py

# Run tests
python tests.py
```

### Adding New Features
1. Update `main.py` for new API endpoints
2. Add tests in `tests.py`
3. Update monitoring in `monitoring.py`
4. Rebuild Docker image
5. Update documentation

## 📈 Advanced Monitoring

### Uptime Kuma Integration
See [docs/uptime-kuma.md](docs/uptime-kuma.md) for detailed setup instructions.

### Prefect Workflow Integration
See [docs/prefect-setup.md](docs/prefect-setup.md) for workflow orchestration.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

## 🆘 Support

- **Issues**: Open a GitHub issue
- **Documentation**: Check the docs/ directory
- **Tests**: Run `python tests.py` for diagnostics
