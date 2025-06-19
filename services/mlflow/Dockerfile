FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install MLflow and dependencies
RUN pip install --no-cache-dir \
    mlflow==2.8.1 \
    requests \
    psutil

# Create directories for MLflow data
RUN mkdir -p /app/mlflow /app/mlruns

# Set environment variables
ENV MLFLOW_HOST=0.0.0.0
ENV MLFLOW_PORT=5000
ENV MLFLOW_BACKEND_STORE_URI=sqlite:///app/mlflow/mlflow.db
ENV MLFLOW_DEFAULT_ARTIFACT_ROOT=/app/mlruns

# Expose MLflow port
EXPOSE 5000

# Health check - MLflow doesn't have /health endpoint, check root instead
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/', timeout=5)" || exit 1

# Start MLflow server with proper Gunicorn binding
CMD ["sh", "-c", "chown -R root:root /app && mlflow server --backend-store-uri sqlite:///app/mlflow/mlflow.db --default-artifact-root /app/mlruns --host 0.0.0.0 --port 5000 --gunicorn-opts '--bind=0.0.0.0:5000 --workers=1'"]
