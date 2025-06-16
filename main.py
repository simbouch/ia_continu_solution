from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import requests
import logging
import os
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="IA Continu Solution API",
    description="FastAPI application with monitoring and notification capabilities",
    version="1.0.0"
)

def send_discord_embed(message: str, status: str = "Succès") -> None:
    """Send a notification to Discord via Webhook when API status changes."""
    DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
    
    if not DISCORD_WEBHOOK_URL:
        logger.warning("Discord webhook URL not configured")
        return
    
    # Color mapping for different statuses
    color_map = {
        "Succès": 5814783,  # Green
        "Erreur": 15158332,  # Red
        "Avertissement": 16776960,  # Yellow
        "Info": 3447003  # Blue
    }
    
    data = {
        "embeds": [{
            "title": "Résultats du pipeline",
            "description": message,
            "color": color_map.get(status, 3447003),
            "fields": [{
                "name": "Status",
                "value": status,
                "inline": True
            }, {
                "name": "Timestamp",
                "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "inline": True
            }],
            "footer": {
                "text": "IA Continu Solution"
            }
        }]
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data, timeout=30)
        if response.status_code != 204:
            logger.error(f"Erreur lors de l'envoi de l'embed : {response.status_code}")
        else:
            logger.info("Embed envoyé avec succès !")
    except requests.RequestException as e:
        logger.error(f"Erreur de connexion Discord : {e}")

@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint returning basic API information."""
    return {
        "message": "IA Continu Solution API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint for monitoring services."""
    try:
        # Perform basic health checks here
        # You can add database connectivity, external service checks, etc.
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "checks": {
                "api": "ok",
                "database": "ok",  # Add actual database check if needed
                "external_services": "ok"  # Add actual external service checks if needed
            }
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.post("/notify")
async def send_notification(message: str, status: str = "Info") -> Dict[str, str]:
    """Endpoint to send notifications via Discord webhook."""
    try:
        send_discord_embed(message, status)
        return {"message": "Notification sent successfully"}
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to send notification")

@app.get("/status")
async def get_status() -> Dict[str, Any]:
    """Get detailed application status."""
    return {
        "application": "IA Continu Solution",
        "status": "running",
        "uptime": "Available",  # You can implement actual uptime calculation
        "environment": os.getenv("ENVIRONMENT", "development"),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
