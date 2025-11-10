import { test, expect } from '@playwright/test';
import { MapPage, RiskAssessmentForm, ResultsPanel, ErrorDisplay } from '../utils/page-objects';

/**
 * Error handling and resilience E2E tests
 * Tests application behavior under error conditions
 */

test.describe('Error Handling - API Failures', () => {
  test('Handle API server unavailable', async ({ page, context }) => {
    // Block backend API requests
    await context.route('**/api/**', route => route.abort());

    const mapPage = new MapPage(page);
    const assessmentForm = new RiskAssessmentForm(page);
    const errorDisplay = new ErrorDisplay(page);

    await mapPage.goto();

    // Try to submit assessment
    await assessmentForm.selectHazard('earthquake');
    await assessmentForm.submitAssessment();

    // Should show error message
    await page.waitForTimeout(2000);
    expect(await errorDisplay.isErrorVisible()).toBeTruthy();

    const errorText = await errorDisplay.getErrorText();
    expect(errorText.toLowerCase()).toMatch(/error|fail|unavailable|network/);
  });

  test('Handle 404 Not Found response', async ({ page, context }) => {
    // Intercept and return 404
    await context.route('**/api/assess-risk', route => {
      route.fulfill({
        status: 404,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Endpoint not found' }),
      });
    });

    const mapPage = new MapPage(page);
    const assessmentForm = new RiskAssessmentForm(page);
    const errorDisplay = new ErrorDisplay(page);

    await mapPage.goto();

    await assessmentForm.selectHazard('flood');
    await assessmentForm.submitAssessment();

    await page.waitForTimeout(2000);
    expect(await errorDisplay.isErrorVisible()).toBeTruthy();
  });

  test('Handle 500 Internal Server Error', async ({ page, context }) => {
    // Intercept and return 500
    await context.route('**/api/assess-risk', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal server error' }),
      });
    });

    const mapPage = new MapPage(page);
    const assessmentForm = new RiskAssessmentForm(page);
    const errorDisplay = new ErrorDisplay(page);

    await mapPage.goto();

    await assessmentForm.selectHazard('storm');
    await assessmentForm.submitAssessment();

    await page.waitForTimeout(2000);
    
    // Should display user-friendly error
    expect(await errorDisplay.isErrorVisible()).toBeTruthy();
    const errorText = await errorDisplay.getErrorText();
    expect(errorText.length).toBeGreaterThan(0);
  });

  test('Handle 422 Validation Error', async ({ page, context }) => {
    // Intercept and return validation error
    await context.route('**/api/assess-risk', route => {
      route.fulfill({
        status: 422,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: [
            {
              loc: ['body', 'latitude'],
              msg: 'Latitude must be between -90 and 90',
              type: 'value_error',
            },
          ],
        }),
      });
    });

    const mapPage = new MapPage(page);
    const assessmentForm = new RiskAssessmentForm(page);
    const errorDisplay = new ErrorDisplay(page);

    await mapPage.goto();

    await assessmentForm.selectHazard('fire');
    await assessmentForm.submitAssessment();

    await page.waitForTimeout(2000);
    
    // Should show validation error
    expect(await errorDisplay.isErrorVisible()).toBeTruthy();
    const errorText = await errorDisplay.getErrorText();
    expect(errorText.toLowerCase()).toMatch(/latitude|validation|invalid/);
  });

  test('Handle slow API response (timeout)', async ({ page, context }) => {
    // Delay response significantly
    await context.route('**/api/assess-risk', route => {
      setTimeout(() => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ assessments: [] }),
        });
      }, 30000); // 30 second delay
    });

    const mapPage = new MapPage(page);
    const assessmentForm = new RiskAssessmentForm(page);

    await mapPage.goto();

    await assessmentForm.selectHazard('earthquake');
    await assessmentForm.submitAssessment();

    // Should show loading indicator
    const loadingIndicator = page.locator('[class*="loading"], [class*="spinner"], [aria-busy="true"]').first();
    expect(await loadingIndicator.isVisible({ timeout: 2000 }).catch(() => false)).toBeTruthy();

    // After timeout, should show error or keep loading
    await page.waitForTimeout(5000);
  });
});

test.describe('Error Handling - Network Errors', () => {
  test('Handle network disconnection', async ({ page, context }) => {
    const mapPage = new MapPage(page);
    const assessmentForm = new RiskAssessmentForm(page);
    const errorDisplay = new ErrorDisplay(page);

    await mapPage.goto();

    // Simulate network disconnection
    await context.setOffline(true);

    await assessmentForm.selectHazard('flood');
    await assessmentForm.submitAssessment();

    await page.waitForTimeout(2000);
    
    // Should handle offline gracefully
    const hasError = await errorDisplay.isErrorVisible();
    const hasOfflineIndicator = await page.locator('text=/offline|no connection|network error/i')
      .first().isVisible({ timeout: 2000 }).catch(() => false);

    expect(hasError || hasOfflineIndicator).toBeTruthy();

    // Restore connection
    await context.setOffline(false);
  });

  test('Retry after network error', async ({ page, context }) => {
    const mapPage = new MapPage(page);
    const assessmentForm = new RiskAssessmentForm(page);
    const resultsPanel = new ResultsPanel(page);

    await mapPage.goto();

    let requestCount = 0;
    await context.route('**/api/assess-risk', route => {
      requestCount++;
      if (requestCount === 1) {
        // First request fails
        route.abort();
      } else {
        // Subsequent requests succeed
        route.continue();
      }
    });

    await assessmentForm.selectHazard('storm');
    await assessmentForm.submitAssessment();

    // First attempt should fail
    await page.waitForTimeout(2000);

    // Retry button if available
    const retryButton = page.locator('button:has-text("Retry"), button:has-text("Try Again")').first();
    if (await retryButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await retryButton.click();
      
      // Second attempt should succeed
      await resultsPanel.waitForResults();
      expect(await resultsPanel.isVisible()).toBeTruthy();
    }
  });
});

