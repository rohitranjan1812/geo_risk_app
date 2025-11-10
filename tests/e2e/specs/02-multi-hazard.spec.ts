import { test, expect } from '@playwright/test';
import { RiskAssessmentForm, ResultsPanel } from '../utils/page-objects';
import scenarios from '../fixtures/test-scenarios.json';

/**
 * Multi-hazard scenario E2E tests
 * Tests complex scenarios with multiple hazards
 */

test.describe('Multi-Hazard Scenarios', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  for (const scenario of scenarios.multiHazardScenarios) {
    test(`${scenario.name}: Assess multiple hazards simultaneously`, async ({ page, request }) => {
      const assessmentForm = new RiskAssessmentForm(page);
      const resultsPanel = new ResultsPanel(page);

      // Fill in custom location if needed
      const latInput = page.locator('input[name*="latitude"], input[placeholder*="Lat"]').first();
      const lonInput = page.locator('input[name*="longitude"], input[placeholder*="Lon"]').first();
      
      if (await latInput.isVisible({ timeout: 2000 }).catch(() => false)) {
        await latInput.fill(scenario.location.latitude.toString());
        await lonInput.fill(scenario.location.longitude.toString());
      }

      // Select all hazards for this scenario
      await assessmentForm.selectMultipleHazards(scenario.hazards);

      // Input risk factors
      await assessmentForm.fillRiskFactors({
        populationDensity: scenario.riskFactors.population_density,
        buildingCode: scenario.riskFactors.building_code_rating,
        infrastructure: scenario.riskFactors.infrastructure_quality,
      });

      // Submit assessment
      await assessmentForm.submitAssessment();

      // Wait for results
      await resultsPanel.waitForResults();

      // Verify all hazards have results
      for (const hazard of scenario.hazards) {
        const score = await resultsPanel.getRiskScore(hazard).catch(() => 0);
        const expectedMin = scenario.expectedMinScores[hazard] || 0;
        
        // Verify score is calculated and meets minimum threshold
        expect(score).toBeGreaterThan(0);
        
        // For high-risk scenarios, verify scores are appropriately high
        if (expectedMin > 0) {
          expect(score).toBeGreaterThanOrEqual(expectedMin * 0.7); // Allow 30% variance
        }
      }

      // Verify risk levels are assigned
      for (const hazard of scenario.hazards) {
        const level = await resultsPanel.getRiskLevel(hazard).catch(() => '');
        expect(['low', 'moderate', 'high', 'critical']).toContain(level);
      }

      // Take screenshot for documentation
      await page.screenshot({ 
        path: `screenshots/${scenario.name.replace(/\s+/g, '-')}.png`,
        fullPage: true 
      });
    });
  }

  test('All hazards assessment: Compare relative risks', async ({ page }) => {
    const assessmentForm = new RiskAssessmentForm(page);
    const resultsPanel = new ResultsPanel(page);

    // Select ALL hazards
    await assessmentForm.selectMultipleHazards(['earthquake', 'flood', 'fire', 'storm']);

    // Use uniform moderate risk factors
    await assessmentForm.fillRiskFactors({
      populationDensity: 5000,
      buildingCode: 6.0,
      infrastructure: 6.0,
    });

    await assessmentForm.submitAssessment();
    await resultsPanel.waitForResults();

    // Collect all scores
    const scores = {
      earthquake: await resultsPanel.getRiskScore('earthquake').catch(() => 0),
      flood: await resultsPanel.getRiskScore('flood').catch(() => 0),
      fire: await resultsPanel.getRiskScore('fire').catch(() => 0),
      storm: await resultsPanel.getRiskScore('storm').catch(() => 0),
    };

    // Verify all hazards assessed
    expect(Object.values(scores).every(s => s > 0)).toBeTruthy();

    // Verify scores are in reasonable range (0-100)
    expect(Object.values(scores).every(s => s <= 100)).toBeTruthy();
    expect(Object.values(scores).every(s => s >= 0)).toBeTruthy();
  });

  test('Hazard combination: Earthquake + Fire correlation', async ({ page }) => {
    const assessmentForm = new RiskAssessmentForm(page);
    const resultsPanel = new ResultsPanel(page);

    // Earthquake zones often have fire risk due to infrastructure damage
    await assessmentForm.selectMultipleHazards(['earthquake', 'fire']);

    // High population, moderate infrastructure
    await assessmentForm.fillRiskFactors({
      populationDensity: 8000,
      buildingCode: 6.5,
      infrastructure: 6.0,
    });

    await assessmentForm.submitAssessment();
    await resultsPanel.waitForResults();

    const earthquakeScore = await resultsPanel.getRiskScore('earthquake');
    const fireScore = await resultsPanel.getRiskScore('fire');

    // Both should show elevated risk
    expect(earthquakeScore).toBeGreaterThan(30);
    expect(fireScore).toBeGreaterThan(20);

    // Recommendations should address both hazards
    const recommendations = await resultsPanel.getRecommendations();
    expect(recommendations.length).toBeGreaterThan(0);
  });

  test('Coastal hazards: Flood + Storm interaction', async ({ page }) => {
    const assessmentForm = new RiskAssessmentForm(page);
    const resultsPanel = new ResultsPanel(page);

    // Coastal areas face both flood and storm risks
    await assessmentForm.selectMultipleHazards(['flood', 'storm']);

    // Poor infrastructure increases vulnerability
    await assessmentForm.fillRiskFactors({
      populationDensity: 4000,
      buildingCode: 5.0,
      infrastructure: 4.5,
    });

    await assessmentForm.submitAssessment();
    await resultsPanel.waitForResults();

    const floodScore = await resultsPanel.getRiskScore('flood');
    const stormScore = await resultsPanel.getRiskScore('storm');

    // Both coastal hazards should register
    expect(floodScore).toBeGreaterThan(0);
    expect(stormScore).toBeGreaterThan(0);

    // With poor infrastructure, scores should be elevated
    expect(Math.max(floodScore, stormScore)).toBeGreaterThan(40);
  });

  test('Risk factor impact: Compare high vs low infrastructure', async ({ page }) => {
    const assessmentForm = new RiskAssessmentForm(page);
    const resultsPanel = new ResultsPanel(page);

    // First assessment: Low infrastructure
    await assessmentForm.selectHazard('flood');
    await assessmentForm.fillRiskFactors({
      populationDensity: 5000,
      buildingCode: 7.0,
      infrastructure: 3.0, // Poor
    });
    await assessmentForm.submitAssessment();
    await resultsPanel.waitForResults();

    const lowInfraScore = await resultsPanel.getRiskScore('flood');

    // Reset and second assessment: High infrastructure
    await page.reload();
    await page.waitForLoadState('networkidle');

    const assessmentForm2 = new RiskAssessmentForm(page);
    const resultsPanel2 = new ResultsPanel(page);

    await assessmentForm2.selectHazard('flood');
    await assessmentForm2.fillRiskFactors({
      populationDensity: 5000,
      buildingCode: 7.0,
      infrastructure: 9.0, // Excellent
    });
    await assessmentForm2.submitAssessment();
    await resultsPanel2.waitForResults();

    const highInfraScore = await resultsPanel2.getRiskScore('flood');

    // Better infrastructure should reduce risk
    expect(highInfraScore).toBeLessThan(lowInfraScore);
    
    // Difference should be significant (at least 10 points)
    expect(lowInfraScore - highInfraScore).toBeGreaterThan(10);
  });
});

