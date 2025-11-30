# Development Guide

## Local Development Setup

### Prerequisites

- Node.js and npm installed
- Google account with access to Google Apps Script
- Basic knowledge of JavaScript and HTML

### Install clasp (Command Line Apps Script Projects)

```bash
npm install -g @google/clasp
```

### Authenticate with Google

```bash
clasp login
```

This will open a browser window for authentication.

### Create a New Apps Script Project

```bash
cd brand-color-harmonizer
clasp create --type standalone --title "Brand Color Harmonizer"
```

This creates a `.clasp.json` file with your script ID.

### Push Code to Apps Script

```bash
clasp push
```

This uploads all `.gs`, `.html`, and `.json` files to your Apps Script project.

### Open in Browser

```bash
clasp open
```

This opens your project in the Apps Script editor.

## Development Workflow

### 1. Make Changes Locally

Edit files in your local directory:
- `Code.gs` - Server-side JavaScript
- `Sidebar.html` - Client-side UI
- `appsscript.json` - Manifest

### 2. Push to Apps Script

```bash
clasp push
```

### 3. Test in Google Slides

1. Open a Google Slides presentation
2. Reload the presentation (the add-on should appear after first installation)
3. Go to Add-ons → Brand Color Harmonizer
4. Test your changes

### 4. Pull Changes (if editing in browser)

If you make changes directly in the Apps Script editor:

```bash
clasp pull
```

## Testing

### Manual Testing Checklist

#### Palette Management
- [ ] Create a new palette
- [ ] Save palette with custom colors
- [ ] Load existing palettes
- [ ] Delete a palette
- [ ] Switch between multiple palettes

#### Color Scanning
- [ ] Scan a presentation with various colors
- [ ] Verify all color types are detected (text, shapes, backgrounds, tables)
- [ ] Check color frequency counts are accurate
- [ ] Verify slide numbers are correct

#### Color Classification
- [ ] Test with on-brand colors (should show as on-brand)
- [ ] Test with near-brand colors (should suggest closest match)
- [ ] Test with off-brand colors (should show as off-brand)

#### Color Replacement
- [ ] Replace a single color
- [ ] Replace multiple colors at once
- [ ] Verify replacements work on all element types
- [ ] Check that slide layout remains intact

### Test Presentation Setup

Create a test presentation with:
1. Multiple slides
2. Various text colors
3. Shapes with different fill colors
4. Tables with cell colors
5. Colored backgrounds
6. Both on-brand and off-brand colors

## Debugging

### View Logs

```bash
clasp logs
```

Or in the Apps Script editor:
- View → Logs
- View → Executions

### Add Logging

```javascript
Logger.log('Debug message: ' + variable);
```

### Common Issues

**Issue**: Add-on doesn't appear in menu
- **Solution**: Refresh the Google Slides presentation
- **Solution**: Check that `onOpen()` is defined in Code.gs

**Issue**: Permission errors
- **Solution**: Remove the add-on authorization and reinstall
- **Solution**: Check `appsscript.json` has correct OAuth scopes

**Issue**: Colors not being detected
- **Solution**: Check that elements have solid fills (gradients not supported in v1)
- **Solution**: Verify color extraction logic in `scanSlideElements()`

**Issue**: Replacement not working
- **Solution**: Check that hex colors are formatted correctly (#RRGGBB)
- **Solution**: Verify RGB conversion in `hexToRgb()`

## Code Structure

### Server-Side (Code.gs)

```
Add-on Initialization
├── onInstall()
├── onOpen()
├── showSidebar()
├── onHomepage()
└── onFileScopeGranted()

Palette Management
├── savePalette()
├── getPalettes()
├── getPalette()
└── deletePalette()

Color Scanning
├── scanPresentation()
├── scanSlideElements()
├── scanTextRange()
├── scanTable()
└── addColorToMap()

Color Utilities
├── colorToHex()
├── rgbToHex()
├── hexToRgb()
└── componentToHex()

Color Classification
├── classifyColors()
├── findClosestBrandColor()
└── colorDistance()

Color Replacement
├── replaceColor()
├── replaceColorInSlide()
├── replaceColorInShape()
├── replaceColorInText()
├── replaceColorInTable()
└── batchReplaceColors()
```

### Client-Side (Sidebar.html)

```
UI Components
├── Tab switching (Palettes / Scan)
├── Palette list
├── New palette form
├── Scan interface
└── Results display

JavaScript Functions
├── loadPalettes()
├── renderPaletteList()
├── savePalette()
├── deletePalette()
├── startScan()
├── renderScanResults()
├── applySelectedReplacements()
└── showMessage()
```

## Best Practices

### Performance

- **Batch Operations**: Use `batchReplaceColors()` instead of multiple single replacements
- **Minimize API Calls**: Cache palette data to avoid repeated property service calls
- **Efficient Scanning**: Skip pure black/white to reduce noise

### User Experience

- **Loading States**: Show spinners during long operations
- **Error Handling**: Display user-friendly error messages
- **Feedback**: Confirm successful operations with success messages

### Code Quality

- **Documentation**: Add JSDoc comments for public functions
- **Error Handling**: Use try-catch blocks for external API calls
- **Validation**: Validate user input before processing

## Deployment

### Test Deployment

1. In Apps Script editor: Deploy → Test deployments
2. Click "Install"
3. Test in a Google Slides presentation

### Production Deployment

1. In Apps Script editor: Deploy → New deployment
2. Select type: "Add-on"
3. Fill in deployment details
4. Choose visibility (Just me, Domain, Public)
5. Click "Deploy"

### Publishing to Marketplace

1. Complete the OAuth verification process
2. Create store listing with screenshots
3. Submit for review
4. Wait for approval (typically 2-4 weeks)

## Version Control

### Git Workflow

```bash
# After making changes
git add .
git commit -m "feat: add feature description"
git push origin claude/brand-color-harmonizer-<session-id>
```

### File Sync

Always keep both local files and Apps Script in sync:

```bash
# After local changes
clasp push

# After Apps Script editor changes
clasp pull
```

## Adding New Features

### Example: Add a New Color Role

1. **Update Sidebar.html**:
   - Add new color input in palette form
   - Update `savePalette()` to include new color

2. **Update Code.gs**:
   - Modify palette data model if needed
   - Update classification logic if required

3. **Test**:
   - Create a palette with the new role
   - Verify scanning picks up suggestions
   - Test replacement functionality

## Resources

- [Google Apps Script Documentation](https://developers.google.com/apps-script)
- [Google Slides API](https://developers.google.com/apps-script/reference/slides)
- [clasp Documentation](https://github.com/google/clasp)
- [Google Workspace Add-ons](https://developers.google.com/workspace/add-ons)

## Support

For development questions:
1. Check the Google Apps Script documentation
2. Search Stack Overflow
3. Open an issue in the repository

---

Happy coding! 🎨
