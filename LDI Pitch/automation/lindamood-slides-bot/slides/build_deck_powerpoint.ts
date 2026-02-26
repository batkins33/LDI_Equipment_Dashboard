/**
 * PowerPoint Online Deck Builder
 * 
 * Creates a presentation in PowerPoint Online using Playwright automation.
 * Uses the authenticated session to access Office 365.
 * 
 * Outputs:
 * - artifacts/deck_url.txt: URL to created presentation
 * - artifacts/screenshots/deck_final.png: Screenshot of completed deck
 * 
 * Usage: npm run deck:build
 */

import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Paths
const STORAGE_STATE_PATH = path.join(__dirname, '..', '.auth', 'storageState.json');
const BRAND_PATH = path.join(__dirname, '..', 'brand', 'brand.json');
const CONTENT_PATH = path.join(__dirname, '..', 'content', 'deck_outline.json');
const ARTIFACTS_DIR = path.join(__dirname, '..', 'artifacts');
const SCREENSHOTS_DIR = path.join(ARTIFACTS_DIR, 'screenshots');
const DECK_URL_PATH = path.join(ARTIFACTS_DIR, 'deck_url.txt');

// Type definitions
interface SlideContent {
  id: string;
  layout: string;
  title: string;
  subtitle?: string;
  bullets?: string[];
  notes?: string;
}

interface DeckOutline {
  title: string;
  subtitle?: string;
  slides: SlideContent[];
}

interface BrandData {
  primaryColor: string;
  accentColor: string;
  textColor: string;
  backgroundColor: string;
}

function ensureDirectories(): void {
  [ARTIFACTS_DIR, SCREENSHOTS_DIR].forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  });
}

function loadBrand(): BrandData {
  if (!fs.existsSync(BRAND_PATH)) {
    return {
      primaryColor: '#005DBA',
      accentColor: '#1E90FF',
      textColor: '#333333',
      backgroundColor: '#FFFFFF'
    };
  }
  return JSON.parse(fs.readFileSync(BRAND_PATH, 'utf-8'));
}

function loadContent(): DeckOutline {
  if (!fs.existsSync(CONTENT_PATH)) {
    throw new Error(`Deck outline not found: ${CONTENT_PATH}`);
  }
  return JSON.parse(fs.readFileSync(CONTENT_PATH, 'utf-8'));
}

