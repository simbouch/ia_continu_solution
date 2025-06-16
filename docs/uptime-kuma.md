# Uptime Kuma Integration Guide

This guide explains how to set up Uptime Kuma for monitoring your IA Continu Solution.

## 🚀 Quick Setup

### 1. Start Uptime Kuma with Docker Compose

Add Uptime Kuma to your `docker-compose.yml`:

```yaml
services:
  # ... existing services ...
  
  uptime-kuma:
    image: louislam/uptime-kuma:latest
    container_name: uptime_kuma
    ports:
      - "3001:3001"
    volumes:
      - uptime-kuma-data:/app/data
    restart: unless-stopped
    depends_on:
      - app
    networks:
      - monitoring-network

volumes:
  uptime-kuma-data:
    driver: local
```

### 2. Start the Service

```bash
docker-compose up -d uptime-kuma
```

### 3. Access Uptime Kuma

Open http://localhost:3001 in your browser.

## ⚙️ Configuration

### Initial Setup

1. **Create Admin Account**
   - Username: admin
   - Password: (choose a secure password)
   - Email: your-email@domain.com

2. **Configure Settings**
   - Go to Settings → General
   - Set your timezone
   - Configure notification preferences

### Add IA Continu Solution Monitor

1. **Click "Add New Monitor"**

2. **Configure Monitor Settings**:
   ```
   Monitor Type: HTTP(s)
   Friendly Name: IA Continu Solution API
   URL: http://fastapi_app:9000/health
   Heartbeat Interval: 30 seconds
   Max Retries: 3
   Max Redirects: 10
   Accepted Status Codes: 200-299
   ```

3. **Advanced Settings**:
   ```
   Request Timeout: 10 seconds
   Request Headers: 
     User-Agent: Uptime-Kuma/1.0
   ```

4. **Save Monitor**

## 📊 Dashboard Configuration

### Status Page Setup

1. **Create Status Page**
   - Go to Status Pages
   - Click "New Status Page"
   - Name: "IA Continu Solution Status"

2. **Add Monitors**
   - Add your API monitor
   - Configure display settings
   - Set custom domain (optional)

3. **Customize Appearance**
   - Logo: Upload your logo
   - Theme: Choose light/dark theme
   - Custom CSS: Add custom styling

### Notification Setup

1. **Discord Integration**
   ```
   Notification Type: Discord
   Discord Webhook URL: your_webhook_url
   Username: Uptime Kuma
   ```

2. **Email Notifications**
   ```
   Notification Type: SMTP Email
   Hostname: your-smtp-server.com
   Port: 587
   Security: STARTTLS
   Username: your-email@domain.com
   Password: your-app-password
   ```

3. **Test Notifications**
   - Click "Test" to verify setup
   - Check Discord/Email for test message

## 🔧 Advanced Configuration

### Custom Health Check Endpoint

Create a detailed health check in your FastAPI app:

```python
@app.get("/health/detailed")
async def detailed_health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "database": "connected",
            "external_api": "responsive",
            "discord_webhook": "configured"
        },
        "metrics": {
            "response_time": "< 100ms",
            "memory_usage": "normal",
            "cpu_usage": "normal"
        }
    }
```

### Multiple Monitor Setup

1. **API Health Monitor**
   - URL: http://fastapi_app:9000/health
   - Interval: 30 seconds

2. **API Response Time Monitor**
   - URL: http://fastapi_app:9000/
   - Interval: 60 seconds
   - Check response time

3. **Discord Webhook Monitor**
   - URL: http://fastapi_app:9000/notify?message=test&status=Info
   - Method: POST
   - Interval: 300 seconds (5 minutes)

### Maintenance Mode

1. **Schedule Maintenance**
   - Go to Maintenance
   - Set start/end times
   - Add description
   - Notify users

2. **Pause Monitoring**
   - Temporarily disable alerts
   - Resume after maintenance

## 📈 Monitoring Best Practices

### Alert Thresholds

- **Response Time**: Alert if > 5 seconds
- **Uptime**: Alert if < 99.9%
- **Consecutive Failures**: Alert after 3 failures

### Notification Strategy

1. **Immediate Alerts**: Critical failures
2. **Escalation**: After 5 minutes of downtime
3. **Recovery Notifications**: When service restored

### Data Retention

- **Statistics**: Keep 1 year of data
- **Logs**: Keep 30 days
- **Heartbeats**: Keep 90 days

## 🔍 Troubleshooting

### Common Issues

1. **Monitor Shows Down but Service is Up**
   - Check network connectivity between containers
   - Verify URL is accessible from Uptime Kuma container
   - Check firewall settings

2. **Notifications Not Working**
   - Test webhook URL manually
   - Check notification settings
   - Verify Discord permissions

3. **High False Positives**
   - Increase retry count
   - Adjust timeout settings
   - Check network stability

### Debug Commands

```bash
# Check Uptime Kuma logs
docker logs uptime_kuma

# Test connectivity from Uptime Kuma container
docker exec uptime_kuma wget -O- http://fastapi_app:9000/health

# Check network connectivity
docker network ls
docker network inspect monitoring-network
```

## 🚀 Production Deployment

### Security Considerations

1. **Use HTTPS**
   - Configure SSL certificates
   - Use reverse proxy (nginx/traefik)

2. **Authentication**
   - Enable 2FA for admin account
   - Use strong passwords
   - Regular password rotation

3. **Network Security**
   - Use private networks
   - Restrict access to admin interface
   - Configure firewall rules

### Backup Strategy

```bash
# Backup Uptime Kuma data
docker run --rm -v uptime-kuma-data:/data -v $(pwd):/backup alpine \
  tar czf /backup/uptime-kuma-backup.tar.gz -C /data .

# Restore from backup
docker run --rm -v uptime-kuma-data:/data -v $(pwd):/backup alpine \
  tar xzf /backup/uptime-kuma-backup.tar.gz -C /data
```

### Performance Optimization

1. **Resource Limits**
   ```yaml
   uptime-kuma:
     deploy:
       resources:
         limits:
           memory: 512M
           cpus: '0.5'
   ```

2. **Database Optimization**
   - Regular cleanup of old data
   - Optimize heartbeat intervals
   - Monitor disk usage

## 📚 Additional Resources

- [Uptime Kuma Documentation](https://github.com/louislam/uptime-kuma)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Discord Webhook Guide](https://support.discord.com/hc/en-us/articles/228383668)
