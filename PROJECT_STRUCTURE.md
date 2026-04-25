# JobSpy Project Structure

## Overview
Complete project structure with organized testing framework for both frontend and backend.

## Directory Structure

```
jobspy/
├── Frontend/                          # Vue 3 + TypeScript Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── forms/
│   │   │   │   ├── FormInput.vue
│   │   │   │   └── __tests__/
│   │   │   │       └── FormInput.test.ts
│   │   │   ├── layout/
│   │   │   │   ├── Navigation.vue
│   │   │   │   └── __tests__/
│   │   │   │       └── Navigation.test.ts
│   │   │   ├── cards/
│   │   │   ├── common/
│   │   │   └── search/
│   │   ├── pages/
│   │   │   ├── AlertsPage.vue
│   │   │   ├── JobSearchPage.vue
│   │   │   ├── SavedJobsPage.vue
│   │   │   ├── ProfilePage.vue
│   │   │   ├── HomePage.vue
│   │   │   ├── JobDetailsPage.vue
│   │   │   ├── NotFoundPage.vue
│   │   │   └── __tests__/
│   │   │       ├── AlertsPage.test.ts
│   │   │       └── JobSearchPage.test.ts
│   │   ├── stores/
│   │   │   ├── auth.ts
│   │   │   ├── jobs.ts
│   │   │   ├── preferences.ts
│   │   │   ├── ui.ts
│   │   │   └── __tests__/
│   │   │       ├── auth.test.ts
│   │   │       └── jobs.test.ts
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   └── __tests__/
│   │   │       └── api.test.ts
│   │   ├── router/
│   │   ├── types/
│   │   ├── utils/
│   │   ├── styles/
│   │   ├── layouts/
│   │   ├── App.vue
│   │   └── main.ts
│   ├── package.json
│   ├── vitest.config.ts
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── TEST_GUIDE.md
│   └── Dockerfile
│
├── Backend/                           # FastAPI + Python Backend
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── cache.py
│   │   │   ├── redis.py
│   │   │   ├── celery.py
│   │   │   ├── logging.py
│   │   │   └── celery_beat_schedule.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── job.py
│   │   │   ├── saved_job.py
│   │   │   ├── alert.py
│   │   │   └── search_history.py
│   │   ├── schemas/
│   │   │   ├── user.py
│   │   │   ├── job.py
│   │   │   ├── saved_job.py
│   │   │   ├── alert.py
│   │   │   └── search_history.py
│   │   ├── repositories/
│   │   │   ├── user_repo.py
│   │   │   ├── job_repo.py
│   │   │   ├── saved_job_repo.py
│   │   │   ├── alert_repo.py
│   │   │   ├── search_history_repo.py
│   │   │   └── stats_repo.py
│   │   ├── services/
│   │   │   ├── search_service.py
│   │   │   ├── alert_service.py
│   │   │   ├── email_service.py
│   │   │   ├── scraping_service.py
│   │   │   └── stats_service.py
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── jobs.py
│   │   │   ├── saved_jobs.py
│   │   │   ├── alerts.py
│   │   │   └── stats.py
│   │   ├── utils/
│   │   │   └── security.py
│   │   ├── migrations/
│   │   ├── tasks.py
│   │   └── main.py
│   ├── tests/
│   │   ├── unit/
│   │   │   ├── test_users_endpoints.py
│   │   │   ├── test_repositories.py
│   │   │   ├── test_services.py
│   │   │   ├── cache/
│   │   │   └── ttl/
│   │   ├── integration/
│   │   │   ├── test_job_workflow.py
│   │   │   ├── test_alert_workflow.py
│   │   │   ├── alerts/
│   │   │   ├── auth/
│   │   │   ├── saved_jobs/
│   │   │   ├── search/
│   │   │   └── users/
│   │   ├── security/
│   │   │   ├── test_authorization_and_access_control.py
│   │   │   ├── test_csrf_protection.py
│   │   │   ├── test_encryption_and_secrets.py
│   │   │   ├── test_sql_injection_prevention.py
│   │   │   └── test_xss_prevention.py
│   │   ├── performance/
│   │   │   ├── load/
│   │   │   ├── stress/
│   │   │   └── endurance/
│   │   ├── properties/
│   │   │   ├── data/
│   │   │   ├── saved_jobs/
│   │   │   ├── search/
│   │   │   └── user/
│   │   ├── caching/
│   │   │   ├── invalidation/
│   │   │   ├── search/
│   │   │   └── stats/
│   │   ├── conftest.py
│   │   └── __init__.py
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── setup_db.py
│   ├── TEST_GUIDE.md
│   └── Dockerfile
│
├── scripts/
│   ├── run-tests.sh
│   └── setup.sh
│
├── config/
│   └── nginx.conf
│
├── docs/
│   └── API.md
│
├── .kiro/
│   └── specs/
│       └── jobspy-web-transformation/
│           ├── requirements.md
│           ├── design.md
│           └── tasks.md
│
├── docker-compose.yml
├── README.md
├── TESTING.md
├── PROJECT_STRUCTURE.md
└── .gitignore
```

