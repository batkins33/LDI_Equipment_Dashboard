/**
 * Brand Color Harmonizer - Google Slides Add-on
 * Scans presentations for off-brand colors and suggests replacements
 */

// ========================================
// Add-on Initialization
// ========================================

/**
 * Runs when the add-on is installed
 */
function onInstall(e) {
  onOpen(e);
}

/**
 * Runs when a presentation is opened
 */
function onOpen(e) {
  SlidesApp.getUi()
    .createAddonMenu()
    .addItem('Open Brand Color Harmonizer', 'showSidebar')
    .addToUi();
}

/**
 * Opens the sidebar
 */
function showSidebar() {
  var html = HtmlService.createHtmlOutputFromFile('Sidebar')
    .setTitle('Brand Color Harmonizer');
  SlidesApp.getUi().showSidebar(html);
}

/**
 * Runs when homepage is triggered
 */
function onHomepage(e) {
  return createHomepageCard();
}

/**
 * Runs when file scope is granted
 */
function onFileScopeGranted(e) {
  return createHomepageCard();
}

/**
 * Creates the homepage card
 */
function createHomepageCard() {
  var card = CardService.newCardBuilder();
  card.setHeader(CardService.newCardHeader()
    .setTitle('Brand Color Harmonizer')
    .setSubtitle('Keep your colors on-brand'));

  var section = CardService.newCardSection()
    .addWidget(CardService.newTextParagraph()
      .setText('Scan your presentation for off-brand colors and get replacement suggestions.'))
    .addWidget(CardService.newTextButton()
      .setText('Open Harmonizer')
      .setOnClickAction(CardService.newAction()
        .setFunctionName('showSidebar')));

  card.addSection(section);
  return card.build();
}

// ========================================
// Brand Palette Management
// ========================================

/**
 * Saves a brand palette
 */
function savePalette(paletteData) {
  try {
    var palettes = getPalettes();
    var palette = {
      id: paletteData.id || Utilities.getUuid(),
      name: paletteData.name,
      colors: paletteData.colors,
      created_at: paletteData.created_at || new Date().toISOString()
    };

    palettes[palette.id] = palette;
    PropertiesService.getUserProperties().setProperty('brand_palettes', JSON.stringify(palettes));

    return { success: true, palette: palette };
  } catch (e) {
    return { success: false, error: e.message };
  }
}

/**
 * Gets all saved palettes
 */
function getPalettes() {
  var stored = PropertiesService.getUserProperties().getProperty('brand_palettes');
  return stored ? JSON.parse(stored) : {};
}

/**
 * Gets a specific palette by ID
 */
function getPalette(paletteId) {
  var palettes = getPalettes();
  return palettes[paletteId] || null;
}

/**
 * Deletes a palette
 */
function deletePalette(paletteId) {
  try {
    var palettes = getPalettes();
    delete palettes[paletteId];
    PropertiesService.getUserProperties().setProperty('brand_palettes', JSON.stringify(palettes));
    return { success: true };
  } catch (e) {
    return { success: false, error: e.message };
  }
}

// ========================================
// Color Scanning
// ========================================

/**
 * Scans the current presentation for all colors
 */
function scanPresentation(paletteId) {
  try {
    var presentation = SlidesApp.getActivePresentation();
    var palette = getPalette(paletteId);

    if (!palette) {
      return { success: false, error: 'Palette not found' };
    }

    var colorMap = {};
    var slides = presentation.getSlides();

    // Scan each slide
    for (var i = 0; i < slides.length; i++) {
      var slide = slides[i];
      var slideNumber = i + 1;
      scanSlideElements(slide, slideNumber, colorMap);
    }

    // Classify colors and add suggestions
    var results = classifyColors(colorMap, palette);

    return {
      success: true,
      deck_id: presentation.getId(),
      palette_id: paletteId,
      colors_found: results,
      total_colors: Object.keys(colorMap).length
    };
  } catch (e) {
    return { success: false, error: e.message };
  }
}

/**
 * Scans all elements on a slide for colors
 */
