/**
 * Google Authentication Script
 * 
 * Performs one-time interactive Google login and persists
 * the browser session to .auth/storageState.json for reuse.
 * 
 * Usage: npm run auth
 */

import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import readline from 'readline';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const AUTH_DIR = path.join(__dirname, '..', '.auth');
const STORAGE_STATE_PATH = path.join(AUTH_DIR, 'storageState.json');

/**
 * Prompt user for confirmation
 */
function prompt(question: string): Promise<string> {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
  
  return new Promise(resolve => {
    rl.question(question, answer => {
      rl.close();
      resolve(answer);
    });
  });
}

/**
 * Ensure auth directory exists
 */
function ensureAuthDir(): void {
  if (!fs.existsSync(AUTH_DIR)) {
    fs.mkdirSync(AUTH_DIR, { recursive: true });
    console.log('📁 Created .auth/ directory');
  }
}

/**
 * Main authentication flow
 */
async function authenticate(): Promise<void> {
  console.log('='.repeat(60));
  console.log('🔐 Google Authentication for Lindamood Slides Bot');
  console.log('='.repeat(60));
  console.log();
  console.log('This script will:');
  console.log('  1. Open a headed Chrome browser');
  console.log('  2. Navigate to Google Drive');
  console.log('  3. Wait for you to complete login (including MFA)');
  console.log('  4. Save your session for reuse');
  console.log();
  console.log('⚠️  Keep the .auth/ directory gitignored - it contains');
  console.log('    your session credentials!');
  console.log();

  // Check if already authenticated
  if (fs.existsSync(STORAGE_STATE_PATH)) {
    console.log('⚠️  Existing authentication found at .auth/storageState.json');
    const answer = await prompt('   Overwrite? (y/N): ');
    if (answer.toLowerCase() !== 'y') {
      console.log('   Authentication cancelled. Using existing credentials.');
      process.exit(0);
    }
  }

  ensureAuthDir();

  console.log('🚀 Launching browser...\n');

  const browser = await chromium.launch({
    headless: false, // Must be headed for interactive login
    slowMo: 100
  });

  try {
    const context = await browser.newContext({
      viewport: { width: 1280, height: 800 }
    });

    const page = await context.newPage();

    // Navigate to Google Drive (will redirect to login if not authenticated)
    console.log('🌐 Opening Google Drive...');
    await page.goto('https://drive.google.com', {
      waitUntil: 'domcontentloaded',
      timeout: 60000
    });

    console.log();
    console.log('='.repeat(60));
    console.log('👉 ACTION REQUIRED:');
    console.log('='.repeat(60));
    console.log();
    console.log('Please complete the Google login in the opened browser.');
    console.log('This includes any MFA prompts (2FA, security keys, etc.)');
    console.log();
    console.log('The script will automatically detect when you reach Google Drive');
    console.log('and save your session.');
    console.log();
    console.log('⚠️  Do not close the browser window!');
    console.log();

    // Wait for successful login detection
    const maxWaitMs = 5 * 60 * 1000; // 5 minutes max
    const checkIntervalMs = 2000;
    let elapsedMs = 0;
    let loggedIn = false;

    while (elapsedMs < maxWaitMs) {
      await page.waitForTimeout(checkIntervalMs);
      elapsedMs += checkIntervalMs;

      // Check if we're on Drive (successful login indicator)
      const url = page.url();
      const title = await page.title().catch(() => '');
      
      // Multiple indicators of successful login
      const onDrive = url.includes('drive.google.com') && !url.includes('accounts.google.com');
      const hasDriveContent = await page.locator('[data-target="drive"], [aria-label*="Drive"], .a-b-f-i').first().isVisible().catch(() => false);
      const titleIndicatesDrive = title.toLowerCase().includes('drive') || title.toLowerCase().includes('my drive');

      if ((onDrive && (hasDriveContent || titleIndicatesDrive)) || titleIndicatesDrive) {
        loggedIn = true;
        console.log();
        console.log('✅ Google Drive detected - Login successful!');
        break;
      }

      // Progress indicator every 30 seconds
      if (elapsedMs % 30000 === 0) {
        const remaining = Math.ceil((maxWaitMs - elapsedMs) / 1000);
        console.log(`   ⏳ Waiting... ${remaining}s remaining`);
      }
    }

    if (!loggedIn) {
      console.log();
      console.log('❌ Timeout: Did not detect successful login within 5 minutes');
      console.log('   If you completed login, please try running the script again.');
      process.exit(1);
    }

    // Save storage state
    console.log();
    console.log('💾 Saving authentication state...');
    await context.storageState({ path: STORAGE_STATE_PATH });
    
    console.log('✅ Authentication saved to .auth/storageState.json');
    console.log();
    console.log('='.repeat(60));
    console.log('🎉 AUTHENTICATION COMPLETE');
    console.log('='.repeat(60));
    console.log();
    console.log('You can now run:');
    console.log('  npm run brand:extract  - Extract Lindamood branding');
    console.log('  npm run deck:build     - Build Google Slides deck');
    console.log('  npm test               - Run E2E tests');
    console.log();
    console.log('Your session will be reused until it expires or you');
    console.log('run npm run auth again.');
    console.log();

  } catch (error) {
    console.error('\n❌ Authentication failed:', error);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

// Run authentication
authenticate().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
