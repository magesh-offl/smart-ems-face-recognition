# Face Recognition Backend

FastAPI backend for face recognition system with MongoDB storage and JWT authentication.

## Features

- **Face Recognition Logging**: Save and manage face detection results
- **1-Hour Cooldown**: Prevents duplicate records for the same person at the same camera within 1 hour
- **API Key & JWT Authentication**: Secure endpoints
- **Filtering & Search**: Query recognition logs by person name, camera ID, and date range
- **CRUD Operations**: Create, read, update, and delete logs
- **MVC + Layered Architecture**: Clean separation of concerns

## Project Structure

```
backend/
├── app/
│   ├── api/v1/              # API routes
│   │   ├── auth.py         # Authentication routes
│   │   └── recognition.py  # Recognition routes
│   ├── controllers/         # Business logic
│   │   └── recognition.py  # Recognition controller
│   ├── services/           # Service layer
│   │   ├── auth.py         # Auth service
│   │   └── recognition.py  # Recognition service
│   ├── repositories/       # Data access layer
│   │   ├── base.py         # Base repository
│   │   ├── recognition.py  # Recognition repository
│   │   └── user.py         # User repository
│   ├── models/             # Pydantic models
│   ├── schemas/            # MongoDB schemas
│   ├── middleware/         # Authentication middleware
│   ├── utils/              # Utilities
│   ├── config.py           # Configuration
│   └── main.py             # FastAPI app
├── .env                    # Environment variables
├── requirements.txt        # Python dependencies
├── run.py                  # Application entry point
└── README.md              # This file
```

## Setup

### 1. Create Virtual Environment

```bash
cd /media/magesh/NewVolume2/Projects/Python/AppDemo/Comp_visn/backend
python3 -m venv benv
source benv/bin/activate  # On Windows: benv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and update values:

```bash
cp .env.example .env
```

Edit `.env`:
- Update `SECRET_KEY` with a secure key
- Update `API_KEY` for API authentication
- Ensure MongoDB URL is correct

### 4. Run Application

```bash
python run.py
```

The application will start on `http://0.0.0.0:8000`

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication

#### Register User
```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "user123",
  "password": "securepass123"
}
```

#### Login
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "user123",
  "password": "securepass123"
}
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Recognition Logs

All recognition endpoints require `X-API-Key` header.

#### Save Recognition
```bash
POST /api/v1/recognition/save
X-API-Key: your-api-key

{
  "person_name": "John Doe",
  "camera_id": "camera_01",
  "confidence_score": 0.95
}
```

#### Get All Logs
```bash
GET /api/v1/recognition/logs?skip=0&limit=10
X-API-Key: your-api-key
```

#### Filter Logs
```bash
GET /api/v1/recognition/filter?person_name=John&camera_id=camera_01&start_date=2025-01-01&end_date=2025-01-31
X-API-Key: your-api-key
```

#### Get Specific Log
```bash
GET /api/v1/recognition/logs/{log_id}
X-API-Key: your-api-key
```

#### Update Log
```bash
PUT /api/v1/recognition/logs/{log_id}
X-API-Key: your-api-key
Content-Type: application/json

{
  "person_name": "Jane Doe",
  "camera_id": "camera_02",
  "confidence_score": 0.98
}
```

#### Delete Log
```bash
DELETE /api/v1/recognition/logs/{log_id}
X-API-Key: your-api-key
```

## Architecture

### MVC + Layered Architecture

1. **API Layer** (`api/`): HTTP endpoints
2. **Controller Layer** (`controllers/`): Request handling and validation
3. **Service Layer** (`services/`): Business logic and 1-hour cooldown logic
4. **Repository Layer** (`repositories/`): Data access and MongoDB operations
5. **Models/Schemas** (`models/`, `schemas/`): Data structures

## Key Features

### 1-Hour Cooldown Logic

When saving face recognition:
- Check if same person was detected at same camera within last 1 hour
- If yes: increment `detection_count` and update `last_detection_time`
- If no: create new recognition log

### Authentication

- **API Key**: For client applications (e.g., recognize2.py)
- **JWT Token**: For user accounts

## Integration with recognize2.py

Update your `recognize2.py` to send recognition data:

```python
import requests

api_url = "http://localhost:8000/api/v1/recognition/save"
api_key = "your-api-key"

# When face is recognized
response = requests.post(
    api_url,
    json={
        "person_name": name,
        "camera_id": "camera_01",
        "confidence_score": score
    },
    headers={"X-API-Key": api_key}
)

if response.status_code == 200:
    print("Recognition saved successfully")
else:
    print(f"Error: {response.text}")
```

## Database

- **MongoDB**: Local instance at `mongodb://127.0.0.1:27017`
- **Database**: `face_recognition_db`
- **Collections**:
  - `recognition_logs`: Face recognition records
  - `users`: User accounts
  - `api_keys`: API keys for clients

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGO_DB_URL` | MongoDB connection string | `mongodb://127.0.0.1:27017` |
| `MONGO_DB_NAME` | MongoDB database name | `face_recognition_db` |
| `API_HOST` | API host | `0.0.0.0` |
| `API_PORT` | API port | `8000` |
| `API_ENV` | Environment (development/production) | `development` |
| `SECRET_KEY` | JWT secret key | Required |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `60` |
| `API_KEY` | API key for client apps | Required |
| `LOG_LEVEL` | Logging level | `INFO` |

## Development

### Running Tests

(Add test setup as needed)

### Code Style

- Follow PEP 8
- Use type hints
- Document functions with docstrings

## Troubleshooting

### MongoDB Connection Error
- Ensure MongoDB is running: `mongosh`
- Check connection string in `.env`

### API Key Not Working
- Update `API_KEY` in `.env`
- Make sure `X-API-Key` header is set in requests

### Port Already in Use
- Change `API_PORT` in `.env`
- Or kill existing process: `lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill`

## License

MIT

## Support

For issues or questions, refer to the FastAPI documentation: https://fastapi.tiangolo.com/
