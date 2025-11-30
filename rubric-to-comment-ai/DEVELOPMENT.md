# Development Guide

## Local Development with clasp

[clasp](https://github.com/google/clasp) (Command Line Apps Script Projects) allows you to develop locally and push to Google Apps Script.

### Setup clasp

```bash
# Install clasp globally
npm install -g @google/clasp

# Login to your Google account
clasp login

# Create a new Apps Script project (or clone existing)
clasp create --type standalone --title "Rubric Feedback Add-on"

# Or clone an existing project
clasp clone <scriptId>
```

### Development Workflow

```bash
# Push local changes to Apps Script
clasp push

# Pull remote changes to local
clasp pull

# Open the project in Apps Script editor
clasp open

# Deploy
clasp deploy
```

### Project Structure

```
rubric-to-comment-ai/
├── Code.gs                 # Main entry point & menu setup
├── RubricManager.gs        # Rubric CRUD operations
├── LLMService.gs          # OpenAI/Gemini API integration
├── CommentService.gs      # Document comment insertion
├── Sidebar.html           # Main UI sidebar
├── Settings.html          # Settings dialog
├── appsscript.json        # Project manifest
├── .clasp.json            # clasp configuration
├── README.md              # User documentation
└── DEVELOPMENT.md         # This file
```

## Code Architecture

### Flow Overview

```
User Opens Sidebar
    ↓
Select/Create Rubric
    ↓
Click "Generate Feedback"
    ↓
getDocumentText() → Extract doc content
    ↓
generateFeedback() → Call LLM API
    ↓
parseFeedback() → Parse AI response
    ↓
Display in Review UI
    ↓
Teacher Reviews/Edits
    ↓
insertFeedback() → Write to document
```

### Key Functions

#### Code.gs
- `onOpen()` - Sets up add-on menu
- `showSidebar()` - Opens main sidebar
- `getDocumentText()` - Extracts document content
- `getDocumentStructure()` - Gets paragraph-level structure

#### RubricManager.gs
- `saveRubric(rubric)` - Saves rubric to user properties
- `getAllRubrics()` - Retrieves all saved rubrics
- `getRubric(id)` - Gets specific rubric
- `deleteRubric(id)` - Deletes rubric
- `validateRubric(rubric)` - Validates rubric structure

#### LLMService.gs
- `generateFeedback(rubric, settings)` - Main entry point
- `generateFeedbackOpenAI()` - OpenAI API call
- `generateFeedbackGemini()` - Gemini API call
- `buildPrompt()` - Constructs LLM prompt
- `parseFeedback()` - Parses LLM response

#### CommentService.gs
- `insertFeedback(feedback)` - Main insertion function
- `insertAcceptedComments()` - Adds comment section
- `insertSummary()` - Adds summary section
- `clearHighlights()` - Removes highlights

### Data Storage

Uses `PropertiesService.getUserProperties()`:

```javascript
// Storage structure
{
  "rubrics": "{...}",           // JSON string of all rubrics
  "openai_api_key": "sk-...",   // OpenAI API key
  "gemini_api_key": "AI..."     // Gemini API key
}
```

**Limits**:
- 500KB total storage per user
- 9KB per property
- ~10-15 detailed rubrics typically fit

### UI State Management

The sidebar has three views:
1. `main-view` - Rubric selection/creation
2. `loading-view` - Feedback generation
3. `review-view` - Comment review/editing

State switching via `showView(viewId)`.

## Testing

### Manual Testing

1. **Test Rubric Creation**
   - Create rubric with 1-5 criteria
   - Verify save/load
   - Test validation

2. **Test Feedback Generation**
   - Test with short doc (~200 words)
   - Test with long doc (~2000 words)
   - Test with empty doc (should error)

3. **Test Comment Review**
   - Accept/edit/discard comments
   - Verify summary display
   - Test insertion

4. **Test API Integration**
   - Test with OpenAI
   - Test with Gemini
   - Test with invalid API key
   - Test with network error

### Unit Testing

Apps Script doesn't have built-in testing, but you can:

1. Use `Logger.log()` for debugging
2. Create test functions:

```javascript
function testRubricValidation() {
  var validRubric = {
    name: "Test",
    criteria: [{label: "A", description: "B"}]
  };
  var result = validateRubric(validRubric);
  Logger.log(result.valid); // should be true
}
```

3. Run via Apps Script editor

### Integration Testing

Test full workflow:
1. Create test Google Doc with sample essay
2. Create test rubric
3. Generate feedback
4. Verify output quality

## API Integration Details

### OpenAI API

**Endpoint**: `https://api.openai.com/v1/chat/completions`

**Request**:
```javascript
{
  model: "gpt-4",
  messages: [
    {role: "system", content: "..."},
    {role: "user", content: "..."}
  ],
  temperature: 0.7,
  max_tokens: 2000
}
```

**Response Parsing**:
```javascript
result.choices[0].message.content
```

### Gemini API

**Endpoint**: `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent`

**Request**:
```javascript
{
  contents: [{
    parts: [{text: "..."}]
  }],
  generationConfig: {
    temperature: 0.7,
    maxOutputTokens: 2000
  }
}
```

**Response Parsing**:
```javascript
result.candidates[0].content.parts[0].text
```

## Prompt Engineering

Current prompt structure:

```
You are providing feedback on student work using the following rubric:

RUBRIC: [name]
1. [criterion label] (Weight: [weight])
   [description]
...

TONE: [supportive/neutral/direct]
COMMENT STYLE: [paragraphs/bullets]

STUDENT WORK:
[document text]

Please provide:
1. INLINE COMMENTS: Specific feedback for different sections, formatted as:
   COMMENT[Section text snippet]: Your feedback here

2. SUMMARY: Overall assessment with:
   - Strengths (bullet points)
   - Areas for improvement (bullet points)
   - Overall score/grade (if applicable)
```

### Optimization Tips

- Keep rubric descriptions concise but specific
- Use consistent formatting in criteria
- Test different temperature values (0.5-0.9)
- Adjust max_tokens based on document length

## Performance Optimization

### Current Bottlenecks

1. **LLM API calls** - 5-30 seconds
2. **Document parsing** - <1 second
3. **Comment insertion** - 1-3 seconds

### Optimization Strategies

1. **Caching**
   - Cache rubric prompts
   - Store recent feedback for review

2. **Batch Processing** (future)
   - Process multiple docs async
   - Queue management

3. **Progressive Loading**
   - Show partial results as they arrive
   - Stream LLM responses

## Security Considerations

### API Key Storage

- Keys stored in `PropertiesService` (user-specific)
- Never logged or exposed in UI
- Not accessible to other users

### Input Validation

- Sanitize rubric inputs
- Escape HTML in feedback display
- Validate API responses

### Rate Limiting

- Implement request throttling
- Handle API rate limit errors gracefully
- Add retry logic with exponential backoff

## Deployment Checklist

Before deploying:

- [ ] Test all core features
- [ ] Test both OpenAI and Gemini
- [ ] Verify error handling
- [ ] Check API key security
- [ ] Test on different document sizes
- [ ] Review OAuth scopes
- [ ] Update version number
- [ ] Write release notes

## Common Issues & Solutions

### Issue: "Script timeout"
**Solution**: Reduce document size or optimize LLM call

### Issue: "Storage limit exceeded"
**Solution**: Delete old rubrics or implement pagination

### Issue: "API rate limit"
**Solution**: Add exponential backoff, show user-friendly message

### Issue: "Comments not inserting"
**Solution**: Check OAuth permissions, verify document edit access

## Contributing

To contribute:

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

### Code Style

- Use descriptive variable names
- Add JSDoc comments for functions
- Keep functions focused and small
- Handle errors gracefully

### Git Workflow

```bash
git checkout -b feature/your-feature
git commit -m "Add: your feature description"
git push origin feature/your-feature
```

## Resources

- [Google Apps Script Docs](https://developers.google.com/apps-script)
- [Google Docs Service](https://developers.google.com/apps-script/reference/document)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Gemini API Docs](https://ai.google.dev/docs)
- [clasp Documentation](https://github.com/google/clasp)

## Version History

### v1.0.0 (2024-01-15)
- Initial release
- Basic rubric management
- OpenAI & Gemini integration
- Comment review system
- Document feedback insertion
