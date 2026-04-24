# Backend Startup Guide

## Overview
The JobSpy backend is a FastAPI application that runs on port 8000. The frontend (running on port 5173) communicates with it via REST API calls.

## Prerequisites

### 1. Python Installation
Ensure Python 3.9+ is installed:
```bash
python --version
```

### 2. Backend Dependencies
All required packages are listed in `Backend/requirements.txt`:
- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **SQLAlchemy** - ORM
- **PostgreSQL** - Database (psycopg2-binary, asyncpg)
- **Redis** - Caching & Celery broker
- **Celery** - Background jobs
- **JWT** - Authentication
- **And more...**

## Setup Steps

### Step 1: Install Dependencies
```bash
cd Backend
pip install -r requirements.txt
```

### Step 2: Create Environment File
Copy the example environment file and configure it:
```bash
cp .env.example .env
```

Edit `.env` with your settings. For local development, the defaults should work:
```
DEBUG=True
ENVIRONMENT=development
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
RELOAD=True
```

### Step 3: Database Setup (Optional for MVP)
For the MVP, you can skip database setup initially. The backend will handle schema creation on first run.

If you want to set up PostgreSQL:
```bash
# Create database
createdb jobspy_db

# Run migrations
alembic upgrade head
```

### Step 4: Start the Backend Server
```bash
cd Backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

## Verification

### 1. Health Check
Open in browser or curl:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "app": "JobSpy Web Application",
  "version": "1.0.0",
  "environment": "development"
}
```

### 2. API Documentation
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### 3. Test API Endpoints
```bash
# Test root endpoint
curl http://localhost:8000/

# Test health check
curl http://localhost:8000/health

# Test auth endpoints (will fail without DB, but shows server is running)
curl -X POST http://localhost:8000/api/v1/auth/register
```

## Frontend Connection

The frontend is configured to connect to `http://localhost:8000/api` (see `Frontend/src/services/api.ts`).

### CORS Configuration
The backend is already configured to accept requests from:
- `http://localhost:5173` (frontend dev server)
- `http://127.0.0.1:5173`
- `http://localhost:3000`
- `http://127.0.0.1:3000`

This is set in `Backend/app/core/config.py`:
```python
CORS_ORIGINS: List[str] = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout user

### Jobs
- `GET /api/v1/jobs` - Search jobs
- `GET /api/v1/jobs/{id}` - Get job details
- `POST /api/v1/jobs/search` - Advanced search

### Saved Jobs
- `GET /api/v1/saved-jobs` - Get user's saved jobs
- `POST /api/v1/saved-jobs` - Save a job
- `DELETE /api/v1/saved-jobs/{id}` - Remove saved job

### Alerts
- `GET /api/v1/alerts` - Get user's alerts
- `POST /api/v1/alerts` - Create alert
- `DELETE /api/v1/alerts/{id}` - Delete alert

### Users
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update profile
- `DELETE /api/v1/users/me` - Delete account

## Troubleshooting

### Port 8000 Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Module Import Errors
Ensure you're in the correct directory and dependencies are installed:
```bash
cd Backend
pip install -r requirements.txt
```

### Database Connection Errors
If you see database errors, you can skip database setup for MVP testing. The backend will still run and serve API endpoints.

### CORS Errors in Frontend
If you see CORS errors in the browser console, verify:
1. Backend is running on port 8000
2. Frontend is running on port 5173
3. Both are in the `CORS_ORIGINS` list in `Backend/app/core/config.py`

## Development Tips

### Hot Reload
The `--reload` flag enables hot reload. Changes to Python files will automatically restart the server.

### Debug Mode
Set `DEBUG=True` in `.env` for detailed error messages and debug information.

### Logging
Check the console output for detailed logs. Adjust `LOG_LEVEL` in `.env` if needed:
- `DEBUG` - Most verbose
- `INFO` - Standard
- `WARNING` - Warnings only
- `ERROR` - Errors only

## Next Steps

1. ✅ Start backend: `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
2. ✅ Verify health check: `curl http://localhost:8000/health`
3. ✅ Frontend should now connect successfully
4. Test authentication flow (login/register)
5. Test job search functionality
6. Test saved jobs and alerts

---

**Status**: Backend is ready to start. Frontend is already running on http://localhost:5173/
