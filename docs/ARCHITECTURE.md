# JobSpy System Architecture

## Overview

JobSpy is a modern, scalable job search platform built with a microservices-inspired architecture. This document describes the system design, components, and data flow.

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Vue.js 3 + Vite + Tailwind CSS                          │   │
│  │  - Job Search Page                                       │   │
│  │  - Saved Jobs Management                                 │   │
│  │  - Alerts Configuration                                  │   │
│  │  - User Profile                                          │   │
│  │  - Authentication                                        │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway / Nginx                         │
│  - Request routing                                              │
│  - SSL/TLS termination                                          │
│  - Rate limiting                                                │
│  - Load balancing                                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Backend API Layer                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  FastAPI + Python 3.11                                   │   │
│  │  - Authentication Router                                 │   │
│  │  - Jobs Router                                           │   │
│  │  - Saved Jobs Router                                     │   │
│  │  - Alerts Router                                         │   │
│  │  - Users Router                                          │   │
│  │  - Export Router                                         │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Business Logic Layer                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Services                                                │   │
│  │  - AuthService (JWT, password hashing)                   │   │
│  │  - JobsService (search, filtering, pagination)           │   │
│  │  - AlertsService (alert management)                      │   │
│  │  - EmailService (notifications)                          │   │
│  │  - ScrapingService (job data collection)                 │   │
│  │  - SearchService (advanced search)                       │   │
│  │  - ExportService (data export)                           │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Data Access Layer                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Repositories (SQLAlchemy ORM)                           │   │
│  │  - UserRepository                                        │   │
│  │  - JobRepository                                         │   │
│  │  - SavedJobRepository                                    │   │
│  │  - AlertRepository                                       │   │
│  │  - SearchHistoryRepository                               │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Data Storage Layer                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  PostgreSQL Database                                     │   │
│  │  - Users table                                           │   │
│  │  - Jobs table                                            │   │
│  │  - SavedJobs table                                        │   │
│  │  - Alerts table                                          │   │
│  │  - SearchHistory table                                   │   │
│  │  - JobSources table                                      │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Redis Cache                                             │   │
│  │  - Job cache                                             │   │
│  │  - Search results cache                                  │   │
│  │  - Session cache                                         │   │
│  │  - Rate limiting cache                                   │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  Background Jobs Layer                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Celery + Redis                                          │   │
│  │  - Scraping tasks (LinkedIn, Indeed, Wuzzuf, Bayt)       │   │
│  │  - Alert checking tasks                                  │   │
│  │  - Email sending tasks                                   │   │
│  │  - Data cleanup tasks                                    │   │
│  │  - Backup tasks                                          │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  External Services Layer                         │
│  - Email service (SMTP)                                         │
│  - Job scraping APIs (LinkedIn, Indeed, Wuzzuf, Bayt)           │
│  - Monitoring (Sentry, DataDog)                                 │
│  - Logging (ELK Stack)                                          │
│  - Cloud storage (S3)                                           │
└─────────────────────────────────────────────────────────────────┘
```

## Component Overview

### Frontend Layer

**Technology**: Vue.js 3, Vite, Tailwind CSS, Pinia

**Responsibilities**:
- User interface rendering
- Form handling and validation
- State management (Pinia stores)
- API communication
- Local storage management
- Real-time updates

**Key Components**:
- Authentication pages (login, register)
- Job search interface
- Saved jobs management
- Alert configuration
- User profile
- Settings

### API Gateway

**Technology**: Nginx

**Responsibilities**:
- Request routing to backend services
- SSL/TLS termination
- Rate limiting
- Load balancing
- Request/response logging
- CORS handling

### Backend API Layer

**Technology**: FastAPI, Python 3.11

**Responsibilities**:
- HTTP request handling
- Request validation
- Response formatting
- Error handling
- Authentication middleware
- API documentation (Swagger/OpenAPI)

**Routers**:
- `auth.py`: Authentication endpoints
- `jobs.py`: Job search and retrieval
- `saved_jobs.py`: Saved jobs management
- `alerts.py`: Alert management
- `users.py`: User profile management
- `exports.py`: Data export functionality

### Business Logic Layer

**Services**:

1. **AuthService**
   - User registration and login
   - JWT token generation and validation
   - Password hashing and verification
   - Refresh token management

2. **JobsService**
   - Job search and filtering
   - Pagination and sorting
   - Job details retrieval
   - Job statistics

3. **AlertsService**
   - Alert creation and management
   - Alert matching logic
   - Alert scheduling
   - Alert notifications

4. **EmailService**
   - Email template rendering
   - SMTP integration
   - Email sending
   - Retry logic

5. **ScrapingService**
   - Job data collection from multiple sources
   - Data normalization
   - Duplicate detection
   - Data validation

6. **SearchService**
   - Advanced search query parsing
   - Search result ranking
   - Search history tracking
   - Search suggestions

7. **ExportService**
   - Data export to multiple formats
   - CSV, PDF, JSON, Excel generation
   - Scheduled exports
   - Cloud storage integration

### Data Access Layer

**Technology**: SQLAlchemy ORM

**Repositories**:
- `UserRepository`: User data access
- `JobRepository`: Job data access
- `SavedJobRepository`: Saved jobs data access
- `AlertRepository`: Alert data access
- `SearchHistoryRepository`: Search history tracking

**Responsibilities**:
- Database query abstraction
- Data validation
- Transaction management
- Query optimization

### Data Storage Layer

**PostgreSQL Database**:
- Primary data store
- ACID compliance
- Relational data modeling
- Indexes for performance
- Backup and recovery

**Redis Cache**:
- Session storage
- Job cache
- Search results cache
- Rate limiting
- Real-time data

### Background Jobs Layer

**Technology**: Celery, Redis

**Tasks**:

1. **Scraping Tasks**
   - LinkedIn job scraping
   - Indeed job scraping
   - Wuzzuf job scraping
   - Bayt job scraping
   - Error handling and retries

2. **Alert Tasks**
   - Alert checking
   - Job matching
   - Email sending
   - Notification delivery

3. **Maintenance Tasks**
   - Data cleanup
   - Statistics updates
   - Cache invalidation
   - Backup execution

4. **Scheduled Tasks**
   - Daily scraping
   - Weekly reports
   - Monthly cleanup
   - Quarterly backups

## Data Flow

### Job Search Flow

```
1. User enters search criteria
   ↓
