FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY services/streamlit/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Streamlit application
COPY services/streamlit/app/ ./app/
COPY services/streamlit/config/ ./config/

# Create logs directory
RUN mkdir -p logs

# Set environment variables
ENV API_URL=http://api:8000
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Expose Streamlit port
EXPOSE 8501

# Health check (removed curl dependency)
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8501/_stcore/health', timeout=5)" || exit 1

# Run Streamlit
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
