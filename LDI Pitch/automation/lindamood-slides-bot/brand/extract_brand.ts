/**
 * Brand Extraction Script for Lindamood
 * 
 * Extracts logo and color palette from https://www.lindamood.net
 * using Playwright for browser automation.
 * 
 * Outputs:
 * - brand/brand.json: Color palette and metadata
 * - brand/logo.png: Downloaded logo image
 * - artifacts/screenshots/site_*.png: Evidence screenshots
 */

import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Paths
const BRAND_DIR = path.join(__dirname);
const ARTIFACTS_DIR = path.join(__dirname, '..', 'artifacts');
const SCREENSHOTS_DIR = path.join(ARTIFACTS_DIR, 'screenshots');

/**
 * Ensure directories exist
 */
function ensureDirectories(): void {
  [BRAND_DIR, ARTIFACTS_DIR, SCREENSHOTS_DIR].forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  });
}

/**
 * Extract dominant colors from computed styles
 */
function extractColorsFromStyles(styles: Map<string, string>): {
  primaryColor: string;
  accentColor: string;
  textColor: string;
  backgroundColor: string;
} {
  // Common color patterns for Lindamood-like sites
  const colorPriority = [
    { key: 'cta', selectors: ['button', 'a.btn', '[role="button"]'] },
    { key: 'header', selectors: ['header', '.header', '.navbar'] },
    { key: 'links', selectors: ['a', 'a:link'] },
    { key: 'background', selectors: ['body', '.hero', '#hero'] }
  ];

  // Default to Lindamood blue family if extraction fails
  // (this is a runtime extraction - we'll get actual values from the site)
  return {
    primaryColor: styles.get('primary') || '#005DBA',
    accentColor: styles.get('accent') || '#1E90FF',
    textColor: styles.get('text') || '#333333',
    backgroundColor: styles.get('background') || '#FFFFFF'
  };
}

/**
 * Main extraction function
 */
