# JobSpy Developer Setup Guide

## Prerequisites

Before setting up your development environment, ensure you have:

- **Git**: Version control system
- **Python**: 3.11 or higher
- **Node.js**: 18 or higher
- **npm**: 9 or higher (comes with Node.js)
- **Docker**: For containerized development
- **Docker Compose**: For multi-container setup
- **PostgreSQL**: 14 or higher (or use Docker)
- **Redis**: 7 or higher (or use Docker)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/jobspy.git
cd jobspy
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
cd Backend
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

#### Setup Environment Variables

```bash
cp .env.example .env
# Edit .env with your local configuration
```

#### Database Setup

```bash
# Run migrations
alembic upgrade head

# Create initial data (optional)
python scripts/seed_database.py
```

#### Start Backend Server

```bash
# Development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the provided script
python scripts/run_backend.py
```

The API will be available at `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 3. Frontend Setup

#### Install Node Dependencies

```bash
cd Frontend
npm install
```

#### Setup Environment Variables

```bash
cp .env.example .env.local
# Edit .env.local with your local configuration
```

#### Start Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

### 4. Database Setup (Using Docker)

```bash
# Start PostgreSQL container
docker run --name jobspy-postgres \
  -e POSTGRES_USER=jobspy \
  -e POSTGRES_PASSWORD=jobspy \
  -e POSTGRES_DB=jobspy \
  -p 5432:5432 \
  -d postgres:14

# Start Redis container
docker run --name jobspy-redis \
  -p 6379:6379 \
  -d redis:7
```

Or use Docker Compose:

```bash
docker-compose up -d postgres redis
```

## Development Workflow

### Running All Services with Docker Compose

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Running Services Individually

#### Terminal 1: Backend

```bash
cd Backend
source venv/bin/activate
uvicorn app.main:app --reload
```

#### Terminal 2: Frontend

```bash
cd Frontend
npm run dev
```

#### Terminal 3: Celery Worker (for background jobs)

```bash
cd Backend
source venv/bin/activate
celery -A app.tasks worker --loglevel=info
```

#### Terminal 4: Celery Beat (for scheduled tasks)

```bash
cd Backend
source venv/bin/activate
celery -A app.tasks beat --loglevel=info
```

## Testing

### Backend Tests

```bash
cd Backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_login

# Run with verbose output
pytest -v

# Run with markers
pytest -m "not slow"
```

### Frontend Tests

```bash
cd Frontend

# Run all tests
npm run test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch

# Run specific test file
npm run test -- tests/unit/auth.spec.js
```

### Integration Tests

```bash
cd Backend

# Run integration tests
pytest tests/integration/

# Run with specific database
pytest --db=postgresql
```

## Code Quality

### Backend Code Quality

```bash
cd Backend

# Linting with pylint
pylint app/

# Code formatting with black
black app/

# Import sorting with isort
isort app/

# Type checking with mypy
mypy app/

# All checks
./scripts/lint.sh
```

### Frontend Code Quality

```bash
cd Frontend

# Linting with ESLint
npm run lint

# Fix linting issues
npm run lint:fix

# Format with Prettier
npm run format

# Type checking
npm run type-check
```

## Debugging

### Backend Debugging

#### Using VS Code

1. Install Python extension
2. Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload"],
      "jinja": true,
      "cwd": "${workspaceFolder}/Backend"
    }
  ]
}
```

3. Set breakpoints and press F5

#### Using pdb

```python
import pdb; pdb.set_trace()
```

### Frontend Debugging

#### Using VS Code

1. Install Debugger for Chrome extension
2. Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "chrome",
      "request": "launch",
      "name": "Launch Chrome",
      "url": "http://localhost:5173",
      "webRoot": "${workspaceFolder}/Frontend"
    }
  ]
}
```

#### Using Browser DevTools

1. Open Chrome DevTools (F12)
2. Go to Sources tab
3. Set breakpoints in code
4. Reload page to trigger breakpoints

## Database Management

### Running Migrations

```bash
cd Backend

# Create new migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

### Database Queries

```bash
# Connect to PostgreSQL
psql -U jobspy -d jobspy -h localhost

# Common queries
SELECT * FROM users;
SELECT * FROM jobs;
SELECT * FROM alerts;
```

### Database Backup

```bash
# Backup database
pg_dump -U jobspy -d jobspy > backup.sql

# Restore database
psql -U jobspy -d jobspy < backup.sql
```

## Environment Variables

### Backend (.env)

```
# Application
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=DEBUG

# Database
DATABASE_URL=postgresql://jobspy:jobspy@localhost:5432/jobspy

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# CORS
CORS_ORIGINS=["http://localhost:5173"]

# Scraping
SCRAPING_ENABLED=True
SCRAPING_INTERVAL=3600
```

### Frontend (.env.local)

```
VITE_API_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
VITE_LOG_LEVEL=debug
```

## Common Issues and Solutions

### Issue: Port Already in Use

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Issue: Database Connection Error

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Check connection string in .env
# Verify database exists
psql -U jobspy -d jobspy -h localhost
```

### Issue: Redis Connection Error

```bash
# Check Redis is running
docker ps | grep redis

# Test Redis connection
redis-cli ping
```

### Issue: Module Not Found

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Clear pip cache
pip cache purge
```

### Issue: Frontend Build Errors

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf .vite
```

## Git Workflow

### Creating a Feature Branch

```bash
# Update main branch
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: add your feature"

# Push to remote
git push origin feature/your-feature-name
```

### Creating a Pull Request

1. Push your branch to GitHub
2. Go to repository on GitHub
3. Click "New Pull Request"
4. Select your branch
5. Add description and submit

### Code Review Process

1. Request review from team members
2. Address feedback
3. Update commits
4. Merge when approved

## Performance Profiling

### Backend Profiling

```bash
# Using cProfile
python -m cProfile -s cumulative app/main.py

# Using py-spy
pip install py-spy
py-spy record -o profile.svg -- python app/main.py
```

### Frontend Profiling

1. Open Chrome DevTools
2. Go to Performance tab
3. Click Record
4. Perform actions
5. Click Stop
6. Analyze results

## Documentation

### Generating API Documentation

```bash
# FastAPI auto-generates Swagger UI at /docs
# ReDoc at /redoc
# Export OpenAPI spec
curl http://localhost:8000/openapi.json > openapi.json
```

### Generating Code Documentation

```bash
# Using Sphinx
cd docs
sphinx-build -b html . _build
```

## Useful Commands

### Backend

```bash
# Run specific test
pytest tests/test_auth.py::test_login -v

# Run with specific marker
pytest -m "not slow" -v

# Generate coverage report
pytest --cov=app --cov-report=html

# Run linting
black app/ && isort app/ && pylint app/
```

### Frontend

```bash
# Build for production
npm run build

# Preview production build
npm run preview

# Analyze bundle size
npm run build -- --analyze
```

### Docker

```bash
# Build images
docker-compose build

# View logs
docker-compose logs -f service-name

# Execute command in container
docker-compose exec backend bash

# Remove all containers
docker-compose down -v
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vue.js Documentation](https://vuejs.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [Celery Documentation](https://docs.celeryproject.io/)
- [Docker Documentation](https://docs.docker.com/)
- [Git Documentation](https://git-scm.com/doc)

## Getting Help

- Check existing issues on GitHub
- Ask in team Slack channel
- Review code comments and documentation
- Pair program with team members
- Check project wiki for additional guides

## Next Steps

1. Set up your development environment
2. Run tests to verify setup
3. Create a feature branch
4. Make your first contribution
5. Submit a pull request

Welcome to the JobSpy development team!
