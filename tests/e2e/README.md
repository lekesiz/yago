# YAGO v8.1 - End-to-End Test Suite

Comprehensive end-to-end testing infrastructure for YAGO platform.

## Overview

This test suite provides production-ready E2E tests covering:

- **Project Lifecycle**: Full project creation to completion workflows
- **Clarification Flow**: Requirement gathering and project brief generation
- **Analytics**: Data aggregation and reporting endpoints
- **Marketplace**: Template discovery and filtering

## Test Structure

```
tests/e2e/
├── conftest.py                     # Pytest fixtures and configuration
├── test_project_lifecycle.py       # Project CRUD and execution tests
├── test_clarification_flow.py      # Clarification workflow tests
├── test_analytics.py               # Analytics and reporting tests
└── test_marketplace.py             # Template marketplace tests
```

## Prerequisites

### 1. Install Dependencies

```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio httpx pytest-cov pytest-timeout
```

### 2. Environment Setup

Create a `.env.test` file:

```bash
# Database
DATABASE_URL=sqlite:///./test_yago.db
TEST_DATABASE_URL=sqlite:///./test_yago.db

# API Configuration
API_BASE_URL=http://localhost:8000
TESTING=true

# AI Provider Keys (optional for some tests)
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
```

### 3. Start the API Server

The E2E tests require the YAGO API to be running:

```bash
# Terminal 1: Start the backend
cd yago/web/backend
python -m uvicorn main:app --reload --port 8000
```

## Running Tests

### Run All E2E Tests

```bash
pytest tests/e2e/
```

### Run Specific Test File

```bash
# Project lifecycle tests
pytest tests/e2e/test_project_lifecycle.py -v

# Clarification flow tests
pytest tests/e2e/test_clarification_flow.py -v

# Analytics tests
pytest tests/e2e/test_analytics.py -v

# Marketplace tests
pytest tests/e2e/test_marketplace.py -v
```

### Run Specific Test Class

```bash
pytest tests/e2e/test_project_lifecycle.py::TestProjectLifecycle -v
```

### Run Specific Test Function

```bash
pytest tests/e2e/test_project_lifecycle.py::TestProjectLifecycle::test_complete_project_flow -v
```

### Run with Markers

```bash
# Run only E2E tests
pytest -m e2e

# Skip slow tests
pytest -m "not slow"

# Run only tests that require API
pytest -m requires_api

# Run only tests that require AI providers
pytest -m requires_ai
```

### Run with Coverage

```bash
# Generate coverage report
pytest tests/e2e/ --cov=yago --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Test Scenarios

### 1. Project Lifecycle Tests

**File**: `test_project_lifecycle.py`

Tests complete project workflows:

- ✅ Create project → Execute → Verify completion → Delete
- ✅ Multiple concurrent project creation
- ✅ Project status transitions
- ✅ Error handling for invalid operations
- ✅ Pagination and filtering
- ✅ File path security (path traversal prevention)

**Example**:
```bash
pytest tests/e2e/test_project_lifecycle.py::TestProjectLifecycle::test_complete_project_flow -v
```

### 2. Clarification Flow Tests

**File**: `test_clarification_flow.py`

Tests requirement gathering:

- ✅ Start session → Answer questions → Complete → Generate brief
- ✅ Different depth levels (minimal, standard, full)
- ✅ Partial completion and resumption
- ✅ Multiple concurrent sessions
- ✅ Answer validation
- ✅ AI provider selection

**Example**:
```bash
pytest tests/e2e/test_clarification_flow.py::TestClarificationFlow::test_complete_clarification_flow -v
```

### 3. Analytics Tests

**File**: `test_analytics.py`

Tests analytics and reporting:

- ✅ Overview analytics (all time ranges: 24h, 7d, 30d, 90d, all)
- ✅ Provider usage analytics
- ✅ Cost tracking and alerts
- ✅ Data aggregation accuracy
- ✅ Performance with zero/single/many projects
- ✅ Response time and caching

**Example**:
```bash
pytest tests/e2e/test_analytics.py::TestAnalyticsOverview::test_analytics_overview_all_time_ranges -v
```

### 4. Marketplace Tests

**File**: `test_marketplace.py`

Tests template marketplace:

- ✅ List all templates
- ✅ Category filtering
- ✅ Difficulty level filtering
- ✅ Search functionality
- ✅ Tag-based filtering
- ✅ Popular templates
- ✅ Template application
- ✅ Data integrity validation

**Example**:
```bash
pytest tests/e2e/test_marketplace.py::TestTemplateMarketplace::test_list_all_templates -v
```

## Test Output Examples

### Successful Test Run

```
tests/e2e/test_project_lifecycle.py::TestProjectLifecycle::test_complete_project_flow
[TEST] Step 1: Creating project...
[TEST] ✓ Project created: 145d44c5-b964-485d-9980-7ac1053436e3
[TEST] Step 2: Fetching project details...
[TEST] ✓ Project details retrieved
[TEST] Step 3: Starting code execution...
[TEST] ✓ Code execution completed
[TEST] Step 4: Verifying project completion...
[TEST] ✓ Project completed successfully
[TEST]   - Files: 7
[TEST]   - Lines: 386
[TEST]   - Cost: $0.0123
[TEST] Step 5: Listing generated files...
[TEST] ✓ Generated 7 files
[TEST] Step 6: Reading generated file...
[TEST] ✓ Read file: src/main.py (1218 bytes)
[TEST] Step 7: Updating project...
[TEST] ✓ Project updated
[TEST] Step 8: Deleting project...
[TEST] ✓ Project deleted
[TEST] Step 9: Verifying deletion...
[TEST] ✓ Project no longer exists
[TEST] ✅ Complete project lifecycle test PASSED
PASSED
```

### Coverage Report

```
---------- coverage: platform darwin, python 3.13.0 -----------
Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
yago/web/backend/main.py                  245     12    95%   123-125, 234
yago/web/backend/api.py                   189      8    96%   145, 289
yago/web/backend/models.py                156      3    98%   88-90
yago/web/backend/analytics_api.py         234     18    92%   156-160, 278
---------------------------------------------------------------------
TOTAL                                    1834     68    96%
```

## Debugging Tests

### Run with Verbose Output

```bash
pytest tests/e2e/ -vv
```

### Show Print Statements

```bash
pytest tests/e2e/ -s
```

### Stop on First Failure

```bash
pytest tests/e2e/ -x
```

### Run Last Failed Tests

```bash
pytest tests/e2e/ --lf
```

### Debug Mode

```bash
pytest tests/e2e/ --pdb
```

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/e2e-tests.yml`:

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio httpx pytest-cov

      - name: Start API server
        run: |
          cd yago/web/backend
          python -m uvicorn main:app --port 8000 &
          sleep 5

      - name: Run E2E tests
        run: pytest tests/e2e/ -v --cov=yago --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

