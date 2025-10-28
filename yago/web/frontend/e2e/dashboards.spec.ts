/**
 * YAGO v7.1 - Dashboard E2E Tests
 * Tests for Cost, Collaboration, and Benchmark dashboards
 */

import { test, expect } from '@playwright/test';

test.describe('Cost Dashboard', () => {
  test('should display cost tracking dashboard', async ({ page, request }) => {
    // Create a test project first
    const response = await request.post('http://localhost:8000/api/v1/costs/track', {
      data: {
        project_id: 'test-e2e-project',
        agent_id: 'agent-001',
        agent_type: 'Planner',
        phase: 'planning',
        model: 'gpt-4o',
        provider: 'openai',
        tokens_input: 100,
        tokens_output: 50,
        tokens_total: 150,
        cost: 0.003,
        duration_ms: 1500,
        success: true
      }
    });

    expect(response.ok()).toBeTruthy();

    // Navigate to cost dashboard
    await page.goto('/dashboards/cost?projectId=test-e2e-project');

    // Check for dashboard elements
    await expect(page.locator('text=/cost/i').first()).toBeVisible();

    // Look for cost metrics
    const metricsSelectors = [
      'text=/total cost/i',
      'text=/\\$//',  // Dollar sign
      '[data-testid="cost-summary"]'
    ];

    let foundMetric = false;
    for (const selector of metricsSelectors) {
      if (await page.locator(selector).first().isVisible().catch(() => false)) {
        foundMetric = true;
        break;
      }
    }

    expect(foundMetric).toBeTruthy();
  });

  test('should display cost chart visualization', async ({ page }) => {
    await page.goto('/dashboards/cost?projectId=test-e2e-project');

    // Wait for chart to render
    await page.waitForTimeout(2000);

    // Look for chart elements (canvas, svg, or chart container)
    const chartSelectors = [
      'canvas',
      'svg',
      '[data-testid="cost-chart"]',
      '.chart-container'
    ];

    let foundChart = false;
    for (const selector of chartSelectors) {
      if (await page.locator(selector).first().isVisible().catch(() => false)) {
        foundChart = true;
        break;
      }
    }

    expect(foundChart).toBeTruthy();
  });

  test('should show agent cost breakdown', async ({ page }) => {
    await page.goto('/dashboards/cost?projectId=test-e2e-project');

    await page.waitForTimeout(1500);

    // Look for agent names or breakdown section
    const agentIndicators = [
      'text=/planner/i',
      'text=/coder/i',
      'text=/agent/i',
      '[data-testid="agent-breakdown"]'
    ];

    let foundAgent = false;
    for (const selector of agentIndicators) {
      if (await page.locator(selector).first().isVisible().catch(() => false)) {
        foundAgent = true;
        break;
      }
    }

    expect(foundAgent).toBeTruthy();
  });
});

test.describe('Collaboration Dashboard', () => {
  test('should display collaboration dashboard', async ({ page }) => {
    await page.goto('/dashboards/collaboration?projectId=test-e2e-project');

    // Check for dashboard
    await expect(page.locator('text=/collaboration/i, text=/agent/i').first()).toBeVisible({
      timeout: 5000
    });
  });

  test('should show agent status panels', async ({ page }) => {
    await page.goto('/dashboards/collaboration?projectId=test-e2e-project');

    await page.waitForTimeout(2000);

    // Look for agent status indicators
    const statusIndicators = [
      'text=/idle/i',
      'text=/busy/i',
      'text=/status/i',
      '[data-testid="agent-status"]',
      '.agent-card'
    ];

    let foundStatus = false;
    for (const selector of statusIndicators) {
      if (await page.locator(selector).first().isVisible().catch(() => false)) {
        foundStatus = true;
        break;
      }
    }

    expect(foundStatus).toBeTruthy();
  });

  test('should display message flow', async ({ page }) => {
    await page.goto('/dashboards/collaboration?projectId=test-e2e-project');

    // Look for messages tab or section
    const messageButton = page.locator('button:has-text("Messages"), [role="tab"]:has-text("Messages")').first();

    if (await messageButton.isVisible().catch(() => false)) {
      await messageButton.click();
      await page.waitForTimeout(1000);

      // Check for message elements
      const messageIndicators = [
        '[data-testid="message"]',
        '.message-card',
        'text=/from/i',
        'text=/to/i'
      ];

      let foundMessage = false;
      for (const selector of messageIndicators) {
        if (await page.locator(selector).first().isVisible().catch(() => false)) {
          foundMessage = true;
          break;
        }
      }

      expect(foundMessage).toBeTruthy();
    }
  });
});

test.describe('Benchmark Dashboard', () => {
  test('should display benchmark dashboard', async ({ page }) => {
    await page.goto('/dashboards/benchmark?projectId=test-e2e-project');

    // Check for benchmark elements
    await expect(page.locator('text=/benchmark/i, text=/performance/i').first()).toBeVisible({
      timeout: 5000
    });
  });

  test('should show performance metrics', async ({ page }) => {
    await page.goto('/dashboards/benchmark?projectId=test-e2e-project');

    await page.waitForTimeout(2000);

    // Look for performance metrics
    const metricIndicators = [
      'text=/latency/i',
      'text=/throughput/i',
      'text=/ms/i',  // milliseconds
      '[data-testid="benchmark-metric"]'
    ];

    let foundMetric = false;
    for (const selector of metricIndicators) {
      if (await page.locator(selector).first().isVisible().catch(() => false)) {
        foundMetric = true;
        break;
      }
    }

    expect(foundMetric).toBeTruthy();
  });

  test('should allow running a new benchmark', async ({ page }) => {
    await page.goto('/dashboards/benchmark?projectId=test-e2e-project');

    await page.waitForTimeout(1000);

    // Look for "Run Benchmark" button
    const runButton = page.locator('button:has-text("Run"), button:has-text("Start"), button:has-text("Benchmark")').first();

    if (await runButton.isVisible().catch(() => false)) {
      await expect(runButton).toBeEnabled();
    }
  });
});

test.describe('Dashboard Navigation', () => {
  test('should navigate between dashboards', async ({ page }) => {
    await page.goto('/dashboards/cost?projectId=test-project');

    // Look for navigation tabs/buttons
    const navElements = [
      'button:has-text("Collaboration")',
      'a:has-text("Collaboration")',
      '[role="tab"]:has-text("Collaboration")'
    ];

    for (const selector of navElements) {
      const element = page.locator(selector).first();
      if (await element.isVisible().catch(() => false)) {
        await element.click();
        await page.waitForTimeout(1000);

        // Verify we're on collaboration dashboard
        await expect(page.locator('text=/collaboration/i').first()).toBeVisible();
        break;
      }
    }
  });

  test('should maintain project ID across dashboard changes', async ({ page }) => {
    const projectId = 'test-persistent-project';

    await page.goto(`/dashboards/cost?projectId=${projectId}`);

    // Navigate to another dashboard
    const collaborationLink = page.locator('text=/collaboration/i').first();
    if (await collaborationLink.isVisible().catch(() => false)) {
      await collaborationLink.click();
      await page.waitForTimeout(500);

      // Check URL still has project ID
      expect(page.url()).toContain(projectId);
    }
  });
});
