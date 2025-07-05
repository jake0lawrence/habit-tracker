import { test, expect } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://127.0.0.1:5000';

test('log habit end-to-end', async ({ page }) => {
  await page.goto(BASE_URL);

  // Open modal for the Meditation habit (key = med)
  await page.getByTestId('log-med').first().click();

  // Fill duration and save
  await page.locator('input[name="duration"]').fill('7');
  await page.getByRole('button', { name: 'Save' }).click();

  // Grid should now show the new entry
  await expect(page.getByText('✅ 7 min')).toBeVisible();

  // Toast should briefly appear
  const toast = page.locator('.toast');
  await expect(toast).toContainText('Saved');
  await expect(toast).toHaveClass(/show/);
});
