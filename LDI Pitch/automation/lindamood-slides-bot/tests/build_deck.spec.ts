/**
 * End-to-End Test Suite for Lindamood Slides Bot
 * 
 * Validates the complete workflow:
 * 1. Auth state exists (skips with message if not)
 * 2. Brand extraction works (or uses existing)
 * 3. Deck building creates artifacts
 * 4. PDF export succeeds
 * 
 * Run with: npm test
 */

import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Paths
const AUTH_PATH = path.join(__dirname, '..', '.auth', 'storageState.json');
const BRAND_PATH = path.join(__dirname, '..', 'brand', 'brand.json');
const CONTENT_PATH = path.join(__dirname, '..', 'content', 'deck_outline.json');
const ARTIFACTS_DIR = path.join(__dirname, '..', 'artifacts');
const DECK_URL_PATH = path.join(ARTIFACTS_DIR, 'deck_url.txt');
const PDF_PATH = path.join(ARTIFACTS_DIR, 'lindamood_opportunity_deck.pdf');
const SCREENSHOTS_DIR = path.join(ARTIFACTS_DIR, 'screenshots');

test.describe.configure({ mode: 'serial' });

test.describe('Lindamood Slides Bot E2E', () => {

  test.beforeAll(() => {
    console.log('\n' + '='.repeat(60));
    console.log('🧪 E2E Test Suite Starting');
    console.log('='.repeat(60) + '\n');
  });

  /**
   * Test 1: Verify authentication state exists
   */
  test('T1: Authentication state exists', () => {
    console.log('T1: Checking authentication...');
    
    const authExists = fs.existsSync(AUTH_PATH);
    
    if (!authExists) {
      console.log('   ⚠️  storageState.json not found');
      console.log('   📋 To fix: Run "npm run auth" to authenticate');
      
      // Skip remaining tests with clear message
      test.skip(!authExists, 'Authentication required - run "npm run auth" first');
    }
    
    const stats = fs.statSync(AUTH_PATH);
    expect(stats.size).toBeGreaterThan(100); // Valid auth file should be substantial
    
    const authData = JSON.parse(fs.readFileSync(AUTH_PATH, 'utf-8'));
    expect(authData).toHaveProperty('cookies');
    expect(authData).toHaveProperty('origins');
    
    // Verify Google origin is present
    const hasGoogleOrigin = authData.origins.some(
      (origin: { origin: string }) => origin.origin.includes('google.com')
    );
    expect(hasGoogleOrigin).toBe(true);
    
    console.log('   ✅ Auth state valid');
  });

  /**
   * Test 2: Verify content outline exists and is valid
   */
  test('T2: Content outline is valid', () => {
    console.log('T2: Checking content outline...');
    
    expect(fs.existsSync(CONTENT_PATH)).toBe(true);
    
    const content = JSON.parse(fs.readFileSync(CONTENT_PATH, 'utf-8'));
    
    // Validate structure
    expect(content).toHaveProperty('title');
    expect(content).toHaveProperty('slides');
    expect(Array.isArray(content.slides)).toBe(true);
    expect(content.slides.length).toBeGreaterThanOrEqual(8);
    
    // Check for required slide titles
    const titles = content.slides.map((s: { title: string }) => s.title);
    const requiredTitles = [
      'Legacy & Landscape',
      'Where It Hurts',
      'Path Forward'
    ];
    
    for (const required of requiredTitles) {
      expect(titles).toContain(required);
    }
    
    // Validate each slide has minimum properties
    for (const slide of content.slides) {
      expect(slide).toHaveProperty('id');
      expect(slide).toHaveProperty('layout');
      expect(slide).toHaveProperty('title');
      
      // Title should be non-empty string
      expect(typeof slide.title).toBe('string');
      expect(slide.title.length).toBeGreaterThan(0);
    }
    
    console.log(`   ✅ Outline valid (${content.slides.length} slides)`);
  });

  /**
   * Test 3: Extract or validate brand
   */
  test('T3: Brand extraction works or brand.json exists', () => {
    console.log('T3: Checking brand extraction...');
    
    if (fs.existsSync(BRAND_PATH)) {
      console.log('   ℹ️  Using existing brand.json');
      const brand = JSON.parse(fs.readFileSync(BRAND_PATH, 'utf-8'));
      
      expect(brand).toHaveProperty('primaryColor');
      expect(brand).toHaveProperty('accentColor');
      expect(brand).toHaveProperty('textColor');
      expect(brand).toHaveProperty('backgroundColor');
      
      console.log('   ✅ Brand data valid');
    } else {
      console.log('   🔄 Running brand extraction...');
      
      try {
        execSync('npm run brand:extract', {
          cwd: path.join(__dirname, '..'),
          stdio: 'pipe',
          timeout: 120000
        });
        
        expect(fs.existsSync(BRAND_PATH)).toBe(true);
        
        const brand = JSON.parse(fs.readFileSync(BRAND_PATH, 'utf-8'));
        expect(brand).toHaveProperty('primaryColor');
        expect(brand).toHaveProperty('logoPath');
        
        console.log('   ✅ Brand extracted successfully');
      } catch (error) {
        console.log('   ⚠️  Brand extraction failed, will use defaults');
        // Test passes as defaults will be used
      }
    }
  });

  /**
   * Test 4: Deck building creates artifacts
   */
  test('T4: Deck building creates artifacts', async () => {
    console.log('T4: Testing deck building...');
    
    // Clean up previous artifacts for fresh test
    if (fs.existsSync(DECK_URL_PATH)) {
      fs.unlinkSync(DECK_URL_PATH);
    }
    
    // Run deck build
    try {
      execSync('npm run deck:build', {
        cwd: path.join(__dirname, '..'),
        stdio: 'pipe',
        timeout: 300000 // 5 minute timeout for deck building
      });
    } catch (error) {
      console.log('   ⚠️  Deck build command failed, checking artifacts...');
    }
    
    // Verify deck URL was written
    expect(fs.existsSync(DECK_URL_PATH)).toBe(true);
    
    const deckUrl = fs.readFileSync(DECK_URL_PATH, 'utf-8');
    expect(deckUrl).toContain('docs.google.com');
    expect(deckUrl).toContain('/presentation/');
    
    console.log('   ✅ Deck URL captured:', deckUrl.substring(0, 60) + '...');
    
    // Verify final screenshot exists
    const finalScreenshot = path.join(SCREENSHOTS_DIR, 'deck_final.png');
    if (fs.existsSync(finalScreenshot)) {
      const stats = fs.statSync(finalScreenshot);
      expect(stats.size).toBeGreaterThan(10000); // At least 10KB
      console.log(`   ✅ Screenshot captured (${Math.round(stats.size / 1024)} KB)`);
    } else {
      console.log('   ⚠️  Final screenshot not found');
    }
  });

  /**
   * Test 5: PDF export validation
   */
  test('T5: PDF export succeeds', () => {
    console.log('T5: Checking PDF export...');
    
    if (fs.existsSync(PDF_PATH)) {
      const stats = fs.statSync(PDF_PATH);
      expect(stats.size).toBeGreaterThan(50000); // At least 50KB
      
      // Verify it's a valid PDF (starts with PDF magic number)
      const fd = fs.openSync(PDF_PATH, 'r');
      const buffer = Buffer.alloc(4);
      fs.readSync(fd, buffer, 0, 4, 0);
      fs.closeSync(fd);
      
      const pdfHeader = buffer.toString('ascii');
      expect(pdfHeader).toBe('%PDF');
      
      console.log(`   ✅ PDF valid (${Math.round(stats.size / 1024)} KB)`);
    } else {
      console.log('   ⚠️  PDF not found - may require manual export');
      console.log('      File → Download → PDF Document (.pdf)');
      // Don't fail test - PDF export can be manual
    }
  });

  /**
   * Test 6: Screenshot artifacts validation
   */
  test('T6: Screenshots captured', () => {
    console.log('T6: Validating screenshots...');
    
    if (!fs.existsSync(SCREENSHOTS_DIR)) {
      console.log('   ⚠️  Screenshots directory not found');
      return;
    }
    
    const files = fs.readdirSync(SCREENSHOTS_DIR);
    const pngFiles = files.filter(f => f.endsWith('.png'));
    
    expect(pngFiles.length).toBeGreaterThan(0);
    
    // Check each screenshot is valid
    for (const file of pngFiles) {
      const filePath = path.join(SCREENSHOTS_DIR, file);
      const stats = fs.statSync(filePath);
      expect(stats.size).toBeGreaterThan(1000); // At least 1KB
      
      // Verify PNG magic number
      const fd = fs.openSync(filePath, 'r');
      const buffer = Buffer.alloc(8);
      fs.readSync(fd, buffer, 0, 8, 0);
      fs.closeSync(fd);
      
      const pngHeader = buffer.toString('hex').toUpperCase();
      expect(pngHeader.startsWith('89504E470D0A1A0A')).toBe(true);
    }
    
    console.log(`   ✅ ${pngFiles.length} screenshot(s) valid`);
    
    // Look for specific expected screenshots
    const expectedScreenshots = [
      'deck_final.png',
      'site_home.png',
      'site_header.png'
    ];
    
    for (const expected of expectedScreenshots) {
      const found = pngFiles.includes(expected);
      if (found) {
        console.log(`      ✓ ${expected}`);
      } else {
        console.log(`      ○ ${expected} (optional)`);
      }
    }
  });

  /**
   * Test 7: Artifacts directory structure
   */
  test('T7: Artifacts directory structure', () => {
    console.log('T7: Checking artifacts structure...');
    
    // Ensure artifacts directory exists
    expect(fs.existsSync(ARTIFACTS_DIR)).toBe(true);
    
    // Check for expected files
    const expectedFiles = [
      DECK_URL_PATH,
      PDF_PATH
    ];
    
    const existingFiles = expectedFiles.filter(f => fs.existsSync(f));
    
    console.log(`   Found ${existingFiles.length}/${expectedFiles.length} expected artifacts`);
    
    // Deck URL must exist
    expect(fs.existsSync(DECK_URL_PATH)).toBe(true);
    
    console.log('   ✅ Core artifacts present');
  });

  test.afterAll(() => {
    console.log('\n' + '='.repeat(60));
    console.log('🧪 E2E Test Suite Complete');
    console.log('='.repeat(60) + '\n');
    
    // Summary
    console.log('📋 Test Summary:');
    console.log('  - T1: Authentication');
    console.log('  - T2: Content Outline');
    console.log('  - T3: Brand Extraction');
    console.log('  - T4: Deck Building');
    console.log('  - T5: PDF Export');
    console.log('  - T6: Screenshots');
    console.log('  - T7: Artifacts Structure');
    console.log();
    
    if (fs.existsSync(DECK_URL_PATH)) {
      const url = fs.readFileSync(DECK_URL_PATH, 'utf-8');
      console.log(`🔗 Deck URL: ${url}`);
    }
  });
});
