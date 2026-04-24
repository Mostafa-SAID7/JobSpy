# Quick Start - JobSpy Web Application

## Current Status
- ✅ **Frontend**: Running on http://localhost:5173/
- ⏳ **Backend**: NOT running (needs to be started)
- ❌ **API Connection**: Failed (backend offline)

## Start Backend (3 Steps)

### 1. Install Dependencies
```bash
cd Backend
pip install -r requirements.txt
```

### 2. Create Environment File
```bash
cp .env.example .env
```

### 3. Start Server
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

## Verify Backend is Running

### Health Check
```bash
curl http://localhost:8000/health
```

### API Documentation
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Test Frontend Connection

Once backend is running:
1. Open http://localhost:5173/ in browser
2. Try to login or register
3. Check browser console for any errors
4. API calls should now work

## Architecture

```
Frontend (Vue 3 + TypeScript)
    ↓ (HTTP/REST)
http://localhost:5173 → http://localhost:8000/api
    ↑ (JSON Response)
Backend (FastAPI + SQLAlchemy)
```

## Key Files

### Frontend
- `Frontend/src/services/api.ts` - API client configuration
- `Frontend/src/stores/` - State management (Pinia)
- `Frontend/src/pages/` - Page components
- `Frontend/src/components/` - Reusable components

### Backend
- `Backend/app/main.py` - FastAPI application entry point
- `Backend/app/routers/` - API endpoints
- `Backend/app/models/` - Database models
- `Backend/app/services/` - Business logic
- `Backend/app/core/config.py` - Configuration

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login user |
| GET | `/api/v1/jobs` | Search jobs |
| GET | `/api/v1/saved-jobs` | Get saved jobs |
| POST | `/api/v1/alerts` | Create alert |

## Troubleshooting

### "Connection Refused" Error
- Backend is not running
- Solution: Run `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

### Port 8000 Already in Use
```bash
# Find and kill process
lsof -i :8000
kill -9 <PID>
```

### Module Not Found Errors
- Dependencies not installed
- Solution: Run `pip install -r requirements.txt` in Backend folder

### CORS Errors
- Frontend and backend CORS mismatch
- Solution: Verify both are running on correct ports (5173 and 8000)

## Documentation

- Full Backend Startup Guide: `.kiro/BACKEND_STARTUP_GUIDE.md`
- Frontend Implementation Summary: `.kiro/IMPLEMENTATION_SUMMARY.md`
- Theme System Guide: `.kiro/THEME_SYSTEM_GUIDE.md`

---

**Next Action**: Start the backend server using the 3 steps above!
