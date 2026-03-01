import { test, expect } from '@playwright/test';

test('loads app shell', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: /Unified Ops Dashboard/i })).toBeVisible();
  await expect(page.getByText(/Backend health/i)).toBeVisible();
});
