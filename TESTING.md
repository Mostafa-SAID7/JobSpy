# JobSpy Testing Documentation

## Quick Start

### Frontend Tests
```bash
cd Frontend
npm run test              # Run all tests
npm run test -- --watch  # Watch mode
npm run test -- --coverage  # With coverage
```

### Backend Tests
```bash
cd Backend
pytest                   # Run all tests
pytest -v               # Verbose output
pytest --cov=app        # With coverage
```

## Test Structure Overview

### Frontend (`Frontend/src/`)
- **Components**: Form inputs, navigation, cards
- **Pages**: Search, alerts, saved jobs, profile
- **Stores**: Authentication, jobs, preferences, UI
- **Services**: API client, utilities

### Backend (`Backend/tests/`)
- **Unit**: Repositories, services, endpoints
- **Integration**: Complete workflows
- **Security**: Auth, CSRF, encryption, injection prevention
- **Performance**: Load, stress, endurance tests
- **Properties**: Hypothesis-based property tests
- **Caching**: Cache invalidation and consistency

## Test Files Created

### Frontend
```
Frontend/src/
├── components/forms/__tests__/FormInput.test.ts
├── components/layout/__tests__/Navigation.test.ts
├── pages/__tests__/
│   ├── AlertsPage.test.ts (existing)
│   └── JobSearchPage.test.ts
├── stores/__tests__/
│   ├── auth.test.ts
│   └── jobs.test.ts
└── services/__tests__/api.test.ts
```

### Backend
```
Backend/tests/
├── unit/
│   ├── test_users_endpoints.py (existing)
│   ├── test_repositories.py
│   └── test_services.py
├── integration/
│   ├── test_job_workflow.py
│   └── test_alert_workflow.py
└── conftest.py (updated)
```

## Running Tests

### All Tests
```bash
# Frontend
cd Frontend && npm run test

# Backend
cd Backend && pytest

# Both (from root)
bash scripts/run-tests.sh
```

### Specific Categories

**Frontend:**
```bash
npm run test -- FormInput.test.ts
npm run test -- stores/__tests__/
npm run test -- --coverage
```

**Backend:**
```bash
pytest tests/unit/
pytest tests/integration/
pytest tests/security/
pytest tests/performance/
pytest --cov=app
```

### Watch Mode
```bash
# Frontend
npm run test -- --watch

# Backend
pytest --watch
```

## Test Coverage

### Frontend Coverage Goals
- Statements: 80%+
- Branches: 75%+
- Functions: 80%+
- Lines: 80%+

### Backend Coverage Goals
- Overall: 85%+
- Critical paths: 95%+
- Security code: 100%
- API endpoints: 90%+

## Key Test Scenarios

### Frontend

**Authentication**
- Login/Register flows
- Token management
- Session restoration
- Logout

**Job Search**
- Search with filters
- Results pagination
- Save/unsave jobs
- Error handling

**Alerts**
- Create/update/delete alerts
- Toggle alert status
- View alert statistics
- Error handling

**Components**
- Form input validation
- Navigation rendering
- Mobile menu toggle
- Loading states

### Backend

**User Management**
- Password change
- Password reset
- Email verification
- Preferences management

**Job Operations**
- Search jobs
- Save/unsave jobs
- Get job details
- Filter and sort

**Alerts**
- Create alerts
- Update alert frequency
- Toggle active status
- Delete alerts
- Check for new jobs

**Security**
- Authorization checks
- CSRF protection
- SQL injection prevention
- XSS prevention
- Encryption

## Debugging Tests

### Frontend
```bash
# Verbose output
npm run test -- --reporter=verbose

# Debug in browser
npm run test -- --inspect-brk

# Single file
npm run test -- FormInput.test.ts
```

### Backend
```bash
# Verbose output
pytest -vv

# With print statements
pytest -s

# Debug with pdb
pytest --pdb

# Single test
pytest tests/unit/test_users_endpoints.py::TestPasswordChangeEndpoint::test_change_password_success
```

## CI/CD Integration

Tests run automatically on:
- Pull requests
- Commits to main branch
- Pre-deployment checks

All tests must pass before merging!

## Best Practices

1. **Write tests first**: Use TDD approach
2. **Keep tests isolated**: No dependencies between tests
3. **Mock external services**: Don't call real APIs
4. **Use descriptive names**: Test names explain what's tested
5. **Test edge cases**: Include boundary conditions
6. **Maintain fixtures**: Keep test data organized
7. **Review coverage**: Aim for high coverage on critical paths
8. **Update tests**: Keep tests in sync with code changes

## Common Issues & Solutions

### Frontend

**Issue**: Tests timeout
- **Solution**: Increase timeout in vitest.config.ts

**Issue**: Component not rendering
- **Solution**: Check props and stubs are correct

**Issue**: Store state not updating
- **Solution**: Ensure `setActivePinia(createPinia())` in beforeEach

### Backend

**Issue**: Async test timeout
- **Solution**: Increase timeout in pytest.ini

**Issue**: Database locked
- **Solution**: Ensure proper cleanup in fixtures

**Issue**: Import errors
- **Solution**: Check PYTHONPATH in conftest.py

## Performance Benchmarks

Expected execution times:
- Frontend unit tests: < 5 seconds
- Backend unit tests: < 5 seconds
- Backend integration tests: < 30 seconds
- All tests: < 2 minutes

## Documentation

- **Frontend**: See `Frontend/TEST_GUIDE.md`
- **Backend**: See `Backend/TEST_GUIDE.md`

## Next Steps

1. Run all tests to verify setup
2. Review coverage reports
3. Add tests for new features
4. Maintain test quality
5. Monitor performance

## Support

For issues or questions:
1. Check the relevant TEST_GUIDE.md
2. Review test examples
3. Check CI/CD logs
4. Consult team documentation
