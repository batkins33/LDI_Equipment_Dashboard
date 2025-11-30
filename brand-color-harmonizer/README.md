# Brand Color Harmonizer

> Scan your Google Slides for off-brand colors and auto-suggest replacements from your brand palette.

## Overview

Brand Color Harmonizer is a Google Slides add-on that helps designers, marketers, and content teams maintain brand consistency by automatically detecting off-brand colors in presentations and suggesting replacements from a predefined brand palette.

## Features

### v1 Core Features

- **Brand Palette Management**
  - Create and save multiple brand palettes
  - Define primary, secondary, accent, and neutral colors
  - Switch between palettes for different brands or projects

- **Smart Color Scanning**
  - Extract all colors from text, shapes, backgrounds, tables, and borders
  - Build a comprehensive color frequency map
  - Track where each color appears (slide numbers)

- **Intelligent Color Classification**
  - **On-brand**: Colors that match your brand palette
  - **Near-brand**: Colors close enough to suggest snapping to the nearest brand color
  - **Off-brand**: Colors outside your brand tolerance

- **One-Click Replacements**
  - Get smart suggestions for the closest brand color match
  - Replace colors across all slides or specific slides
  - Batch apply multiple replacements at once
  - See before/after color swatches

## Installation

### Option 1: Install from Google Workspace Marketplace (Recommended)
*Coming soon - not yet published*

### Option 2: Manual Installation (For Development)

1. **Open Google Apps Script**
   - Go to [script.google.com](https://script.google.com)
   - Click "New Project"

2. **Add the Code Files**
   - Replace the default `Code.gs` with the contents of `Code.gs` from this repo
   - Click `+` next to Files → HTML → Name it `Sidebar` and paste the contents of `Sidebar.html`
   - Click the gear icon (Project Settings) → Check "Show appsscript.json"
   - Replace `appsscript.json` with the contents from this repo

3. **Deploy as Add-on**
   - Click "Deploy" → "Test deployments"
   - Click "Install"
   - Select "Google Slides" from the dropdown
   - Click "Install"

4. **Authorize**
   - Open a Google Slides presentation
   - You'll see "Brand Color Harmonizer" in the Add-ons menu
   - Click to authorize the add-on

## Usage Guide

### 1. Create a Brand Palette

1. Open a Google Slides presentation
2. Go to **Add-ons → Brand Color Harmonizer**
3. Click the **Palettes** tab
4. Click **+ New Palette**
5. Enter a palette name (e.g., "Acme Corp Brand 2024")
6. Define your brand colors:
   - **Primary**: Your main brand color
   - **Secondary**: Supporting color
   - **Accent**: Highlight/call-to-action color
   - **Neutral**: Text/background neutral
7. Click **Save Palette**

### 2. Scan Your Presentation

1. Switch to the **Scan** tab
2. Select a palette from the dropdown
3. Click **Scan Presentation**
4. Wait for the analysis to complete

### 3. Review Results

The scanner will show:
- **Total colors found** in your presentation
- **Number of off-brand colors** detected
- For each color:
  - Color swatch and hex code
  - Usage count and slide locations
  - Classification badge (on-brand, near-brand, off-brand)
  - Suggested replacement color

### 4. Apply Replacements

1. Check the boxes next to colors you want to replace
2. Or click **Select All Off-Brand** for quick fixes
3. Click **Apply Selected Replacements**
4. The add-on will update your presentation automatically

## Technical Details

### Color Detection

The add-on scans the following elements:
- Shape fills and borders
- Text colors
- Table cell backgrounds and text
- Slide backgrounds

### Color Matching Algorithm

Colors are classified using Euclidean distance in RGB color space:
- **Distance 0**: Exact match (on-brand)
- **Distance ≤ 10**: Very close, can snap (near-brand)
- **Distance ≤ 30**: Reasonably close (near-brand)
- **Distance > 30**: Off-brand

### Data Storage

- Palettes are stored in Google Apps Script User Properties
- No external servers or databases
- Data is private to your Google account

### Permissions Required

- `presentations.currentonly`: Read and modify the current presentation
- `script.container.ui`: Display the sidebar interface

## Architecture

```
Brand Color Harmonizer/
├── Code.gs              # Server-side logic
│   ├── Add-on initialization
│   ├── Palette management
│   ├── Color scanning
│   ├── Color classification
│   └── Color replacement
├── Sidebar.html         # Client-side UI
│   ├── Palette editor
│   ├── Scan interface
│   └── Results display
└── appsscript.json      # Add-on manifest
```

## Data Model

### BrandPalette
```javascript
{
  id: string,
  name: string,
  colors: [
    {
      role: "primary" | "secondary" | "accent" | "neutral",
      hex: string
    }
  ],
  created_at: ISO date string
}
```

### ScanResult
```javascript
{
  deck_id: string,
  palette_id: string,
  colors_found: [
    {
      hex: string,
      count: number,
      slide_ids: number[],
      types: string[],
      classification: "on-brand" | "near-brand" | "off-brand",
      suggested_hex: string,
      suggested_role: string,
      distance: number
    }
  ]
}
```

## Limitations (v1)

- Pure black (#000000) and pure white (#ffffff) are currently excluded from scanning
- No font style enforcement
- No multi-document bulk scanning
- No automated logo checks
- No collaboration features beyond Google Slides' built-in capabilities

## Future Enhancements (Roadmap)

- [ ] Support for Google Docs
- [ ] Gradient color detection
- [ ] Custom color tolerance settings
- [ ] Export scan reports
- [ ] Brand palette templates
- [ ] Integration with design systems (Figma, etc.)
- [ ] Font and typography checking
- [ ] Logo compliance verification
- [ ] Team palette sharing

## Contributing

This project is part of the BA_Sandbox repository. To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Specify your license here]

## Support

For issues, questions, or feature requests, please open an issue in the GitHub repository.

## Credits

Developed as part of the Tangent Forge hybrid idea exploration.

---

**Target Users**: Designers, marketers, content teams working in Google Slides/Docs

**Job-to-be-done**: "I want everything to look on-brand without manually hunting for rogue colors."
