import { test, expect } from '@playwright/test';
import { MapPage, RiskAssessmentForm, ResultsPanel } from '../utils/page-objects';
import scenarios from '../fixtures/test-scenarios.json';

/**
 * Performance E2E tests
 * Tests page load times, interaction responsiveness, and data processing speed
 */

test.describe('Performance - Page Load', () => {
  test('Initial page load under 3 seconds', async ({ page }) => {
    const startTime = Date.now();

    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');

    const loadTime = Date.now() - startTime;

    expect(loadTime).toBeLessThan(3000);
    console.log(`Page load time: ${loadTime}ms`);
  });

  test('Map renders within 2 seconds', async ({ page }) => {
    await page.goto('/');

    const startTime = Date.now();
    const mapPage = new MapPage(page);

    await mapPage.waitForMapLoad();

    const renderTime = Date.now() - startTime;

    expect(renderTime).toBeLessThan(2000);
    console.log(`Map render time: ${renderTime}ms`);
  });

  test('Full page load (networkidle) under 5 seconds', async ({ page }) => {
    const startTime = Date.now();

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const loadTime = Date.now() - startTime;

    expect(loadTime).toBeLessThan(5000);
    console.log(`Full page load time: ${loadTime}ms`);
  });

  test('Asset loading efficiency', async ({ page }) => {
    const resourceTimes: Record<string, number> = {};

    page.on('response', response => {
      const url = response.url();
      const timing = response.timing();
      
      if (timing && (url.includes('.js') || url.includes('.css') || url.includes('.png'))) {
        resourceTimes[url] = timing.responseEnd;
      }
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Main JS bundle should load quickly
    const jsBundles = Object.entries(resourceTimes).filter(([url]) => url.includes('.js'));
    expect(jsBundles.length).toBeGreaterThan(0);

    // No individual resource should take > 3 seconds
    Object.values(resourceTimes).forEach(time => {
      expect(time).toBeLessThan(3000);
    });
  });
});

test.describe('Performance - User Interactions', () => {
  test('Risk assessment completes within 3 seconds', async ({ page }) => {
    const mapPage = new MapPage(page);
    const assessmentForm = new RiskAssessmentForm(page);
    const resultsPanel = new ResultsPanel(page);

    await mapPage.goto();

    await assessmentForm.selectHazard('earthquake');
    await assessmentForm.fillRiskFactors({
      populationDensity: 5000,
      buildingCode: 7.0,
      infrastructure: 7.0,
    });

    const startTime = Date.now();
    await assessmentForm.submitAssessment();
    await resultsPanel.waitForResults();
    const assessmentTime = Date.now() - startTime;

    expect(assessmentTime).toBeLessThan(3000);
    console.log(`Assessment time: ${assessmentTime}ms`);
  });

  test('Multiple hazard assessment under 5 seconds', async ({ page }) => {
    const mapPage = new MapPage(page);
    const assessmentForm = new RiskAssessmentForm(page);
    const resultsPanel = new ResultsPanel(page);

    await mapPage.goto();

    await assessmentForm.selectMultipleHazards(['earthquake', 'flood', 'fire', 'storm']);
    await assessmentForm.fillRiskFactors({
      populationDensity: 5000,
      buildingCode: 6.5,
      infrastructure: 6.0,
    });

    const startTime = Date.now();
    await assessmentForm.submitAssessment();
    await resultsPanel.waitForResults();
    const assessmentTime = Date.now() - startTime;

    expect(assessmentTime).toBeLessThan(5000);
    console.log(`Multi-hazard assessment time: ${assessmentTime}ms`);
  });

  test('Map interaction responsiveness', async ({ page }) => {
    const mapPage = new MapPage(page);
    await mapPage.goto();

    const times: number[] = [];

    // Test multiple map clicks
    for (let i = 0; i < 5; i++) {
      const startTime = Date.now();
      await mapPage.clickMap(100 + i * 20, 100 + i * 20);
      await page.waitForTimeout(100);
      times.push(Date.now() - startTime);
    }

    // Average response time should be under 200ms
    const avgTime = times.reduce((a, b) => a + b, 0) / times.length;
    expect(avgTime).toBeLessThan(200);
    console.log(`Average map click response: ${avgTime}ms`);
  });

  test('Search functionality performance', async ({ page }) => {
    const mapPage = new MapPage(page);
    await mapPage.goto();

    const startTime = Date.now();
    await mapPage.searchLocation('San Francisco');
    
    // Wait for search results or map update
    await page.waitForTimeout(1000);
    const searchTime = Date.now() - startTime;

    expect(searchTime).toBeLessThan(2000);
    console.log(`Search time: ${searchTime}ms`);
  });
});

test.describe('Performance - Data Processing', () => {
  test('Sequential assessments maintain performance', async ({ page }) => {
    const mapPage = new MapPage(page);
    const assessmentForm = new RiskAssessmentForm(page);
    const resultsPanel = new ResultsPanel(page);

    await mapPage.goto();

    const times: number[] = [];

    // Run 5 sequential assessments
    for (let i = 0; i < 5; i++) {
      await assessmentForm.selectHazard('earthquake');
      await assessmentForm.fillRiskFactors({
        populationDensity: 5000 + i * 100,
        buildingCode: 7.0,
        infrastructure: 7.0,
      });

      const startTime = Date.now();
      await assessmentForm.submitAssessment();
      await resultsPanel.waitForResults();
      times.push(Date.now() - startTime);

      // Reset for next iteration
      if (i < 4) {
        await page.reload();
        await mapPage.waitForMapLoad();
      }
    }

    // Performance shouldn't degrade
    const firstTime = times[0];
    const lastTime = times[times.length - 1];
    
    // Last assessment shouldn't be more than 50% slower
    expect(lastTime).toBeLessThan(firstTime * 1.5);
    console.log(`Assessment times: ${times.join(', ')}ms`);
  });

  test('Large dataset handling', async ({ page }) => {
    const mapPage = new MapPage(page);
    const assessmentForm = new RiskAssessmentForm(page);
    const resultsPanel = new ResultsPanel(page);

    await mapPage.goto();

    // Assess all hazards with complex factors
    await assessmentForm.selectMultipleHazards(['earthquake', 'flood', 'fire', 'storm']);
    await assessmentForm.fillRiskFactors({
      populationDensity: 10000,
      buildingCode: 5.0,
      infrastructure: 5.0,
    });

    const startTime = Date.now();
    await assessmentForm.submitAssessment();
    await resultsPanel.waitForResults();
    const processingTime = Date.now() - startTime;

    // Even complex calculations should be fast
    expect(processingTime).toBeLessThan(6000);

    // Verify all results rendered
    const recommendations = await resultsPanel.getRecommendations();
    expect(recommendations.length).toBeGreaterThan(0);

    console.log(`Large dataset processing: ${processingTime}ms`);
  });

  test('Memory usage stays stable', async ({ page }) => {
    const mapPage = new MapPage(page);
    const assessmentForm = new RiskAssessmentForm(page);

    await mapPage.goto();

    // Get initial memory if available
    const initialMemory = await page.evaluate(() => {
      return (performance as any).memory?.usedJSHeapSize || 0;
    });

    // Perform multiple operations
    for (let i = 0; i < 10; i++) {
      await assessmentForm.selectHazard('flood');
      await assessmentForm.submitAssessment();
      await page.waitForTimeout(500);
      
      if (i < 9) {
        await page.reload();
        await mapPage.waitForMapLoad();
      }
    }

    // Check memory hasn't grown excessively
    const finalMemory = await page.evaluate(() => {
      return (performance as any).memory?.usedJSHeapSize || 0;
    });

    if (initialMemory > 0 && finalMemory > 0) {
      const memoryGrowth = finalMemory - initialMemory;
      const growthPercent = (memoryGrowth / initialMemory) * 100;

      // Memory shouldn't grow by more than 100%
      expect(growthPercent).toBeLessThan(100);
      console.log(`Memory growth: ${growthPercent.toFixed(2)}%`);
    }
  });
});

test.describe('Performance - Network Efficiency', () => {
  test('API requests are optimized', async ({ page }) => {
    let requestCount = 0;
    const apiRequests: string[] = [];

    page.on('request', request => {
      if (request.url().includes('/api/')) {
        requestCount++;
        apiRequests.push(request.url());
      }
    });

    const mapPage = new MapPage(page);
    const assessmentForm = new RiskAssessmentForm(page);

    await mapPage.goto();

    await assessmentForm.selectHazard('earthquake');
    await assessmentForm.submitAssessment();

    await page.waitForTimeout(2000);

    // Should make minimal API calls
    expect(requestCount).toBeLessThan(10);
    console.log(`API requests made: ${requestCount}`);
    console.log(`API endpoints called:`, apiRequests);
  });

  test('No unnecessary re-renders', async ({ page }) => {
    const mapPage = new MapPage(page);
    await mapPage.goto();

    // Monitor console for React DevTools warnings
    const warnings: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'warning' && msg.text().includes('render')) {
        warnings.push(msg.text());
      }
    });

    // Interact with page
    await mapPage.clickMap(150, 150);
    await page.waitForTimeout(1000);

    // Should have minimal re-render warnings
    expect(warnings.length).toBeLessThan(5);
  });

  test('Export data generation is fast', async ({ page }) => {
    const mapPage = new MapPage(page);
    const assessmentForm = new RiskAssessmentForm(page);
    const resultsPanel = new ResultsPanel(page);

    await mapPage.goto();

    await assessmentForm.selectMultipleHazards(['earthquake', 'flood']);
    await assessmentForm.submitAssessment();
    await resultsPanel.waitForResults();

    const startTime = Date.now();
    const downloadPromise = page.waitForEvent('download', { timeout: 5000 });
    
    await resultsPanel.exportData('json');
    await downloadPromise;
    
    const exportTime = Date.now() - startTime;

    expect(exportTime).toBeLessThan(2000);
    console.log(`Export generation time: ${exportTime}ms`);
  });
});

test.describe('Performance - Lighthouse Metrics', () => {
  test('Performance score targets', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Get Web Vitals if available
    const vitals = await page.evaluate(() => {
      return {
        lcp: (performance as any).getEntriesByType?.('largest-contentful-paint')?.[0]?.renderTime || 0,
        fid: (performance as any).getEntriesByType?.('first-input')?.[0]?.processingStart || 0,
        cls: (performance as any).getEntriesByType?.('layout-shift')?.reduce((sum: number, entry: any) => sum + entry.value, 0) || 0,
      };
    });

    console.log('Web Vitals:', vitals);

    // LCP should be under 2.5s
    if (vitals.lcp > 0) {
      expect(vitals.lcp).toBeLessThan(2500);
    }

    // CLS should be under 0.1
    if (vitals.cls > 0) {
      expect(vitals.cls).toBeLessThan(0.1);
    }
  });
});
