# FastAPI Backend Setup & Usage Guide

## Project Summary

A complete FastAPI backend has been created at `/Comp_Visn/backend/` with the following features:

- ✅ **MVC + Layered Architecture** (Controllers → Services → Repositories → DB)
- ✅ **MongoDB Integration** with 1-hour cooldown detection
- ✅ **JWT & API Key Authentication**
- ✅ **Comprehensive REST APIs** for CRUD operations
- ✅ **Separate Virtual Environment** (benv)
- ✅ **Ready for Integration** with recognize2.py

## Directory Structure

```
/Comp_Visn/
├── face_recognition/          # Your existing face recognition code
│   ├── recognize2.py          # Original version
│   ├── recognize2_with_api.py # NEW: Version with API integration
│   └── ... (other files)
│
└── backend/                   # NEW: FastAPI Backend
    ├── benv/                  # Virtual environment
    ├── app/
    │   ├── api/v1/
    │   │   ├── auth.py       # Authentication endpoints
    │   │   └── recognition.py # Recognition endpoints
    │   ├── controllers/       # Business logic layer
    │   ├── services/          # Service layer (with 1-hour cooldown)
    │   ├── repositories/      # Data access layer
    │   ├── models/            # Pydantic models
    │   ├── schemas/           # MongoDB schemas
    │   ├── middleware/        # Auth middleware
    │   ├── utils/             # Utilities & client
    │   ├── config.py          # Configuration
    │   └── main.py            # FastAPI app
    ├── .env                   # Environment variables
    ├── .env.example           # Example env file
    ├── requirements.txt       # Python dependencies
    ├── run.py                 # Entry point
    ├── README.md              # API documentation
    ├── INTEGRATION_GUIDE.md   # How to integrate with recognize2.py
    └── SETUP.md              # This file
```

## Quick Start (5 minutes)

### 1️⃣ Start MongoDB (if not running)

```bash
mongosh  # or mongodb-compass
```

### 2️⃣ Start the Backend

```bash
cd /media/magesh/NewVolume2/Projects/Python/AppDemo/Comp_visn/backend
source benv/bin/activate
python run.py
```

Output should show:
```
INFO:     Application startup complete
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
```

### 3️⃣ Test the API

Open browser: http://localhost:8000/docs

You should see the Swagger UI with all endpoints.

### 4️⃣ Update recognize2.py

Use the provided `recognize2_with_api.py` as a template:

```bash
# Option 1: Use the new version directly
cp recognize2_with_api.py recognize2.py

# Option 2: Or manually integrate as shown in INTEGRATION_GUIDE.md
```

## Configuration

### Environment Variables (.env)

Edit `/backend/.env`:

```env
# MongoDB
MONGO_DB_URL=mongodb://127.0.0.1:27017
MONGO_DB_NAME=face_recognition_db

# API
API_HOST=0.0.0.0
API_PORT=8000
API_ENV=development

# JWT (Change these in production!)
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# API Key (Used by recognize2.py)
API_KEY=your-api-key-change-this

# Logging
LOG_LEVEL=INFO
```

## Architecture Overview

### Layered Architecture

```
┌─────────────────────────────────────────┐
│         API Layer (/api/v1)             │
│   (HTTP Endpoints - auth & recognition) │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│    Controller Layer (/controllers)      │
│   (Request handling & validation)       │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│      Service Layer (/services)          │
│  (Business logic - 1-hour cooldown)     │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│    Repository Layer (/repositories)     │
│      (Data access - MongoDB)            │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│         MongoDB Database                │
│   (Collections: recognition_logs,       │
│    users, api_keys)                     │
└─────────────────────────────────────────┘
```

### Data Flow

**Saving a Recognition:**
```
recognize2.py 
  ↓ (HTTP POST with API Key)
Recognition API Endpoint (/api/v1/recognition/save)
  ↓
RecognitionController.save_recognition()
  ↓
RecognitionService.save_recognition()
  ↓ (Checks 1-hour cooldown)
RecognitionRepository.create_or_update_log()
  ↓
MongoDB (recognition_logs collection)
```

## API Endpoints

### Authentication

```bash
# Register User
POST /api/v1/auth/register
{
  "username": "admin",
  "password": "securepass123"
}

# Login
POST /api/v1/auth/login
{
  "username": "admin",
  "password": "securepass123"
}
```

### Recognition (Requires X-API-Key header)

```bash
# Save Recognition (1-hour cooldown applied)
POST /api/v1/recognition/save
Headers: X-API-Key: your-api-key
{
  "person_name": "John Doe",
  "camera_id": "camera_01",
  "confidence_score": 0.95
}

# Get All Logs
GET /api/v1/recognition/logs?skip=0&limit=10
Headers: X-API-Key: your-api-key

# Filter Logs
GET /api/v1/recognition/filter?person_name=John&camera_id=camera_01
Headers: X-API-Key: your-api-key

# Get Single Log
GET /api/v1/recognition/logs/{log_id}
Headers: X-API-Key: your-api-key

# Update Log
PUT /api/v1/recognition/logs/{log_id}
Headers: X-API-Key: your-api-key
{
  "person_name": "Jane Doe"
}

# Delete Log
DELETE /api/v1/recognition/logs/{log_id}
Headers: X-API-Key: your-api-key
```

## 1-Hour Cooldown Logic

