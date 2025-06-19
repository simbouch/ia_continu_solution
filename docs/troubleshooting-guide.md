# 🔧 Troubleshooting Guide - IA Continu Solution

## 🎯 Overview

This guide provides solutions to common issues, debugging procedures, and maintenance tasks for the IA Continu Solution ML pipeline.

## 🚨 Common Issues & Solutions

### **1. Services Not Starting**

#### **Problem**: Docker containers fail to start
```bash
Error: Container exits immediately or fails to start
```

#### **Diagnosis**
```bash
# Check container logs
docker-compose logs [service-name]

# Check container status
docker-compose ps

# Check system resources
docker stats
```

#### **Solutions**
1. **Port Conflicts**
   ```bash
   # Check port usage
   netstat -tulpn | grep :8000
   
   # Solution: Change ports in docker-compose.yml
   ports:
     - "8001:8000"  # Change external port
   ```

2. **Memory Issues**
   ```bash
   # Check Docker memory limit
   docker system info | grep Memory
   
   # Solution: Increase Docker memory in Docker Desktop
   # Recommended: 8GB minimum, 16GB optimal
   ```

3. **Missing Environment Variables**
   ```bash
   # Check .env file exists
   ls -la .env
   
   # Solution: Copy and configure environment
   cp .env.example .env
   # Edit .env with your settings
   ```

### **2. Authentication Issues**

#### **Problem**: 403 Forbidden or 401 Unauthorized errors
```json
{"detail": "Could not validate credentials"}
```

#### **Solutions**
1. **Get Valid Token**
   ```bash
   # Login to get token
   curl -X POST "http://localhost:8000/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"username": "testuser", "password": "test123"}'
   ```

2. **Check Token Format**
   ```bash
   # Correct format
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   
   # Common mistake (missing "Bearer ")
   Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

3. **Token Expiration**
   ```bash
   # Tokens expire after 24 hours
   # Solution: Login again to get new token
   ```

### **3. Database Connection Issues**

#### **Problem**: SQLite database errors
```
sqlite3.OperationalError: database is locked
```

#### **Solutions**
1. **Database Lock**
   ```bash
   # Stop all services
   docker-compose down
   
   # Remove database lock
   rm -f data/app.db-wal data/app.db-shm
   
   # Restart services
   docker-compose up -d
   ```

2. **Database Corruption**
   ```bash
   # Backup current database
   cp data/app.db data/app.db.backup
   
   # Reset database (WARNING: loses data)
   rm data/app.db
   docker-compose restart api
   ```

### **4. MLflow Service Issues**

#### **Problem**: MLflow UI not accessible
```
Connection refused on port 5000
```

#### **Solutions**
1. **Check Service Status**
   ```bash
   # Check if MLflow container is running
   docker-compose ps mlflow
   
   # Check MLflow logs
   docker-compose logs mlflow
   ```

2. **Internal vs External Access**
   ```bash
   # MLflow works internally but external UI may have issues
   # This is expected - internal functionality works correctly
   
   # Test internal access
   curl http://localhost:5000/health
   ```

### **5. Prefect Automation Issues**

#### **Problem**: Prefect workflows not running
```
No flows executing or automation stopped
```

#### **Solutions**
1. **Check Prefect Service**
   ```bash
   # Check Prefect container
   docker-compose logs prefect
   
   # Restart Prefect service
   docker-compose restart prefect
   ```

2. **Verify Flow Registration**
   ```bash
   # Access Prefect container
   docker exec -it ia_continu_solution-prefect-1 bash
   
   # Check registered flows
   prefect flow ls
   ```

### **6. Discord Notifications Not Working**

#### **Problem**: No Discord notifications received
```
Discord webhook calls failing
```

#### **Solutions**
1. **Check Webhook URL**
   ```bash
   # Verify webhook URL in .env
   cat .env | grep DISCORD_WEBHOOK_URL
   
   # Test webhook manually
   curl -X POST "YOUR_WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d '{"content": "Test message"}'
   ```

2. **Check Service Logs**
   ```bash
   # Check monitoring service logs
   docker-compose logs monitoring
   
   # Look for Discord-related errors
   ```

### **7. Streamlit UI Issues**

#### **Problem**: Streamlit interface not loading
```
Streamlit app shows errors or won't load
```

#### **Solutions**
1. **Check Dependencies**
   ```bash
   # Check Streamlit logs
   docker-compose logs streamlit
   
   # Look for missing package errors
   ```

2. **Authentication Issues**
   ```bash
   # Use default credentials
   Username: testuser
   Password: test123
   
   # Or try admin credentials
   Username: admin
   Password: admin123
   ```

## 🔍 Debugging Procedures

### **Health Check Sequence**
```bash
# 1. Check all services
docker-compose ps

# 2. Test API health
curl http://localhost:8000/health

# 3. Test authentication
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "test123"}'

