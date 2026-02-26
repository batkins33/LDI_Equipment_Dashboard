import { defineConfig, devices } from '@playwright/test';
import path from 'path';

/**
 * Playwright configuration for Lindamood Slides Bot
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './tests',
  fullyParallel: false, // Sequential for stateful automation
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1, // Single worker for stateful browser sessions
  reporter: [
    ['list'],
    ['html', { open: 'never' }],
  ],
  use: {
    baseURL: 'https://www.lindamood.net',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    // Storage state for authenticated Google sessions
    storageState: process.env.SKIP_AUTH ? undefined : path.join(__dirname, '.auth', 'storageState.json'),
    // Default browser settings
    headless: false, // Headed by default for interactive workflows
    viewport: { width: 1920, height: 1080 },
    actionTimeout: 30000,
    navigationTimeout: 60000,
    launchOptions: {
      slowMo: 100, // Small delay for stability
    },
  },

  projects: [
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        channel: 'chromium',
      },
    },
  ],

  // Global timeout for the entire test suite
  globalTimeout: 10 * 60 * 1000, // 10 minutes
  
  // Timeout per test
  timeout: 5 * 60 * 1000, // 5 minutes per test
});
