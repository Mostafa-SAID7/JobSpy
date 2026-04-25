# Frontend Testing Guide

## Overview
This guide covers all frontend tests for the JobSpy application.

## Test Structure

```
Frontend/src/
├── components/
│   ├── forms/
│   │   └── __tests__/
│   │       └── FormInput.test.ts
│   ├── layout/
│   │   └── __tests__/
│   │       └── Navigation.test.ts
│   └── ...
├── pages/
│   └── __tests__/
│       ├── AlertsPage.test.ts
│       └── JobSearchPage.test.ts
├── stores/
│   └── __tests__/
│       ├── auth.test.ts
│       └── jobs.test.ts
└── services/
    └── __tests__/
        └── api.test.ts
```

## Running Tests

### Run all tests
```bash
npm run test
```

### Run tests in watch mode
```bash
npm run test -- --watch
```

### Run specific test file
```bash
npm run test -- FormInput.test.ts
```

### Run tests with coverage
```bash
npm run test -- --coverage
```

## Test Categories

### 1. Component Tests
- **FormInput.test.ts**: Input field component
  - Rendering with label and placeholder
  - v-model binding
  - Disabled state
  - Required field indicator
  - Error message display

- **Navigation.test.ts**: Navigation bar component
  - Rendering and branding
  - Authentication state display
  - Navigation links
  - Mobile menu toggle
  - Logout functionality

### 2. Page Tests
- **AlertsPage.test.ts**: Alert management page
  - Display alerts list
  - Toggle alert active status
  - Delete alert functionality
  - Edit alert frequency
  - Error handling and loading states
  - Statistics calculation

- **JobSearchPage.test.ts**: Job search page
  - Search form rendering
  - Search functionality
  - Results display
  - Pagination
  - Save job functionality
  - Error handling

### 3. Store Tests
- **auth.test.ts**: Authentication store
  - Initial state
  - Login action
  - Register action
  - Logout action
  - Token management
  - Error handling

- **jobs.test.ts**: Jobs store
  - Search jobs
  - Save/unsave jobs
  - Alert management (create, update, delete)
  - Error handling

### 4. Service Tests
- **api.test.ts**: API service
  - Authentication endpoints
  - Job search endpoints
  - Saved jobs endpoints
  - Alerts endpoints
  - Error handling

## Writing New Tests

### Component Test Template
```typescript
import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import MyComponent from '../MyComponent.vue'

describe('MyComponent', () => {
  describe('Feature Name', () => {
    it('should do something', () => {
      const wrapper = mount(MyComponent, {
        props: { /* props */ }
      })
      
      expect(wrapper.find('.selector').exists()).toBe(true)
    })
  })
})
```

### Store Test Template
```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useMyStore } from '../myStore'

describe('MyStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should do something', async () => {
    const store = useMyStore()
    await store.myAction()
    expect(store.state).toBe(expectedValue)
  })
})
```

## Best Practices

1. **Use descriptive test names**: Test names should clearly describe what is being tested
2. **Organize with describe blocks**: Group related tests together
3. **Mock external dependencies**: Use `vi.mock()` for API calls and external services
4. **Test user interactions**: Focus on what users see and do
5. **Keep tests isolated**: Each test should be independent
6. **Use beforeEach for setup**: Initialize common test data
7. **Test error cases**: Include tests for error scenarios

## Debugging Tests

### Run single test
```bash
npm run test -- --reporter=verbose FormInput.test.ts
```

### Debug in browser
```bash
npm run test -- --inspect-brk
```

### View test output
```bash
npm run test -- --reporter=verbose
```

## Coverage Goals

- **Statements**: 80%+
- **Branches**: 75%+
- **Functions**: 80%+
- **Lines**: 80%+

## Common Issues

### Issue: Tests timeout
**Solution**: Increase timeout in vitest.config.ts or use `vi.useFakeTimers()`

### Issue: Component not rendering
**Solution**: Check that all required props are provided and stubs are correct

### Issue: Store state not updating
**Solution**: Ensure `setActivePinia(createPinia())` is called in beforeEach

## CI/CD Integration

Tests run automatically on:
- Pull requests
- Commits to main branch
- Pre-deployment checks

Ensure all tests pass before merging!
