# JobSpy API Reference

## Overview

JobSpy provides a RESTful API for job search, management, and alerts. All API requests require authentication via JWT tokens.

**Base URL**: `https://api.jobspy.com/api/v1`

**API Documentation**: Available at `/docs` (Swagger UI) and `/redoc` (ReDoc)

## Authentication

### JWT Token

All API requests require a JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### Obtaining a Token

**Endpoint**: `POST /auth/login`

```bash
curl -X POST https://api.jobspy.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Refreshing a Token

**Endpoint**: `POST /auth/refresh`

```bash
curl -X POST https://api.jobspy.com/api/v1/auth/refresh \
  -H "Authorization: Bearer <refresh_token>"
```

## Authentication Endpoints

### Register User

**Endpoint**: `POST /auth/register`

**Request**:
```json
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe"
}
```

**Response** (201 Created):
```json
{
  "id": "user_123",
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Login

**Endpoint**: `POST /auth/login`

**Request**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Logout

**Endpoint**: `POST /auth/logout`

**Response** (200 OK):
```json
{
  "message": "Successfully logged out"
}
```

## Jobs Endpoints

### Search Jobs

**Endpoint**: `GET /jobs/search`

**Query Parameters**:
- `q` (string): Search query
- `location` (string): Job location
- `salary_min` (integer): Minimum salary
- `salary_max` (integer): Maximum salary
- `job_type` (string): Job type (full-time, part-time, contract, freelance)
- `experience_level` (string): Experience level (entry, mid, senior, executive)
- `page` (integer): Page number (default: 1)
- `limit` (integer): Results per page (default: 20, max: 100)
- `sort` (string): Sort order (recent, relevant, salary_high, salary_low)

**Example**:
```bash
curl -X GET "https://api.jobspy.com/api/v1/jobs/search?q=python&location=New%20York&salary_min=100000&page=1&limit=20" \
  -H "Authorization: Bearer <token>"
```

**Response** (200 OK):
```json
{
  "total": 150,
  "page": 1,
  "limit": 20,
  "results": [
    {
      "id": "job_123",
      "title": "Senior Python Developer",
      "company": "Tech Corp",
      "location": "New York, NY",
      "salary_min": 120000,
      "salary_max": 160000,
      "job_type": "full-time",
      "experience_level": "senior",
      "description": "We are looking for...",
      "posted_date": "2024-01-15T10:30:00Z",
      "source": "linkedin",
      "url": "https://example.com/job/123"
    }
  ]
}
```

### Get Job Details

**Endpoint**: `GET /jobs/{job_id}`

**Example**:
```bash
curl -X GET "https://api.jobspy.com/api/v1/jobs/job_123" \
  -H "Authorization: Bearer <token>"
```

**Response** (200 OK):
```json
{
  "id": "job_123",
  "title": "Senior Python Developer",
  "company": "Tech Corp",
  "location": "New York, NY",
  "salary_min": 120000,
  "salary_max": 160000,
  "job_type": "full-time",
  "experience_level": "senior",
  "description": "We are looking for...",
  "requirements": ["Python", "FastAPI", "PostgreSQL"],
  "benefits": ["Health Insurance", "401k", "Remote Work"],
  "posted_date": "2024-01-15T10:30:00Z",
  "source": "linkedin",
  "url": "https://example.com/job/123",
  "company_rating": 4.5,
  "company_reviews_count": 250
}
```

### Get Job Statistics

**Endpoint**: `GET /jobs/stats`

**Query Parameters**:
- `location` (string): Filter by location
- `job_type` (string): Filter by job type

**Example**:
```bash
curl -X GET "https://api.jobspy.com/api/v1/jobs/stats?location=New%20York" \
  -H "Authorization: Bearer <token>"
```

**Response** (200 OK):
```json
{
  "total_jobs": 5000,
  "average_salary": 125000,
  "salary_range": {
    "min": 50000,
    "max": 300000
  },
  "top_companies": [
    {"name": "Tech Corp", "count": 150},
    {"name": "Innovation Inc", "count": 120}
  ],
  "top_skills": [
    {"skill": "Python", "count": 800},
    {"skill": "JavaScript", "count": 750}
  ],
  "job_types": {
    "full-time": 4000,
    "part-time": 600,
    "contract": 300,
    "freelance": 100
  }
}
```

## Saved Jobs Endpoints

### Save a Job

**Endpoint**: `POST /saved-jobs`

**Request**:
```json
{
  "job_id": "job_123",
  "notes": "Interesting opportunity"
}
```

**Response** (201 Created):
```json
{
  "id": "saved_job_123",
  "job_id": "job_123",
  "user_id": "user_123",
  "notes": "Interesting opportunity",
  "rating": null,
  "saved_at": "2024-01-15T10:30:00Z"
}
```

### Get Saved Jobs

**Endpoint**: `GET /saved-jobs`

**Query Parameters**:
- `page` (integer): Page number (default: 1)
- `limit` (integer): Results per page (default: 20)
- `sort` (string): Sort order (recent, rating, salary)

**Example**:
```bash
curl -X GET "https://api.jobspy.com/api/v1/saved-jobs?page=1&limit=20" \
  -H "Authorization: Bearer <token>"
```

**Response** (200 OK):
```json
{
  "total": 45,
  "page": 1,
  "limit": 20,
  "results": [
    {
      "id": "saved_job_123",
      "job": {
        "id": "job_123",
        "title": "Senior Python Developer",
        "company": "Tech Corp",
        "location": "New York, NY",
        "salary_min": 120000,
        "salary_max": 160000
      },
      "notes": "Interesting opportunity",
      "rating": 5,
      "saved_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Update Saved Job

**Endpoint**: `PUT /saved-jobs/{saved_job_id}`

**Request**:
```json
{
  "notes": "Updated notes",
  "rating": 4
}
```

**Response** (200 OK):
```json
{
  "id": "saved_job_123",
  "job_id": "job_123",
  "notes": "Updated notes",
  "rating": 4,
  "saved_at": "2024-01-15T10:30:00Z"
}
```

### Delete Saved Job

**Endpoint**: `DELETE /saved-jobs/{saved_job_id}`

**Response** (204 No Content)

## Alerts Endpoints

### Create Alert

**Endpoint**: `POST /alerts`

**Request**:
```json
{
  "name": "Python Jobs in NYC",
  "keywords": ["python", "developer"],
  "locations": ["New York, NY"],
  "salary_min": 100000,
  "job_types": ["full-time"],
  "experience_levels": ["mid", "senior"],
  "frequency": "daily",
  "notification_method": "email"
}
```

**Response** (201 Created):
```json
{
  "id": "alert_123",
  "name": "Python Jobs in NYC",
  "keywords": ["python", "developer"],
  "locations": ["New York, NY"],
  "salary_min": 100000,
  "job_types": ["full-time"],
  "experience_levels": ["mid", "senior"],
  "frequency": "daily",
  "notification_method": "email",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Get Alerts

**Endpoint**: `GET /alerts`

**Example**:
```bash
curl -X GET "https://api.jobspy.com/api/v1/alerts" \
  -H "Authorization: Bearer <token>"
```

**Response** (200 OK):
```json
{
  "total": 5,
  "results": [
    {
      "id": "alert_123",
      "name": "Python Jobs in NYC",
      "keywords": ["python", "developer"],
      "locations": ["New York, NY"],
      "frequency": "daily",
      "notification_method": "email",
      "is_active": true,
      "last_triggered": "2024-01-15T08:00:00Z",
      "jobs_matched": 12
    }
  ]
}
```

### Update Alert

**Endpoint**: `PUT /alerts/{alert_id}`

**Request**:
```json
{
  "name": "Updated Alert Name",
  "frequency": "weekly",
  "is_active": false
}
```

**Response** (200 OK):
```json
{
  "id": "alert_123",
  "name": "Updated Alert Name",
  "frequency": "weekly",
  "is_active": false
}
```

### Delete Alert

**Endpoint**: `DELETE /alerts/{alert_id}`

**Response** (204 No Content)

## Users Endpoints

### Get Current User

**Endpoint**: `GET /users/me`

**Example**:
```bash
curl -X GET "https://api.jobspy.com/api/v1/users/me" \
  -H "Authorization: Bearer <token>"
```

**Response** (200 OK):
```json
{
  "id": "user_123",
  "email": "user@example.com",
  "full_name": "John Doe",
  "profile_photo": "https://example.com/photo.jpg",
  "bio": "Software engineer",
  "location": "New York, NY",
  "skills": ["Python", "JavaScript", "PostgreSQL"],
  "experience_level": "senior",
  "preferred_job_types": ["full-time", "remote"],
  "preferred_locations": ["New York, NY", "Remote"],
  "salary_expectations": {
    "min": 120000,
    "max": 200000
  },
  "created_at": "2024-01-01T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Update User Profile

**Endpoint**: `PUT /users/me`

**Request**:
```json
{
  "full_name": "John Doe",
  "bio": "Senior Software Engineer",
  "location": "New York, NY",
  "skills": ["Python", "JavaScript", "PostgreSQL", "FastAPI"],
  "experience_level": "senior",
  "preferred_job_types": ["full-time", "remote"],
  "preferred_locations": ["New York, NY", "Remote"],
  "salary_expectations": {
    "min": 130000,
    "max": 220000
  }
}
```

**Response** (200 OK):
```json
{
  "id": "user_123",
  "email": "user@example.com",
  "full_name": "John Doe",
  "bio": "Senior Software Engineer",
  "location": "New York, NY",
  "skills": ["Python", "JavaScript", "PostgreSQL", "FastAPI"],
  "experience_level": "senior",
  "preferred_job_types": ["full-time", "remote"],
  "preferred_locations": ["New York, NY", "Remote"],
  "salary_expectations": {
    "min": 130000,
    "max": 220000
  },
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Delete User Account

**Endpoint**: `DELETE /users/me`

**Response** (204 No Content)

## Export Endpoints

### Export Saved Jobs

**Endpoint**: `POST /exports/saved-jobs`

**Request**:
```json
{
  "format": "csv",
  "include_notes": true,
  "include_ratings": true
}
```

**Response** (200 OK):
```
Content-Type: text/csv
Content-Disposition: attachment; filename="saved_jobs.csv"

job_id,title,company,location,salary_min,salary_max,notes,rating
job_123,Senior Python Developer,Tech Corp,New York NY,120000,160000,Interesting opportunity,5
```

### Export Search Results

**Endpoint**: `POST /exports/search-results`

**Request**:
```json
{
  "query": "python",
  "location": "New York",
  "format": "json"
}
```

**Response** (200 OK):
```json
{
  "query": "python",
  "location": "New York",
  "total_results": 150,
  "exported_at": "2024-01-15T10:30:00Z",
  "jobs": [...]
}
```

## Error Responses

### Error Format

All error responses follow this format:

```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "details": {
    "field": "error details"
  }
}
```

### Common Error Codes

- `400`: Bad Request - Invalid parameters
- `401`: Unauthorized - Missing or invalid token
- `403`: Forbidden - Insufficient permissions
- `404`: Not Found - Resource not found
- `409`: Conflict - Resource already exists
- `422`: Unprocessable Entity - Validation error
- `429`: Too Many Requests - Rate limit exceeded
- `500`: Internal Server Error - Server error

### Example Error Response

```json
{
  "error": "validation_error",
  "message": "Validation failed",
  "details": {
    "email": "Invalid email format",
    "password": "Password must be at least 8 characters"
  }
}
```

## Rate Limiting

API requests are rate limited:

- **Free tier**: 100 requests per hour
- **Premium tier**: 1000 requests per hour

Rate limit headers:
- `X-RateLimit-Limit`: Total requests allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Unix timestamp when limit resets

## Pagination

List endpoints support pagination:

- `page` (integer): Page number (default: 1)
- `limit` (integer): Results per page (default: 20, max: 100)

Response includes:
- `total`: Total number of results
- `page`: Current page
- `limit`: Results per page
- `results`: Array of results

## Sorting

Supported sort options vary by endpoint:

- `recent`: Most recent first
- `relevant`: Most relevant first
- `salary_high`: Highest salary first
- `salary_low`: Lowest salary first
- `rating`: Highest rating first

## Filtering

Most endpoints support filtering via query parameters:

- `q`: Search query
- `location`: Filter by location
- `salary_min`: Minimum salary
- `salary_max`: Maximum salary
- `job_type`: Filter by job type
- `experience_level`: Filter by experience level

## Webhooks

Subscribe to events via webhooks:

- `job.created`: New job posted
- `alert.triggered`: Alert matched jobs
- `saved_job.created`: Job saved
- `saved_job.deleted`: Job unsaved

## SDK Examples

### Python

```python
import requests

headers = {
    "Authorization": f"Bearer {token}"
}

# Search jobs
response = requests.get(
    "https://api.jobspy.com/api/v1/jobs/search",
    params={"q": "python", "location": "New York"},
    headers=headers
)
jobs = response.json()
```

### JavaScript

```javascript
const headers = {
  "Authorization": `Bearer ${token}`
};

// Search jobs
const response = await fetch(
  "https://api.jobspy.com/api/v1/jobs/search?q=python&location=New%20York",
  { headers }
);
const jobs = await response.json();
```

## Support

For API support:
- Email: api-support@jobspy.com
- Documentation: https://docs.jobspy.com
- Status Page: https://status.jobspy.com
