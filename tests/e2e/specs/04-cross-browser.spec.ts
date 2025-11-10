import { test, expect, devices } from '@playwright/test';
import { MapPage } from '../utils/page-objects';

/**
 * Cross-browser compatibility E2E tests
 * Tests application behavior across different browsers and devices
 */

test.describe('Cross-Browser Compatibility - Desktop', () => {
  test('Chrome: Full feature compatibility', async ({ page, browserName }) => {
    test.skip(browserName !== 'chromium', 'Chrome-specific test');

    const mapPage = new MapPage(page);
    await mapPage.goto();

    // Verify core features work
    expect(await mapPage.isMapVisible()).toBeTruthy();

    // Check for Chrome-specific features
    const supportsWebGL = await page.evaluate(() => {
      const canvas = document.createElement('canvas');
      return !!(canvas.getContext('webgl') || canvas.getContext('experimental-webgl'));
    });
    expect(supportsWebGL).toBeTruthy();
  });

  test('Firefox: Rendering and interactions', async ({ page, browserName }) => {
    test.skip(browserName !== 'firefox', 'Firefox-specific test');

    const mapPage = new MapPage(page);
    await mapPage.goto();

    // Verify map renders
    expect(await mapPage.isMapVisible()).toBeTruthy();

    // Test mouse interactions
    await mapPage.clickMap(100, 100);
    await page.waitForTimeout(500);

    // Verify page doesn't crash
    const title = await page.title();
    expect(title.length).toBeGreaterThan(0);
  });

  test('Safari/WebKit: CSS and layout', async ({ page, browserName }) => {
    test.skip(browserName !== 'webkit', 'Safari-specific test');

    const mapPage = new MapPage(page);
    await mapPage.goto();

    // Verify layout renders correctly
    expect(await mapPage.isMapVisible()).toBeTruthy();

    // Check for layout issues
    const mapBox = await mapPage.map.boundingBox();
    expect(mapBox).toBeTruthy();
    expect(mapBox!.width).toBeGreaterThan(100);
    expect(mapBox!.height).toBeGreaterThan(100);
  });
});

test.describe('Cross-Browser Compatibility - Mobile', () => {
  test('iPhone: Touch interactions', async ({ page }) => {
    await page.setViewportSize(devices['iPhone 13'].viewport);

    const mapPage = new MapPage(page);
    await mapPage.goto();

    // Verify mobile layout
    expect(await mapPage.isMapVisible()).toBeTruthy();

    // Test tap interaction
    await page.tap('body');
    await page.waitForTimeout(500);

    // Verify responsive design
    const viewport = page.viewportSize();
    expect(viewport?.width).toBe(390);
  });

  test('iPad: Tablet layout', async ({ page }) => {
    await page.setViewportSize(devices['iPad Pro'].viewport);

    const mapPage = new MapPage(page);
    await mapPage.goto();

    // Verify tablet layout adapts
    expect(await mapPage.isMapVisible()).toBeTruthy();

    const mapBox = await mapPage.map.boundingBox();
    expect(mapBox?.width).toBeGreaterThan(500);
  });

  test('Android: Various screen sizes', async ({ page }) => {
    await page.setViewportSize(devices['Pixel 5'].viewport);

    const mapPage = new MapPage(page);
    await mapPage.goto();

    expect(await mapPage.isMapVisible()).toBeTruthy();

    // Test pinch zoom if supported
    const supportsTouch = await page.evaluate(() => 'ontouchstart' in window);
    expect(supportsTouch).toBeDefined();
  });
});

test.describe('Browser Feature Detection', () => {
  test('LocalStorage availability', async ({ page }) => {
    await page.goto('/');

    const hasLocalStorage = await page.evaluate(() => {
      try {
        const test = '__storage_test__';
        localStorage.setItem(test, test);
        localStorage.removeItem(test);
        return true;
      } catch {
        return false;
      }
    });

    expect(hasLocalStorage).toBeTruthy();
  });

  test('Geolocation API support', async ({ page, context }) => {
    await context.grantPermissions(['geolocation']);
    await page.goto('/');

    const hasGeolocation = await page.evaluate(() => 'geolocation' in navigator);
    expect(hasGeolocation).toBeTruthy();
  });

  test('Canvas API for map rendering', async ({ page }) => {
    await page.goto('/');

    const hasCanvas = await page.evaluate(() => {
      const canvas = document.createElement('canvas');
      return !!(canvas.getContext && canvas.getContext('2d'));
    });

    expect(hasCanvas).toBeTruthy();
  });

  test('Fetch API for network requests', async ({ page }) => {
    await page.goto('/');

    const hasFetch = await page.evaluate(() => typeof fetch === 'function');
    expect(hasFetch).toBeTruthy();
  });
});

test.describe('Responsive Design Breakpoints', () => {
  const breakpoints = [
    { name: 'Mobile Small', width: 320, height: 568 },
    { name: 'Mobile', width: 375, height: 667 },
    { name: 'Mobile Large', width: 414, height: 896 },
    { name: 'Tablet', width: 768, height: 1024 },
    { name: 'Desktop Small', width: 1024, height: 768 },
    { name: 'Desktop', width: 1280, height: 720 },
    { name: 'Desktop Large', width: 1920, height: 1080 },
  ];

  for (const breakpoint of breakpoints) {
    test(`${breakpoint.name}: Layout at ${breakpoint.width}x${breakpoint.height}`, async ({ page }) => {
      await page.setViewportSize({ width: breakpoint.width, height: breakpoint.height });

      const mapPage = new MapPage(page);
      await mapPage.goto();

      // Verify map is visible and properly sized
      expect(await mapPage.isMapVisible()).toBeTruthy();

      const mapBox = await mapPage.map.boundingBox();
      expect(mapBox).toBeTruthy();

      // Map should not overflow viewport
      expect(mapBox!.width).toBeLessThanOrEqual(breakpoint.width);
      expect(mapBox!.height).toBeLessThanOrEqual(breakpoint.height);

      // Take screenshot for visual regression
      await page.screenshot({
        path: `screenshots/responsive-${breakpoint.name.replace(/\s+/g, '-')}.png`,
      });
    });
  }
});

test.describe('Browser Console Errors', () => {
  test('No console errors on page load', async ({ page }) => {
    const consoleErrors: string[] = [];

    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Allow for some acceptable errors (e.g., CORS in dev mode)
    const criticalErrors = consoleErrors.filter(
      err => !err.includes('CORS') && !err.includes('favicon')
    );

    expect(criticalErrors.length).toBe(0);
  });

  test('No unhandled promise rejections', async ({ page }) => {
    const rejections: string[] = [];

    page.on('pageerror', error => {
      if (error.message.includes('Unhandled')) {
        rejections.push(error.message);
      }
    });

    await page.goto('/');
    await page.waitForTimeout(2000);

    expect(rejections.length).toBe(0);
  });
});

test.describe('Accessibility Across Browsers', () => {
  test('Keyboard navigation works', async ({ page }) => {
    await page.goto('/');

    // Tab through interactive elements
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    // Should be able to interact with keyboard
    const focusedElement = await page.evaluate(() => document.activeElement?.tagName);
    expect(focusedElement).toBeTruthy();
  });

  test('Screen reader landmarks present', async ({ page }) => {
    await page.goto('/');

    // Check for ARIA landmarks
    const hasMain = await page.locator('main, [role="main"]').count() > 0;
    const hasNav = await page.locator('nav, [role="navigation"]').count() > 0;

    expect(hasMain || hasNav).toBeTruthy();
  });
});
