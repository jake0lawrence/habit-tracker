import { test, expect } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://127.0.0.1:5000';

test('log habit end-to-end', async ({ page }) => {
  // Login first so routes requiring authentication succeed
  await page.goto(`${BASE_URL}/login`);
  await page.locator('input[name="username"]').fill('playwright');
  await page.getByRole('button', { name: 'Login' }).click();

  await page.goto(BASE_URL);

  // Open modal for the Meditation habit (key = med)
  await page.getByTestId('log-med').first().click();

  // Fill duration and save
  await page.locator('input[name="duration"]').fill('7');
  await page.getByRole('button', { name: 'Save' }).click();

  // Grid should now show the new entry
  await expect(page.getByText('✅ 7 min')).toBeVisible();
});
