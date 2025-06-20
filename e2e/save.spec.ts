import { test, expect } from '@playwright/test';

test('log habit end-to-end', async ({ page }) => {
  await page.goto(process.env.BASE_URL || 'http://localhost:5000');
  await page.getByRole('button', { name: 'Log', exact: true }).click();
  await page.getByLabel('Duration (minutes):').fill('7');
  await page.getByRole('button', { name: 'Save' }).click();
  await expect(page.getByText('✅ 7 min')).toBeVisible();
});