test.describe('Error Handling - Invalid Inputs', () => {
  test('Validate latitude boundaries', async ({ page }) => {
    const errorDisplay = new ErrorDisplay(page);
    await page.goto('/');

    // Try invalid latitude (> 90)
    const latInput = page.locator('input[name*="latitude"]').first();
    if (await latInput.isVisible({ timeout: 2000 }).catch(() => false)) {
      await latInput.fill('95.0');
      await page.keyboard.press('Tab');

      await page.waitForTimeout(500);
      
      // Should show validation error
      const validationError = page.locator('text=/latitude.*between|invalid latitude/i').first();
      const hasValidationError = await validationError.isVisible({ timeout: 2000 }).catch(() => false);
      const hasGeneralError = await errorDisplay.isErrorVisible();

      expect(hasValidationError || hasGeneralError).toBeTruthy();
    }
  });

  test('Validate required fields', async ({ page }) => {
    const assessmentForm = new RiskAssessmentForm(page);
    const errorDisplay = new ErrorDisplay(page);

    await page.goto('/');

    // Submit without selecting hazards
    await assessmentForm.submitAssessment();

    await page.waitForTimeout(1000);

    // Should show validation message
    const requiredError = page.locator('text=/required|select.*hazard/i').first();
    const hasRequiredError = await requiredError.isVisible({ timeout: 2000 }).catch(() => false);
    const hasGeneralError = await errorDisplay.isErrorVisible();

    expect(hasRequiredError || hasGeneralError).toBeTruthy();
  });

  test('Validate numeric input ranges', async ({ page }) => {
    const assessmentForm = new RiskAssessmentForm(page);
    await page.goto('/');

    // Try invalid building code rating (> 10)
    const buildingInput = page.locator('input[name*="building"]').first();
    if (await buildingInput.isVisible({ timeout: 2000 }).catch(() => false)) {
      await buildingInput.fill('15');
      await page.keyboard.press('Tab');

      await page.waitForTimeout(500);

      // Should show validation or auto-correct
      const value = await buildingInput.inputValue();
      // Either corrected to max (10) or shows error
      const isValidated = parseFloat(value) <= 10;
      const hasError = await page.locator('text=/must be.*10|maximum/i')
        .first().isVisible({ timeout: 1000 }).catch(() => false);

      expect(isValidated || hasError).toBeTruthy();
    }
  });
});

test.describe('Error Handling - Recovery and Resilience', () => {
  test('Dismiss error and continue workflow', async ({ page, context }) => {
    const mapPage = new MapPage(page);
    const assessmentForm = new RiskAssessmentForm(page);
    const resultsPanel = new ResultsPanel(page);
    const errorDisplay = new ErrorDisplay(page);

    // Cause initial error
    await context.route('**/api/assess-risk', route => route.abort(), { times: 1 });

    await mapPage.goto();

    await assessmentForm.selectHazard('earthquake');
    await assessmentForm.submitAssessment();

    await page.waitForTimeout(2000);
    expect(await errorDisplay.isErrorVisible()).toBeTruthy();

    // Dismiss error
    await errorDisplay.dismissError();

    // Network now works - retry should succeed
    await assessmentForm.submitAssessment();
    await resultsPanel.waitForResults();

    expect(await resultsPanel.isVisible()).toBeTruthy();
  });

  test('Handle partial data in response', async ({ page, context }) => {
    const mapPage = new MapPage(page);
    const assessmentForm = new RiskAssessmentForm(page);
    const resultsPanel = new ResultsPanel(page);

    // Return incomplete data
    await context.route('**/api/assess-risk', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          assessments: [
            {
              hazard_type: 'earthquake',
              // Missing fields
            },
          ],
        }),
      });
    });

    await mapPage.goto();

    await assessmentForm.selectHazard('earthquake');
    await assessmentForm.submitAssessment();

    await page.waitForTimeout(2000);

    // Should handle gracefully - either show error or partial results
    const hasResults = await resultsPanel.isVisible().catch(() => false);
    const hasError = await page.locator('[class*="error"]').isVisible({ timeout: 2000 }).catch(() => false);

    expect(hasResults || hasError).toBeTruthy();
  });

  test('Graceful degradation: Continue with cached data', async ({ page, context }) => {
    const mapPage = new MapPage(page);
    const assessmentForm = new RiskAssessmentForm(page);
    const resultsPanel = new ResultsPanel(page);

    await mapPage.goto();

    // First successful request
    await assessmentForm.selectHazard('flood');
    await assessmentForm.submitAssessment();
    await resultsPanel.waitForResults();

    const firstScore = await resultsPanel.getRiskScore('flood');

    // Reload and block API
    await context.route('**/api/**', route => route.abort());
    await page.reload();

    // App should still be usable (may show cached data or offline mode)
    const isMapVisible = await mapPage.isMapVisible().catch(() => false);
    expect(isMapVisible).toBeTruthy();
  });
});
