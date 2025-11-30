/**
 * LLMService.gs
 * Handles LLM API integration for generating feedback
 */

/**
 * Generate feedback using OpenAI API
 */
function generateFeedbackOpenAI(documentText, rubric, settings) {
  try {
    var apiKey = getApiKey('openai');
    if (!apiKey) {
      throw new Error('OpenAI API key not set. Please add it in Settings.');
    }

    var prompt = buildPrompt(documentText, rubric, settings);

    var payload = {
      model: settings.model || 'gpt-4',
      messages: [
        {
          role: 'system',
          content: 'You are an expert educational feedback assistant. Provide constructive, rubric-aligned feedback for student work.'
        },
        {
          role: 'user',
          content: prompt
        }
      ],
      temperature: 0.7,
      max_tokens: 2000
    };

    var options = {
      method: 'post',
      contentType: 'application/json',
      headers: {
        'Authorization': 'Bearer ' + apiKey
      },
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    };

    var response = UrlFetchApp.fetch('https://api.openai.com/v1/chat/completions', options);
    var result = JSON.parse(response.getContentText());

    if (result.error) {
      throw new Error(result.error.message);
    }

    var feedbackText = result.choices[0].message.content;
    return parseFeedback(feedbackText);

  } catch (error) {
    Logger.log('Error generating feedback: ' + error.toString());
    throw error;
  }
}

/**
 * Generate feedback using Google Gemini API
 */
function generateFeedbackGemini(documentText, rubric, settings) {
  try {
    var apiKey = getApiKey('gemini');
    if (!apiKey) {
      throw new Error('Gemini API key not set. Please add it in Settings.');
    }

    var prompt = buildPrompt(documentText, rubric, settings);

    var payload = {
      contents: [{
        parts: [{
          text: prompt
        }]
      }],
      generationConfig: {
        temperature: 0.7,
        maxOutputTokens: 2000
      }
    };

    var options = {
      method: 'post',
      contentType: 'application/json',
      headers: {
        'x-goog-api-key': apiKey
      },
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    };

    var url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent';
    var response = UrlFetchApp.fetch(url, options);
    var result = JSON.parse(response.getContentText());

    if (result.error) {
      throw new Error(result.error.message);
    }

    var feedbackText = result.candidates[0].content.parts[0].text;
    return parseFeedback(feedbackText);

  } catch (error) {
    Logger.log('Error generating feedback: ' + error.toString());
    throw error;
  }
}

/**
 * Build the prompt for the LLM
 */
function buildPrompt(documentText, rubric, settings) {
  var tone = settings.tone || 'supportive';
  var style = settings.commentStyle || 'paragraphs';

  var prompt = 'You are providing feedback on student work using the following rubric:\n\n';

  // Add rubric criteria
  prompt += 'RUBRIC: ' + rubric.name + '\n';
  for (var i = 0; i < rubric.criteria.length; i++) {
    var criterion = rubric.criteria[i];
    prompt += '\n' + (i + 1) + '. ' + criterion.label;
    if (criterion.weight) {
      prompt += ' (Weight: ' + criterion.weight + ')';
    }
    prompt += '\n   ' + criterion.description + '\n';
  }

  prompt += '\nTONE: ' + tone + '\n';
  prompt += 'COMMENT STYLE: ' + style + '\n\n';

  prompt += 'STUDENT WORK:\n' + documentText + '\n\n';

  prompt += 'Please provide:\n';
  prompt += '1. INLINE COMMENTS: Specific feedback for different sections, formatted as:\n';
  prompt += '   COMMENT[Section text snippet]: Your feedback here\n\n';
  prompt += '2. SUMMARY: Overall assessment with:\n';
  prompt += '   - Strengths (bullet points)\n';
  prompt += '   - Areas for improvement (bullet points)\n';
  prompt += '   - Overall score/grade (if applicable)\n';

  return prompt;
}

/**
 * Parse LLM response into structured feedback
 */
function parseFeedback(feedbackText) {
  var feedback = {
    comments: [],
    summary: {
      strengths: [],
      improvements: [],
      grade: ''
    }
  };

  // Parse inline comments
  var commentRegex = /COMMENT\[(.*?)\]:\s*(.*?)(?=\n\n|COMMENT\[|SUMMARY:|$)/gs;
  var match;

  while ((match = commentRegex.exec(feedbackText)) !== null) {
    feedback.comments.push({
      anchor: match[1].trim(),
      text: match[2].trim(),
      accepted: false
    });
  }

  // Parse summary section
  var summaryMatch = feedbackText.match(/SUMMARY:([\s\S]*?)$/);
  if (summaryMatch) {
    var summaryText = summaryMatch[1];

    // Extract strengths
    var strengthsMatch = summaryText.match(/Strengths:?([\s\S]*?)(?=Areas for improvement:|Overall score:|$)/i);
    if (strengthsMatch) {
      var strengthsText = strengthsMatch[1];
      var strengthLines = strengthsText.match(/[-•]\s*(.*)/g);
      if (strengthLines) {
        feedback.summary.strengths = strengthLines.map(function(line) {
          return line.replace(/^[-•]\s*/, '').trim();
        });
      }
    }

    // Extract improvements
    var improvementsMatch = summaryText.match(/Areas for improvement:?([\s\S]*?)(?=Overall score:|$)/i);
    if (improvementsMatch) {
      var improvementsText = improvementsMatch[1];
      var improvementLines = improvementsText.match(/[-•]\s*(.*)/g);
      if (improvementLines) {
        feedback.summary.improvements = improvementLines.map(function(line) {
          return line.replace(/^[-•]\s*/, '').trim();
        });
      }
    }

    // Extract grade
    var gradeMatch = summaryText.match(/Overall score[\/:]?\s*(.*)/i);
    if (gradeMatch) {
      feedback.summary.grade = gradeMatch[1].trim();
    }
  }

  return feedback;
}

/**
 * Get API key from user properties
 */
function getApiKey(provider) {
  var userProps = PropertiesService.getUserProperties();
  return userProps.getProperty(provider + '_api_key');
}

/**
 * Save API key to user properties
 */
function saveApiKey(provider, apiKey) {
  var userProps = PropertiesService.getUserProperties();
  userProps.setProperty(provider + '_api_key', apiKey);
  return { success: true };
}

/**
 * Main function to generate feedback (routes to appropriate provider)
 */
function generateFeedback(rubric, settings) {
  try {
    var documentText = getDocumentText();

    if (!documentText || documentText.trim().length === 0) {
      throw new Error('Document is empty. Please add some content first.');
    }

    var provider = settings.provider || 'openai';

    var feedback;
    if (provider === 'gemini') {
      feedback = generateFeedbackGemini(documentText, rubric, settings);
    } else {
      feedback = generateFeedbackOpenAI(documentText, rubric, settings);
    }

    return { success: true, feedback: feedback };

  } catch (error) {
    Logger.log('Error in generateFeedback: ' + error.toString());
    return { success: false, error: error.toString() };
  }
}
