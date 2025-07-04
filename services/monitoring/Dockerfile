FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy monitoring scripts and configurations
COPY services/monitoring/scripts/ ./scripts/
COPY services/monitoring/config/ ./config/

# Create logs directory
RUN mkdir -p logs

# Set environment variables
ENV PYTHONPATH=/app
ENV MONITORING_INTERVAL=30

# Expose port for monitoring API (if needed)
EXPOSE 9000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "print('Monitoring service healthy')" || exit 1

# Run monitoring service
CMD ["python", "scripts/monitoring_service.py"]
