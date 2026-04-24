# PostgreSQL Setup Guide

## Overview
This guide walks you through setting up PostgreSQL for the JobSpy backend with the credentials: `admin:admin`

## Prerequisites
- PostgreSQL 12+ installed and running
- psql command-line tool available
- Backend folder with `.env` file configured

## Step 1: Create Database and User

### Option A: Using psql (Recommended)

```bash
# Connect to PostgreSQL as default user
psql -U postgres

# In psql prompt, run:
CREATE USER admin WITH PASSWORD 'admin';
CREATE DATABASE jobspy_db OWNER admin;
GRANT ALL PRIVILEGES ON DATABASE jobspy_db TO admin;
\q
```

### Option B: Using SQL Script

Create a file `setup_postgres.sql`:
```sql
CREATE USER admin WITH PASSWORD 'admin';
CREATE DATABASE jobspy_db OWNER admin;
GRANT ALL PRIVILEGES ON DATABASE jobspy_db TO admin;
```

Then run:
```bash
psql -U postgres -f setup_postgres.sql
```

## Step 2: Verify Connection

Test the connection with the new credentials:
```bash
psql -U admin -d jobspy_db -h localhost
```

You should see:
```
jobspy_db=>
```

Type `\q` to exit.

## Step 3: Initialize Backend Database

From the `Backend` folder:

```bash
# Install dependencies (if not already done)
pip install -r requirements.txt

# Run database setup script
python setup_db.py
```

Expected output:
```
🔧 Setting up database...
📍 Database URL: postgresql+asyncpg://admin:admin@localhost:5432/jobspy_db
✅ Database tables created successfully!
✅ Database connection verified!
```

## Step 4: Verify Database Tables

Connect to the database and check tables:
```bash
psql -U admin -d jobspy_db

# In psql prompt:
\dt
```

You should see tables like:
- users
- jobs
- saved_jobs
- alerts
- search_history

## Step 5: Start Backend Server

From the `Backend` folder:
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
🚀 Starting JobSpy Web Application v1.0.0
📍 Environment: development
🔧 Debug Mode: False
🗄️  Database: postgresql+asyncpg://admin:admin@localhost:5432/jobspy_db
✅ Database initialized successfully
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Troubleshooting

### Connection Refused
**Error**: `psycopg2.OperationalError: could not connect to server`

**Solution**:
- Ensure PostgreSQL is running: `sudo service postgresql status`
- Start PostgreSQL: `sudo service postgresql start`
- Check connection string in `.env`

### Authentication Failed
**Error**: `FATAL: password authentication failed for user "admin"`

**Solution**:
- Verify credentials in `.env`: `DATABASE_URL=postgresql+asyncpg://admin:admin@localhost:5432/jobspy_db`
- Reset user password:
  ```bash
  psql -U postgres
  ALTER USER admin WITH PASSWORD 'admin';
  ```

### Database Does Not Exist
**Error**: `FATAL: database "jobspy_db" does not exist`

**Solution**:
- Create database: `CREATE DATABASE jobspy_db OWNER admin;`
- Verify: `psql -U admin -d jobspy_db`

### Tables Not Created
**Error**: Tables missing when connecting to database

**Solution**:
- Run setup script: `python setup_db.py`
- Check for errors in output
- Verify database permissions: `GRANT ALL PRIVILEGES ON DATABASE jobspy_db TO admin;`

## Environment Variables

The `.env` file in `Backend/` folder contains:
```
DATABASE_URL=postgresql+asyncpg://admin:admin@localhost:5432/jobspy_db
```

This is automatically loaded by the application via `pydantic_settings`.

## Database Schema

The database includes the following tables:

### users
- id (UUID, primary key)
- email (String, unique)
- full_name (String)
- hashed_password (String)
- is_active (Boolean)
- is_verified (Boolean)
- created_at (DateTime)
- updated_at (DateTime)
- last_login (DateTime)

### jobs
- id (UUID, primary key)
- title (String)
- company (String)
- location (String)
- job_type (String)
- description (Text)
- salary_min (Integer)
- salary_max (Integer)
- source (String)
- source_url (String, unique)
- posted_at (DateTime)
- view_count (Integer)
- created_at (DateTime)
- updated_at (DateTime)

### saved_jobs
- id (UUID, primary key)
- user_id (UUID, foreign key)
- job_id (UUID, foreign key)
- notes (Text)
- saved_at (DateTime)
- updated_at (DateTime)

### alerts
- id (UUID, primary key)
- user_id (UUID, foreign key)
- title (String)
- keywords (Array)
- location (String)
- is_active (Boolean)
- created_at (DateTime)
- updated_at (DateTime)

### search_history
- id (UUID, primary key)
- user_id (UUID, foreign key)
- query (String)
- filters (JSON)
- results_count (Integer)
- searched_at (DateTime)

## Next Steps

1. ✅ PostgreSQL installed and running
2. ✅ Database and user created
3. ✅ Backend `.env` configured
4. ✅ Database tables initialized
5. ✅ Backend server running
6. Test API endpoints at http://localhost:8000/api/docs
7. Connect frontend to backend

## API Testing

Once the backend is running, test endpoints:

```bash
# Health check
curl http://localhost:8000/health

# API documentation
http://localhost:8000/api/docs

# Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","full_name":"Test User"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review `.kiro/BACKEND_STARTUP_GUIDE.md`
3. Check backend logs for detailed error messages
4. Verify PostgreSQL is running: `psql -U postgres -c "SELECT version();"`
