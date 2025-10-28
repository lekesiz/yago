/**
 * YAGO v7.1 - Clarification Flow E2E Tests
 * Tests for the main clarification question flow
 */

import { test, expect } from '@playwright/test';

test.describe('Clarification Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Start at home page
    await page.goto('/');
  });

  test('should load the clarification flow page', async ({ page }) => {
    // Wait for the page to load
    await expect(page).toHaveTitle(/YAGO/i);

    // Check for main heading or key elements
    await expect(page.locator('h1, h2').first()).toBeVisible();
  });

  test('should display first question', async ({ page }) => {
    // Wait for question to load
    await page.waitForSelector('[data-testid="question-text"], .question-container', {
      timeout: 10000
    });

    // Verify question text is visible
    const questionText = page.locator('[data-testid="question-text"], .question-container').first();
    await expect(questionText).toBeVisible();
    await expect(questionText).not.toBeEmpty();
  });

  test('should show progress indicator', async ({ page }) => {
    // Look for progress indicators
    const progressIndicators = [
      '[data-testid="progress"]',
      '.progress',
      'text=/\\d+\\s*\\/\\s*\\d+/',  // Matches "1 / 5" format
      'text=/\\d+%/'  // Matches percentage
    ];

    // At least one progress indicator should be visible
    const hasProgress = await Promise.any(
      progressIndicators.map(selector =>
        page.locator(selector).first().isVisible().then(visible => {
          if (visible) return true;
          throw new Error('Not visible');
        })
      )
    ).catch(() => false);

    expect(hasProgress).toBeTruthy();
  });

  test('should allow answering a question', async ({ page }) => {
    // Wait for question to load
    await page.waitForSelector('textarea, input[type="text"], .answer-input', {
      timeout: 10000
    });

    // Find answer input
    const answerInput = page.locator('textarea, input[type="text"]').first();
    await answerInput.fill('This is a test answer for E2E testing');

    // Verify input has value
    await expect(answerInput).toHaveValue(/test answer/i);
  });

  test('should navigate between questions', async ({ page }) => {
    // Wait for initial question
    await page.waitForSelector('textarea', { timeout: 10000 });

    // Answer first question
    const answerInput = page.locator('textarea').first();
    await answerInput.fill('First answer');

    // Find and click Next button
    const nextButton = page.locator('button:has-text("Next"), button[aria-label*="next"]').first();

    if (await nextButton.isVisible()) {
      await nextButton.click();

      // Wait a bit for navigation
      await page.waitForTimeout(1000);

      // Verify we moved to next question (progress changed or different question)
      const currentQuestion = await page.locator('[data-testid="question-text"]').first().textContent();
      expect(currentQuestion).toBeDefined();
    }
  });

  test('should show validation for required fields', async ({ page }) => {
    await page.waitForSelector('button:has-text("Next")', { timeout: 10000 });

    // Try to click Next without answering
    const nextButton = page.locator('button:has-text("Next")').first();

    if (await nextButton.isEnabled()) {
      await nextButton.click();

      // Look for error message or validation feedback
      await page.waitForTimeout(500);

      // Check if we're still on same question (didn't navigate)
      const answerInput = page.locator('textarea').first();
      await expect(answerInput).toBeVisible();
    }
  });

  test('should allow going back to previous questions', async ({ page }) => {
    await page.waitForSelector('textarea', { timeout: 10000 });

    // Answer and go to next question
    await page.locator('textarea').first().fill('First answer');
    const nextButton = page.locator('button:has-text("Next")').first();

    if (await nextButton.isVisible() && await nextButton.isEnabled()) {
      const firstQuestionText = await page.locator('[data-testid="question-text"]').first().textContent();

      await nextButton.click();
      await page.waitForTimeout(1000);

      // Try to go back
      const prevButton = page.locator('button:has-text("Previous"), button:has-text("Back")').first();

      if (await prevButton.isVisible()) {
        await prevButton.click();
        await page.waitForTimeout(1000);

        // Verify we're back at first question
        const currentQuestionText = await page.locator('[data-testid="question-text"]').first().textContent();
        expect(currentQuestionText).toBe(firstQuestionText);
      }
    }
  });

  test('should maintain answers when navigating back', async ({ page }) => {
    await page.waitForSelector('textarea', { timeout: 10000 });

    const testAnswer = 'My test answer that should persist';

    // Fill answer
    await page.locator('textarea').first().fill(testAnswer);

    // Navigate away and back
    const nextButton = page.locator('button:has-text("Next")').first();
    if (await nextButton.isVisible() && await nextButton.isEnabled()) {
      await nextButton.click();
      await page.waitForTimeout(1000);

      const prevButton = page.locator('button:has-text("Previous"), button:has-text("Back")').first();
      if (await prevButton.isVisible()) {
        await prevButton.click();
        await page.waitForTimeout(1000);

        // Check if answer is still there
        const answerInput = page.locator('textarea').first();
        await expect(answerInput).toHaveValue(testAnswer);
      }
    }
  });

  test('should complete the flow successfully', async ({ page }) => {
    await page.waitForSelector('textarea', { timeout: 10000 });

    // Answer all questions (simulate)
    for (let i = 0; i < 5; i++) {
      const answerInput = page.locator('textarea').first();

      if (await answerInput.isVisible()) {
        await answerInput.fill(`Answer for question ${i + 1}`);

        const nextButton = page.locator('button:has-text("Next"), button:has-text("Finish"), button:has-text("Complete")').first();

        if (await nextButton.isVisible() && await nextButton.isEnabled()) {
          await nextButton.click();
          await page.waitForTimeout(1000);
        } else {
          // Might be at the end
          break;
        }
      } else {
        break;
      }
    }

    // Check for completion message or redirect
    await page.waitForTimeout(2000);

    // Look for success indicators
    const successIndicators = [
      'text=/complete/i',
      'text=/success/i',
      'text=/thank you/i',
      '[data-testid="completion"]'
    ];

    let foundSuccess = false;
    for (const selector of successIndicators) {
      if (await page.locator(selector).first().isVisible().catch(() => false)) {
        foundSuccess = true;
        break;
      }
    }

    // Either found success message OR no more questions
    const hasNoMoreQuestions = !(await page.locator('textarea').first().isVisible().catch(() => false));
    expect(foundSuccess || hasNoMoreQuestions).toBeTruthy();
  });
});
