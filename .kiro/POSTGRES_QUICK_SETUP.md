# PostgreSQL Quick Setup (5 Minutes)

## TL;DR - Copy & Paste Commands

### 1. Create Database & User
```bash
psql -U postgres -c "CREATE USER admin WITH PASSWORD 'admin';"
psql -U postgres -c "CREATE DATABASE jobspy_db OWNER admin;"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE jobspy_db TO admin;"
```

### 2. Verify Connection
```bash
psql -U admin -d jobspy_db -h localhost
# Type: \q to exit
```

### 3. Initialize Backend Database
```bash
cd Backend
pip install -r requirements.txt
python setup_db.py
```

### 4. Start Backend
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Expected Output

```
🚀 Starting JobSpy Web Application v1.0.0
📍 Environment: development
🔧 Debug Mode: False
🗄️  Database: postgresql+asyncpg://admin:admin@localhost:5432/jobspy_db
✅ Database initialized successfully
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Credentials
- **User**: admin
- **Password**: admin
- **Database**: jobspy_db
- **Host**: localhost
- **Port**: 5432

## Files Modified
- ✅ `Backend/app/main.py` - Restored with all routers
- ✅ `Backend/app/core/config.py` - Updated with admin:admin credentials
- ✅ `Backend/.env` - Created with PostgreSQL connection string
- ✅ `Backend/setup_db.py` - Created for database initialization

## Routers Registered
- ✅ `/api/v1/auth` - Authentication (register, login, refresh, logout)
- ✅ `/api/v1/jobs` - Job search and management
- ✅ `/api/v1/saved-jobs` - Save/unsave jobs
- ✅ `/api/v1/alerts` - Create and manage job alerts
- ✅ `/api/v1/users` - User profile management

## API Documentation
Once running, visit: http://localhost:8000/api/docs

## Troubleshooting

| Error | Solution |
|-------|----------|
| `could not connect to server` | Start PostgreSQL: `sudo service postgresql start` |
| `password authentication failed` | Reset: `psql -U postgres -c "ALTER USER admin WITH PASSWORD 'admin';"` |
| `database does not exist` | Create: `psql -U postgres -c "CREATE DATABASE jobspy_db OWNER admin;"` |
| `tables not created` | Run: `python setup_db.py` |

## Next Steps
1. ✅ PostgreSQL setup complete
2. ✅ Backend running with real database
3. ⏳ Frontend already running on http://localhost:5173
4. Test API at http://localhost:8000/api/docs
5. Connect frontend to backend API

## Full Guide
See `.kiro/POSTGRESQL_SETUP_GUIDE.md` for detailed instructions.
