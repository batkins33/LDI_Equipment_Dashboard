# Quick Start Guide

Get Brand Color Harmonizer running in 5 minutes!

## For End Users

### Installation (Manual - Development Mode)

1. **Go to Google Apps Script**
   - Visit [script.google.com](https://script.google.com)
   - Click "New Project"

2. **Copy the Code**
   - Open `Code.gs` from this repo
   - Replace all content in the Apps Script editor with the code
   - Save (Ctrl/Cmd + S)

3. **Add the Sidebar**
   - Click `+` next to "Files"
   - Select "HTML"
   - Name it `Sidebar`
   - Copy content from `Sidebar.html` in this repo
   - Paste and save

4. **Update Manifest**
   - Click the gear icon (Project Settings)
   - Check "Show appsscript.json in editor"
   - Go back to Editor
   - Click on `appsscript.json`
   - Replace with content from this repo
   - Save

5. **Test It**
   - Click "Deploy" → "Test deployments"
   - Click "Install"
   - Select installation config: "Installed"
   - Click "Done"

6. **Use It**
   - Open any Google Slides presentation
   - Refresh the page
   - Go to "Add-ons" menu
   - Click "Brand Color Harmonizer"
   - Start creating palettes and scanning!

## For Developers

### Setup

```bash
# Clone the repo (or navigate to the folder)
cd brand-color-harmonizer

# Install clasp globally
npm install -g @google/clasp

# Install project dependencies
npm install

# Login to Google
npm run login

# Create new Apps Script project
npm run create

# Push code to Apps Script
npm run push

# Open in browser
npm run open
```

### Development Cycle

```bash
# Make changes locally to Code.gs or Sidebar.html

# Push changes
npm run push

# View logs
npm run logs

# Test in a Google Slides presentation
```

## First Time Usage

### 1. Create Your First Palette

1. Open the add-on sidebar
2. Click "Palettes" tab
3. Click "+ New Palette"
4. Enter your brand name
5. Set your brand colors:
   - **Primary**: #1a73e8 (example)
   - **Secondary**: #34a853 (example)
   - **Accent**: #fbbc04 (example)
   - **Neutral**: #5f6368 (example)
6. Click "Save Palette"

### 2. Scan Your Presentation

1. Switch to "Scan" tab
2. Select your palette from dropdown
3. Click "Scan Presentation"
4. Wait for results

### 3. Fix Off-Brand Colors

1. Review the color analysis
2. Check boxes next to colors you want to replace
3. Or click "Select All Off-Brand"
4. Click "Apply Selected Replacements"
5. Done! Your presentation is now on-brand

## Example Brand Palettes

### Tech Startup
- Primary: #6366f1 (Indigo)
- Secondary: #8b5cf6 (Purple)
- Accent: #ec4899 (Pink)
- Neutral: #6b7280 (Gray)

### Professional Services
- Primary: #1e40af (Navy Blue)
- Secondary: #0891b2 (Cyan)
- Accent: #f59e0b (Amber)
- Neutral: #4b5563 (Slate)

### Creative Agency
- Primary: #ef4444 (Red)
- Secondary: #f97316 (Orange)
- Accent: #eab308 (Yellow)
- Neutral: #71717a (Zinc)

### Healthcare
- Primary: #0ea5e9 (Sky Blue)
- Secondary: #10b981 (Emerald)
- Accent: #06b6d4 (Cyan)
- Neutral: #64748b (Slate)

## Tips

- **Start Small**: Test with a simple presentation first
- **Use Named Palettes**: Give palettes descriptive names like "Q1 2024 Campaign"
- **Multiple Palettes**: Create different palettes for different brands or campaigns
- **Tolerance**: The add-on uses smart color matching - similar colors will be suggested
- **Batch Operations**: Select multiple colors to replace them all at once

## Troubleshooting

**Add-on not appearing?**
- Refresh your Google Slides presentation
- Check that authorization was completed

**Colors not being detected?**
- Only solid colors are supported (no gradients in v1)
- Pure black and white are filtered out

**Can't save palette?**
- Make sure all color fields are filled
- Check that palette name is not empty

**Replacement not working?**
- Ensure you selected colors to replace
- Check that you clicked "Apply Selected Replacements"

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [DEVELOPMENT.md](DEVELOPMENT.md) for development guide
- Explore advanced features and customization options

---

Need help? Open an issue in the repository!
