# JobSpy Web Application - System Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER BROWSER                                │
│                  (http://localhost:5173)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    HTTP/REST (JSON)
                             │
        ┌────────────────────┴────────────────────┐
        │                                         │
        ▼                                         ▼
┌──────────────────────┐              ┌──────────────────────┐
│   FRONTEND (Vue 3)   │              │  BACKEND (FastAPI)   │
│  Port: 5173          │              │  Port: 8000          │
│  ├─ Pages            │              │  ├─ Routers          │
│  ├─ Components       │              │  ├─ Models           │
│  ├─ Stores (Pinia)   │              │  ├─ Services         │
│  ├─ Services (API)   │              │  ├─ Repositories     │
│  └─ Styles (Tailwind)│              │  └─ Middleware       │
└──────────────────────┘              └──────┬───────────────┘
                                             │
                                    Database/Cache
                                             │
                        ┌────────────────────┼────────────────────┐
                        │                    │                    │
                        ▼                    ▼                    ▼
                   ┌─────────┐          ┌─────────┐          ┌─────────┐
                   │PostgreSQL│          │ Redis   │          │ Celery  │
                   │Database  │          │ Cache   │          │ Tasks   │
                   └─────────┘          └─────────┘          └─────────┘
```

## Frontend Architecture (Vue 3 + TypeScript)

### Directory Structure
```
Frontend/src/
├── pages/                    # Page components (routed)
│   ├── auth/
│   │   ├── LoginPage.vue
│   │   └── RegisterPage.vue
│   ├── HomePage.vue
│   ├── JobSearchPage.vue
│   ├── JobDetailsPage.vue
│   ├── SavedJobsPage.vue
│   ├── AlertsPage.vue
│   ├── ProfilePage.vue
│   └── NotFoundPage.vue
│
├── components/               # Reusable components
│   ├── layout/
│   │   ├── AppHeader.vue
│   │   ├── AppFooter.vue
│   │   ├── MainLayout.vue
│   │   ├── AuthLayout.vue
│   │   └── ThemeToggle.vue
│   ├── cards/
│   │   ├── JobCard.vue
│   │   ├── AlertCard.vue
│   │   └── StatsCard.vue
│   ├── forms/
│   │   ├── FormInput.vue
│   │   ├── FormSelect.vue
│   │   ├── FormCheckbox.vue
│   │   └── FormButton.vue
│   ├── search/
│   │   ├── SearchBar.vue
│   │   ├── FilterPanel.vue
│   │   └── Pagination.vue
│   └── common/
│       ├── Toast.vue
│       └── ToastContainer.vue
│
├── stores/                   # Pinia state management
│   ├── auth.ts              # Authentication state
│   ├── jobs.ts              # Jobs, saved jobs, alerts state
│   └── ui.ts                # UI state (toasts, modals)
│
├── services/
│   └── api.ts               # Axios API client
│
├── types/
│   └── index.ts             # TypeScript interfaces
│
├── styles/
│   └── index.css            # Global styles
│
├── router/                  # Vue Router configuration
├── layouts/                 # Layout components
└── main.ts                  # Application entry point
```

### Data Flow
```
User Action (Click, Form Submit)
    ↓
Component Event Handler
    ↓
Pinia Store Action
    ↓
API Service (axios)
    ↓
HTTP Request to Backend
    ↓
Backend Response
    ↓
Store State Update
    ↓
Component Re-render
    ↓
UI Update
```

### Key Technologies
- **Vue 3**: Progressive JavaScript framework
- **TypeScript**: Type-safe JavaScript
- **Pinia**: State management (Vuex alternative)
- **Axios**: HTTP client
- **Tailwind CSS**: Utility-first CSS framework
- **Vite**: Build tool and dev server

## Backend Architecture (FastAPI + SQLAlchemy)

### Directory Structure
```
Backend/app/
├── main.py                  # FastAPI application entry point
│
├── core/                    # Core configuration
│   ├── config.py           # Settings from environment
│   ├── database.py         # Database connection
│   ├── redis.py            # Redis connection
│   ├── celery.py           # Celery configuration
│   ├── logging.py          # Logging setup
│   └── __init__.py
│
├── models/                  # SQLAlchemy ORM models
│   ├── user.py             # User model
│   ├── job.py              # Job model
│   ├── saved_job.py        # Saved job model
│   ├── alert.py            # Alert model
│   ├── search_history.py   # Search history model
│   └── __init__.py
│
├── schemas/                 # Pydantic request/response schemas
│   ├── user.py
│   ├── job.py
│   ├── saved_job.py
│   ├── alert.py
│   ├── search_history.py
│   └── __init__.py
│
├── repositories/            # Data access layer
│   ├── user_repo.py
│   ├── job_repo.py
│   ├── saved_job_repo.py
│   ├── alert_repo.py
│   ├── search_history_repo.py
│   └── __init__.py
│
├── services/               # Business logic layer
│   ├── auth_service.py
│   ├── search_service.py
│   ├── scraping_service.py
│   ├── alert_service.py
│   ├── email_service.py
│   └── __init__.py
│
├── routers/                # API endpoints
│   ├── auth.py            # Authentication endpoints
│   ├── users.py           # User endpoints
│   ├── jobs.py            # Job search endpoints
│   ├── saved_jobs.py      # Saved jobs endpoints
│   ├── alerts.py          # Alerts endpoints
│   └── __init__.py
│
├── utils/                  # Utility functions
│   ├── security.py        # JWT, password hashing
│   └── __init__.py
│
├── migrations/             # Alembic database migrations
│   ├── env.py
│   ├── script.py.mako
│   ├── versions/
│   └── __init__.py
│
├── tasks.py               # Celery background tasks
└── __init__.py
```

### Request Flow
```
HTTP Request
    ↓
CORS Middleware (validate origin)
    ↓
Router (match endpoint)
    ↓
Endpoint Handler
    ↓
Service Layer (business logic)
    ↓
Repository Layer (database access)
    ↓
Database Query
    ↓
Response Schema (Pydantic validation)
    ↓
HTTP Response (JSON)
```

### Key Technologies
- **FastAPI**: Modern Python web framework
- **Uvicorn**: ASGI server
- **SQLAlchemy**: ORM for database
- **Pydantic**: Data validation
- **PostgreSQL**: Primary database
- **Redis**: Caching and Celery broker
- **Celery**: Background job queue
- **JWT**: Authentication tokens

## API Endpoints

### Authentication (`/api/v1/auth`)
```
POST   /register          - Register new user
POST   /login             - Login user
POST   /refresh           - Refresh access token
POST   /logout            - Logout user
```

### Jobs (`/api/v1/jobs`)
```
GET    /                  - Search jobs (with filters)
GET    /{id}              - Get job details
POST   /search            - Advanced search
```

### Saved Jobs (`/api/v1/saved-jobs`)
```
GET    /                  - Get user's saved jobs
POST   /                  - Save a job
DELETE /{id}              - Remove saved job
```

### Alerts (`/api/v1/alerts`)
```
GET    /                  - Get user's alerts
POST   /                  - Create alert
DELETE /{id}              - Delete alert
```

### Users (`/api/v1/users`)
```
GET    /me                - Get current user profile
PUT    /me                - Update profile
DELETE /me                - Delete account
```

## Authentication Flow

### Login Process
```
1. User enters email/password
2. Frontend sends POST /api/v1/auth/login
3. Backend verifies credentials
4. Backend generates JWT tokens:
   - access_token (short-lived, 1 hour)
   - refresh_token (long-lived, 7 days)
5. Frontend stores tokens in localStorage
6. Frontend adds Authorization header to all requests:
   Authorization: Bearer <access_token>
```

### Token Refresh
```
1. Access token expires
2. Frontend detects 401 response
3. Frontend sends POST /api/v1/auth/refresh with refresh_token
4. Backend validates refresh_token
5. Backend generates new access_token
6. Frontend retries original request with new token
```

## State Management (Pinia)

### Auth Store (`stores/auth.ts`)
```typescript
State:
  - user: User | null
  - token: string | null
  - isAuthenticated: boolean
  - loading: boolean

Actions:
  - login(email, password)
  - register(email, password, name)
  - logout()
  - refreshToken()
  - fetchUser()
```

### Jobs Store (`stores/jobs.ts`)
```typescript
State:
  - jobs: Job[]
  - savedJobs: SavedJob[]
  - alerts: Alert[]
  - loading: boolean
  - filters: SearchFilters

Actions:
  - searchJobs(query, filters)
  - getJobDetails(id)
  - addSavedJob(jobId)
  - removeSavedJob(jobId)
  - fetchSavedJobs()
  - createAlert(criteria)
  - deleteAlert(id)
  - fetchAlerts()
```

### UI Store (`stores/ui.ts`)
```typescript
State:
  - toasts: Toast[]
  - theme: 'light' | 'dark'
  - sidebarOpen: boolean

Actions:
  - showToast(message, type)
  - removeToast(id)
  - toggleTheme()
  - toggleSidebar()
```

## Database Schema

### Users Table
```sql
users
├── id (UUID, PK)
├── email (String, UNIQUE)
├── hashed_password (String)
├── full_name (String)
├── is_active (Boolean)
├── created_at (DateTime)
└── updated_at (DateTime)
```

### Jobs Table
```sql
jobs
├── id (UUID, PK)
├── title (String)
├── company (String)
├── location (String)
├── description (Text)
├── salary_min (Float)
├── salary_max (Float)
├── job_type (String)
├── source (String)
├── source_url (String)
├── posted_at (DateTime)
├── created_at (DateTime)
└── updated_at (DateTime)
```

### Saved Jobs Table
```sql
saved_jobs
├── id (UUID, PK)
├── user_id (UUID, FK → users)
├── job_id (UUID, FK → jobs)
├── created_at (DateTime)
└── updated_at (DateTime)
```

### Alerts Table
```sql
alerts
├── id (UUID, PK)
├── user_id (UUID, FK → users)
├── title (String)
├── keywords (String[])
├── location (String)
├── job_type (String)
├── is_active (Boolean)
├── created_at (DateTime)
└── updated_at (DateTime)
```

## Environment Configuration

### Frontend (.env)
```
VITE_API_BASE_URL=http://localhost:8000/api
```

### Backend (.env)
```
DEBUG=True
ENVIRONMENT=development
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/jobspy_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
```

## Deployment Architecture

### Development
```
Local Machine
├── Frontend (npm run dev) → http://localhost:5173
└── Backend (uvicorn) → http://localhost:8000
```

### Production
```
Docker Compose / Kubernetes
├── Frontend Container (Nginx)
├── Backend Container (Uvicorn)
├── PostgreSQL Container
├── Redis Container
└── Celery Worker Container
```

## Security Considerations

1. **CORS**: Configured to allow only frontend origin
2. **JWT**: Tokens signed with SECRET_KEY
3. **Password**: Hashed with bcrypt
4. **HTTPS**: Required in production
5. **Rate Limiting**: Implemented on API endpoints
6. **Input Validation**: Pydantic schemas validate all inputs
7. **SQL Injection**: Protected by SQLAlchemy ORM

## Performance Optimization

1. **Caching**: Redis for frequently accessed data
2. **Database Indexing**: Indexes on email, job_id, user_id
3. **Pagination**: Large result sets paginated
4. **Async/Await**: Non-blocking I/O operations
5. **Connection Pooling**: Database connection pool
6. **Lazy Loading**: Components loaded on demand

## Monitoring & Logging

1. **Application Logs**: Structured JSON logging
2. **Error Tracking**: Exception handlers with detailed info
3. **Performance Metrics**: Request/response times
4. **Health Checks**: `/health` endpoint for monitoring

---

**Status**: Architecture is complete and ready for development!
