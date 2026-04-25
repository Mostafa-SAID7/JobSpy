# Contributing to JobSpy

Thank you for your interest in contributing to JobSpy! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Coding Standards](#coding-standards)
5. [Testing Requirements](#testing-requirements)
6. [Commit Message Format](#commit-message-format)
7. [Pull Request Process](#pull-request-process)
8. [Code Review Guidelines](#code-review-guidelines)
9. [Documentation Requirements](#documentation-requirements)
10. [Release Process](#release-process)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. We pledge to:

- Be respectful and inclusive
- Welcome diverse perspectives
- Focus on constructive feedback
- Respect confidentiality
- Report inappropriate behavior

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing opinions
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment or discrimination
- Offensive comments or language
- Trolling or insulting comments
- Personal attacks
- Publishing private information
- Other conduct that violates professional standards

### Reporting

Report violations to: conduct@jobspy.com

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+
- Git
- Docker (optional)

### Setup Development Environment

1. **Fork the Repository**
   ```bash
   # Go to GitHub and fork the repository
   ```

2. **Clone Your Fork**
   ```bash
   git clone https://github.com/yourusername/jobspy.git
   cd jobspy
   ```

3. **Add Upstream Remote**
   ```bash
   git remote add upstream https://github.com/original/jobspy.git
   ```

4. **Follow Developer Setup Guide**
   - See [DEVELOPER_SETUP.md](DEVELOPER_SETUP.md) for detailed instructions

## Development Workflow

### Creating a Feature Branch

1. **Update Main Branch**
   ```bash
   git checkout main
   git pull upstream main
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

   Branch naming conventions:
   - `feature/`: New features
   - `bugfix/`: Bug fixes
   - `docs/`: Documentation updates
   - `refactor/`: Code refactoring
   - `test/`: Test additions
   - `perf/`: Performance improvements

3. **Make Changes**
   - Write code following coding standards
   - Add tests for new functionality
   - Update documentation

4. **Commit Changes**
   - Follow commit message format
   - Make atomic commits
   - Write clear commit messages

5. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

### Keeping Your Branch Updated

```bash
# Fetch latest changes
git fetch upstream

# Rebase on main
git rebase upstream/main

# Force push to your fork
git push -f origin feature/your-feature-name
```

## Coding Standards

### Backend (Python)

#### Code Style

- Follow PEP 8 style guide
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use type hints for all functions

#### Tools

```bash
# Format code with Black
black app/

# Sort imports with isort
isort app/

# Lint with pylint
pylint app/

# Type check with mypy
mypy app/
```

#### Example

```python
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter()

def get_user_by_id(
    user_id: str,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get user by ID from database.
    
    Args:
        user_id: The user ID to retrieve
        db: Database session
        
    Returns:
        User object or None if not found
    """
    return db.query(User).filter(User.id == user_id).first()
```

### Frontend (JavaScript/Vue)

#### Code Style

- Follow ESLint configuration
- Use 2 spaces for indentation
- Use semicolons
- Use single quotes for strings
- Use const/let (no var)

#### Tools

```bash
# Lint with ESLint
npm run lint

# Fix linting issues
npm run lint:fix

# Format with Prettier
npm run format

# Type check
npm run type-check
```

#### Example

```vue
<template>
  <div class="job-card">
    <h2>{{ job.title }}</h2>
    <p>{{ job.company }}</p>
    <button @click="saveJob">Save Job</button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import type { Job } from '@/types';

interface Props {
  job: Job;
}

const props = defineProps<Props>();
const isSaved = ref(false);

const saveJob = (): void => {
  isSaved.value = !isSaved.value;
  // Save job logic
};
</script>

<style scoped>
.job-card {
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}
</style>
```

### Documentation

- Use clear, concise language
- Include code examples
- Document all public APIs
- Update README for major changes
- Add docstrings to all functions

## Testing Requirements

### Backend Tests

All new code must include tests:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test
pytest tests/test_auth.py::test_login
```

**Coverage Requirements**:
- Minimum 80% code coverage
- All public functions tested
- Edge cases covered
- Error conditions tested

**Example Test**:

```python
import pytest
from app.services.auth_service import AuthService

@pytest.fixture
def auth_service():
    return AuthService()

def test_login_success(auth_service):
    """Test successful login."""
    result = auth_service.login("user@example.com", "password123")
    assert result is not None
    assert result.access_token is not None

def test_login_invalid_credentials(auth_service):
    """Test login with invalid credentials."""
    with pytest.raises(AuthenticationError):
        auth_service.login("user@example.com", "wrongpassword")
```

### Frontend Tests

```bash
# Run all tests
npm run test

# Run with coverage
npm run test:coverage

# Run specific test
npm run test -- tests/unit/auth.spec.js
```

**Example Test**:

```javascript
import { describe, it, expect, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import JobCard from '@/components/JobCard.vue';

describe('JobCard.vue', () => {
  let wrapper;

  beforeEach(() => {
    const job = {
      id: '1',
      title: 'Senior Developer',
      company: 'Tech Corp'
    };
    wrapper = mount(JobCard, { props: { job } });
  });

  it('renders job title', () => {
    expect(wrapper.text()).toContain('Senior Developer');
  });

  it('emits save event when button clicked', async () => {
    await wrapper.find('button').trigger('click');
    expect(wrapper.emitted('save')).toBeTruthy();
  });
});
```

## Commit Message Format

Follow conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Test additions
- `chore`: Build/dependency changes

### Scope

Optional scope of the change:
- `auth`: Authentication
- `jobs`: Job search
- `alerts`: Alerts
- `api`: API endpoints
- `db`: Database
- `ui`: User interface

### Subject

- Use imperative mood ("add" not "added")
- Don't capitalize first letter
- No period at the end
- Maximum 50 characters

### Body

- Explain what and why, not how
- Wrap at 72 characters
- Separate from subject with blank line

### Footer

- Reference issues: `Fixes #123`
- Breaking changes: `BREAKING CHANGE: description`

### Examples

```
feat(auth): add two-factor authentication

Implement TOTP-based 2FA for enhanced security.
Users can enable 2FA in account settings.

Fixes #456
```

```
fix(jobs): correct salary range filtering

The salary filter was excluding jobs with
exact minimum salary match. Now includes
jobs where salary equals the minimum.

Fixes #789
```

## Pull Request Process

### Before Submitting

1. **Update Your Branch**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run Tests**
   ```bash
   # Backend
   pytest --cov=app
   
   # Frontend
   npm run test
   ```

3. **Run Linting**
   ```bash
   # Backend
   black app/ && isort app/ && pylint app/
   
   # Frontend
   npm run lint:fix
   ```

4. **Build Locally**
   ```bash
   # Backend
   python -m pytest
   
   # Frontend
   npm run build
   ```

### Creating a Pull Request

1. **Push Your Branch**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create PR on GitHub**
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Select your branch
   - Fill in PR template

3. **PR Title Format**
   ```
   [Type] Brief description
   
   Examples:
   [Feature] Add job recommendations
   [Fix] Correct alert matching logic
   [Docs] Update API documentation
   ```

4. **PR Description**
   - Describe changes clearly
   - Reference related issues
   - Include screenshots if UI changes
   - List testing performed

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Fixes #123

## Testing
- [ ] Unit tests added
- [ ] Integration tests added
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No new warnings generated
```

## Code Review Guidelines

### For Authors

- Respond to feedback promptly
- Ask questions if feedback is unclear
- Make requested changes
- Push updates to same branch
- Don't force push after review starts

### For Reviewers

- Review within 24 hours if possible
- Be constructive and respectful
- Suggest improvements, don't demand
- Approve when satisfied
- Use "Request Changes" for blocking issues

### Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests are adequate
- [ ] Documentation is updated
- [ ] No security issues
- [ ] No performance regressions
- [ ] Commits are well-organized
- [ ] PR description is clear

## Documentation Requirements

### Code Documentation

- Add docstrings to all public functions
- Include type hints
- Document parameters and return values
- Include usage examples for complex functions

### User Documentation

- Update README for major features
- Add to appropriate guide (USER_GUIDE.md, FAQ.md)
- Include screenshots for UI changes
- Update API documentation

### Developer Documentation

- Update DEVELOPER_SETUP.md if setup changes
- Update ARCHITECTURE.md for structural changes
- Add comments for complex logic
- Document new dependencies

## Release Process

### Version Numbering

Follow semantic versioning: `MAJOR.MINOR.PATCH`

- `MAJOR`: Breaking changes
- `MINOR`: New features (backward compatible)
- `PATCH`: Bug fixes

### Release Steps

1. **Create Release Branch**
   ```bash
   git checkout -b release/v1.2.0
   ```

2. **Update Version**
   - Update version in `package.json`
   - Update version in `pyproject.toml`
   - Update CHANGELOG.md

3. **Create Release PR**
   - Title: `Release v1.2.0`
   - Description: List changes

4. **Merge to Main**
   - Merge release PR
   - Tag release: `git tag v1.2.0`
   - Push tag: `git push origin v1.2.0`

5. **Create GitHub Release**
   - Go to Releases
   - Create release from tag
   - Add release notes

## Getting Help

- **Questions**: Ask in GitHub Discussions
- **Issues**: Report bugs in GitHub Issues
- **Chat**: Join our Slack community
- **Email**: contact@jobspy.com

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project website

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

## Additional Resources

- [Developer Setup Guide](DEVELOPER_SETUP.md)
- [Architecture Overview](ARCHITECTURE.md)
- [API Reference](API_REFERENCE.md)
- [Database Schema](DATABASE_SCHEMA.md)
- [GitHub Issues](https://github.com/yourusername/jobspy/issues)
- [GitHub Discussions](https://github.com/yourusername/jobspy/discussions)

Thank you for contributing to JobSpy!
