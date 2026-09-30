import { test, expect } from '@playwright/test';

test.describe('GovCon Intelligence Engine Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the local Vite dev server
    await page.goto('http://localhost:5173');
  });

  test('should load the dashboard and display headers', async ({ page }) => {
    // Check main title
    const mainHeading = page.locator('text=GovCon Intelligence');
    await expect(mainHeading).toBeVisible();

    const subtitle = page.locator('text=Active Federal Opportunities');
    await expect(subtitle).toBeVisible();
  });

  test('should have essential action buttons', async ({ page }) => {
    // We expect Discovery and Validation buttons to exist
    await expect(page.locator('button', { hasText: 'Run Discovery Agent' })).toBeVisible();
    await expect(page.locator('button', { hasText: 'Run AI Validation' })).toBeVisible();
  });

  test('should render the data table headers', async ({ page }) => {
    await expect(page.locator('th', { hasText: 'Company' })).toBeVisible();
    await expect(page.locator('th', { hasText: 'Status' })).toBeVisible();
    await expect(page.locator('th', { hasText: 'Key Executive' })).toBeVisible();
  });
});