2. Frontend sends request to API
   ↓
3. API validates input
   ↓
4. Check Redis cache for results
   ↓
5. If cache miss:
   - Query PostgreSQL database
   - Apply filters and sorting
   - Cache results in Redis
   ↓
6. Return results to frontend
   ↓
7. Frontend renders job list
```

### Job Alert Flow

```
1. User creates alert with criteria
   ↓
2. Alert stored in PostgreSQL
   ↓
3. Celery Beat schedules alert check task
   ↓
4. Alert task runs at scheduled time
   ↓
5. Query jobs matching alert criteria
   ↓
6. Compare with previously matched jobs
   ↓
7. If new matches found:
   - Create email notification
   - Send via EmailService
   - Update alert status
   ↓
8. User receives email notification
```

### Job Scraping Flow

```
1. Celery Beat triggers scraping task
   ↓
2. Scraping service connects to job sources
   ↓
3. Fetch job listings from each source
   ↓
4. Normalize job data
   ↓
5. Check for duplicates
   ↓
6. Validate data quality
   ↓
7. Store in PostgreSQL
   ↓
8. Invalidate Redis cache
   ↓
9. Trigger alert checking
```

### Authentication Flow

```
1. User submits login credentials
   ↓
2. API validates credentials
   ↓
3. Query user from database
   ↓
4. Verify password hash
   ↓
5. Generate JWT token
   ↓
6. Return token to frontend
   ↓
7. Frontend stores token in localStorage
   ↓
8. Frontend includes token in API requests
   ↓
9. API validates token on each request
```

## Design Patterns

### Repository Pattern

Abstracts data access logic:
```python
class JobRepository:
    def get_by_id(self, job_id):
        return db.query(Job).filter(Job.id == job_id).first()
    
    def search(self, criteria):
        query = db.query(Job)
        # Apply filters
        return query.all()
```

### Service Layer Pattern

Encapsulates business logic:
```python
class JobsService:
    def __init__(self, job_repo):
        self.job_repo = job_repo
    
    def search_jobs(self, criteria):
        # Business logic
        return self.job_repo.search(criteria)
