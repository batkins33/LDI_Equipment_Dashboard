/**
 * Google Slides Deck Builder
 * 
 * Creates a Google Slides presentation titled "Lindamood Automation Opportunity"
 * using branding from brand/brand.json and content from content/deck_outline.json.
 * 
 * Outputs:
 * - artifacts/deck_url.txt: URL to created deck
 * - artifacts/screenshots/deck_final.png: Screenshot of completed deck
 * - artifacts/lindamood_opportunity_deck.pdf: PDF export (via Google Slides)
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
const PDF_PATH = path.join(ARTIFACTS_DIR, 'lindamood_opportunity_deck.pdf');

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
  logoPath?: string;
  source: string;
  extractedAt: string;
}

/**
 * Ensure directories exist
 */
function ensureDirectories(): void {
  [ARTIFACTS_DIR, SCREENSHOTS_DIR].forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  });
}

/**
 * Load brand data
 */
function loadBrand(): BrandData {
  if (!fs.existsSync(BRAND_PATH)) {
    console.warn('⚠️  brand.json not found, using default branding');
    return {
      primaryColor: '#005DBA',
      accentColor: '#1E90FF',
      textColor: '#333333',
      backgroundColor: '#FFFFFF',
      source: 'default',
      extractedAt: new Date().toISOString()
    };
  }
  return JSON.parse(fs.readFileSync(BRAND_PATH, 'utf-8'));
}

/**
 * Load deck outline
 */
function loadContent(): DeckOutline {
  if (!fs.existsSync(CONTENT_PATH)) {
    throw new Error(`Deck outline not found: ${CONTENT_PATH}`);
  }
  return JSON.parse(fs.readFileSync(CONTENT_PATH, 'utf-8'));
}

/**
 * Verify authentication exists
 */
function verifyAuth(): void {
  if (!fs.existsSync(STORAGE_STATE_PATH)) {
    console.error('❌ Authentication required!');
    console.error('   Run: npm run auth');
    console.error('   This will save your Google session to .auth/storageState.json');
    process.exit(1);
  }
}

/**
 * Main deck building function
 */
