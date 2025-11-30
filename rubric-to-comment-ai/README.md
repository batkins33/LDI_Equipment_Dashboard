# Rubric-to-Comment AI

A Google Docs Add-on that transforms grading rubrics and student drafts into personalized, rubric-aligned feedback with inline comments and summary assessments.

## Overview

**One-liner**: Turn a grading rubric + a student draft into personalized inline comments and summary feedback in Google Docs.

**Target User**: Middle/high school & college teachers using Google Docs / Classroom.

**Job-to-be-done**: "I want to give high-quality, rubric-aligned feedback in minutes instead of hours."

## Features

### Core v1 Features

1. **Rubric Management**
   - Create and save multiple rubrics with custom criteria
   - Define criterion labels, descriptions, and weights
   - Customize tone (supportive/neutral/direct) and comment style (paragraphs/bullets)
   - Quickly reuse saved rubrics across different assignments

2. **AI-Powered Feedback Generation**
   - Analyzes student work against rubric criteria
   - Generates targeted inline comments for specific sections
   - Provides overall summary with strengths and areas for improvement
   - Optional grade/assessment suggestion

3. **Teacher Review & Control**
   - Review all AI-generated comments before insertion
   - Accept, edit, or discard individual comments
   - No automatic posting - full teacher oversight
   - Preview mode ensures quality control

4. **Document Integration**
   - Highlights referenced text in the document
   - Inserts comments as a structured feedback section
   - Maintains document formatting
   - Clear visual organization of feedback

## Technology Stack

- **Platform**: Google Docs Add-on (Google Workspace Add-on)
- **Backend**: Google Apps Script (JavaScript)
- **LLM Integration**: OpenAI GPT-4 or Google Gemini API
- **Storage**: PropertiesService (user preferences & saved rubrics)

## Installation & Setup

### Prerequisites

