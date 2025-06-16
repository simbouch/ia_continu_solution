# Prefect Workflow Integration Guide

This guide explains how to set up Prefect for workflow orchestration in your IA Continu Solution.

## 🚀 Quick Setup

### 1. Add Prefect to Docker Compose

Update your `docker-compose.yml`:

```yaml
services:
  # ... existing services ...
  
  prefect-server:
    image: prefecthq/prefect:3-latest
    command: prefect server start --host 0.0.0.0
    container_name: prefect-server
    ports:
      - "4200:4200"
    volumes:
      - prefect_data:/root/.prefect
    environment:
      - PREFECT_SERVER_API_HOST=0.0.0.0
      - PREFECT_API_URL=http://prefect-server:4200/api
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:4200/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    networks:
      - monitoring-network

  prefect-worker:
    build: 
      context: .
      dockerfile: Dockerfile.prefect
    container_name: prefect-worker
    depends_on:
      prefect-server:
        condition: service_healthy
      app:
        condition: service_healthy
    environment:
      - PREFECT_API_URL=http://prefect-server:4200/api
      - PYTHONIOENCODING=utf-8
      - API_URL=http://fastapi_app:8000
      - DISCORD_WEBHOOK_URL=${DISCORD_WEBHOOK_URL:-}
    restart: unless-stopped
    networks:
      - monitoring-network

volumes:
  prefect_data:
    driver: local
```

### 2. Create Prefect Dockerfile

Create `Dockerfile.prefect`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy Prefect flow
COPY flow.py .

# Create non-root user
RUN adduser --disabled-password --gecos '' prefectuser
RUN chown -R prefectuser:prefectuser /app
USER prefectuser

# Wait for Prefect server and start flow
CMD ["sh", "-c", "sleep 10 && python flow.py"]
```

### 3. Start Prefect Services

```bash
docker-compose up -d prefect-server prefect-worker
```

### 4. Access Prefect Dashboard

Open http://localhost:4200 in your browser.

## ⚙️ Workflow Configuration

### Basic Flow Structure

The `flow.py` file contains your monitoring workflow:

```python
import os
import random
import requests
from prefect import flow, task
from prefect.logging import get_run_logger
from datetime import datetime

@task(retries=2, retry_delay_seconds=1)
def check_model_performance():
    """Monitor model performance metrics"""
    logger = get_run_logger()
    
    # Simulate model metrics
    accuracy = random.uniform(0.7, 0.95)
    drift_score = random.uniform(0.0, 1.0)
    
    logger.info(f"Model accuracy: {accuracy:.3f}")
    logger.info(f"Drift score: {drift_score:.3f}")
    
    # Check thresholds
    if accuracy < 0.85:
        logger.warning(f"Low accuracy: {accuracy:.3f}")
        return {"status": "warning", "accuracy": accuracy, "drift_score": drift_score}
    
    if drift_score > 0.7:
        logger.error(f"High drift: {drift_score:.3f}")
        raise ValueError("Model drift detected")
    
    logger.info("Model performing well")
    return {"status": "healthy", "accuracy": accuracy, "drift_score": drift_score}

@task
def check_api_health():
    """Monitor API health"""
    logger = get_run_logger()
    
    try:
        api_url = os.getenv("API_URL", "http://fastapi_app:8000")
        response = requests.get(f"{api_url}/health", timeout=5)
        
        if response.status_code == 200:
            logger.info("API health check passed")
            return {"api_status": "healthy"}
        else:
            logger.warning(f"API unhealthy: {response.status_code}")
            return {"api_status": "unhealthy", "status_code": response.status_code}
            
    except requests.RequestException as e:
        logger.error(f"API unreachable: {e}")
        return {"api_status": "unreachable", "error": str(e)}

@flow(log_prints=True)
def monitoring_flow():
    """Main monitoring workflow"""
    logger = get_run_logger()
    logger.info("Starting monitoring workflow")
    
    # Run monitoring tasks
    model_metrics = check_model_performance()
    api_metrics = check_api_health()
    
    # Log results
    logger.info(f"Model: {model_metrics.get('status')}")
    logger.info(f"API: {api_metrics.get('api_status')}")
    
    return {"model": model_metrics, "api": api_metrics}

if __name__ == "__main__":
    # Deploy flow to run every 30 seconds
    monitoring_flow.serve(
        name="ia-continu-monitoring",
        interval=30,
        description="IA Continu Solution monitoring workflow"
    )