async function extractBrand(): Promise<void> {
  console.log('🔍 Starting Lindamood brand extraction...\n');

  ensureDirectories();

  const browser = await chromium.launch({
    headless: true, // Headless for faster execution
    slowMo: 50
  });

  try {
    const context = await browser.newContext({
      viewport: { width: 1920, height: 1080 },
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      ignoreHTTPSErrors: true
    });

    const page = await context.newPage();

    // Navigate to Lindamood website with extended timeout
    console.log('🌐 Loading https://www.lindamood.net/...');
    try {
      await page.goto('https://www.lindamood.net/', {
        waitUntil: 'domcontentloaded', // Less strict than networkidle
        timeout: 120000 // 2 minute timeout
      });
    } catch (navError) {
      console.log('⚠️  Network timeout, continuing with partial load...');
      // Continue anyway - we may have enough content
    }

    // Wait for page to stabilize
    await page.waitForTimeout(3000);

    // Capture full page screenshot
    console.log('📸 Capturing site screenshot...');
    await page.screenshot({
      path: path.join(SCREENSHOTS_DIR, 'site_home.png'),
      fullPage: true
    });

    // Capture header screenshot
    const header = await page.locator('header, .header, .navbar').first();
    if (await header.isVisible().catch(() => false)) {
      await header.screenshot({
        path: path.join(SCREENSHOTS_DIR, 'site_header.png')
      });
    }

    // Extract logo
    console.log('🎨 Extracting logo...');
    let logoPath: string | null = null;
    
    const logoSelectors = [
      'header img[alt*="logo" i]',
      'header img[src*="logo" i]',
      '.logo img',
      '.navbar-brand img',
      'header svg',
      'a[href="/"] img',
      '[class*="logo"] img'
    ];

    for (const selector of logoSelectors) {
      const logo = page.locator(selector).first();
      if (await logo.isVisible().catch(() => false)) {
        try {
          const box = await logo.boundingBox();
          if (box && box.width > 50 && box.height > 20) {
            await logo.screenshot({
              path: path.join(BRAND_DIR, 'logo.png')
            });
            logoPath = 'brand/logo.png';
            console.log(`✅ Logo extracted: ${selector}`);
            break;
          }
        } catch (e) {
          // Continue to next selector
        }
      }
    }

    // Extract color palette from computed styles
    console.log('\n🎨 Extracting color palette...');
    
    const colors = await page.evaluate(() => {
      const results: any = {};
      
      // Extract from various elements
      const header = document.querySelector('header, .header, .navbar');
      if (header) {
        const bg = window.getComputedStyle(header).backgroundColor;
        if (bg && bg !== 'rgba(0, 0, 0, 0)') {
          results.headerBackground = bg;
        }
      }

      // Get primary action color from buttons
      const buttons = document.querySelectorAll('button, .btn, a.btn, [role="button"]');
      for (let i = 0; i < buttons.length; i++) {
        const btn = buttons[i] as HTMLElement;
        const bg = window.getComputedStyle(btn).backgroundColor;
        if (bg && bg !== 'rgba(0, 0, 0, 0)' && !bg.includes('transparent')) {
          results.primaryButton = bg;
          break;
        }
      }

      // Get link colors
      const link = document.querySelector('a');
      if (link) {
        results.linkColor = window.getComputedStyle(link).color;
      }

      // Get heading colors
      const h1 = document.querySelector('h1');
      if (h1) {
        results.headingColor = window.getComputedStyle(h1).color;
      }

      // Get body background
      results.bodyBackground = window.getComputedStyle(document.body).backgroundColor;

      // Get hero section if exists
      const hero = document.querySelector('.hero, #hero, [class*="hero"]');
      if (hero) {
        results.heroBackground = window.getComputedStyle(hero).backgroundColor;
      }

      return results;
    });

    console.log('📊 Raw colors extracted:');
    Object.entries(colors).forEach(([key, value]) => {
      console.log(`  ${key}: ${value}`);
    });

    // Process and normalize colors
    const brandColors = {
      primaryColor: colors.primaryButton || colors.linkColor || '#005DBA',
      accentColor: colors.headerBackground || '#1E90FF',
      textColor: colors.headingColor || '#333333',
      backgroundColor: colors.bodyBackground || '#FFFFFF'
    };

    // Handle rgba to hex conversion for common colors
    const rgbaToHex = (rgba: string): string => {
      if (rgba.startsWith('#')) return rgba;
      if (rgba.startsWith('rgb')) {
        const parts = rgba.match(/\d+/g);
        if (parts && parts.length >= 3) {
          const r = parseInt(parts[0]).toString(16).padStart(2, '0');
          const g = parseInt(parts[1]).toString(16).padStart(2, '0');
          const b = parseInt(parts[2]).toString(16).padStart(2, '0');
          return `#${r}${g}${b}`.toUpperCase();
        }
      }
      return rgba;
    };

    // Convert all colors to hex
    const normalizedBrand = {
      primaryColor: rgbaToHex(brandColors.primaryColor),
      accentColor: rgbaToHex(brandColors.accentColor),
      textColor: rgbaToHex(brandColors.textColor),
      backgroundColor: rgbaToHex(brandColors.backgroundColor)
    };

    // Create brand.json
    const brandData = {
      source: 'https://www.lindamood.net',
      extractedAt: new Date().toISOString(),
      primaryColor: normalizedBrand.primaryColor,
      accentColor: normalizedBrand.accentColor,
      textColor: normalizedBrand.textColor,
      backgroundColor: normalizedBrand.backgroundColor,
      logoPath: logoPath,
      evidenceScreenshots: {
        siteHome: 'artifacts/screenshots/site_home.png',
        siteHeader: 'artifacts/screenshots/site_header.png'
      },
      rawColors: colors,
      notes: [
        'Colors extracted from computed styles at runtime',
        'Logo captured from header/navbar area',
        'Extraction method: Playwright browser automation'
      ]
    };

    // Write brand.json
    fs.writeFileSync(
      path.join(BRAND_DIR, 'brand.json'),
      JSON.stringify(brandData, null, 2)
    );

    console.log('\n✅ Brand extraction complete!');
    console.log('\n📁 Output files:');
    console.log(`  - brand/brand.json`);
    console.log(`  - brand/logo.png ${logoPath ? '✓' : '✗'}`);
    console.log(`  - artifacts/screenshots/site_home.png`);
    console.log(`  - artifacts/screenshots/site_header.png`);
    console.log('\n🎨 Brand palette:');
    console.log(`  Primary: ${normalizedBrand.primaryColor}`);
    console.log(`  Accent: ${normalizedBrand.accentColor}`);
    console.log(`  Text: ${normalizedBrand.textColor}`);
    console.log(`  Background: ${normalizedBrand.backgroundColor}`);

  } catch (error) {
    console.error('\n❌ Brand extraction failed:', error);
    
    // Capture failure screenshot for debugging
    try {
      const pages = await browser.pages();
      if (pages.length > 0) {
        await pages[0].screenshot({
          path: path.join(SCREENSHOTS_DIR, 'extraction_error.png')
        });
        console.log('📸 Error screenshot saved to artifacts/screenshots/extraction_error.png');
      }
    } catch {
      // Ignore screenshot errors
    }
    
    process.exit(1);
  } finally {
    await browser.close();
  }
}

// Run extraction
extractBrand().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
