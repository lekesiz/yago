# E2E Tests Quick Start Guide

Get up and running with YAGO E2E tests in 5 minutes!

## Quick Setup

### 1. Install Dependencies (30 seconds)

```bash
pip install -r requirements-test.txt
```

### 2. Start API Server (Terminal 1)

```bash
cd yago/web/backend
python -m uvicorn main:app --reload --port 8000
```

Wait for: `Uvicorn running on http://127.0.0.1:8000`

### 3. Run Tests (Terminal 2)

```bash
# Run all E2E tests
pytest tests/e2e/ -v

# Expected output:
# ✓ 45+ tests pass in 5-10 minutes
# ✓ Coverage report: 96%+
```

## Common Commands

```bash
# Run single test file
pytest tests/e2e/test_project_lifecycle.py -v

# Run specific test
pytest tests/e2e/test_project_lifecycle.py::TestProjectLifecycle::test_complete_project_flow -v

# Skip slow tests
pytest tests/e2e/ -m "not slow"

# Generate coverage report
pytest tests/e2e/ --cov=yago --cov-report=html
open htmlcov/index.html
```

## What Gets Tested?

✅ **Project Lifecycle** (8 tests)
- Create → Execute → Verify → Delete
- Multiple projects
- Error handling
- Security

✅ **Clarification Flow** (10 tests)
- Start → Answer → Complete → Generate brief
- Different depth levels
- Partial completion
- AI provider selection

✅ **Analytics** (12 tests)
- Overview analytics (all time ranges)
- Provider usage
- Cost tracking
- Performance

✅ **Marketplace** (15 tests)
- Template listing
- Filtering & search
- Category & tags
- Data integrity

## Troubleshooting

### API Not Running
```bash
# Error: Connection refused
# Fix: Start API server
cd yago/web/backend && python -m uvicorn main:app --port 8000
```

### Database Errors
```bash
# Fix: Reset test database
rm test_yago.db
```

### Tests Too Slow
```bash
# Skip slow tests
pytest tests/e2e/ -m "not slow"
```

## Next Steps

- See `tests/e2e/README.md` for complete documentation
- See `E2E_TEST_SUMMARY.md` for detailed test coverage
- Add your own tests following existing patterns

## Need Help?

- Check `tests/e2e/README.md` for detailed docs
- Review existing tests for patterns
- Run with `-v` for verbose output
- Run with `--pdb` to debug failures

---

**Happy Testing!** 🚀
