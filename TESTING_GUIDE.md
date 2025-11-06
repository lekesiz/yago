# YAGO Testing Guide

## Backend Testing

### Setup

```bash
cd yago/web/backend

# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test file
pytest tests/test_auth_service.py

# Run tests in parallel
pytest -n auto
```

### Test Organization

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_auth_service.py     # Authentication tests
├── test_validation.py       # Input validation tests
├── test_models.py           # Database model tests
└── test_api_endpoints.py    # API endpoint tests
```

### Writing Tests

```python
# Example: Testing a service
def test_create_user(db_session):
    """Test user creation"""
    user = AuthService.create_user(
        db=db_session,
        email="test@example.com",
        password="StrongPass123!"
    )

    assert user.email == "test@example.com"
    assert user.is_active is True
```

### Test Coverage Goals

- **Unit Tests:** 80%+ coverage
- **Integration Tests:** 70%+ coverage
- **E2E Tests:** Critical paths covered

## Frontend Testing

### Setup

```bash
cd yago/web/frontend

# Install dependencies
npm install

# Run unit tests
npm run test

# Run with UI
npm run test:ui

# Run with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e
```

### Test Organization

```
src/
├── test/
│   ├── setup.ts           # Test configuration
│   └── testUtils.tsx      # Test utilities
├── services/
│   └── __tests__/
│       └── logger.test.ts # Service tests
├── config/
│   └── __tests__/
│       └── env.test.ts    # Config tests
└── components/
    └── __tests__/
        └── *.test.tsx     # Component tests
```

### Writing Component Tests

```typescript
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import MyComponent from '../MyComponent';

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });

  it('handles user interaction', async () => {
    const { user } = render(<MyComponent />);
    await user.click(screen.getByRole('button'));
    expect(screen.getByText('Clicked')).toBeInTheDocument();
  });
});
```

## Test Fixtures

### Backend Fixtures (conftest.py)

```python
@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    # Returns User instance

@pytest.fixture
def auth_token(test_user):
    """Create JWT token"""
    # Returns token string

@pytest.fixture
def auth_headers(auth_token):
    """Create auth headers"""
    # Returns dict with Authorization header
```

### Frontend Test Utilities

```typescript
// Custom render with providers
import { render } from '@/test/testUtils';

const { container } = render(<Component />);
```

## Testing Best Practices

### 1. Test Naming

```python
# Good
def test_user_creation_with_valid_email():
    pass

# Bad
def test1():
    pass
```

### 2. Arrange-Act-Assert Pattern

```python
def test_something():
    # Arrange
    user = create_user()

    # Act
    result = user.do_something()

    # Assert
    assert result == expected
```

### 3. Test Isolation

- Each test should be independent
- Use fixtures for setup
- Clean up after tests

### 4. Mock External Services

```python
@pytest.mark.unit
def test_api_call(mocker):
    mock_response = mocker.patch('requests.get')
    mock_response.return_value.json.return_value = {...}

    result = call_external_api()
    assert result == expected
```

## Coverage Reports

### Backend

```bash
pytest --cov --cov-report=html
# Open htmlcov/index.html
```

### Frontend

```bash
npm run test:coverage
# Open coverage/index.html
```

## CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run backend tests
        run: |
          cd yago/web/backend
          pip install -r requirements-test.txt
          pytest --cov

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run frontend tests
        run: |
          cd yago/web/frontend
          npm install
          npm run test
```

## Common Issues

### Backend

**Issue:** Import errors in tests
```python
# Solution: Add to conftest.py
import sys
sys.path.insert(0, os.path.dirname(__file__))
```

**Issue:** Database not resetting
```python
# Solution: Use transactions in fixtures
@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    # ... use session
    transaction.rollback()
```

### Frontend

**Issue:** Module not found
```typescript
// Solution: Update vitest.config.ts aliases
resolve: {
  alias: {
    '@': path.resolve(__dirname, './src'),
  }
}
```

**Issue:** DOM not available
```typescript
// Solution: Set environment in vitest.config.ts
test: {
  environment: 'jsdom'
}
```

## Performance Testing

### Load Testing (Backend)

```bash
# Install locust
pip install locust

# Run load test
locust -f tests/load/locustfile.py
```

### Performance Testing (Frontend)

```bash
# Lighthouse CI
npm run build
lighthouse http://localhost:3000 --output=html
```

## Test Markers

### Backend (pytest)

```python
@pytest.mark.unit
def test_fast():
    pass

@pytest.mark.integration
def test_with_db():
    pass

@pytest.mark.slow
def test_long_running():
    pass

# Run specific markers
pytest -m unit
pytest -m "not slow"
```

## Debugging Tests

### Backend

```bash
# Run with verbose output
pytest -vv

# Run with pdb on failure
pytest --pdb

# Run last failed tests
pytest --lf
```

### Frontend

```bash
# Run in watch mode
npm run test -- --watch

# Run specific test file
npm run test src/services/__tests__/logger.test.ts

# Debug in browser
npm run test:ui
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Vitest Documentation](https://vitest.dev/)
- [Testing Library](https://testing-library.com/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