function scanSlideElements(slide, slideNumber, colorMap) {
  var elements = slide.getPageElements();

  for (var i = 0; i < elements.length; i++) {
    var element = elements[i];

    try {
      // Check shapes
      if (element.getPageElementType() === SlidesApp.PageElementType.SHAPE) {
        var shape = element.asShape();

        // Fill color
        if (shape.getFill().getSolidFill()) {
          var fillColor = shape.getFill().getSolidFill().getColor();
          addColorToMap(fillColor, slideNumber, 'shape-fill', colorMap);
        }

        // Border color
        if (shape.getBorder() && shape.getBorder().getLineFill() && shape.getBorder().getLineFill().getSolidFill()) {
          var borderColor = shape.getBorder().getLineFill().getSolidFill().getColor();
          addColorToMap(borderColor, slideNumber, 'shape-border', colorMap);
        }

        // Text color
        if (shape.getText()) {
          scanTextRange(shape.getText(), slideNumber, colorMap);
        }
      }

      // Check text boxes
      if (element.getPageElementType() === SlidesApp.PageElementType.TEXT_BOX) {
        var textBox = element.asTextBox();
        scanTextRange(textBox.getText(), slideNumber, colorMap);
      }

      // Check tables
      if (element.getPageElementType() === SlidesApp.PageElementType.TABLE) {
        var table = element.asTable();
        scanTable(table, slideNumber, colorMap);
      }
    } catch (e) {
      // Skip elements that can't be accessed
      Logger.log('Error scanning element: ' + e.message);
    }
  }

  // Check slide background
  try {
    var background = slide.getBackground();
    if (background.getSolidFill()) {
      var bgColor = background.getSolidFill().getColor();
      addColorToMap(bgColor, slideNumber, 'slide-background', colorMap);
    }
  } catch (e) {
    Logger.log('Error scanning background: ' + e.message);
  }
}

/**
 * Scans a text range for colors
 */
function scanTextRange(textRange, slideNumber, colorMap) {
  try {
    var textStyle = textRange.getTextStyle();
    if (textStyle.getForegroundColor()) {
      addColorToMap(textStyle.getForegroundColor(), slideNumber, 'text', colorMap);
    }
  } catch (e) {
    Logger.log('Error scanning text: ' + e.message);
  }
}

/**
 * Scans a table for colors
 */
function scanTable(table, slideNumber, colorMap) {
  var numRows = table.getNumRows();
  var numCols = table.getNumColumns();

  for (var r = 0; r < numRows; r++) {
    for (var c = 0; c < numCols; c++) {
      try {
        var cell = table.getCell(r, c);

        // Cell fill
        if (cell.getFill().getSolidFill()) {
          var fillColor = cell.getFill().getSolidFill().getColor();
          addColorToMap(fillColor, slideNumber, 'table-cell', colorMap);
        }

        // Cell text
        if (cell.getText()) {
          scanTextRange(cell.getText(), slideNumber, colorMap);
        }
      } catch (e) {
        Logger.log('Error scanning table cell: ' + e.message);
      }
    }
  }
}

/**
 * Adds a color to the color map
 */
function addColorToMap(colorObj, slideNumber, type, colorMap) {
  var hex = colorToHex(colorObj);

  if (!hex || hex === '#000000' || hex === '#ffffff') {
    // Skip pure black and white for now
    return;
  }

  if (!colorMap[hex]) {
    colorMap[hex] = {
      hex: hex,
      count: 0,
      slide_ids: [],
      types: []
    };
  }

  colorMap[hex].count++;
  if (colorMap[hex].slide_ids.indexOf(slideNumber) === -1) {
    colorMap[hex].slide_ids.push(slideNumber);
  }
  if (colorMap[hex].types.indexOf(type) === -1) {
    colorMap[hex].types.push(type);
  }
}

/**
 * Converts a Color object to hex
 */