When `save_recognition()` is called:

1. ✅ Query MongoDB for existing log:
   - Same person_name
   - Same camera_id
   - last_detection_time within last 1 hour

2. ✅ If found:
   - Increment `detection_count` by 1
   - Update `last_detection_time` to now
   - Return same log_id

3. ✅ If not found:
   - Create new document
   - Set `detection_count` = 1
   - Set `timestamp` and `last_detection_time` to now
   - Return new log_id

**Example:**
```
Time 1: John detected at camera_01 → Create log (detection_count=1)
Time 2: John detected at camera_01 (40 min later) → Update log (detection_count=2)
Time 3: John detected at camera_01 (70 min later) → Create new log (cooldown expired)
```

## Testing the API

### Using cURL

```bash
# Save recognition
curl -X POST "http://localhost:8000/api/v1/recognition/save" \
  -H "X-API-Key: your-api-key-change-this" \
  -H "Content-Type: application/json" \
  -d '{
    "person_name": "John Doe",
    "camera_id": "camera_01",
    "confidence_score": 0.95
  }'

# Get logs
curl -X GET "http://localhost:8000/api/v1/recognition/logs?skip=0&limit=10" \
  -H "X-API-Key: your-api-key-change-this"

# Filter logs
curl -X GET "http://localhost:8000/api/v1/recognition/filter?person_name=John" \
  -H "X-API-Key: your-api-key-change-this"
```

### Using Python

```python
from app.utils.client import RecognitionAPIClient

client = RecognitionAPIClient(
    base_url="http://localhost:8000",
    api_key="your-api-key-change-this"
)

# Save recognition
result = client.save_recognition("John Doe", "camera_01", 0.95)
print(result)  # {'success': True, 'log_id': '...'}

# Get all logs
logs = client.get_all_logs()
print(logs)

# Filter logs
filtered = client.filter_logs(person_name="John")
print(filtered)
```

## MongoDB Collections

### recognition_logs
```json
{
  "_id": ObjectId("..."),
  "person_name": "John Doe",
  "camera_id": "camera_01",
  "timestamp": ISODate("2025-01-22T10:30:00Z"),
  "confidence_score": 0.95,
  "detection_count": 2,
  "last_detection_time": ISODate("2025-01-22T11:10:00Z")
}
```

### users
```json
{
  "_id": ObjectId("..."),
  "username": "admin",
  "hashed_password": "$2b$12$...",
  "created_at": ISODate("2025-01-22T10:00:00Z"),
  "is_active": true
}
```

## Integration with recognize2.py

See `INTEGRATION_GUIDE.md` for detailed steps.

Quick version:
1. Copy `recognize2_with_api.py` or update your `recognize2.py`
2. Change `API_KEY` to match backend `.env`
3. When face is recognized, call: `api_client.save_recognition(name, camera_id, score)`

## Troubleshooting

### Backend won't start
```bash
# Check if port is already in use
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or change port in .env: API_PORT=8001
```

### MongoDB connection error
```bash
# Ensure MongoDB is running
mongosh

# Check connection string in .env
MONGO_DB_URL=mongodb://127.0.0.1:27017
```

### API Key not working
- Verify `API_KEY` in backend `.env`
- Make sure `X-API-Key` header is set in requests
- Ensure key is sent correctly (exact match, case-sensitive)

### Port 8000 already in use
- Change `API_PORT` in `.env`
- Or kill existing process on port 8000

### Recognize2.py can't find backend
- Ensure backend path is correct in sys.path
- Verify backend is running: `http://localhost:8000/docs`
- Check network connectivity

## Production Deployment

### Security Checklist
- [ ] Change `SECRET_KEY` to random string
- [ ] Change `API_KEY` to secure value
- [ ] Set `API_ENV=production`
- [ ] Update CORS origins (don't use "*")
- [ ] Use HTTPS (setup with reverse proxy)
- [ ] Add database authentication
- [ ] Setup logging to file
- [ ] Add rate limiting
- [ ] Setup monitoring/alerts

### Performance
- [ ] Enable MongoDB indexing
- [ ] Setup connection pooling
- [ ] Add caching layer (Redis)
- [ ] Use async tasks for cleanup
- [ ] Load test the API

## File Locations

| File | Location |
|------|----------|
| Backend Root | `/Comp_Visn/backend/` |
| Virtual Env | `/Comp_Visn/backend/benv/` |
| API Code | `/Comp_Visn/backend/app/` |
| Config | `/Comp_Visn/backend/.env` |
| Recognize2 Integration | `/Comp_Visn/face_recognition/recognize2_with_api.py` |
| API Docs | `http://localhost:8000/docs` |

## Next Steps

1. ✅ Start backend: `python run.py`
2. ✅ Test API: Visit `http://localhost:8000/docs`
3. ✅ Update recognize2.py with API calls
4. ✅ Monitor MongoDB for saved logs
5. ✅ Query logs via API endpoints

## Support Resources

- FastAPI Docs: https://fastapi.tiangolo.com/
- MongoDB Python: https://pymongo.readthedocs.io/
- Pydantic Docs: https://docs.pydantic.dev/
- JWT Guide: https://tools.ietf.org/html/rfc7519

---

**Backend Version:** 1.0.0  
**Created:** January 22, 2026  
**Python:** 3.10+  
**FastAPI:** 0.104.1
