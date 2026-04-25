# Quick Start - Testing

## 🚀 Run All Tests

```bash
bash scripts/run-tests.sh
```

## 📋 Frontend Tests

```bash
cd Frontend

# Run all tests
npm run test

# Watch mode
npm run test -- --watch

# With coverage
npm run test -- --coverage

# Specific test
npm run test -- FormInput.test.ts
```

## 🔧 Backend Tests

```bash
cd Backend

# Run all tests
pytest

# Verbose output
pytest -v

# With coverage
pytest --cov=app --cov-report=html

# Specific category
pytest tests/unit/
pytest tests/integration/
pytest tests/security/
```

## 📊 Test Files Created

### Frontend (7 files)
```
✓ FormInput.test.ts
✓ Navigation.test.ts
✓ JobSearchPage.test.ts
✓ AlertsPage.test.ts (existing)
✓ auth.test.ts
✓ jobs.test.ts
✓ api.test.ts
```

### Backend (7+ files)
```
✓ test_repositories.py
✓ test_services.py
✓ test_job_workflow.py
✓ test_alert_workflow.py
✓ test_users_endpoints.py (existing)
✓ Security tests (5 files)
✓ Performance tests (3 categories)
✓ Property tests (4 categories)
✓ Caching tests (3 categories)
```

## 📚 Documentation

- **Frontend Guide**: `Frontend/TEST_GUIDE.md`
- **Backend Guide**: `Backend/TEST_GUIDE.md`
- **Master Guide**: `TESTING.md`
- **Project Structure**: `PROJECT_STRUCTURE.md`
- **Implementation Checklist**: `IMPLEMENTATION_CHECKLIST.md`

## ✅ What's Tested

### Frontend
- ✅ Form components
- ✅ Navigation
- ✅ Job search page
- ✅ Alerts page
- ✅ Authentication store
- ✅ Jobs store
- ✅ API service

### Backend
- ✅ User repository
- ✅ Job repository
- ✅ Saved job repository
- ✅ Search service
- ✅ Alert service
- ✅ User endpoints
- ✅ Job workflows
- ✅ Alert workflows
- ✅ Security (auth, CSRF, encryption, injection, XSS)
- ✅ Performance (load, stress, endurance)
- ✅ Properties (hypothesis-based)
- ✅ Caching (invalidation, consistency)

## 🎯 Coverage Goals

- Frontend: 80%+
- Backend: 85%+
- Critical paths: 95%+
- Security code: 100%

## 🔍 Debugging

### Frontend
```bash
# Verbose output
npm run test -- --reporter=verbose

# Debug in browser
npm run test -- --inspect-brk
```

### Backend
```bash
# Verbose output
pytest -vv

# With print statements
pytest -s

# Debug with pdb
pytest --pdb
```

## 📈 Performance

Expected execution times:
- Frontend tests: < 5 seconds
- Backend tests: < 5 seconds
- Integration tests: < 30 seconds
- All tests: < 2 minutes

## 🚦 CI/CD Ready

Tests are ready for:
- GitHub Actions
- GitLab CI
- Jenkins
- Any CI/CD platform

## 📝 Key Files

### Configuration
- `Frontend/vitest.config.ts`
- `Backend/tests/conftest.py`

### Automation
- `scripts/run-tests.sh`

### Documentation
- `TESTING.md` (master guide)
- `Frontend/TEST_GUIDE.md`
- `Backend/TEST_GUIDE.md`

## 🎓 Best Practices

1. Run tests before committing
2. Maintain high coverage
3. Update tests with code changes
4. Review test failures carefully
5. Keep tests isolated
6. Mock external services
7. Test error scenarios
8. Document test purposes

## 🆘 Troubleshooting

### Frontend tests fail
- Check `Frontend/TEST_GUIDE.md`
- Verify vitest.config.ts
- Check node_modules installed

### Backend tests fail
- Check `Backend/TEST_GUIDE.md`
- Verify conftest.py fixtures
- Check database setup

### Coverage too low
- Add tests for uncovered code
- Review coverage reports
- Focus on critical paths

## 📞 Support

1. Check relevant TEST_GUIDE.md
2. Review test examples
3. Check CI/CD logs
4. Consult team documentation

## 🎉 You're Ready!

Everything is set up and ready to test. Start with:

```bash
bash scripts/run-tests.sh
```

Happy testing! 🚀