# 4. Test prediction (with token from step 3)
curl -X POST "http://localhost:8000/predict" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"features": [0.5, 0.5]}'

# 5. Check monitoring services
curl http://localhost:3001  # Uptime Kuma
curl http://localhost:9090  # Prometheus
curl http://localhost:3000  # Grafana
```

### **Log Analysis**
```bash
# View all service logs
docker-compose logs

# View specific service logs
docker-compose logs api
docker-compose logs mlflow
docker-compose logs prefect
docker-compose logs monitoring
docker-compose logs streamlit

# Follow logs in real-time
docker-compose logs -f api

# View last 50 lines
docker-compose logs --tail=50 api
```

### **Performance Debugging**
```bash
# Check resource usage
docker stats

# Check disk usage
df -h
docker system df

# Check network connectivity
docker network ls
docker network inspect ia_continu_solution_default
```

## 🛠️ Maintenance Tasks

### **Regular Maintenance**
```bash
# 1. Update Docker images (weekly)
docker-compose pull
docker-compose up -d

# 2. Clean up unused resources (weekly)
docker system prune -f

# 3. Backup database (daily)
cp data/app.db backups/app_$(date +%Y%m%d).db

# 4. Check log sizes (weekly)
du -sh logs/
```

### **Database Maintenance**
```bash
# Vacuum SQLite database
sqlite3 data/app.db "VACUUM;"

# Check database integrity
sqlite3 data/app.db "PRAGMA integrity_check;"

# Backup database
sqlite3 data/app.db ".backup backups/app_backup.db"
```

### **Performance Optimization**
```bash
# 1. Clean up old Docker images
docker image prune -a

# 2. Restart services to clear memory
docker-compose restart

# 3. Check for resource leaks
docker stats --no-stream

# 4. Monitor disk space
df -h
```

## 🔧 Configuration Issues

### **Environment Variables**
```bash
# Check all environment variables
docker-compose config

# Verify specific variables
echo $DISCORD_WEBHOOK_URL
echo $MLFLOW_TRACKING_URI
```

### **Port Configuration**
```yaml
# Common port conflicts and solutions
services:
  api:
    ports:
      - "8001:8000"  # Change if 8000 is in use
  
  streamlit:
    ports:
      - "8502:8501"  # Change if 8501 is in use
  
  mlflow:
    ports:
      - "5001:5000"  # Change if 5000 is in use
```

### **Volume Mounting Issues**
```bash
# Check volume permissions
ls -la data/
ls -la logs/

# Fix permissions if needed
sudo chown -R $USER:$USER data/
sudo chown -R $USER:$USER logs/
```

## 🚨 Emergency Procedures

### **Complete System Reset**
```bash
# WARNING: This will delete all data
docker-compose down -v
docker system prune -a -f
rm -rf data/ logs/
mkdir -p data logs
docker-compose up -d
```

### **Service Recovery**
```bash
# Restart single service
docker-compose restart api

# Rebuild and restart service
docker-compose up -d --build api

# Force recreate service
docker-compose up -d --force-recreate api
```

### **Data Recovery**
```bash
# Restore from backup
cp backups/app_backup.db data/app.db
docker-compose restart api

# Check data integrity after restore
curl http://localhost:8000/health
```

## 📊 Monitoring & Alerts

### **Key Metrics to Monitor**
- **API Response Time**: Should be < 100ms
- **Memory Usage**: Should be < 80% per container
- **Disk Space**: Should have > 1GB free
- **Error Rate**: Should be < 1% of requests

### **Alert Thresholds**
```yaml
Critical:
  - API down for > 1 minute
  - Memory usage > 90%
  - Disk space < 500MB
  - Error rate > 5%

Warning:
  - API response time > 500ms
  - Memory usage > 80%
  - Disk space < 1GB
  - Error rate > 1%
```

## 📞 Getting Help

### **Log Collection for Support**
```bash
# Collect all logs
mkdir support_logs
docker-compose logs > support_logs/all_services.log
docker-compose ps > support_logs/service_status.txt
docker stats --no-stream > support_logs/resource_usage.txt
docker system info > support_logs/docker_info.txt

# Create support package
tar -czf support_package_$(date +%Y%m%d).tar.gz support_logs/
```

### **System Information**
```bash
# Collect system information
echo "=== System Info ===" > system_info.txt
uname -a >> system_info.txt
docker --version >> system_info.txt
docker-compose --version >> system_info.txt
free -h >> system_info.txt
df -h >> system_info.txt
```

### **Common Support Questions**
1. **What version are you running?** Check `docker-compose.yml` version
2. **What error messages do you see?** Provide full error logs
3. **When did the issue start?** Check service restart times
4. **What changed recently?** Review recent configuration changes

---

**Troubleshooting Guide Version**: 1.0.0  
**Last Updated**: June 19, 2025  
**Support**: Check logs and follow procedures above