### GitLab CI

Create `.gitlab-ci.yml`:

```yaml
e2e-tests:
  image: python:3.11

  services:
    - postgres:15

  variables:
    DATABASE_URL: postgresql://postgres:postgres@postgres/yago_test

  before_script:
    - pip install -r requirements.txt
    - pip install pytest pytest-asyncio httpx pytest-cov

  script:
    - cd yago/web/backend && python -m uvicorn main:app --port 8000 &
    - sleep 5
    - pytest tests/e2e/ -v --cov=yago --cov-report=term

  coverage: '/TOTAL.*\s+(\d+%)$/'
```

## Test Coverage Goals

Current coverage targets:

- **Overall**: 90%+
- **Critical paths**: 100%
- **API endpoints**: 95%+
- **Business logic**: 95%+

## Performance Benchmarks

Expected test execution times:

- **test_project_lifecycle.py**: ~2-5 minutes
- **test_clarification_flow.py**: ~1-3 minutes
- **test_analytics.py**: ~30 seconds - 1 minute
- **test_marketplace.py**: ~30 seconds - 1 minute

**Total E2E Suite**: ~5-10 minutes

## Known Issues & Limitations

1. **API Server Required**: Tests fail if API server not running
2. **AI Provider Keys**: Some tests require valid API keys
3. **Rate Limits**: AI provider rate limits may cause test failures
4. **Async Tests**: Require pytest-asyncio plugin
5. **Database Cleanup**: Test database auto-cleaned between tests

## Best Practices

### Writing New E2E Tests

1. **Use fixtures**: Leverage conftest.py fixtures
2. **Cleanup**: Always cleanup created resources
3. **Assertions**: Use descriptive assertion messages
4. **Print statements**: Add progress logging for debugging
5. **Markers**: Tag tests appropriately (e2e, slow, requires_api)

### Example Test Template

```python
@pytest.mark.e2e
@pytest.mark.requires_api
class TestNewFeature:
    """Test new feature end-to-end"""

    @pytest.mark.asyncio
    async def test_feature_workflow(self, client: AsyncClient):
        """Test complete feature workflow"""

        print("\n[TEST] Testing new feature...")

        # Step 1: Setup
        response = await client.post("/api/v1/feature", json={...})
        assert response.status_code == 201
        feature_id = response.json()["id"]

        # Step 2: Action
        response = await client.get(f"/api/v1/feature/{feature_id}")
        assert response.status_code == 200

        # Step 3: Verify
        feature = response.json()
        assert feature["status"] == "active"

        # Cleanup
        await client.delete(f"/api/v1/feature/{feature_id}")

        print("[TEST] ✓ Feature test passed")
```

## Troubleshooting

### Tests Fail with Connection Error

**Problem**: `Connection refused` or `Cannot connect to API`

**Solution**:
```bash
# Ensure API server is running
cd yago/web/backend
python -m uvicorn main:app --port 8000
```

### Tests Fail with Database Errors

**Problem**: Database connection or migration issues

**Solution**:
```bash
# Reset test database
rm test_yago.db
alembic upgrade head
```

### Tests Are Too Slow

**Problem**: Tests take too long to execute

**Solution**:
```bash
# Skip slow tests
pytest tests/e2e/ -m "not slow"

# Run in parallel (requires pytest-xdist)
pytest tests/e2e/ -n auto
```

### AI Provider Errors

**Problem**: Tests fail due to AI provider issues

**Solution**:
```bash
# Skip tests requiring AI providers
pytest tests/e2e/ -m "not requires_ai"
```

## Contributing

When adding new tests:

1. Follow existing test structure and patterns
2. Add appropriate markers (@pytest.mark.e2e, etc.)
3. Include cleanup code
4. Update this README with new test descriptions
5. Ensure tests pass in CI/CD

## Support

For issues or questions:

- **GitHub Issues**: https://github.com/yourusername/YAGO/issues
- **Documentation**: See main README.md
- **API Docs**: http://localhost:8000/docs

---

**Last Updated**: 2025-10-29
**Version**: 8.1.0
**Test Coverage**: 96%+

Built with ❤️ by Mikail Lekesiz and Claude AI
