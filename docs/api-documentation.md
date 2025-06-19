# 📚 API Documentation - IA Continu Solution

## 🎯 Overview

The IA Continu Solution provides a comprehensive RESTful API for machine learning operations, authentication, and system monitoring. This documentation covers all available endpoints, authentication methods, and usage examples.

## 🔐 Authentication

### **JWT Token Authentication**
All protected endpoints require a valid JWT token in the Authorization header.

#### **Login Endpoint**
```http
POST /auth/login
Content-Type: application/json

{
    "username": "testuser",
    "password": "test123"
}
```

**Response:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 86400
}
```

#### **Using the Token**
Include the token in the Authorization header for all protected endpoints:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### **Default Users**
| Username | Password | Role | Permissions |
|----------|----------|------|-------------|
| `admin` | `admin123` | Administrator | Full access to all endpoints |
| `testuser` | `test123` | Standard User | Predictions and basic operations |

## 🏥 Health & Status Endpoints

### **Health Check**
```http
GET /health
```

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2025-06-19T14:30:22Z",
    "services": {
        "database": true,
        "ml_model": true,
        "monitoring": true
    },
    "metrics": {
        "uptime": 3600,
        "memory_usage": "45%",
        "active_connections": 5
    }
}
```

### **Model Information**
```http
GET /model/info
Authorization: Bearer <token>
```

**Response:**
```json
{
    "model_version": "v20250619_143022",
    "model_loaded": true,
    "model_type": "LogisticRegression",
    "accuracy": 0.997,
    "training_samples": 1000,
    "timestamp": "2025-06-19T14:30:22Z"
}
```

## 🤖 Machine Learning Endpoints

### **Make Predictions**
```http
POST /predict
Authorization: Bearer <token>
Content-Type: application/json

{
    "features": [0.5, 0.5]
}
```

**Response:**
```json
{
    "prediction": 1,
    "confidence": 0.987,
    "model_version": "v20250619_143022",
    "timestamp": "2025-06-19T14:30:22Z"
}
```

**Parameters:**
- `features` (array): Array of numerical features for prediction
  - Must contain exactly 2 numerical values
  - Values should be normalized between -3 and 3 for optimal performance

**Response Fields:**
- `prediction` (integer): Predicted class (0 or 1)
- `confidence` (float): Prediction confidence score (0.0 to 1.0)
- `model_version` (string): Version of the model used for prediction
- `timestamp` (string): ISO timestamp of the prediction

### **Generate Training Data**
```http
POST /generate
Authorization: Bearer <token>
Content-Type: application/json

{
    "samples": 1000
}
```

**Response:**
```json
{
    "status": "success",
    "generation_id": "gen_20250619_143022",
    "samples_created": 1000,
    "timestamp": "2025-06-19T14:30:22Z",
    "dataset_info": {
        "feature1_mean": 0.05,
        "feature2_mean": -0.02,
        "class_distribution": {
            "class_0": 487,
            "class_1": 513
        }
    }
}
```

**Parameters:**
- `samples` (integer): Number of samples to generate (default: 1000, max: 10000)

## 👤 Authentication Endpoints

### **User Login**
```http
POST /auth/login
Content-Type: application/json

{
    "username": "testuser",
    "password": "test123"
}
```

### **User Logout**
```http
POST /auth/logout
Authorization: Bearer <token>
```

**Response:**
```json
{
    "message": "Successfully logged out"
}
```

### **Current User Info**
```http
GET /auth/me
Authorization: Bearer <token>
```

**Response:**
```json
{
    "username": "testuser",
    "role": "user",
    "permissions": ["read", "write"],
    "created_at": "2025-06-19T10:00:00Z",
    "last_login": "2025-06-19T14:30:22Z"
}
```

### **List Users (Admin Only)**
```http
GET /auth/users
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
    "users": [
        {
            "username": "admin",
            "role": "admin",
            "created_at": "2025-06-19T10:00:00Z",
            "last_login": "2025-06-19T14:25:00Z"
        },
        {
            "username": "testuser", 
            "role": "user",
            "created_at": "2025-06-19T10:00:00Z",
            "last_login": "2025-06-19T14:30:22Z"
        }
    ],
    "total": 2
}
```

## 📊 Data Management Endpoints

### **List Datasets**
```http
GET /datasets/list
Authorization: Bearer <token>
```

