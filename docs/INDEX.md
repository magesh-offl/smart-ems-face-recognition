# 📚 FastAPI Backend - Documentation Index

Welcome to the Face Recognition Backend! This document is your guide to all available documentation.

## 🎯 Start Here

**New to this project?** Start with these files in order:

1. 📄 **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** ← Start here!
   - Overview of what was created
   - Architecture explanation
   - Key features summary
   - Quick start guide

2. ⚡ **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)**
   - Commands to start/stop backend
   - Most used API calls
   - Quick troubleshooting
   - Important URLs and file locations

3. 📖 **[README.md](README.md)**
   - Complete API documentation
   - All endpoints explained
   - Database schema
   - Environment variables reference

4. 🚀 **[SETUP.md](SETUP.md)**
   - Detailed setup instructions
   - Architecture deep dive
   - Production deployment guide
   - Performance optimization
   - Security checklist

5. 🔗 **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)**
   - How to modify recognize2.py
   - Code examples for integration
   - Python client library usage
   - Error handling

---

## 📂 File Guide

### Documentation Files

| File | Size | Purpose | When to Read |
|------|------|---------|--------------|
| `PROJECT_SUMMARY.md` | 14 KB | Complete overview | First (overview) |
| `QUICK_REFERENCE.md` | 8 KB | Quick commands & tips | Frequently (reference) |
| `README.md` | 7 KB | API documentation | When using API |
| `SETUP.md` | 11 KB | Setup & deployment | During setup/deployment |
| `INTEGRATION_GUIDE.md` | 9 KB | Integrate with recognize2.py | When integrating |
| `INDEX.md` | This file | Documentation guide | When lost/confused |

### Configuration Files

| File | Purpose |
|------|---------|
| `.env` | Local environment variables (CHANGE BEFORE PRODUCTION) |
| `.env.example` | Template for environment variables |
| `requirements.txt` | Python dependencies |

### Application Files

| Directory | Purpose |
|-----------|---------|
| `app/api/v1/` | REST API endpoints |
| `app/controllers/` | Business logic controllers |
| `app/services/` | Service layer (1-hour cooldown here) |
| `app/repositories/` | Data access layer (MongoDB) |
| `app/models/` | Pydantic request/response models |
| `app/schemas/` | MongoDB document schemas |
| `app/middleware/` | Authentication middleware |
| `app/utils/` | Utilities (client, logger, exceptions) |

### Entry Points

| File | Purpose |
|------|---------|
| `run.py` | Start the backend server |
| `app/main.py` | FastAPI application definition |
| `app/config.py` | Configuration management |

---

## 🚀 Quick Commands

### Start Backend
```bash
cd /media/magesh/NewVolume2/Projects/Python/AppDemo/Comp_visn/backend
source benv/bin/activate
python run.py
```

### Access API Documentation
```
http://localhost:8000/docs
```

### Run Tests
```bash
# Test if backend is working
python -c "from app.main import app; print('✓ Working')"
```

---

## 🎯 Common Tasks

### I want to...