test.describe('Edge Cases and Boundary Conditions', () => {
  test('Minimum risk factors: All zeros', async ({ page }) => {
    const assessmentForm = new RiskAssessmentForm(page);
    const resultsPanel = new ResultsPanel(page);

    await assessmentForm.selectHazard('earthquake');
    await assessmentForm.fillRiskFactors({
      populationDensity: 0,
      buildingCode: 0,
      infrastructure: 0,
    });

    await assessmentForm.submitAssessment();
    
    // Should either show validation error or very low risk
    const hasError = await page.locator('[class*="error"], [role="alert"]')
      .isVisible({ timeout: 2000 }).catch(() => false);
    
    if (!hasError) {
      await resultsPanel.waitForResults();
      const score = await resultsPanel.getRiskScore('earthquake');
      expect(score).toBeDefined();
    }
  });

  test('Maximum risk factors: All extreme values', async ({ page }) => {
    const assessmentForm = new RiskAssessmentForm(page);
    const resultsPanel = new ResultsPanel(page);

    await assessmentForm.selectMultipleHazards(['earthquake', 'flood']);
    await assessmentForm.fillRiskFactors({
      populationDensity: 50000,
      buildingCode: 0,
      infrastructure: 0,
    });

    await assessmentForm.submitAssessment();
    await resultsPanel.waitForResults();

    // Worst-case scenario should show high/critical risk
    const earthquakeScore = await resultsPanel.getRiskScore('earthquake');
    const earthquakeLevel = await resultsPanel.getRiskLevel('earthquake');

    expect(earthquakeScore).toBeGreaterThan(50);
    expect(['high', 'critical']).toContain(earthquakeLevel);
  });
});