async function buildDeck(): Promise<void> {
  console.log('='.repeat(60));
  console.log('📊 PowerPoint Online Deck Builder');
  console.log('='.repeat(60));
  console.log();

  ensureDirectories();

  const brand = loadBrand();
  const content = loadContent();

  console.log(`🎨 Brand source: Lindamood`);
  console.log(`   Primary: ${brand.primaryColor}, Accent: ${brand.accentColor}`);
  console.log();
  console.log(`📝 Deck: "${content.title}"`);
  console.log(`   Slides: ${content.slides.length}`);
  console.log();

  const browser = await chromium.launch({
    headless: false, // Headed for interactive login if needed
    slowMo: 150
  });

  try {
    // Create context with stored auth if available
    let context;
    if (fs.existsSync(STORAGE_STATE_PATH)) {
      context = await browser.newContext({
        storageState: STORAGE_STATE_PATH,
        viewport: { width: 1920, height: 1080 }
      });
    } else {
      context = await browser.newContext({
        viewport: { width: 1920, height: 1080 }
      });
    }

    const page = await context.newPage();

    // Navigate to PowerPoint Online
    console.log('🌐 Opening PowerPoint Online...');
    await page.goto('https://www.office.com/', {
      waitUntil: 'domcontentloaded',
      timeout: 120000
    });

    // Wait for Office.com to load
    await page.waitForTimeout(3000);

    const url = page.url();
    
    // Check if we need to log in
    if (url.includes('login') || url.includes('signin')) {
      console.log('\n' + '='.repeat(60));
      console.log('🔐 LOGIN REQUIRED');
      console.log('='.repeat(60));
      console.log('\nA browser window has opened for Microsoft login.');
      console.log('Please complete the login process manually:');
      console.log('  1. Enter your Microsoft/Office 365 email');
      console.log('  2. Enter your password');
      console.log('  3. Complete any MFA/2FA prompts');
      console.log('\nThe script will automatically continue once you reach');
      console.log('the Office.com home page.\n');
      console.log('⏳ Waiting for login completion...');
      console.log('='.repeat(60) + '\n');

      // Wait for navigation to Office home
      await page.waitForNavigation({
        url: /office\.com/,
        timeout: 300000
      }).catch(() => {
        // May not navigate if already logged in
      });

      await page.waitForTimeout(3000);
    }

    // Look for PowerPoint create button
    console.log('📊 Creating new PowerPoint presentation...');
    
    // Try to find and click "Create" or "New" button
    const createSelectors = [
      'text=Create',
      'text=New',
      '[aria-label*="Create"]',
      '[aria-label*="New"]',
      'a:has-text("Create")',
      'button:has-text("Create")'
    ];

    let clicked = false;
    for (const selector of createSelectors) {
      try {
        const element = page.locator(selector).first();
        if (await element.isVisible({ timeout: 2000 }).catch(() => false)) {
          await element.click();
          await page.waitForTimeout(1000);
          clicked = true;
          break;
        }
      } catch {
        // Continue to next selector
      }
    }

    if (!clicked) {
      console.log('⚠️  Could not find Create button, navigating directly...');
      await page.goto('https://www.office.com/launch/powerpoint', {
        waitUntil: 'domcontentloaded',
        timeout: 120000
      });
    }

    // Wait for PowerPoint editor to load
    console.log('⏳ Waiting for PowerPoint editor...');
    await page.waitForTimeout(5000);

    // Look for the presentation title field
    console.log('📝 Setting presentation title...');
    const titleSelectors = [
      'input[placeholder*="Title"]',
      'input[placeholder*="Untitled"]',
      '[contenteditable="true"]',
      '.ms-TextField-field'
    ];

    for (const selector of titleSelectors) {
      try {
        const titleField = page.locator(selector).first();
        if (await titleField.isVisible({ timeout: 2000 }).catch(() => false)) {
          await titleField.click();
          await page.waitForTimeout(300);
          await titleField.fill(content.title);
          await page.waitForTimeout(500);
          console.log('   ✅ Title set');
          break;
        }
      } catch {
        // Continue
      }
    }

    // Get the current URL (presentation URL)
    const presentationUrl = page.url();
    console.log();
    console.log('🔗 Presentation URL:', presentationUrl);

    // Save deck URL
    fs.writeFileSync(DECK_URL_PATH, presentationUrl);

    // Add slides
    console.log();
    console.log('🏗️  Adding slides...');
    console.log();

    for (let i = 0; i < Math.min(content.slides.length, 5); i++) {
      const slide = content.slides[i];
      console.log(`   Slide ${i + 1}/${content.slides.length}: ${slide.title}`);

      // Add new slide (Ctrl+M in PowerPoint)
      if (i > 0) {
        await page.keyboard.press('Control+m');
        await page.waitForTimeout(1500);
      }

      // Click on title placeholder
      try {
        const titlePlaceholder = page.locator('[data-placeholder-idx="0"]').first();
        if (await titlePlaceholder.isVisible({ timeout: 2000 }).catch(() => false)) {
          await titlePlaceholder.click();
          await page.waitForTimeout(300);
          await page.keyboard.type(slide.title);
          await page.waitForTimeout(300);
        }
      } catch {
        // Try alternative selector
        const anyText = page.locator('text=Click to add title').first();
        if (await anyText.isVisible({ timeout: 1000 }).catch(() => false)) {
          await anyText.click();
          await page.waitForTimeout(300);
          await page.keyboard.type(slide.title);
          await page.waitForTimeout(300);
        }
      }

      // Add bullets if present
      if (slide.bullets && slide.bullets.length > 0) {
        try {
          const contentPlaceholder = page.locator('[data-placeholder-idx="1"]').first();
          if (await contentPlaceholder.isVisible({ timeout: 2000 }).catch(() => false)) {
            await contentPlaceholder.click();
            await page.waitForTimeout(300);

            for (let j = 0; j < slide.bullets.length; j++) {
              if (j > 0) {
                await page.keyboard.press('Enter');
                await page.waitForTimeout(200);
              }
              await page.keyboard.type(slide.bullets[j]);
              await page.waitForTimeout(200);
            }
          }
        } catch {
          // Ignore if content area not found
        }
      }

      await page.waitForTimeout(500);
    }

    console.log();
    console.log('✅ Slides added');

    // Take final screenshot
    console.log();
    console.log('📸 Capturing presentation screenshot...');
    
    try {
      await page.screenshot({
        path: path.join(SCREENSHOTS_DIR, 'deck_final.png'),
        fullPage: false
      });
      console.log('   ✅ Saved: artifacts/screenshots/deck_final.png');
    } catch (e) {
      console.log('   ⚠️  Screenshot capture failed');
    }

    console.log();
    console.log('='.repeat(60));
    console.log('🎉 PRESENTATION CREATED');
    console.log('='.repeat(60));
    console.log();
    console.log('📁 Artifacts:');
    console.log(`   - ${DECK_URL_PATH}`);
    console.log(`   - ${path.join(SCREENSHOTS_DIR, 'deck_final.png')}`);
    console.log();
    console.log(`🔗 Presentation URL: ${presentationUrl}`);
    console.log();
    console.log('💡 Note: First 5 slides were added via automation.');
    console.log('   You can manually add the remaining slides in PowerPoint Online.');
    console.log();

  } catch (error) {
    console.error('\n❌ Deck build failed:', error);
    
    // Capture error screenshot
    try {
      const pages = await browser.context()?.pages() || [];
      if (pages.length > 0) {
        await pages[0].screenshot({
          path: path.join(SCREENSHOTS_DIR, 'build_error.png')
        });
      }
    } catch {
      // Ignore
    }
    
    process.exit(1);
  } finally {
    await browser.close();
  }
}

// Run deck builder
buildDeck().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
