FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY services/prefect/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Prefect flows and configurations
COPY services/prefect/flows/ ./flows/
COPY services/prefect/config/ ./config/

# Create logs directory
RUN mkdir -p logs

# Set environment variables
ENV PREFECT_API_URL=http://prefect-server:4200/api
ENV PYTHONIOENCODING=utf-8

# Expose port (if needed for custom flows)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://prefect-server:4200/api/health', timeout=5)" || exit 1

# Default command - can be overridden in docker-compose
CMD ["python", "flows/ml_automation_flow.py"]
