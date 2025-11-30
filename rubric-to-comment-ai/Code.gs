/**
 * Rubric-to-Comment AI
 * Google Docs Add-on for generating rubric-aligned feedback
 *
 * Main entry point and menu setup
 */

/**
 * Called when the add-on is installed
 */
function onInstall(e) {
  onOpen(e);
}

/**
 * Called when a document is opened
 */
function onOpen(e) {
  DocumentApp.getUi()
    .createAddonMenu()
    .addItem('Open Rubric Feedback', 'showSidebar')
    .addItem('Settings', 'showSettings')
    .addToUi();
}

/**
 * Opens the main sidebar for rubric feedback
 */
function showSidebar() {
  var html = HtmlService.createHtmlOutputFromFile('Sidebar')
    .setTitle('Rubric Feedback')
    .setWidth(350);
  DocumentApp.getUi().showSidebar(html);
}

/**
 * Opens settings dialog
 */
function showSettings() {
  var html = HtmlService.createHtmlOutputFromFile('Settings')
    .setWidth(400)
    .setHeight(300);
  DocumentApp.getUi().showModalDialog(html, 'Settings');
}

/**
 * Get document text for analysis
 */
function getDocumentText() {
  var doc = DocumentApp.getActiveDocument();
  var body = doc.getBody();
  return body.getText();
}

/**
 * Get document structure with paragraphs for targeted commenting
 */
function getDocumentStructure() {
  var doc = DocumentApp.getActiveDocument();
  var body = doc.getBody();
  var paragraphs = body.getParagraphs();

  var structure = [];
  for (var i = 0; i < paragraphs.length; i++) {
    var para = paragraphs[i];
    var text = para.getText();
    if (text.trim().length > 0) {
      structure.push({
        index: i,
        text: text,
        type: para.getType().toString()
      });
    }
  }

  return structure;
}

/**
 * Test function to verify setup
 */
function testSetup() {
  Logger.log('Add-on is correctly set up!');
  return 'Success';
}