async function buildDeck(): Promise<void> {
  console.log('='.repeat(60));
  console.log('📊 Lindamood Slides Deck Builder');
  console.log('='.repeat(60));
  console.log();

  // Verify prerequisites
  verifyAuth();
  ensureDirectories();

  const brand = loadBrand();
  const content = loadContent();

  console.log(`🎨 Brand source: ${brand.source}`);
  console.log(`   Primary: ${brand.primaryColor}, Accent: ${brand.accentColor}`);
  console.log();
  console.log(`📝 Deck: "${content.title}"`);
  console.log(`   Slides: ${content.slides.length}`);
  console.log();

  const browser = await chromium.launch({
    headless: false, // Headed so you can see and interact with login
    slowMo: 150
  });

  try {
    // Load authenticated context
    const context = await browser.newContext({
      storageState: STORAGE_STATE_PATH,
      viewport: { width: 1920, height: 1080 },
      acceptDownloads: true // Enable PDF downloads
    });

    const page = await context.newPage();

    // Configure download behavior for PDF export
    await page.setViewportSize({ width: 1920, height: 1080 });

    // Navigate to Google Slides
    console.log('🌐 Opening Google Slides...');
    await page.goto('https://docs.google.com/presentation/create', {
      waitUntil: 'domcontentloaded',
      timeout: 120000
    });

    // Wait for Google Slides editor to fully load
    console.log('⏳ Waiting for Google Slides editor...');
    
    // Check if we're on the editor page or login page
    let retries = 0;
    const maxRetries = 10;
    
    while (retries < maxRetries) {
      const url = page.url();
      
      // If we're on a login page, wait for manual login
      if (url.includes('accounts.google.com') || url.includes('signin')) {
        console.log('\n' + '='.repeat(60));
        console.log('🔐 LOGIN REQUIRED');
        console.log('='.repeat(60));
        console.log('\nA browser window has opened for Google login.');
        console.log('Please complete the login process manually:');
        console.log('  1. Enter your Google email');
        console.log('  2. Enter your password');
        console.log('  3. Complete any MFA/2FA prompts');
        console.log('\nThe script will automatically continue once you reach');
        console.log('the Google Slides editor.\n');
        console.log('⏳ Waiting for login completion...');
        console.log('='.repeat(60) + '\n');
        
        // Wait for redirect away from login page
        await page.waitForNavigation({ 
          url: /docs\.google\.com\/presentation/,
          timeout: 300000 // 5 minute timeout for manual login
        }).catch(() => {
          // Navigation may not happen if already on right page
        });
        
        // Continue checking
        retries = 0;
        continue;
      }
      
      // Check if we're on the presentation editor
      if (url.includes('docs.google.com/presentation')) {
        // Wait for the editor to be interactive
        try {
          await page.waitForSelector('[role="button"], [aria-label*="slide"]', { timeout: 10000 }).catch(() => null);
          console.log('✅ Editor loaded');
          break;
        } catch {
          retries++;
          if (retries < maxRetries) {
            console.log(`   Retry ${retries}/${maxRetries}...`);
            await page.waitForTimeout(2000);
          }
        }
      } else {
        retries++;
        if (retries < maxRetries) {
          console.log(`   Waiting for editor... (${retries}/${maxRetries})`);
          await page.waitForTimeout(2000);
        }
      }
    }

    if (retries >= maxRetries) {
      console.error('\n❌ Failed to load Google Slides editor');
      console.error('   Current URL:', page.url());
      process.exit(1);
    }

    await page.waitForTimeout(2000);

    // Rename the presentation
    console.log('📝 Setting presentation title...');
    
    // Click on the title field (various possible selectors)
    const titleSelectors = [
      '[aria-label*="Document title"]',
      '[data-tooltip="Rename"]',
      '.docs-title-input',
      'input.docs-title-input',
      '[role="heading"]'
    ];

    let titleClicked = false;
    for (const selector of titleSelectors) {
      try {
        const titleElement = page.locator(selector).first();
        if (await titleElement.isVisible({ timeout: 2000 }).catch(() => false)) {
          await titleElement.click();
          await page.waitForTimeout(500);
          
          // Select all and type new title
          await page.keyboard.press('Control+a');
          await page.waitForTimeout(200);
          await page.keyboard.type(content.title);
          await page.waitForTimeout(500);
          await page.keyboard.press('Enter');
          
          titleClicked = true;
          console.log('   ✅ Title set');
          break;
        }
      } catch {
        // Continue to next selector
      }
    }

    if (!titleClicked) {
      console.log('   ⚠️  Could not set title automatically (will use default)');
    }

    await page.waitForTimeout(2000);

    // Get the current URL (will be used for deck URL)
    const deckUrl = page.url();
    console.log();
    console.log('🔗 Deck URL:', deckUrl);

    // Save deck URL
    fs.writeFileSync(DECK_URL_PATH, deckUrl);

    // Delete the default blank slide if it exists
    try {
      const deleteSlideShortcut = async () => {
        // Focus slide thumbnail panel
        await page.keyboard.press('Tab');
        await page.waitForTimeout(200);
        // Delete the slide
        await page.keyboard.press('Delete');
        await page.waitForTimeout(500);
      };
      await deleteSlideShortcut();
    } catch {
      // Ignore if deletion fails
    }

    // Build slides from outline
    console.log();
    console.log('🏗️  Building slides...');
    console.log();

    for (let i = 0; i < content.slides.length; i++) {
      const slide = content.slides[i];
      if (!slide) continue;
      console.log(`   Slide ${i + 1}/${content.slides.length}: ${slide.title}`);

      // Insert new slide using keyboard shortcut
      // Ctrl+M inserts a new slide in Google Slides
      await page.keyboard.press('Control+m');
      await page.waitForTimeout(1000);

      // Add title
      await addSlideTitle(page, slide.title);

      // Add subtitle if present
      if (slide.subtitle) {
        await addSlideSubtitle(page, slide.subtitle);
      }

      // Add bullets if present
      if (slide.bullets && slide.bullets.length > 0) {
        await addSlideBullets(page, slide.bullets);
      }

      // Add notes if present
      if (slide.notes) {
        await addSlideNotes(page, slide.notes);
      }

      await page.waitForTimeout(500);
    }

    console.log();
    console.log('✅ All slides created');

    // Take final screenshot
    console.log();
    console.log('📸 Capturing deck screenshot...');
    
    // Navigate to first slide
    await page.keyboard.press('Home');
    await page.waitForTimeout(1000);
    
    await page.screenshot({
      path: path.join(SCREENSHOTS_DIR, 'deck_final.png'),
      fullPage: false
    });
    console.log('   Saved: artifacts/screenshots/deck_final.png');

    // Export to PDF
    console.log();
    console.log('📄 Exporting PDF...');
    
    try {
      // Open File menu
      await page.keyboard.press('Alt+f');
      await page.waitForTimeout(500);
      
      // Navigate to Download
      await page.keyboard.press('ArrowDown');
      await page.waitForTimeout(200);
      await page.keyboard.press('ArrowDown');
      await page.waitForTimeout(200);
      await page.keyboard.press('ArrowDown');
      await page.waitForTimeout(200);
      await page.keyboard.press('ArrowRight');
      await page.waitForTimeout(500);
      
      // Select PDF Document
      await page.keyboard.press('ArrowDown');
      await page.waitForTimeout(200);
      await page.keyboard.press('ArrowDown');
      await page.waitForTimeout(200);
      await page.keyboard.press('Enter');
      await page.waitForTimeout(5000); // Wait for download dialog

      // Handle download dialog if present
      const [download] = await Promise.all([
        page.waitForEvent('download', { timeout: 10000 }).catch(() => null),
        page.waitForTimeout(1000)
      ]);

      if (download) {
        await download.saveAs(PDF_PATH);
        console.log('   ✅ PDF downloaded');
      } else {
        console.log('   ⚠️  PDF download may require manual interaction');
        console.log('      Check your browser downloads for the PDF');
      }
    } catch (e) {
      console.log('   ⚠️  PDF export requires manual action:');
      console.log('      File → Download → PDF Document (.pdf)');
    }

    // Update deck URL file with final URL
    const finalUrl = page.url();
    fs.writeFileSync(DECK_URL_PATH, finalUrl);

    console.log();
    console.log('='.repeat(60));
    console.log('🎉 DECK BUILD COMPLETE');
    console.log('='.repeat(60));
    console.log();
    console.log('📁 Artifacts:');
    console.log(`   - ${DECK_URL_PATH}`);
    console.log(`   - ${path.join(SCREENSHOTS_DIR, 'deck_final.png')}`);
    if (fs.existsSync(PDF_PATH)) {
      const stats = fs.statSync(PDF_PATH);
      console.log(`   - ${PDF_PATH} (${Math.round(stats.size / 1024)} KB)`);
    }
    console.log();
    console.log(`🔗 Deck URL: ${finalUrl}`);
    console.log();

  } catch (error) {
    console.error('\n❌ Deck build failed:', error);
    
    // Capture error screenshot
    try {
      const pages = await browser.pages();
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

/**
 * Add title to current slide
 */
async function addSlideTitle(page: any, title: string): Promise<void> {
  // Try to find and fill title text box
  const titleSelectors = [
    '[placeholder*="Click to add title"]',
    '[data-placeholder="Click to add title"]',
    '.p-placeholder-title',
    '[aria-label*="title"]'
  ];

  for (const selector of titleSelectors) {
    try {
      const titleBox = page.locator(selector).first();
      if (await titleBox.isVisible({ timeout: 1000 }).catch(() => false)) {
        await titleBox.click();
        await page.waitForTimeout(300);
        await page.keyboard.type(title);
        await page.waitForTimeout(200);
        return;
      }
    } catch {
      // Continue to next selector
    }
  }

  // Fallback: try Tab navigation to title box
  try {
    await page.keyboard.press('Tab');
    await page.waitForTimeout(200);
    await page.keyboard.type(title);
  } catch {
    // Ignore
  }
}

/**
 * Add subtitle to current slide
 */
async function addSlideSubtitle(page: any, subtitle: string): Promise<void> {
  const subtitleSelectors = [
    '[placeholder*="subtitle"]',
    '[data-placeholder*="subtitle"]',
    '.p-placeholder-subtitle',
    '[aria-label*="subtitle"]'
  ];

  for (const selector of subtitleSelectors) {
    try {
      const subtitleBox = page.locator(selector).first();
      if (await subtitleBox.isVisible({ timeout: 1000 }).catch(() => false)) {
        await subtitleBox.click();
        await page.waitForTimeout(300);
        await page.keyboard.type(subtitle);
        await page.waitForTimeout(200);
        return;
      }
    } catch {
      // Continue
    }
  }
}

/**
 * Add bullets to current slide
 */
async function addSlideBullets(page: any, bullets: string[]): Promise<void> {
  const contentSelectors = [
    '[placeholder*="Click to add text"]',
    '[data-placeholder*="text"]',
    '.p-placeholder-body',
    '[aria-label*="body"]'
  ];

  let contentBox = null;
  
  for (const selector of contentSelectors) {
    try {
      const box = page.locator(selector).first();
      if (await box.isVisible({ timeout: 1000 }).catch(() => false)) {
        contentBox = box;
        break;
      }
    } catch {
      // Continue
    }
  }

  if (!contentBox) {
    // Try Tab to reach content area
    await page.keyboard.press('Tab');
    await page.waitForTimeout(200);
    await page.keyboard.press('Tab');
    await page.waitForTimeout(200);
  } else {
    await contentBox.click();
    await page.waitForTimeout(300);
  }

  // Type each bullet
  for (let i = 0; i < bullets.length; i++) {
    if (i > 0) {
      await page.keyboard.press('Enter');
      await page.waitForTimeout(200);
    }
    await page.keyboard.type(bullets[i]);
    await page.waitForTimeout(200);
  }
}

/**
 * Add notes to current slide
 */
async function addSlideNotes(page: any, notes: string): Promise<void> {
  // Open notes panel with Ctrl+Alt+M
  await page.keyboard.down('Control');
  await page.keyboard.down('Alt');
  await page.keyboard.down('m');
  await page.keyboard.up('m');
  await page.keyboard.up('Alt');
  await page.keyboard.up('Control');
  
  await page.waitForTimeout(1000);

  // Find notes text area
  const notesSelectors = [
    '[aria-label*="speaker notes"]',
    '[data-placeholder*="Click to add speaker notes"]',
    '.p-notes-text'
  ];

  for (const selector of notesSelectors) {
    try {
      const notesBox = page.locator(selector).first();
      if (await notesBox.isVisible({ timeout: 1000 }).catch(() => false)) {
        await notesBox.click();
        await page.waitForTimeout(300);
        await page.keyboard.type(notes);
        await page.waitForTimeout(200);
        
        // Close notes panel
        await page.keyboard.press('Control+Alt+m');
        await page.waitForTimeout(500);
        return;
      }
    } catch {
      // Continue
    }
  }
}

// Run deck builder
buildDeck().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