function colorToHex(colorObj) {
  try {
    if (colorObj.getColorType() === SlidesApp.ColorType.RGB) {
      var rgbColor = colorObj.asRgbColor();
      var r = Math.round(rgbColor.getRed() * 255);
      var g = Math.round(rgbColor.getGreen() * 255);
      var b = Math.round(rgbColor.getBlue() * 255);
      return rgbToHex(r, g, b);
    }
    return null;
  } catch (e) {
    return null;
  }
}

/**
 * Converts RGB to hex
 */
function rgbToHex(r, g, b) {
  return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}

/**
 * Converts a color component to hex
 */
function componentToHex(c) {
  var hex = c.toString(16);
  return hex.length == 1 ? "0" + hex : hex;
}

// ========================================
// Color Classification
// ========================================

/**
 * Classifies colors as on-brand, near-brand, or off-brand
 */
function classifyColors(colorMap, palette) {
  var results = [];
  var threshold = 30; // Color distance threshold for "near-brand"
  var snapThreshold = 10; // Very close colors can be snapped

  for (var hex in colorMap) {
    var colorData = colorMap[hex];
    var closest = findClosestBrandColor(hex, palette.colors);

    var classification = 'off-brand';
    if (closest.distance === 0) {
      classification = 'on-brand';
    } else if (closest.distance <= snapThreshold) {
      classification = 'near-brand';
    } else if (closest.distance <= threshold) {
      classification = 'near-brand';
    }

    results.push({
      hex: hex,
      count: colorData.count,
      slide_ids: colorData.slide_ids,
      types: colorData.types,
      classification: classification,
      suggested_hex: classification === 'on-brand' ? null : closest.hex,
      suggested_role: classification === 'on-brand' ? null : closest.role,
      distance: closest.distance
    });
  }

  // Sort by count (most used first)
  results.sort(function(a, b) {
    return b.count - a.count;
  });

  return results;
}

/**
 * Finds the closest brand color to a given hex color
 */
function findClosestBrandColor(hex, brandColors) {
  var minDistance = Infinity;
  var closestColor = null;
  var closestRole = null;

  for (var i = 0; i < brandColors.length; i++) {
    var brandColor = brandColors[i];
    var distance = colorDistance(hex, brandColor.hex);

    if (distance < minDistance) {
      minDistance = distance;
      closestColor = brandColor.hex;
      closestRole = brandColor.role;
    }
  }

  return {
    hex: closestColor,
    role: closestRole,
    distance: minDistance
  };
}

/**
 * Calculates the distance between two colors using Delta E (simplified)
 */
function colorDistance(hex1, hex2) {
  var rgb1 = hexToRgb(hex1);
  var rgb2 = hexToRgb(hex2);

  if (!rgb1 || !rgb2) return Infinity;

  // Simple Euclidean distance in RGB space
  var rDiff = rgb1.r - rgb2.r;
  var gDiff = rgb1.g - rgb2.g;
  var bDiff = rgb1.b - rgb2.b;

  return Math.sqrt(rDiff * rDiff + gDiff * gDiff + bDiff * bDiff);
}

/**
 * Converts hex to RGB
 */
function hexToRgb(hex) {
  var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  } : null;
}

// ========================================
// Color Replacement
// ========================================

/**
 * Replaces a color throughout the presentation
 */
function replaceColor(fromHex, toHex, slideIds) {
  try {
    var presentation = SlidesApp.getActivePresentation();
    var slides = presentation.getSlides();
    var replacementCount = 0;

    var targetSlides = slideIds && slideIds.length > 0
      ? slideIds.map(function(id) { return slides[id - 1]; })
      : slides;

    for (var i = 0; i < targetSlides.length; i++) {
      var slide = targetSlides[i];
      replacementCount += replaceColorInSlide(slide, fromHex, toHex);
    }

    return { success: true, count: replacementCount };
  } catch (e) {
    return { success: false, error: e.message };
  }
}

/**
 * Replaces color in a single slide
 */
