import { Page, Locator, expect } from '@playwright/test';

/**
 * Page object models for E2E tests
 */

export class MapPage {
  readonly page: Page;
  readonly map: Locator;
  readonly searchInput: Locator;
  readonly searchButton: Locator;
  readonly locationMarker: Locator;

  constructor(page: Page) {
    this.page = page;
    this.map = page.locator('.leaflet-container, [class*="map"]').first();
    this.searchInput = page.locator('input[placeholder*="Search"], input[type="search"]').first();
    this.searchButton = page.locator('button:has-text("Search"), button[type="submit"]').first();
    this.locationMarker = page.locator('.leaflet-marker-icon, [class*="marker"]').first();
  }

  async goto() {
    await this.page.goto('/');
    await this.waitForMapLoad();
  }

  async waitForMapLoad() {
    await this.map.waitFor({ state: 'visible', timeout: 10000 });
  }

  async searchLocation(query: string) {
    await this.searchInput.fill(query);
    await this.searchButton.click();
  }

  async clickMap(x: number, y: number) {
    const box = await this.map.boundingBox();
    if (box) {
      await this.page.mouse.click(box.x + x, box.y + y);
    }
  }

  async isMapVisible(): Promise<boolean> {
    return await this.map.isVisible();
  }
}

export class RiskAssessmentForm {
  readonly page: Page;
  readonly hazardCheckboxes: Locator;
  readonly populationInput: Locator;
  readonly buildingCodeInput: Locator;
  readonly infrastructureInput: Locator;
  readonly assessButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.hazardCheckboxes = page.locator('input[type="checkbox"][name*="hazard"], label:has(input[type="checkbox"])');
    this.populationInput = page.locator('input[name*="population"], input[placeholder*="Population"]').first();
    this.buildingCodeInput = page.locator('input[name*="building"], input[placeholder*="Building"]').first();
    this.infrastructureInput = page.locator('input[name*="infrastructure"], input[placeholder*="Infrastructure"]').first();
    this.assessButton = page.locator('button:has-text("Assess"), button:has-text("Calculate")').first();
  }

  async selectHazard(hazardType: string) {
    const checkbox = this.page.locator(`input[type="checkbox"][value="${hazardType}"], label:has-text("${hazardType}") input`).first();
    await checkbox.check();
  }

  async selectMultipleHazards(hazardTypes: string[]) {
    for (const hazard of hazardTypes) {
      await this.selectHazard(hazard);
    }
  }

  async fillRiskFactors(factors: {
    populationDensity?: number;
    buildingCode?: number;
    infrastructure?: number;
  }) {
    if (factors.populationDensity !== undefined) {
      await this.populationInput.fill(factors.populationDensity.toString());
    }
    if (factors.buildingCode !== undefined) {
      await this.buildingCodeInput.fill(factors.buildingCode.toString());
    }
    if (factors.infrastructure !== undefined) {
      await this.infrastructureInput.fill(factors.infrastructure.toString());
    }
  }

  async submitAssessment() {
    await this.assessButton.click();
  }
}

export class ResultsPanel {
  readonly page: Page;
  readonly resultsContainer: Locator;
  readonly riskScores: Locator;
  readonly riskLevels: Locator;
  readonly recommendations: Locator;
  readonly exportButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.resultsContainer = page.locator('[class*="result"], [class*="assessment"]').first();
    this.riskScores = page.locator('[class*="score"], [data-testid*="score"]');
    this.riskLevels = page.locator('[class*="level"], [data-testid*="level"]');
    this.recommendations = page.locator('[class*="recommendation"]');
    this.exportButton = page.locator('button:has-text("Export"), button:has-text("Download")').first();
  }

  async waitForResults() {
    await this.resultsContainer.waitFor({ state: 'visible', timeout: 15000 });
  }

  async getRiskScore(hazardType: string): Promise<number> {
    const scoreElement = this.page.locator(`[data-hazard="${hazardType}"] [class*="score"], :has-text("${hazardType}") ~ [class*="score"]`).first();
    const text = await scoreElement.textContent();
    return parseFloat(text?.replace(/[^0-9.]/g, '') || '0');
  }

  async getRiskLevel(hazardType: string): Promise<string> {
    const levelElement = this.page.locator(`[data-hazard="${hazardType}"] [class*="level"], :has-text("${hazardType}") ~ [class*="level"]`).first();
    const text = await levelElement.textContent();
    return text?.toLowerCase().trim() || '';
  }

  async getRecommendations(): Promise<string[]> {
    const elements = await this.recommendations.all();
    const recommendations: string[] = [];
    for (const el of elements) {
      const text = await el.textContent();
      if (text) recommendations.push(text.trim());
    }
    return recommendations;
  }

  async exportData(format: 'json' | 'csv' = 'json'): Promise<void> {
    const downloadPromise = this.page.waitForEvent('download');
    await this.exportButton.click();
    
    // Select format if there's a dropdown
    const formatButton = this.page.locator(`button:has-text("${format.toUpperCase()}")`);
    if (await formatButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await formatButton.click();
    }
    
    await downloadPromise;
  }

  async isVisible(): Promise<boolean> {
    return await this.resultsContainer.isVisible();
  }
}

export class ErrorDisplay {
  readonly page: Page;
  readonly errorMessage: Locator;
  readonly errorDialog: Locator;
  readonly closeButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.errorMessage = page.locator('[class*="error"], [role="alert"]').first();
    this.errorDialog = page.locator('[role="dialog"]:has-text("Error"), [class*="modal"]:has-text("Error")').first();
    this.closeButton = page.locator('button:has-text("Close"), button:has-text("Dismiss")').first();
  }

  async isErrorVisible(): Promise<boolean> {
    return await this.errorMessage.isVisible({ timeout: 5000 }).catch(() => false);
  }

  async getErrorText(): Promise<string> {
    const text = await this.errorMessage.textContent();
    return text?.trim() || '';
  }

  async dismissError() {
    if (await this.closeButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await this.closeButton.click();
    }
  }
}