```

## 📊 Dashboard Usage

### Viewing Flow Runs

1. **Flow Runs Tab**
   - View all flow executions
   - Check run status and duration
   - Access detailed logs

2. **Flow Details**
   - Click on a flow name
   - View flow graph
   - See task dependencies

3. **Task Runs**
   - Individual task execution details
   - Task logs and outputs
   - Retry information

### Monitoring Metrics

1. **Success Rate**
   - Track flow success percentage
   - Identify failure patterns
   - Monitor performance trends

2. **Execution Time**
   - Average flow duration
   - Task-level timing
   - Performance optimization

3. **Error Analysis**
   - Failed task details
   - Error messages and stack traces
   - Retry attempts

## 🔧 Advanced Configuration

### Custom Schedules

```python
from prefect.schedules import IntervalSchedule
from datetime import timedelta

# Every 5 minutes
schedule = IntervalSchedule(interval=timedelta(minutes=5))

# Cron-style schedule (every hour at minute 0)
from prefect.schedules import CronSchedule
schedule = CronSchedule(cron="0 * * * *")

@flow(schedule=schedule)
def scheduled_monitoring():
    # Your monitoring logic
    pass
```

### Notifications Integration

```python
from prefect.blocks.notifications import DiscordWebhook

@task
def send_alert(message: str):
    """Send alert via Discord"""
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if webhook_url:
        discord_webhook = DiscordWebhook(url=webhook_url)
        discord_webhook.notify(message)
```

### Data Storage

```python
from prefect.filesystems import LocalFileSystem

# Save monitoring results
@task
def save_results(data: dict):
    """Save monitoring results to file"""
    import json
    from datetime import datetime
    
    filename = f"monitoring_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(f"/app/data/{filename}", "w") as f:
        json.dump(data, f, indent=2)
    
    return filename
```

## 🔍 Troubleshooting

### Common Issues

1. **Flow Not Starting**
   ```bash
   # Check Prefect server logs
   docker logs prefect-server
   
   # Check worker logs
   docker logs prefect-worker
   
   # Verify API connectivity
   curl http://localhost:4200/api/health
   ```

2. **Tasks Failing**
   - Check task logs in dashboard
   - Verify environment variables
   - Test API connectivity

3. **Worker Connection Issues**
   ```bash
   # Check network connectivity
   docker exec prefect-worker curl http://prefect-server:4200/api/health
   
   # Restart worker
   docker restart prefect-worker
   ```

### Debug Commands

```bash
# Access Prefect CLI in container
docker exec -it prefect-worker prefect --help

# List flows
docker exec prefect-worker prefect flow ls

# Check deployments
docker exec prefect-worker prefect deployment ls

# View flow runs
docker exec prefect-worker prefect flow-run ls
```

## 🚀 Production Deployment

### Scaling Workers

```yaml
prefect-worker:
  deploy:
    replicas: 3
  environment:
    - PREFECT_WORKER_PREFETCH_SECONDS=10
    - PREFECT_WORKER_QUERY_SECONDS=5
```

### Resource Management

```yaml
prefect-server:
  deploy:
    resources:
      limits:
        memory: 1G
        cpus: '1.0'
      reservations:
        memory: 512M
        cpus: '0.5'
```

### Data Persistence

```yaml
volumes:
  prefect_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /opt/prefect/data
```

## 📈 Monitoring Best Practices

### Flow Design

1. **Idempotent Tasks**: Ensure tasks can be safely retried
2. **Error Handling**: Implement proper exception handling
3. **Logging**: Use structured logging for better debugging
4. **Timeouts**: Set appropriate task timeouts

### Performance Optimization

1. **Parallel Execution**: Use concurrent tasks where possible
2. **Resource Limits**: Set memory and CPU limits
3. **Caching**: Cache expensive operations
4. **Batch Processing**: Group similar operations

### Alerting Strategy

1. **Flow Failures**: Alert on consecutive failures
2. **Performance Degradation**: Monitor execution times
3. **Resource Usage**: Alert on high memory/CPU usage
4. **Data Quality**: Monitor data validation failures

## 📚 Additional Resources

- [Prefect Documentation](https://docs.prefect.io/)
- [Prefect Cloud](https://www.prefect.io/cloud/)
- [Workflow Patterns](https://docs.prefect.io/concepts/flows/)
- [Task Configuration](https://docs.prefect.io/concepts/tasks/)