```

### Dependency Injection

Loose coupling between components:
```python
@app.get("/jobs")
def search_jobs(service: JobsService = Depends()):
    return service.search_jobs(criteria)
```

### Caching Strategy

Multi-level caching:
1. Redis cache for frequently accessed data
2. Database query optimization
3. Frontend local storage for user preferences

### Error Handling

Consistent error responses:
```python
{
    "error": "error_code",
    "message": "Human-readable message",
    "details": {...}
}
```

## Scalability Considerations

### Horizontal Scaling

- **Frontend**: Deploy multiple instances behind load balancer
- **Backend**: Deploy multiple FastAPI instances
- **Database**: Read replicas for scaling reads
- **Cache**: Redis cluster for distributed caching
- **Jobs**: Multiple Celery workers for parallel processing

### Vertical Scaling

- Increase server resources (CPU, RAM)
- Optimize database queries
- Implement caching strategies
- Use connection pooling

### Performance Optimization

1. **Database Optimization**
   - Proper indexing
   - Query optimization
   - Connection pooling
   - Read replicas

2. **Caching Strategy**
   - Redis for hot data
   - Browser caching for static assets
   - CDN for static content

3. **API Optimization**
   - Pagination for large datasets
   - Lazy loading
   - Compression
   - Async operations

4. **Frontend Optimization**
   - Code splitting
   - Lazy loading components
   - Image optimization
   - Minification

## Security Architecture

### Authentication

- JWT tokens for stateless authentication
- Refresh tokens for token rotation
- Password hashing with bcrypt
- Secure token storage

### Authorization

- Role-based access control (RBAC)
- Resource-level permissions
- API endpoint protection
- Data isolation per user

### Data Protection

- Encryption at rest (database)
- Encryption in transit (HTTPS/TLS)
- Secure password storage
- PII data masking

### API Security

- Rate limiting
- CORS configuration
- CSRF protection
- Input validation
- SQL injection prevention
- XSS protection

## Monitoring and Observability

### Logging

- Structured JSON logging
- Centralized logging (ELK Stack)
- Log levels (DEBUG, INFO, WARNING, ERROR)
- Request/response logging

### Metrics

- Application metrics (requests, errors, latency)
- Database metrics (queries, connections)
- Cache metrics (hits, misses)
- Job metrics (success, failure, duration)

### Tracing

- Distributed tracing
- Request flow tracking
- Performance profiling
- Error tracking (Sentry)

### Alerting

- Error rate alerts
- Performance degradation alerts
- Uptime monitoring
- Resource utilization alerts

## Deployment Architecture

### Docker Containerization

- Backend: FastAPI + Gunicorn
- Frontend: Nginx + Vue.js
- Database: PostgreSQL
- Cache: Redis
- Jobs: Celery worker + Celery Beat

### Orchestration

- Docker Compose for local development
- Kubernetes for production (optional)
- Container registry for image storage

### CI/CD Pipeline

- GitHub Actions for automation
- Testing on every commit
- Linting and security scanning
- Automated deployment

## Technology Stack

### Frontend
- Vue.js 3
- Vite
- Tailwind CSS
- Pinia (state management)
- Axios (HTTP client)

### Backend
- FastAPI
- Python 3.11
- SQLAlchemy (ORM)
- Alembic (migrations)
- Pydantic (validation)

### Database
- PostgreSQL
- Redis

### Background Jobs
- Celery
- Redis (broker)

### DevOps
- Docker
- Docker Compose
- GitHub Actions
- Nginx

### Monitoring
- Sentry (error tracking)
- DataDog/New Relic (performance)
- ELK Stack (logging)
- UptimeRobot (uptime)

## Future Enhancements

1. **GraphQL API**: Alternative to REST API
2. **WebSockets**: Real-time job updates
3. **Machine Learning**: Job recommendations
4. **Mobile App**: Native mobile applications
5. **Microservices**: Separate services for different domains
6. **Event Streaming**: Kafka for event-driven architecture
7. **API Gateway**: Kong or similar for advanced routing

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vue.js Documentation](https://vuejs.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [Celery Documentation](https://docs.celeryproject.io/)
- [Docker Documentation](https://docs.docker.com/)