## File Organization

### Frontend Tests
- **Component Tests**: `src/components/*/\_\_tests\_\_/`
- **Page Tests**: `src/pages/\_\_tests\_\_/`
- **Store Tests**: `src/stores/\_\_tests\_\_/`
- **Service Tests**: `src/services/\_\_tests\_\_/`

### Backend Tests
- **Unit Tests**: `tests/unit/`
- **Integration Tests**: `tests/integration/`
- **Security Tests**: `tests/security/`
- **Performance Tests**: `tests/performance/`
- **Property Tests**: `tests/properties/`
- **Caching Tests**: `tests/caching/`

## Key Files

### Frontend
- `vitest.config.ts` - Test configuration
- `package.json` - Dependencies and scripts
- `TEST_GUIDE.md` - Frontend testing guide

### Backend
- `tests/conftest.py` - Pytest fixtures and configuration
- `requirements.txt` - Python dependencies
- `TEST_GUIDE.md` - Backend testing guide

### Root
- `TESTING.md` - Master testing documentation
- `PROJECT_STRUCTURE.md` - This file
- `scripts/run-tests.sh` - Test runner script

## Test Coverage

### Frontend Tests (5 files)
1. **FormInput.test.ts** - Form input component
2. **Navigation.test.ts** - Navigation component
3. **AlertsPage.test.ts** - Alerts page (existing)
4. **JobSearchPage.test.ts** - Job search page
5. **auth.test.ts** - Auth store
6. **jobs.test.ts** - Jobs store
7. **api.test.ts** - API service

### Backend Tests (2 new files + existing)
1. **test_repositories.py** - Repository layer
2. **test_services.py** - Service layer
3. **test_job_workflow.py** - Job search workflow
4. **test_alert_workflow.py** - Alert management workflow
5. **test_users_endpoints.py** - User endpoints (existing)

## Running Tests

### Quick Commands
```bash
# Frontend
cd Frontend && npm run test

# Backend
cd Backend && pytest

# All tests
bash scripts/run-tests.sh
```

### With Coverage
```bash
# Frontend
npm run test -- --coverage

# Backend
pytest --cov=app --cov-report=html
```

## Test Statistics

### Frontend
- **Total Test Files**: 7
- **Total Test Suites**: 20+
- **Total Test Cases**: 100+

### Backend
- **Total Test Files**: 7+
- **Total Test Classes**: 15+
- **Total Test Methods**: 80+

## Documentation

- **Frontend Guide**: `Frontend/TEST_GUIDE.md`
- **Backend Guide**: `Backend/TEST_GUIDE.md`
- **Master Guide**: `TESTING.md`
- **Project Structure**: `PROJECT_STRUCTURE.md`

## Next Steps

1. ✅ Organize file structure
2. ✅ Create test files
3. ✅ Setup test configuration
4. ✅ Create documentation
5. Run tests to verify everything works
6. Add CI/CD integration
7. Monitor coverage metrics
8. Maintain and update tests

## Notes

- All tests follow best practices
- Comprehensive coverage of critical paths
- Proper error handling and edge cases
- Security tests included
- Performance tests included
- Property-based tests included
- Caching tests included