**Start the backend**
→ See [QUICK_REFERENCE.md](QUICK_REFERENCE.md#-startstop-backend)

**Save face recognition data**
→ See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md#full-example-integration)

**Query recognition logs**
→ See [README.md](README.md#api-endpoints) or [QUICK_REFERENCE.md](QUICK_REFERENCE.md#-most-used-api-calls)

**Modify recognize2.py**
→ See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)

**Deploy to production**
→ See [SETUP.md](SETUP.md#production-deployment)

**Fix an error**
→ See [SETUP.md](SETUP.md#troubleshooting) or [QUICK_REFERENCE.md](QUICK_REFERENCE.md#-common-issues--solutions)

**Understand the architecture**
→ See [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md#-architecture-overview)

**Configure environment**
→ See [README.md](README.md#environment-variables) or [SETUP.md](SETUP.md#configuration)

**Test the API**
→ See [QUICK_REFERENCE.md](QUICK_REFERENCE.md#-most-used-api-calls)

**Monitor database**
→ See [QUICK_REFERENCE.md](QUICK_REFERENCE.md#-database-queries-mongodb)

**Understand 1-hour cooldown**
→ See [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md#1-hour-cooldown-logic) or [SETUP.md](SETUP.md#1-hour-cooldown-logic)

---

## 📊 Architecture at a Glance

```
HTTP Requests from recognize2.py
         ↓
   API Layer (api/v1/)
         ↓
Controllers (handle requests)
         ↓
Services (business logic + 1-hour cooldown)
         ↓
Repositories (database operations)
         ↓
MongoDB (recognition_logs collection)
```

---

## 🔑 Key Concepts

### 1. **1-Hour Cooldown**
When saving face recognition:
- If same person at same camera in last 1 hour → Update existing log (increment counter)
- Otherwise → Create new log

**Learn more:** [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md#1-hour-cooldown-logic)

### 2. **API Authentication**
Two types of authentication:
- **API Key** (for recognize2.py): `X-API-Key` header
- **JWT Token** (for user login): Bearer token

**Learn more:** [README.md](README.md#api-authentication)

### 3. **MVC + Layered Architecture**
Separation of concerns:
- **API Layer**: HTTP endpoints
- **Controller Layer**: Request handling
- **Service Layer**: Business logic
- **Repository Layer**: Data access
- **Database**: MongoDB

**Learn more:** [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md#-architecture-overview)

---

## 🔍 API Endpoints Overview

### Authentication
```
POST   /api/v1/auth/register          Register user
POST   /api/v1/auth/login             Login & get token
```

### Recognition (Requires X-API-Key)
```
POST   /api/v1/recognition/save       Save recognition (1h cooldown)
GET    /api/v1/recognition/logs       Get all logs
GET    /api/v1/recognition/filter     Filter logs
GET    /api/v1/recognition/logs/{id}  Get single log
PUT    /api/v1/recognition/logs/{id}  Update log
DELETE /api/v1/recognition/logs/{id}  Delete log
```

**Full documentation:** [README.md](README.md#api-endpoints)

---

## 📍 File Locations

```
/Comp_Visn/
├── backend/                         ← Backend root
│   ├── benv/                        ← Virtual environment
│   ├── app/                         ← Application code
│   ├── .env                         ← Configuration
│   ├── requirements.txt             ← Dependencies
│   ├── run.py                       ← Start server
│   ├── PROJECT_SUMMARY.md           ← Overview
│   ├── QUICK_REFERENCE.md           ← Quick tips
│   ├── README.md                    ← API docs
│   ├── SETUP.md                     ← Setup guide
│   └── INTEGRATION_GUIDE.md         ← Integration guide
│
└── face_recognition/
    ├── recognize2.py                ← Original version
    └── recognize2_with_api.py       ← With API integration
```

---

## ✅ Checklist for Getting Started

- [ ] Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
- [ ] Start backend: `python run.py`
- [ ] Visit `http://localhost:8000/docs`
- [ ] Test an API endpoint
- [ ] Read [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
- [ ] Modify recognize2.py
- [ ] Verify data is saved in MongoDB
- [ ] Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for common tasks

---

## 🆘 Help & Support

### If you...

**Don't know where to start**
→ Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) first

**Need to run a command**
→ Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md#-startstop-backend)

**Get an error**
→ See [QUICK_REFERENCE.md](QUICK_REFERENCE.md#-common-issues--solutions) or [SETUP.md](SETUP.md#troubleshooting)

**Want to integrate with recognize2.py**
→ Read [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)

**Need API examples**
→ See [QUICK_REFERENCE.md](QUICK_REFERENCE.md#-most-used-api-calls) or [README.md](README.md#api-endpoints)

**Want to understand architecture**
→ See [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md#-architecture-overview)

**Need to deploy**
→ Read [SETUP.md](SETUP.md#production-deployment)

---

## 📚 External Resources

| Topic | Resource |
|-------|----------|
| FastAPI | https://fastapi.tiangolo.com/ |
| MongoDB | https://docs.mongodb.com/ |
| Pydantic | https://docs.pydantic.dev/ |
| PyMongo | https://pymongo.readthedocs.io/ |

---

## 🔄 Documentation Relationship

```
INDEX.md (You are here)
   ↓
PROJECT_SUMMARY.md (Overview & Architecture)
   ├─→ QUICK_REFERENCE.md (Common commands)
   ├─→ README.md (API documentation)
   ├─→ SETUP.md (Setup & Deployment)
   └─→ INTEGRATION_GUIDE.md (Integrate with recognize2.py)
```

---

## 💡 Quick Tips

1. **Always activate venv first**
   ```bash
   source benv/bin/activate
   ```

2. **Check API docs frequently**
   ```
   http://localhost:8000/docs
   ```

3. **Monitor MongoDB changes**
   ```bash
   mongosh
   db.recognition_logs.watch()
   ```

4. **Test with cURL**
   ```bash
   curl -X GET "http://localhost:8000/api/v1/recognition/logs" \
     -H "X-API-Key: your-api-key-change-this"
   ```

5. **Read error messages carefully** - They contain important info!

---

## 🎓 Recommended Reading Order

For different needs:

### Complete Beginner
1. This file (INDEX.md)
2. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
3. [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
4. [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)

### Setting Up for First Time
1. [SETUP.md](SETUP.md) - Section "Quick Start"
2. [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
3. [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)

### Using the APIs
1. [README.md](README.md) - API Endpoints section
2. [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Most Used API Calls
3. Interactive Swagger UI at `/docs`

### Integrating with recognize2.py
1. [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) - Full Example
2. [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Python Client Usage

### Production Deployment
1. [SETUP.md](SETUP.md) - Production Deployment section
2. [SETUP.md](SETUP.md) - Security Checklist

---

## 📝 Notes

- **Always keep `.env` secure** - Don't commit to version control
- **Change API_KEY before production** - Use secure, random values
- **MongoDB must be running** - Start with `mongosh` before starting backend
- **Port 8000** - Default API port (changeable in .env)
- **Virtual environment is required** - Always activate before running

---

## ✨ What's Included

✅ Complete FastAPI backend  
✅ MongoDB integration  
✅ 1-hour cooldown logic  
✅ JWT & API Key authentication  
✅ CRUD APIs for recognition logs  
✅ Python client library  
✅ Comprehensive documentation  
✅ Quick reference guide  
✅ Integration examples  
✅ Ready to use!

---

**Last Updated:** January 22, 2026  
**Backend Version:** 1.0.0  
**Status:** ✅ Ready to Use

For questions, refer to the appropriate documentation file above.
