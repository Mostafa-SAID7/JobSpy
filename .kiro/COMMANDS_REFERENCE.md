# Commands Reference - JobSpy Web Application

## Quick Reference Card

### 🚀 START BACKEND (3 Commands)

```bash
# 1. Navigate to Backend folder
cd Backend

# 2. Install dependencies (first time only)
pip install -r requirements.txt

# 3. Start the server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

---

### ✅ VERIFY BACKEND IS RUNNING

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","app":"JobSpy Web Application","version":"1.0.0","environment":"development"}
```

---

### 🌐 ACCESS FRONTEND

```
Frontend: http://localhost:5173/
Backend API Docs: http://localhost:8000/api/docs
Backend ReDoc: http://localhost:8000/api/redoc
```

---

## Frontend Commands

### Development Server
```bash
cd Frontend
npm run dev
```
**Runs on**: http://localhost:5173/

### Production Build
```bash
cd Frontend
npm run build
```
**Output**: `Frontend/dist/` folder

### Preview Build
```bash
cd Frontend
npm run preview
```

### Type Check
```bash
cd Frontend
npm run type-check
```

### Lint
```bash
cd Frontend
npm run lint
```

---

## Backend Commands

### Start Development Server
```bash
cd Backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Start Production Server
```bash
cd Backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Run Tests
```bash
cd Backend
pytest
```

### Run Tests with Coverage
```bash
cd Backend
pytest --cov=app
```

### Format Code
```bash
cd Backend
black app/
```

### Lint Code
```bash
cd Backend
flake8 app/
```

### Type Check
```bash
cd Backend
mypy app/
```

### Database Migrations

#### Create Migration
```bash
cd Backend
alembic revision --autogenerate -m "Description of changes"
```

#### Apply Migrations
```bash
cd Backend
alembic upgrade head
```

#### Rollback Migration
```bash
cd Backend
alembic downgrade -1
```

---

## Docker Commands

### Build Docker Images
```bash
docker-compose build
```

### Start All Services
```bash
docker-compose up
```

### Start in Background
```bash
docker-compose up -d
```

### Stop All Services
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs -f
```

### View Backend Logs Only
```bash
docker-compose logs -f backend
```

### View Frontend Logs Only
```bash
docker-compose logs -f frontend
```

---

## API Testing Commands

### Test Health Endpoint
```bash
curl http://localhost:8000/health
```

### Test Root Endpoint
```bash
curl http://localhost:8000/
```

### Register User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "full_name": "Test User"
  }'
```

### Login User
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'
```

### Search Jobs
```bash
curl "http://localhost:8000/api/v1/jobs?query=developer&location=remote"
```

### Get Job Details
```bash
curl http://localhost:8000/api/v1/jobs/{job_id}
```

### Get Saved Jobs (requires token)
```bash
curl -H "Authorization: Bearer {token}" \
  http://localhost:8000/api/v1/saved-jobs
```

### Save a Job (requires token)
```bash
curl -X POST http://localhost:8000/api/v1/saved-jobs \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"job_id": "{job_id}"}'
```

### Create Alert (requires token)
```bash
curl -X POST http://localhost:8000/api/v1/alerts \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Developer",
    "keywords": ["python", "developer"],
    "location": "remote",
    "job_type": "full-time"
  }'
```

---

## Environment Setup

### Create Backend .env File
```bash
cd Backend
cp .env.example .env
```

### Create Frontend .env File
```bash
cd Frontend
cp .env.example .env
```

### Edit Backend .env
```bash
# Linux/Mac
nano Backend/.env

# Windows
notepad Backend\.env
```

---

## Troubleshooting Commands

### Check if Port 8000 is in Use
```bash
# Linux/Mac
lsof -i :8000

# Windows (PowerShell)
Get-NetTCPConnection -LocalPort 8000
```

### Kill Process on Port 8000
```bash
# Linux/Mac
kill -9 <PID>

# Windows (PowerShell)
Stop-Process -Id <PID> -Force
```

### Check if Port 5173 is in Use
```bash
# Linux/Mac
lsof -i :5173

# Windows (PowerShell)
Get-NetTCPConnection -LocalPort 5173
```

### Check Python Version
```bash
python --version
```

### Check Node Version
```bash
node --version
npm --version
```

### Check if PostgreSQL is Running
```bash
# Linux/Mac
pg_isready -h localhost -p 5432

# Windows
psql -U postgres -c "SELECT 1"
```

### Check if Redis is Running
```bash
redis-cli ping
```

---

## Git Commands

### Clone Repository
```bash
git clone <repository-url>
cd JobSpy
```

### Create Feature Branch
```bash
git checkout -b feature/feature-name
```

### Commit Changes
```bash
git add .
git commit -m "feat: description of changes"
```

### Push Changes
```bash
git push origin feature/feature-name
```

### Create Pull Request
```bash
# Use GitHub web interface or GitHub CLI
gh pr create --title "PR Title" --body "PR Description"
```

---

## Development Workflow

### 1. Start Backend
```bash
cd Backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Start Frontend (in new terminal)
```bash
cd Frontend
npm run dev
```

### 3. Open Browser
```
http://localhost:5173/
```

### 4. Make Changes
- Edit files in `Frontend/src/` or `Backend/app/`
- Changes auto-reload in development mode

### 5. Test Changes
- Test in browser at http://localhost:5173/
- Check browser console for errors
- Check backend terminal for errors

### 6. Commit Changes
```bash
git add .
git commit -m "feat: description"
git push origin feature-branch
```

---

## Performance Monitoring

### Frontend Build Analysis
```bash
cd Frontend
npm run build
# Check output size in terminal
```

### Backend Performance
```bash
# Monitor in terminal where backend is running
# Look for response times and errors
```

### Database Query Performance
```bash
# Enable query logging in Backend/.env
DATABASE_ECHO=True
```

---

## Useful Links

### Local URLs
- Frontend: http://localhost:5173/
- Backend API: http://localhost:8000/
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- Health Check: http://localhost:8000/health

### Documentation
- `.kiro/QUICK_START.md` - Quick start guide
- `.kiro/BACKEND_STARTUP_GUIDE.md` - Backend setup
- `.kiro/SYSTEM_ARCHITECTURE.md` - System design
- `.kiro/TESTING_CHECKLIST.md` - Testing guide
- `.kiro/CURRENT_STATUS.md` - Current status

---

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'fastapi'"
**Solution**: Run `pip install -r requirements.txt` in Backend folder

### Issue: "npm: command not found"
**Solution**: Install Node.js from https://nodejs.org/

### Issue: "python: command not found"
**Solution**: Install Python from https://www.python.org/

### Issue: "Port 8000 already in use"
**Solution**: Kill existing process or use different port

### Issue: "CORS error in browser console"
**Solution**: Verify backend is running on port 8000 and frontend on 5173

### Issue: "Cannot find module '@/stores/auth'"
**Solution**: Run `npm install` in Frontend folder

### Issue: "Database connection error"
**Solution**: Skip database setup for MVP or configure PostgreSQL

---

## Quick Checklist

- [ ] Python 3.9+ installed
- [ ] Node.js 16+ installed
- [ ] Backend dependencies installed: `pip install -r requirements.txt`
- [ ] Frontend dependencies installed: `npm install`
- [ ] Backend .env file created: `cp .env.example .env`
- [ ] Backend running: `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
- [ ] Frontend running: `npm run dev`
- [ ] Browser open to http://localhost:5173/
- [ ] No errors in browser console
- [ ] No errors in backend terminal

---

**Last Updated**: April 24, 2026  
**Status**: Ready to use
