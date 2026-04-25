# Backend Testing Guide

## Overview
This guide covers all backend tests for the JobSpy API.

## Test Structure

```
Backend/tests/
├── unit/
│   ├── test_users_endpoints.py
│   ├── test_repositories.py
│   ├── test_services.py
│   ├── cache/
│   └── ttl/
├── integration/
│   ├── test_job_workflow.py
│   ├── test_alert_workflow.py
│   ├── alerts/
│   ├── auth/
│   ├── saved_jobs/
│   ├── search/
│   └── users/
├── security/
│   ├── test_authorization_and_access_control.py
│   ├── test_csrf_protection.py
│   ├── test_encryption_and_secrets.py
│   ├── test_sql_injection_prevention.py
│   └── test_xss_prevention.py
├── performance/
│   ├── load/
│   ├── stress/
│   └── endurance/
├── properties/
│   ├── data/
│   ├── saved_jobs/
│   ├── search/
│   └── user/
└── caching/
    ├── invalidation/
    ├── search/
    └── stats/
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test category
```bash
# Unit tests
pytest Backend/tests/unit/

# Integration tests
pytest Backend/tests/integration/

# Security tests
pytest Backend/tests/security/

# Performance tests
pytest Backend/tests/performance/
```

### Run specific test file
```bash
pytest Backend/tests/unit/test_users_endpoints.py
```

### Run specific test class
```bash
pytest Backend/tests/unit/test_users_endpoints.py::TestPasswordChangeEndpoint
```

### Run specific test
```bash
pytest Backend/tests/unit/test_users_endpoints.py::TestPasswordChangeEndpoint::test_change_password_success
```

### Run with coverage
```bash
pytest --cov=app --cov-report=html
```

### Run with verbose output
```bash
pytest -v
```

### Run with markers
```bash
pytest -m asyncio
```

## Test Categories

### 1. Unit Tests

#### test_users_endpoints.py
- **TestPasswordChangeEndpoint**: Password change functionality
  - Successful password change
  - Wrong current password
  - Not authenticated
  - User not found

- **TestPasswordResetEndpoints**: Password reset flow
  - Request password reset
  - Confirm password reset
  - Invalid/expired tokens

- **TestEmailVerificationEndpoints**: Email verification
  - Send verification email
  - Verify email
  - Already verified
  - Invalid/expired tokens

- **TestUserPreferencesEndpoints**: User preferences
  - Get preferences
  - Update preferences
  - Invalid data

- **TestUserStatsEndpoint**: User statistics
  - Get stats
  - Correct counts
  - Authentication

- **TestErrorHandling**: Error scenarios
  - Invalid JSON payload
  - Missing required fields
  - Invalid email format

- **TestCacheInvalidation**: Cache management
  - Cache invalidated after password change
  - Cache invalidated after preferences update

#### test_repositories.py
- **TestUserRepository**: User data access
  - Create user
  - Get by email/ID
  - Update user
  - Delete user

- **TestJobRepository**: Job data access
  - Create job
  - Search jobs
  - Get by ID
  - Get by source

- **TestSavedJobRepository**: Saved jobs data access
  - Save job
  - Get user saved jobs
  - Unsave job
  - Check if saved

#### test_services.py
- **TestSearchService**: Job search service
  - Search jobs
  - Search with filters
  - Search multiple sources

- **TestAlertService**: Alert management service
  - Create alert
  - Update alert
  - Delete alert
  - Get user alerts
  - Toggle alert
  - Check for new jobs

### 2. Integration Tests

#### test_job_workflow.py
- Search and save job workflow
- Get saved jobs workflow
- Unsave job workflow
- Search with filters
- Job details retrieval

#### test_alert_workflow.py
- Create and manage alerts
- Update alert
- Toggle alert active status
- Delete alert
- Alert validation
- Get alert statistics

### 3. Security Tests

#### test_authorization_and_access_control.py
- User can only access own data
- Admin access control
- Role-based access

#### test_csrf_protection.py
- CSRF token validation
- Token expiration

#### test_encryption_and_secrets.py
- Password hashing
- Secret key management
- Token encryption

#### test_sql_injection_prevention.py
- SQL injection prevention
- Query parameterization

#### test_xss_prevention.py
- XSS prevention
- Input sanitization

### 4. Performance Tests

#### Load Tests
- Concurrent user requests
- Response time under load

#### Stress Tests
- System behavior under extreme load
- Resource limits

#### Endurance Tests
- Long-running stability
- Memory leaks

### 5. Property-Based Tests

Using Hypothesis for property-based testing:
- Data validation properties
- Search functionality properties
- User management properties

### 6. Caching Tests

#### Invalidation Tests
- Cache invalidation on updates
- Cache consistency

#### Search Caching
- Search result caching
- Cache hit rates

#### Stats Caching
- Statistics caching
- Cache expiration

## Writing New Tests

### Unit Test Template
```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
class TestMyFeature:
    """Test my feature"""
    
    async def test_something(self, db: AsyncSession):
        """Test description"""
        # Arrange
        data = {"key": "value"}
        
        # Act
        result = await my_function(data)
        
        # Assert
        assert result is not None
```

### Integration Test Template
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
class TestMyWorkflow:
    """Test my workflow"""
    
    async def test_workflow(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict
    ):
        """Test workflow description"""
        response = await client.get(
            "/endpoint",
            headers=auth_headers
        )
        
        assert response.status_code == 200
```

## Best Practices

1. **Use fixtures**: Leverage pytest fixtures for setup/teardown
2. **Mock external services**: Use `unittest.mock` for external APIs
3. **Test edge cases**: Include boundary conditions
4. **Use descriptive names**: Test names should explain what's tested
5. **Keep tests isolated**: Each test should be independent
6. **Use async/await**: Properly handle async code
7. **Test error paths**: Include error scenarios
8. **Use markers**: Organize tests with pytest markers

## Fixtures

### Available Fixtures
- `db`: AsyncSession for database access
- `test_user`: Pre-created test user
- `auth_headers`: Authorization headers for authenticated requests
- `client`: AsyncClient for API testing

### Creating Custom Fixtures
```python
@pytest.fixture
async def my_fixture():
    """My custom fixture"""
    setup_code()
    yield resource
    cleanup_code()
```

## Debugging Tests

### Run with print statements
```bash
pytest -s Backend/tests/unit/test_users_endpoints.py
```

### Run with pdb debugger
```bash
pytest --pdb Backend/tests/unit/test_users_endpoints.py
```

### Run with detailed output
```bash
pytest -vv Backend/tests/unit/test_users_endpoints.py
```

## Coverage Goals

- **Overall**: 85%+
- **Critical paths**: 95%+
- **Security code**: 100%
- **API endpoints**: 90%+

## CI/CD Integration

Tests run automatically on:
- Pull requests
- Commits to main branch
- Pre-deployment checks

Ensure all tests pass before merging!

## Performance Benchmarks

Expected test execution times:
- Unit tests: < 5 seconds
- Integration tests: < 30 seconds
- Security tests: < 60 seconds
- All tests: < 2 minutes

## Troubleshooting

### Issue: Async test timeout
**Solution**: Increase timeout in pytest.ini or use `pytest-asyncio` markers

### Issue: Database locked
**Solution**: Ensure proper cleanup in fixtures

### Issue: Import errors
**Solution**: Check PYTHONPATH and sys.path in conftest.py

### Issue: Fixture not found
**Solution**: Ensure fixture is defined in conftest.py or same file
