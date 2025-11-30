/**
 * CommentService.gs
 * Handles inserting comments into Google Docs
 */

/**
 * Insert a comment at a specific location in the document
 */
function insertComment(anchorText, commentText) {
  try {
    var doc = DocumentApp.getActiveDocument();
    var body = doc.getBody();

    // Find the anchor text in the document
    var searchResult = body.findText(anchorText);

    if (!searchResult) {
      Logger.log('Could not find anchor text: ' + anchorText);
      return { success: false, error: 'Text not found in document' };
    }

    var element = searchResult.getElement();
    var startOffset = searchResult.getStartOffset();
    var endOffset = searchResult.getEndOffsetInclusive();

    // Get the text element
    var textElement = element.asText();

    // Add comment to the range
    // Note: Google Apps Script doesn't support adding comments directly via API
    // We'll add a suggestion instead, or highlight the text
    // For now, we'll insert the comment as a footnote or annotation

    // Alternative: Insert as a highlighted note
    textElement.setBackgroundColor(startOffset, endOffset, '#FFFF00');

    // Insert comment text as a footnote
    var position = doc.newPosition(element, endOffset + 1);

    // Since we can't add comments directly, we'll add them to a comment section
    // at the end or use the suggestion mode

    return {
      success: true,
      message: 'Text highlighted. Comment: ' + commentText
    };

  } catch (error) {
    Logger.log('Error inserting comment: ' + error.toString());
    return { success: false, error: error.toString() };
  }
}

/**
 * Insert all accepted comments into the document
 */
function insertAcceptedComments(comments) {
  try {
    var results = [];
    var doc = DocumentApp.getActiveDocument();

    // First, add a "Feedback Comments" section at the end
    var body = doc.getBody();
    body.appendParagraph('\n--- FEEDBACK COMMENTS ---').setHeading(DocumentApp.ParagraphHeading.HEADING2);

    for (var i = 0; i < comments.length; i++) {
      if (comments[i].accepted) {
        var comment = comments[i];

        // Highlight the text in the document
        var searchResult = body.findText(comment.anchor);
        if (searchResult) {
          var element = searchResult.getElement().asText();
          var startOffset = searchResult.getStartOffset();
          var endOffset = searchResult.getEndOffsetInclusive();

          // Highlight in yellow
          element.setBackgroundColor(startOffset, endOffset, '#FFFF00');

          // Add reference number
          var refNum = '[' + (i + 1) + ']';
          element.insertText(endOffset + 1, refNum);
          element.setForegroundColor(endOffset + 1, endOffset + refNum.length, '#FF0000');
        }

        // Add comment to the feedback section
        var commentPara = body.appendParagraph('[' + (i + 1) + '] ' + comment.text);
        commentPara.setIndentFirstLine(0);
        commentPara.setIndentStart(18);

        // Add the quoted text
        var quotePara = body.appendParagraph('   "' + comment.anchor + '"');
        quotePara.setItalic(true);
        quotePara.setForegroundColor('#666666');

        body.appendParagraph(''); // spacing

        results.push({ success: true, index: i });
      }
    }

    return { success: true, count: results.length };

  } catch (error) {
    Logger.log('Error inserting comments: ' + error.toString());
    return { success: false, error: error.toString() };
  }
}

/**
 * Insert summary feedback at the end of the document
 */
function insertSummary(summary) {
  try {
    var doc = DocumentApp.getActiveDocument();
    var body = doc.getBody();

    // Add summary section
    body.appendParagraph('\n--- OVERALL FEEDBACK ---').setHeading(DocumentApp.ParagraphHeading.HEADING2);

    // Strengths
    if (summary.strengths && summary.strengths.length > 0) {
      body.appendParagraph('Strengths:').setBold(true);
      for (var i = 0; i < summary.strengths.length; i++) {
        var strengthPara = body.appendParagraph('• ' + summary.strengths[i]);
        strengthPara.setIndentFirstLine(0);
        strengthPara.setIndentStart(18);
      }
      body.appendParagraph('');
    }

    // Areas for improvement
    if (summary.improvements && summary.improvements.length > 0) {
      body.appendParagraph('Areas for Improvement:').setBold(true);
      for (var i = 0; i < summary.improvements.length; i++) {
        var improvementPara = body.appendParagraph('• ' + summary.improvements[i]);
        improvementPara.setIndentFirstLine(0);
        improvementPara.setIndentStart(18);
      }
      body.appendParagraph('');
    }

    // Overall grade
    if (summary.grade) {
      var gradePara = body.appendParagraph('Overall Assessment: ' + summary.grade);
      gradePara.setBold(true);
    }

    return { success: true };

  } catch (error) {
    Logger.log('Error inserting summary: ' + error.toString());
    return { success: false, error: error.toString() };
  }
}

/**
 * Insert complete feedback (comments + summary)
 */
function insertFeedback(feedback) {
  try {
    // Insert accepted comments
    var commentResult = insertAcceptedComments(feedback.comments);

    // Insert summary
    var summaryResult = insertSummary(feedback.summary);

    if (commentResult.success && summaryResult.success) {
      return {
        success: true,
        message: 'Feedback inserted successfully. ' + commentResult.count + ' comments added.'
      };
    } else {
      throw new Error('Error inserting feedback');
    }

  } catch (error) {
    Logger.log('Error in insertFeedback: ' + error.toString());
    return { success: false, error: error.toString() };
  }
}

/**
 * Clear all highlights from the document
 */
function clearHighlights() {
  try {
    var doc = DocumentApp.getActiveDocument();
    var body = doc.getBody();
    var text = body.editAsText();

    // Remove all background colors
    text.setBackgroundColor(null);

    return { success: true };

  } catch (error) {
    Logger.log('Error clearing highlights: ' + error.toString());
    return { success: false, error: error.toString() };
  }
}
