FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install MLflow and dependencies
RUN pip install --no-cache-dir \
    mlflow==2.8.1 \
    requests \
    psutil

# Create directories for MLflow data with proper permissions
RUN mkdir -p /app/mlflow /app/mlruns && chmod -R 777 /app

# Expose MLflow port
EXPOSE 5000

# Start MLflow server with simple file-based backend
CMD ["mlflow", "server", "--backend-store-uri", "file:///app/mlflow", "--default-artifact-root", "/app/mlruns", "--host", "0.0.0.0", "--port", "5000"]