- Google account with access to Google Docs
- API key from either:
  - [OpenAI](https://platform.openai.com/api-keys) (recommended: GPT-4)
  - [Google AI Studio](https://makersuite.google.com/app/apikey) (Gemini)

### Installation Steps

1. **Create a New Apps Script Project**
   - Open [Google Apps Script](https://script.google.com)
   - Click "New Project"
   - Give it a name (e.g., "Rubric Feedback Add-on")

2. **Copy the Code Files**
   - Delete the default `Code.gs` content
   - Copy all `.gs` files from this repository into your project:
     - `Code.gs`
     - `RubricManager.gs`
     - `LLMService.gs`
     - `CommentService.gs`
   - Create HTML files by clicking the `+` button:
     - `Sidebar.html`
     - `Settings.html`
   - Copy the `appsscript.json` manifest

3. **Configure the Manifest**
   - Click on "Project Settings" (gear icon)
   - Check "Show appsscript.json manifest file in editor"
   - Replace the manifest content with the provided `appsscript.json`

4. **Test the Add-on**
   - Click "Run" → Select `testSetup` function
   - Authorize the add-on (first time only)
   - Open a Google Doc
   - Click "Extensions" → "Rubric Feedback Add-on" → "Open Rubric Feedback"

5. **Configure API Key**
   - In the sidebar, click "Settings"
   - Choose your LLM provider (OpenAI or Gemini)
   - Enter your API key
   - Click "Save API Key"

### Deployment (Optional)

To use across multiple documents:

1. Click "Deploy" → "New deployment"
2. Select type: "Add-on"
3. Configure:
   - **Description**: "Rubric-based feedback generator"
   - **Add-on title**: "Rubric Feedback"
   - **Short description**: Brief description
4. Click "Deploy"

For organization-wide deployment, see [Google Workspace Marketplace](https://developers.google.com/workspace/marketplace).

## Usage Guide

### Creating a Rubric

1. Open the sidebar: Extensions → Rubric Feedback → Open Rubric Feedback
2. Select "Create new rubric..." from the dropdown
3. Enter:
   - **Rubric Name**: e.g., "Essay Rubric - Argumentative"
   - **Criteria**: Add one or more criteria
     - Label (e.g., "Thesis Statement")
     - Description (e.g., "Clear, arguable claim stated in introduction")
     - Weight (optional, e.g., "25%")
4. Choose:
   - **Tone**: Supportive, Neutral, or Direct
   - **Comment Style**: Paragraphs or Bullet Points
5. Click "Save Rubric"

### Generating Feedback

1. Open a student's Google Doc
2. Open the sidebar
3. Select a saved rubric
4. Click "Generate Feedback"
5. Wait for AI analysis (typically 10-30 seconds)

### Reviewing & Inserting Comments

1. Review the **Summary**:
   - Strengths
   - Areas for improvement
   - Overall assessment
2. Review individual **Comments**:
   - See which text each comment references
   - Click "Accept" to include in final feedback
   - Click "Edit" to modify the comment text
   - Click "Discard" to remove
3. Click "Insert Accepted Feedback" when ready
4. Comments will be added to the document with:
   - Highlighted references in yellow
   - Numbered comment markers
   - Organized feedback section at the end

### Best Practices

- **Rubric Quality**: More specific criteria = better feedback
- **Document Length**: Works best with 500-3000 word documents
- **Review Everything**: Always review AI comments before inserting
- **Edit Freely**: Customize AI suggestions to match your voice
- **Save Rubrics**: Create rubric templates for recurring assignments

## Data Model

### Rubric Structure
```javascript
{
  id: "uuid",
  name: "Essay Rubric",
  criteria: [
    {
      label: "Thesis Statement",
      description: "Clear, arguable claim",
      weight: "25%"
    },
    // ... more criteria
  ],
  tone: "supportive",
  commentStyle: "paragraphs",
  createdAt: "2024-01-15T10:30:00Z",
  updatedAt: "2024-01-15T10:30:00Z"
}
```

### Feedback Structure
```javascript
{
  comments: [
    {
      anchor: "Text snippet from document",
      text: "Feedback comment",
      accepted: true/false
    }
  ],
  summary: {
    strengths: ["Strength 1", "Strength 2"],
    improvements: ["Improvement 1", "Improvement 2"],
    grade: "Assessment/score"
  }
}
```

## API Costs & Limits

### OpenAI (GPT-4)
- ~$0.03-0.10 per feedback generation (depending on document length)
- Rate limits: 3 requests/minute (tier 1)

### Google Gemini
- Free tier: 60 requests/minute
- More economical for high-volume use

**Recommendation**: Start with Gemini for testing, upgrade to GPT-4 for production quality.

## Limitations (v1)

- No gradebook integration
- Single document processing (no batch mode)
- No analytics or usage tracking
- 9KB storage limit for saved rubrics (~10-15 detailed rubrics)
- Cannot add true Google Docs comments via API (uses alternative feedback section)

## Future Enhancements (Roadmap)

- [ ] Google Classroom integration
- [ ] Batch processing for multiple students
- [ ] Export feedback to CSV/Excel
- [ ] Comment history and revision tracking
- [ ] Custom prompt templates
- [ ] Integration with Google Forms for rubric creation
- [ ] Student-facing feedback view
- [ ] Analytics dashboard for teachers

## Troubleshooting

### "API key not set" error
- Go to Settings and enter your API key
- Ensure you selected the correct provider

### "Document is empty" error
- Make sure the document has text content
- The add-on analyzes body text only

### Slow performance
- Large documents (>3000 words) may take longer
- Check your internet connection
- Verify API rate limits haven't been exceeded

### Comments not appearing
- Ensure you clicked "Accept" on desired comments
- Check that you clicked "Insert Accepted Feedback"
- Refresh the document if needed

### Storage limit reached
- Delete old rubrics you no longer use
- Export important rubrics as text/JSON for backup

## Support & Contributing

For issues, questions, or feature requests:
- Open an issue in this repository
- Contact: [your-email@example.com]

## License

MIT License - See LICENSE file for details

## Acknowledgments

Built with:
- Google Apps Script
- OpenAI GPT-4 API
- Google Gemini API

---

**Version**: 1.0.0
**Last Updated**: 2024-01-15
**Author**: [Your Name]