function replaceColorInSlide(slide, fromHex, toHex) {
  var count = 0;
  var elements = slide.getPageElements();
  var toRgb = hexToRgb(toHex);

  for (var i = 0; i < elements.length; i++) {
    var element = elements[i];

    try {
      if (element.getPageElementType() === SlidesApp.PageElementType.SHAPE) {
        var shape = element.asShape();
        count += replaceColorInShape(shape, fromHex, toRgb);
      }

      if (element.getPageElementType() === SlidesApp.PageElementType.TEXT_BOX) {
        var textBox = element.asTextBox();
        count += replaceColorInText(textBox.getText(), fromHex, toRgb);
      }

      if (element.getPageElementType() === SlidesApp.PageElementType.TABLE) {
        var table = element.asTable();
        count += replaceColorInTable(table, fromHex, toRgb);
      }
    } catch (e) {
      Logger.log('Error replacing color in element: ' + e.message);
    }
  }

  // Replace in background
  try {
    var background = slide.getBackground();
    if (background.getSolidFill()) {
      var bgColor = background.getSolidFill().getColor();
      if (colorToHex(bgColor) === fromHex) {
        background.setSolidFill(toRgb.r, toRgb.g, toRgb.b);
        count++;
      }
    }
  } catch (e) {
    Logger.log('Error replacing background color: ' + e.message);
  }

  return count;
}

/**
 * Replaces color in a shape
 */
function replaceColorInShape(shape, fromHex, toRgb) {
  var count = 0;

  // Replace fill color
  try {
    if (shape.getFill().getSolidFill()) {
      var fillColor = shape.getFill().getSolidFill().getColor();
      if (colorToHex(fillColor) === fromHex) {
        shape.getFill().setSolidFill(toRgb.r, toRgb.g, toRgb.b);
        count++;
      }
    }
  } catch (e) {}

  // Replace border color
  try {
    if (shape.getBorder() && shape.getBorder().getLineFill() && shape.getBorder().getLineFill().getSolidFill()) {
      var borderColor = shape.getBorder().getLineFill().getSolidFill().getColor();
      if (colorToHex(borderColor) === fromHex) {
        shape.getBorder().getLineFill().setSolidFill(toRgb.r, toRgb.g, toRgb.b);
        count++;
      }
    }
  } catch (e) {}

  // Replace text color
  if (shape.getText()) {
    count += replaceColorInText(shape.getText(), fromHex, toRgb);
  }

  return count;
}

/**
 * Replaces color in text
 */
function replaceColorInText(textRange, fromHex, toRgb) {
  var count = 0;

  try {
    var textStyle = textRange.getTextStyle();
    if (textStyle.getForegroundColor() && colorToHex(textStyle.getForegroundColor()) === fromHex) {
      textStyle.setForegroundColor(toRgb.r, toRgb.g, toRgb.b);
      count++;
    }
  } catch (e) {}

  return count;
}

/**
 * Replaces color in a table
 */
function replaceColorInTable(table, fromHex, toRgb) {
  var count = 0;
  var numRows = table.getNumRows();
  var numCols = table.getNumColumns();

  for (var r = 0; r < numRows; r++) {
    for (var c = 0; c < numCols; c++) {
      try {
        var cell = table.getCell(r, c);

        // Replace cell fill
        if (cell.getFill().getSolidFill()) {
          var fillColor = cell.getFill().getSolidFill().getColor();
          if (colorToHex(fillColor) === fromHex) {
            cell.getFill().setSolidFill(toRgb.r, toRgb.g, toRgb.b);
            count++;
          }
        }

        // Replace cell text
        if (cell.getText()) {
          count += replaceColorInText(cell.getText(), fromHex, toRgb);
        }
      } catch (e) {}
    }
  }

  return count;
}

/**
 * Batch replace multiple colors
 */
function batchReplaceColors(replacements) {
  try {
    var totalCount = 0;

    for (var i = 0; i < replacements.length; i++) {
      var replacement = replacements[i];
      var result = replaceColor(replacement.fromHex, replacement.toHex, replacement.slideIds);

      if (result.success) {
        totalCount += result.count;
      }
    }

    return { success: true, totalCount: totalCount };
  } catch (e) {
    return { success: false, error: e.message };
  }
}
