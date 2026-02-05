# ⚡ Quick Reference - FastAPI Backend Commands

## 🚀 Start/Stop Backend

### Start Server
```bash
cd /media/magesh/NewVolume2/Projects/Python/AppDemo/Comp_visn/backend
source benv/bin/activate
python run.py
```

### Stop Server
```bash
Ctrl + C
```

## 📍 Important URLs

| URL | Purpose |
|-----|---------|
| `http://localhost:8000` | API Base URL |
| `http://localhost:8000/docs` | Swagger UI (Interactive API Docs) |
| `http://localhost:8000/redoc` | ReDoc (Alternative API Docs) |
| `http://localhost:8000/health` | Health Check |

## 🔑 Default Configuration

```env
API_KEY=your-api-key-change-this
SECRET_KEY=your-secret-key-change-this
MONGO_DB_URL=mongodb://127.0.0.1:27017
API_PORT=8000
```

**Located at:** `/Comp_Visn/backend/.env`

## 💻 Most Used API Calls

### 1. Save Recognition (From recognize2.py)
```bash
curl -X POST "http://localhost:8000/api/v1/recognition/save" \
  -H "X-API-Key: your-api-key-change-this" \
  -H "Content-Type: application/json" \
  -d '{
    "person_name": "John Doe",
    "camera_id": "camera_01",
    "confidence_score": 0.95
  }'
```

Response:
```json
{
  "success": true,
  "log_id": "507f1f77bcf86cd799439011",
  "message": "Recognition saved successfully"
}
```

### 2. Get All Logs
```bash
curl -X GET "http://localhost:8000/api/v1/recognition/logs?skip=0&limit=10" \
  -H "X-API-Key: your-api-key-change-this"
```

### 3. Filter Logs
```bash
curl -X GET "http://localhost:8000/api/v1/recognition/filter?person_name=John&camera_id=camera_01" \
  -H "X-API-Key: your-api-key-change-this"
```

### 4. Update Log
```bash
curl -X PUT "http://localhost:8000/api/v1/recognition/logs/{log_id}" \
  -H "X-API-Key: your-api-key-change-this" \
  -H "Content-Type: application/json" \
  -d '{
    "person_name": "Jane Doe"
  }'
```

### 5. Delete Log
```bash
curl -X DELETE "http://localhost:8000/api/v1/recognition/logs/{log_id}" \
  -H "X-API-Key: your-api-key-change-this"
```

## 🐍 Python API Client Usage

### Setup
```python
from app.utils.client import RecognitionAPIClient

client = RecognitionAPIClient(
    base_url="http://localhost:8000",
    api_key="your-api-key-change-this"
)
```

### Save Recognition
```python
result = client.save_recognition("John Doe", "camera_01", 0.95)
print(result)  # {'success': True, 'log_id': '...'}
```

### Get Logs
```python
logs = client.get_all_logs(skip=0, limit=10)
print(logs['logs'])  # List of recognition logs
```

### Filter
```python
filtered = client.filter_logs(
    person_name="John",
    camera_id="camera_01",
    skip=0,
    limit=50
)
```

### Delete
```python
result = client.delete_log(log_id)
print(result['success'])  # True/False
```

## 📊 Database Queries (MongoDB)

### Connect to MongoDB
```bash
mongosh
```

### View All Recognition Logs
```javascript
use face_recognition_db
db.recognition_logs.find()
```

### Find Logs for Specific Person
```javascript
db.recognition_logs.find({ person_name: "John Doe" })
```

### Count Total Recognitions
```javascript
db.recognition_logs.countDocuments()
```

### Find Logs from Last 24 Hours
```javascript
db.recognition_logs.find({
  timestamp: { $gte: new Date(Date.now() - 24 * 60 * 60 * 1000) }
})
```

### View Detection Counts
```javascript
db.recognition_logs.find({}, { person_name: 1, detection_count: 1 })
```

## 🔧 Troubleshooting

### Backend won't start - Port already in use
```bash
# Find process on port 8000
lsof -i :8000

# Kill it
kill -9 <PID>
```

### MongoDB connection error
```bash
# Check if MongoDB is running
mongosh

# If not, start MongoDB service
sudo systemctl start mongod  # Linux
brew services start mongodb-community  # macOS
```

### API Key authentication failing
1. Check `.env` file has `API_KEY` set
2. Verify `X-API-Key` header matches exactly
3. No spaces before/after the key value

