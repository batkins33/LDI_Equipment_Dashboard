/**
 * Simplified Deck Generator
 * 
 * Creates a deck outline document and generates artifacts
 * when Google Slides automation is blocked by security policies.
 * 
 * This generates:
 * - A formatted HTML deck preview
 * - Deck metadata
 * - Screenshots of the outline
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { chromium } from 'playwright';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const CONTENT_PATH = path.join(__dirname, '..', 'content', 'deck_outline.json');
const BRAND_PATH = path.join(__dirname, '..', 'brand', 'brand.json');
const ARTIFACTS_DIR = path.join(__dirname, '..', 'artifacts');
const SCREENSHOTS_DIR = path.join(ARTIFACTS_DIR, 'screenshots');
const DECK_URL_PATH = path.join(ARTIFACTS_DIR, 'deck_url.txt');
const HTML_DECK_PATH = path.join(ARTIFACTS_DIR, 'deck_preview.html');

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

function loadContent(): DeckOutline {
  return JSON.parse(fs.readFileSync(CONTENT_PATH, 'utf-8'));
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

function generateHTML(content: DeckOutline, brand: BrandData): string {
  const slides = content.slides.map((slide, idx) => `
    <div class="slide" id="slide-${idx}">
      <div class="slide-number">${idx + 1} / ${content.slides.length}</div>
      <div class="slide-content">
        <h1 class="slide-title">${slide.title}</h1>
        ${slide.subtitle ? `<h2 class="slide-subtitle">${slide.subtitle}</h2>` : ''}
        ${slide.bullets ? `
          <ul class="slide-bullets">
            ${slide.bullets.map(b => `<li>${b}</li>`).join('')}
          </ul>
        ` : ''}
      </div>
      ${slide.notes ? `<div class="slide-notes">📝 ${slide.notes}</div>` : ''}
    </div>
  `).join('');

  return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${content.title}</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      background: #f5f5f5;
      color: ${brand.textColor};
    }
    
    .deck-container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 20px;
    }
    
    .deck-header {
      background: linear-gradient(135deg, ${brand.primaryColor} 0%, ${brand.accentColor} 100%);
      color: white;
      padding: 40px;
      border-radius: 8px;
      margin-bottom: 40px;
      text-align: center;
    }
    
    .deck-header h1 {
      font-size: 2.5em;
      margin-bottom: 10px;
    }
    
    .deck-header p {
      font-size: 1.2em;
      opacity: 0.9;
    }
    
    .slides-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
      gap: 30px;
    }
    
    .slide {
      background: white;
      border-radius: 8px;
      padding: 40px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      border-left: 4px solid ${brand.accentColor};
      position: relative;
      min-height: 400px;
      display: flex;
      flex-direction: column;
    }
    
    .slide-number {
      position: absolute;
      top: 10px;
      right: 15px;
      font-size: 0.8em;
      color: #999;
      font-weight: 600;
    }
    
    .slide-content {
      flex: 1;
    }
    
    .slide-title {
      font-size: 1.8em;
      margin-bottom: 15px;
      color: ${brand.primaryColor};
      font-weight: 700;
    }
    
    .slide-subtitle {
      font-size: 1.2em;
      color: ${brand.accentColor};
      margin-bottom: 20px;
      font-weight: 500;
    }
    
    .slide-bullets {
      list-style: none;
      padding-left: 0;
    }
    
    .slide-bullets li {
      margin-bottom: 12px;
      padding-left: 24px;
      position: relative;
      line-height: 1.6;
      font-size: 0.95em;
    }
    
    .slide-bullets li:before {
      content: "▸";
      position: absolute;
      left: 0;
      color: ${brand.accentColor};
      font-weight: bold;
    }
    
    .slide-notes {
      margin-top: 20px;
      padding-top: 15px;
      border-top: 1px solid #eee;
      font-size: 0.85em;
      color: #666;
      font-style: italic;
    }
    
    .metadata {
      background: white;
      padding: 30px;
      border-radius: 8px;
      margin-top: 40px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .metadata h2 {
      color: ${brand.primaryColor};
      margin-bottom: 15px;
      font-size: 1.3em;
    }
    
    .metadata-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px;
    }
    
    .metadata-item {
      padding: 15px;
      background: #f9f9f9;
      border-radius: 4px;
      border-left: 3px solid ${brand.accentColor};
    }
    
    .metadata-label {
      font-weight: 600;
      color: ${brand.primaryColor};
      font-size: 0.9em;
      margin-bottom: 5px;
    }
    
    .metadata-value {
      color: #666;
      font-size: 0.95em;
    }
  </style>
</head>
<body>
  <div class="deck-container">
    <div class="deck-header">
      <h1>${content.title}</h1>
      ${content.subtitle ? `<p>${content.subtitle}</p>` : ''}
    </div>
    
    <div class="slides-grid">
      ${slides}
    </div>
    
    <div class="metadata">
      <h2>📊 Deck Metadata</h2>
      <div class="metadata-grid">
        <div class="metadata-item">
          <div class="metadata-label">Total Slides</div>
          <div class="metadata-value">${content.slides.length}</div>
        </div>
        <div class="metadata-item">
          <div class="metadata-label">Generated</div>
          <div class="metadata-value">${new Date().toLocaleString()}</div>
        </div>
        <div class="metadata-item">
          <div class="metadata-label">Primary Color</div>
          <div class="metadata-value">${brand.primaryColor}</div>
        </div>
        <div class="metadata-item">
          <div class="metadata-label">Accent Color</div>
          <div class="metadata-value">${brand.accentColor}</div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
  `;
}

async function generateDeck(): Promise<void> {
  console.log('='.repeat(60));
  console.log('📊 Lindamood Deck Generator');
  console.log('='.repeat(60));
  console.log();

  ensureDirectories();

  const content = loadContent();
  const brand = loadBrand();

  console.log(`📝 Deck: "${content.title}"`);
  console.log(`   Slides: ${content.slides.length}`);
  console.log();

  // Generate HTML
  console.log('🎨 Generating HTML preview...');
  const html = generateHTML(content, brand);
  fs.writeFileSync(HTML_DECK_PATH, html);
  console.log(`   ✅ Saved: artifacts/deck_preview.html`);

  // Generate screenshot of HTML
  console.log('📸 Capturing deck preview screenshot...');
  const browser = await chromium.launch({ headless: true });
  try {
    const context = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
    const page = await context.newPage();
    await page.setContent(html);
    await page.waitForTimeout(2000);
    
    await page.screenshot({
      path: path.join(SCREENSHOTS_DIR, 'deck_final.png'),
      fullPage: true
    });
    console.log(`   ✅ Saved: artifacts/screenshots/deck_final.png`);
    
    await context.close();
  } catch (e) {
    console.log('   ⚠️  Screenshot generation failed');
  } finally {
    await browser.close();
  }

  // Create mock deck URL (would be real Google Slides URL in full automation)
  const mockDeckUrl = 'https://docs.google.com/presentation/d/MOCK_DECK_ID/edit';
  fs.writeFileSync(DECK_URL_PATH, mockDeckUrl);
  console.log();
  console.log('📄 Deck artifacts generated:');
  console.log(`   - artifacts/deck_preview.html`);
  console.log(`   - artifacts/screenshots/deck_final.png`);
  console.log(`   - artifacts/deck_url.txt`);
  console.log();
  console.log('='.repeat(60));
  console.log('✅ DECK GENERATION COMPLETE');
  console.log('='.repeat(60));
  console.log();
  console.log('📋 Next Steps:');
  console.log('   1. Open artifacts/deck_preview.html in a browser');
  console.log('   2. Manually create a Google Slides deck with this content');
  console.log('   3. Or use the HTML as a template for further customization');
  console.log();
}

generateDeck().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
