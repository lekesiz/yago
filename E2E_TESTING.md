# YAGO v7.1 - E2E Testing Guide

**Created**: 2025-10-28
**Testing Framework**: Playwright
**Coverage**: Clarification Flow, Dashboards, API Integration

---

## Table of Contents

1. [Overview](#overview)
2. [Setup](#setup)
3. [Running Tests](#running-tests)
4. [Test Structure](#test-structure)
5. [Writing Tests](#writing-tests)
6. [CI/CD Integration](#cicd-integration)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Overview

YAGO v7.1 includes comprehensive end-to-end tests powered by Playwright. These tests cover:

- **Clarification Flow**: Complete user journey through question answering
- **Cost Dashboard**: Cost tracking and visualization
- **Collaboration Dashboard**: Agent status and message flow
- **Benchmark Dashboard**: Performance metrics and benchmarking

### Test Statistics
- **Test Files**: 2
- **Test Cases**: 20+
- **Browser Coverage**: Chromium (Chrome/Edge)
- **Test Types**: Integration, E2E, Visual Regression

---

## Setup

### Prerequisites
```bash
# Node.js 20+ and npm installed
node --version  # Should be v20+
npm --version
```

### Install Dependencies
```bash
cd yago/web/frontend

# Install Playwright and dependencies
npm install

# Install Playwright browsers
npx playwright install --with-deps chromium
```

### Verify Installation
```bash
# Check Playwright version
npx playwright --version

# List installed browsers
npx playwright install --dry-run
```

---

## Running Tests

### Quick Commands

```bash
# Run all tests (headless mode)
npm test

# Run tests with browser visible
npm run test:headed

# Run tests with interactive UI
npm run test:ui

# Run tests in debug mode
npm run test:debug

# View last test report
npm run test:report
```

### Advanced Commands

```bash
# Run specific test file
npx playwright test e2e/clarification-flow.spec.ts

# Run specific test case
npx playwright test -g "should display first question"

# Run tests in parallel
npx playwright test --workers=4

# Run tests with specific browser
npx playwright test --project=chromium

# Run tests with trace
npx playwright test --trace on
```

### Running with Backend

E2E tests require the backend to be running:

```bash
# Terminal 1: Start backend
cd yago/web/backend
python clarification_api.py

# Terminal 2: Run tests (frontend dev server starts automatically)
cd yago/web/frontend
npm test
```

---

## Test Structure

### Directory Layout
```
yago/web/frontend/
├── e2e/                                  # E2E test files
│   ├── clarification-flow.spec.ts        # Clarification flow tests
│   └── dashboards.spec.ts                # Dashboard tests
├── playwright.config.ts                  # Playwright configuration
├── playwright-report/                    # HTML test reports
└── test-results/                         # Test artifacts
```

### Test File Organization

Each test file follows this structure:

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    // Setup before each test
  });

  test('should do something', async ({ page }) => {
    // Test case
  });
});
```

---

## Writing Tests

### Basic Test Example

```typescript
import { test, expect } from '@playwright/test';

test('should load homepage', async ({ page }) => {
  // Navigate to page
  await page.goto('/');

  // Check for element
  await expect(page.locator('h1')).toBeVisible();

  // Verify text
  await expect(page.locator('h1')).toContainText('YAGO');
});
```

### Interacting with Elements

```typescript
// Click button
await page.click('button:has-text("Next")');

// Fill input
await page.fill('input[name="answer"]', 'My answer');

// Select dropdown
await page.selectOption('select', 'option-value');

// Check checkbox
await page.check('input[type="checkbox"]');
```

### Waiting for Elements

```typescript
// Wait for selector
await page.waitForSelector('[data-testid="question"]');

// Wait for navigation
await page.waitForURL('**/dashboard');

// Wait for timeout
await page.waitForTimeout(1000);

// Wait for load state
await page.waitForLoadState('networkidle');
```

### Assertions

```typescript
// Visibility
await expect(page.locator('button')).toBeVisible();
await expect(page.locator('button')).toBeHidden();

// Text content
await expect(page.locator('h1')).toHaveText('Title');
await expect(page.locator('p')).toContainText('partial');

// Input values
await expect(page.locator('input')).toHaveValue('expected');

// Count
await expect(page.locator('li')).toHaveCount(5);

// URL
await expect(page).toHaveURL(/dashboard/);

// Enabled/Disabled
await expect(page.locator('button')).toBeEnabled();
await expect(page.locator('button')).toBeDisabled();
```

### API Testing

```typescript
test('should create project via API', async ({ request }) => {
  const response = await request.post('http://localhost:8000/api/v1/costs/track', {
    data: {
      project_id: 'test-project',
      agent_id: 'agent-001',
      // ... more data
    }
  });

  expect(response.ok()).toBeTruthy();
  const data = await response.json();
  expect(data.project_id).toBe('test-project');
});
```

### Screenshots

```typescript
// Take screenshot
await page.screenshot({ path: 'screenshot.png' });

// Screenshot on failure (automatic via config)
// Configured in playwright.config.ts: screenshot: 'only-on-failure'

// Full page screenshot
await page.screenshot({ path: 'full.png', fullPage: true });
```

### Visual Regression Testing

```typescript
test('should match visual snapshot', async ({ page }) => {
  await page.goto('/dashboard');

  // Compare screenshot
  await expect(page).toHaveScreenshot('dashboard.png');
});
```

---

## CI/CD Integration

### GitHub Actions Workflow

The E2E tests are integrated into the CI pipeline (`.github/workflows/ci.yml`):

```yaml
e2e-tests:
  name: E2E Tests
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: 20

    - name: Install dependencies
      run: |
        cd yago/web/frontend
        npm ci

    - name: Install Playwright
      run: npx playwright install --with-deps

    - name: Start backend
      run: |
        cd yago/web/backend
        pip install -r ../requirements.txt
        python clarification_api.py &
        sleep 10

    - name: Run E2E tests
      run: |
        cd yago/web/frontend
        npm test

    - name: Upload test results
      if: always()
      uses: actions/upload-artifact@v4
      with:
        name: playwright-report
        path: yago/web/frontend/playwright-report/
```

### Running in Docker

```dockerfile
# Dockerfile.e2e
FROM mcr.microsoft.com/playwright:v1.40.0-jammy

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

CMD ["npm", "test"]
```

```bash
# Build and run
docker build -f Dockerfile.e2e -t yago-e2e .
docker run -e CI=true yago-e2e
```

---

## Best Practices

### 1. Use Data Test IDs

```typescript
// Good - Stable selector
await page.click('[data-testid="next-button"]');

// Bad - Fragile selector
await page.click('.btn-primary.ml-2');
```

### 2. Avoid Hard Waits

```typescript
// Good - Wait for condition
await page.waitForSelector('[data-testid="question"]');

// Bad - Arbitrary timeout
await page.waitForTimeout(5000);
```

### 3. Independent Tests

```typescript
// Good - Each test is independent
test('test 1', async ({ page }) => {
  await page.goto('/');
  // Test logic
});

test('test 2', async ({ page }) => {
  await page.goto('/');
  // Test logic
});

// Bad - Tests depend on each other
test('test 1', async ({ page }) => {
  await page.goto('/');
  // Leaves state
});

test('test 2', async ({ page }) => {
  // Expects state from test 1
});
```

### 4. Use Page Objects

```typescript
// page-objects/dashboard.ts
export class DashboardPage {
  constructor(private page: Page) {}

  async navigateTo() {
    await this.page.goto('/dashboard');
  }

  async getCostMetric() {
    return await this.page.locator('[data-testid="cost-metric"]').textContent();
  }
}

// In test
const dashboard = new DashboardPage(page);
await dashboard.navigateTo();
const cost = await dashboard.getCostMetric();
```

### 5. Handle Flakiness

```typescript
// Retry flaky assertions
await expect(async () => {
  const text = await page.locator('[data-testid="status"]').textContent();
  expect(text).toBe('Ready');
}).toPass({ timeout: 5000 });

// Wait for network idle
await page.goto('/dashboard', { waitUntil: 'networkidle' });
```

---

## Troubleshooting

### Tests Fail Locally

**Problem**: Tests pass in CI but fail locally

**Solutions**:
```bash
# Clear browser cache
npx playwright install --force

# Run with same settings as CI
CI=true npm test

# Check browser version
npx playwright --version
```

### Backend Not Running

**Problem**: Tests fail with connection errors

**Solutions**:
```bash
# Check backend is running
curl http://localhost:8000/api/v1/costs/health

# Start backend manually
cd yago/web/backend
python clarification_api.py

# Check logs
tail -f yago.log
```

### Timeout Errors

**Problem**: Tests timeout waiting for elements

**Solutions**:
```typescript
// Increase timeout
await page.waitForSelector('[data-testid="element"]', {
  timeout: 10000
});

// Or in config
test.setTimeout(60000);
```

### Visual Regression Failures

**Problem**: Screenshot comparisons fail

**Solutions**:
```bash
# Update baselines
npx playwright test --update-snapshots

# Generate missing screenshots
npx playwright test --update-snapshots --grep "visual"

# Check diff
open playwright-report/index.html
```

### Flaky Tests

**Problem**: Tests pass/fail inconsistently

**Solutions**:
```typescript
// Add retries in config
export default defineConfig({
  retries: 2,
});

// Or for specific test
test('flaky test', async ({ page }) => {
  test.retry(3);
  // Test logic
});

// Wait for stability
await page.waitForLoadState('networkidle');
```

---

## Test Coverage

### Current Coverage

| Feature | Tests | Coverage |
|---------|-------|----------|
| Clarification Flow | 10 | 95% |
| Cost Dashboard | 3 | 80% |
| Collaboration Dashboard | 3 | 75% |
| Benchmark Dashboard | 3 | 75% |
| Navigation | 2 | 90% |

### Coverage Goals

- [ ] 100% critical user paths
- [ ] 90% dashboard interactions
- [ ] 85% API endpoints
- [ ] 80% error scenarios

---

## Resources

### Documentation
- [Playwright Official Docs](https://playwright.dev/docs/intro)
- [Best Practices](https://playwright.dev/docs/best-practices)
- [API Reference](https://playwright.dev/docs/api/class-playwright)

### Examples
- [Playwright Examples](https://github.com/microsoft/playwright/tree/main/tests)
- [Real-world Examples](https://github.com/mxschmitt/playwright-test-examples)

### Support
- [GitHub Issues](https://github.com/microsoft/playwright/issues)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/playwright)
- [Discord Community](https://discord.com/invite/playwright)

---

**Last Updated**: 2025-10-28
**Maintainer**: YAGO Development Team
**Version**: 7.1.0
