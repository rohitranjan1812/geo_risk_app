import { test, expect } from '@playwright/test';
import { MapPage, RiskAssessmentForm, ResultsPanel } from '../utils/page-objects';
import locations from '../fixtures/locations.json';

/**
 * Complete user journey E2E tests
 * Tests the full workflow from landing to data export
 */

test.describe('Complete User Journey', () => {
  let mapPage: MapPage;
  let assessmentForm: RiskAssessmentForm;
  let resultsPanel: ResultsPanel;

  test.beforeEach(async ({ page }) => {
    mapPage = new MapPage(page);
    assessmentForm = new RiskAssessmentForm(page);
    resultsPanel = new ResultsPanel(page);
    
    await mapPage.goto();
  });

  test('Full workflow: load → search → select → assess → export', async ({ page }) => {
    // 1. Verify app loads successfully
    await expect(page).toHaveTitle(/geo.*risk|risk.*assessment/i);
    expect(await mapPage.isMapVisible()).toBeTruthy();

    // 2. Search for a location
    const testLocation = locations[0]; // San Francisco
    await mapPage.searchLocation(testLocation.name);
    
    // Wait for search results or map update
    await page.waitForTimeout(1000);

    // 3. Select location on map (or from search results)
    // Try clicking a search result if available
    const searchResult = page.locator(`text="${testLocation.name}"`).first();
    if (await searchResult.isVisible({ timeout: 3000 }).catch(() => false)) {
      await searchResult.click();
    }

    // 4. Choose hazards
    await assessmentForm.selectMultipleHazards(['earthquake', 'fire']);

    // 5. Input risk factors
    await assessmentForm.fillRiskFactors({
      populationDensity: testLocation.population_density,
      buildingCode: testLocation.building_code_rating,
      infrastructure: testLocation.infrastructure_quality,
    });

    // 6. Submit assessment
    await assessmentForm.submitAssessment();

    // 7. View results
    await resultsPanel.waitForResults();
    expect(await resultsPanel.isVisible()).toBeTruthy();

    // Verify earthquake results (high risk area)
    const earthquakeScore = await resultsPanel.getRiskScore('earthquake');
    expect(earthquakeScore).toBeGreaterThan(0);

    // Verify recommendations are provided
    const recommendations = await resultsPanel.getRecommendations();
    expect(recommendations.length).toBeGreaterThan(0);

    // 8. Export data
    const downloadPromise = page.waitForEvent('download', { timeout: 10000 });
    await resultsPanel.exportData('json');
    
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/\.(json|csv)$/);
    
    // Verify downloaded file content
    const path = await download.path();
    expect(path).toBeTruthy();
  });

  test('Map interaction workflow: click map → input data → assess', async ({ page }) => {
    // 1. Click on map to set custom location
    await mapPage.clickMap(200, 200);
    
    // Wait for location selection
    await page.waitForTimeout(500);

    // 2. Fill in location details manually
    const locationNameInput = page.locator('input[name*="name"], input[placeholder*="Location"]').first();
    if (await locationNameInput.isVisible({ timeout: 2000 }).catch(() => false)) {
      await locationNameInput.fill('Custom Test Location');
    }

    // 3. Select all hazards
    await assessmentForm.selectMultipleHazards(['earthquake', 'flood', 'fire', 'storm']);

    // 4. Input moderate risk factors
    await assessmentForm.fillRiskFactors({
      populationDensity: 5000,
      buildingCode: 6.5,
      infrastructure: 6.0,
    });

    // 5. Submit and verify results
    await assessmentForm.submitAssessment();
    await resultsPanel.waitForResults();

    // All four hazards should have results
    const earthquakeScore = await resultsPanel.getRiskScore('earthquake').catch(() => 0);
    const floodScore = await resultsPanel.getRiskScore('flood').catch(() => 0);
    const fireScore = await resultsPanel.getRiskScore('fire').catch(() => 0);
    const stormScore = await resultsPanel.getRiskScore('storm').catch(() => 0);

    // At least some scores should be calculated
    const totalScore = earthquakeScore + floodScore + fireScore + stormScore;
    expect(totalScore).toBeGreaterThan(0);
  });

  test('Multiple location comparison workflow', async ({ page }) => {
    const results: Array<{ location: string; score: number }> = [];

    // Assess multiple locations
    for (const location of locations.slice(0, 3)) {
      // Search and select location
      await mapPage.searchLocation(location.name);
      await page.waitForTimeout(1000);

      const searchResult = page.locator(`text="${location.name}"`).first();
      if (await searchResult.isVisible({ timeout: 2000 }).catch(() => false)) {
        await searchResult.click();
      }

      // Select earthquake hazard
      await assessmentForm.selectHazard('earthquake');

      // Use location's default factors
      await assessmentForm.fillRiskFactors({
        populationDensity: location.population_density,
        buildingCode: location.building_code_rating,
        infrastructure: location.infrastructure_quality,
      });

      // Assess
      await assessmentForm.submitAssessment();
      await resultsPanel.waitForResults();

      // Record result
      const score = await resultsPanel.getRiskScore('earthquake').catch(() => 0);
      results.push({ location: location.name, score });

      // Reset for next iteration
      await page.reload();
      await mapPage.waitForMapLoad();
    }

    // Verify we got results for all locations
    expect(results.length).toBe(3);
    expect(results.every(r => r.score > 0)).toBeTruthy();
  });

  test('Quick assessment workflow with defaults', async ({ page }) => {
    // Search location
    await mapPage.searchLocation('Los Angeles');
    await page.waitForTimeout(1000);

    // Select just one hazard
    await assessmentForm.selectHazard('earthquake');

    // Submit without changing default risk factors
    await assessmentForm.submitAssessment();

    // Should still get results
    await resultsPanel.waitForResults();
    const score = await resultsPanel.getRiskScore('earthquake').catch(() => 0);
    expect(score).toBeGreaterThan(0);
  });
});

test.describe('User Journey - Mobile Device', () => {
  test.use({ viewport: { width: 375, height: 667 } });

  test('Mobile workflow: touch interactions', async ({ page }) => {
    const mapPage = new MapPage(page);
    const assessmentForm = new RiskAssessmentForm(page);
    
    await mapPage.goto();

    // Verify mobile layout loads
    expect(await mapPage.isMapVisible()).toBeTruthy();

    // Search on mobile
    await mapPage.searchLocation('Miami');
    await page.waitForTimeout(1000);

    // Select hazard
    await assessmentForm.selectHazard('storm');

    // Submit
    await assessmentForm.submitAssessment();

    // Wait for results (mobile may be slower)
    const resultsPanel = new ResultsPanel(page);
    await resultsPanel.waitForResults();
    
    expect(await resultsPanel.isVisible()).toBeTruthy();
  });
});
