import { test, expect } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://127.0.0.1:5000';

test('navigate between weeks', async ({ page }) => {
  await page.goto(BASE_URL);
  const initial = await page.locator('#habit-grid').getAttribute('data-week-label');
  await page.locator('#week-nav button').first().click();
  await expect(page.locator('#habit-grid')).not.toHaveAttribute('data-week-label', initial);
  await page.locator('#week-nav button').nth(1).click();
  await expect(page.locator('#habit-grid')).toHaveAttribute('data-week-label', initial);
});