**Response:**
```json
{
    "datasets": [
        {
            "generation_id": "gen_20250619_143022",
            "samples_count": 1000,
            "created_at": "2025-06-19T14:30:22Z",
            "hour_generated": 14
        }
    ],
    "total_datasets": 1
}
```

### **Prediction History**
```http
GET /predictions/history?limit=50
Authorization: Bearer <token>
```

**Response:**
```json
{
    "predictions": [
        {
            "id": 1,
            "features": [0.5, 0.5],
            "prediction": 1,
            "confidence": 0.987,
            "model_version": "v20250619_143022",
            "timestamp": "2025-06-19T14:30:22Z",
            "user": "testuser"
        }
    ],
    "total": 1
}
```

## 📈 Monitoring Endpoints

### **Prediction Statistics**
```http
GET /predictions/stats
Authorization: Bearer <token>
```

**Response:**
```json
{
    "total_predictions": 150,
    "average_confidence": 0.94,
    "class_distribution": {
        "class_0": 73,
        "class_1": 77
    },
    "daily_predictions": 45,
    "model_performance": {
        "current_accuracy": 0.997,
        "last_training": "2025-06-19T14:30:22Z"
    }
}
```

### **Training History**
```http
GET /training/history?limit=10
Authorization: Bearer <token>
```

**Response:**
```json
{
    "trainings": [
        {
            "model_version": "v20250619_143022",
            "accuracy": 0.997,
            "training_samples": 1000,
            "training_duration": 1.23,
            "timestamp": "2025-06-19T14:30:22Z"
        }
    ],
    "total": 1
}
```

## ⚠️ Error Handling

### **Standard Error Response**
```json
{
    "detail": "Error description",
    "error_code": "VALIDATION_ERROR",
    "timestamp": "2025-06-19T14:30:22Z"
}
```

### **Common HTTP Status Codes**
- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

### **Authentication Errors**
```json
{
    "detail": "Could not validate credentials",
    "error_code": "INVALID_TOKEN",
    "timestamp": "2025-06-19T14:30:22Z"
}
```

### **Validation Errors**
```json
{
    "detail": [
        {
            "loc": ["body", "features"],
            "msg": "ensure this value has at least 2 items",
            "type": "value_error.list.min_items"
        }
    ],
    "error_code": "VALIDATION_ERROR"
}
```

## 🔧 Usage Examples

### **Python Client Example**
```python
import requests

# Authentication
login_response = requests.post(
    "http://localhost:8000/auth/login",
    json={"username": "testuser", "password": "test123"}
)
token = login_response.json()["access_token"]

# Headers for authenticated requests
headers = {"Authorization": f"Bearer {token}"}

# Make a prediction
prediction_response = requests.post(
    "http://localhost:8000/predict",
    json={"features": [0.5, 0.5]},
    headers=headers
)
prediction = prediction_response.json()
print(f"Prediction: {prediction['prediction']}, Confidence: {prediction['confidence']}")

# Generate training data
generate_response = requests.post(
    "http://localhost:8000/generate",
    json={"samples": 1000},
    headers=headers
)
dataset = generate_response.json()
print(f"Generated {dataset['samples_created']} samples")
```

### **cURL Examples**
```bash
# Login
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "test123"}'

# Make prediction (replace TOKEN with actual token)
curl -X POST "http://localhost:8000/predict" \
     -H "Authorization: Bearer TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"features": [0.5, 0.5]}'

# Check health
curl -X GET "http://localhost:8000/health"
```

## 📝 Rate Limiting

### **Current Limits**
- **Authentication**: 10 requests per minute per IP
- **Predictions**: 100 requests per minute per user
- **Data Generation**: 5 requests per minute per user
- **Other Endpoints**: 60 requests per minute per user

### **Rate Limit Headers**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## 🔒 Security Considerations

### **Best Practices**
1. **Token Security**: Store JWT tokens securely, never in plain text
2. **HTTPS**: Use HTTPS in production environments
3. **Token Expiration**: Tokens expire after 24 hours, implement refresh logic
4. **Input Validation**: Always validate input data before sending requests
5. **Error Handling**: Implement proper error handling for all API calls

### **Production Deployment**
- Use environment variables for sensitive configuration
- Implement proper logging and monitoring
- Set up rate limiting and DDoS protection
- Use a reverse proxy (nginx/traefik) for SSL termination
- Implement proper backup and disaster recovery procedures

---

**API Version**: v1.0.0  
**Documentation Updated**: June 19, 2025  
**Base URL**: http://localhost:8000  
**Interactive Documentation**: http://localhost:8000/docs