### Can't find backend module in recognize2.py
```python
import sys
sys.path.insert(0, '/media/magesh/NewVolume2/Projects/Python/AppDemo/Comp_visn/backend')
```

## 📝 File Locations Reference

| Item | Location |
|------|----------|
| Backend Root | `/media/magesh/NewVolume2/Projects/Python/AppDemo/Comp_visn/backend/` |
| Virtual Env | `/media/magesh/NewVolume2/Projects/Python/AppDemo/Comp_visn/backend/benv/` |
| Config File | `/media/magesh/NewVolume2/Projects/Python/AppDemo/Comp_visn/backend/.env` |
| Main App | `/media/magesh/NewVolume2/Projects/Python/AppDemo/Comp_visn/backend/app/main.py` |
| Entry Point | `/media/magesh/NewVolume2/Projects/Python/AppDemo/Comp_visn/backend/run.py` |
| API Routes | `/media/magesh/NewVolume2/Projects/Python/AppDemo/Comp_visn/backend/app/api/v1/` |
| Recognize2 | `/media/magesh/NewVolume2/Projects/Python/AppDemo/Comp_visn/face_recognition/recognize2.py` |
| Recognize2 (API) | `/media/magesh/NewVolume2/Projects/Python/AppDemo/Comp_visn/face_recognition/recognize2_with_api.py` |

## 🎯 Integration Checklist

- [ ] Backend started and running on port 8000
- [ ] Can access `http://localhost:8000/docs`
- [ ] MongoDB is running and accessible
- [ ] Updated `API_KEY` in `.env` (if needed)
- [ ] Updated `API_KEY` in recognize2.py (must match)
- [ ] recognize2.py successfully imports `RecognitionAPIClient`
- [ ] Test API call from recognize2.py
- [ ] Verify data appears in MongoDB `recognition_logs` collection
- [ ] Test filtering logs via API

## 🐛 Enable Debug Logging

Edit `.env`:
```env
LOG_LEVEL=DEBUG
```

Then restart backend:
```bash
python run.py
```

## 🔍 Monitor MongoDB in Real-Time

```bash
# Terminal 1 - Start watch on collection
mongosh
use face_recognition_db
db.recognition_logs.watch()

# Terminal 2 - Send recognition data from recognize2.py
# You'll see inserts/updates in real-time in Terminal 1
```

## ⏱️ Test 1-Hour Cooldown Logic

```python
from app.utils.client import RecognitionAPIClient

client = RecognitionAPIClient(...)

# First call - creates new log
result1 = client.save_recognition("John", "cam_01", 0.95)
log_id = result1['log_id']

# Get the log - detection_count should be 1
log = client.get_log(log_id)
print(log['detection_count'])  # 1

# Second call within 1 hour - updates same log
result2 = client.save_recognition("John", "cam_01", 0.98)
print(result2['log_id'] == log_id)  # True (same log)

# Check log again - detection_count should be 2
log = client.get_log(log_id)
print(log['detection_count'])  # 2
```

## 📦 Virtual Environment Management

### Activate
```bash
source /Comp_Visn/backend/benv/bin/activate
```

### Deactivate
```bash
deactivate
```

### Check Python Version
```bash
python --version
```

### List Installed Packages
```bash
pip list
```

## 🚨 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'fastapi'` | Activate venv: `source benv/bin/activate` |
| `Connection refused: 27017` | Start MongoDB: `mongosh` |
| `Port 8000 already in use` | Kill process: `lsof -i :8000 \| kill` |
| `API Key invalid` | Check `.env` and request header match |
| `CORS error` | Backend not running or wrong URL |
| `No module named 'app'` | Add to sys.path in recognize2.py |

## 📚 API Endpoint Summary

```
POST   /api/v1/auth/register              # Register user
POST   /api/v1/auth/login                 # Login user

POST   /api/v1/recognition/save           # Save recognition (1h cooldown)
GET    /api/v1/recognition/logs           # Get all logs
GET    /api/v1/recognition/filter         # Filter logs
GET    /api/v1/recognition/logs/{id}      # Get single log
PUT    /api/v1/recognition/logs/{id}      # Update log
DELETE /api/v1/recognition/logs/{id}      # Delete log

GET    /health                            # Health check
GET    /                                  # Root endpoint
```

---

**Last Updated:** January 22, 2026  
**Backend Version:** 1.0.0
