# Quick Start Guide

Get started with Rubric-to-Comment AI in 5 minutes!

## Step 1: Set Up the Add-on (2 min)

1. Open [Google Apps Script](https://script.google.com)
2. Click **"New Project"**
3. Name it "Rubric Feedback"
4. Delete the default code in `Code.gs`

## Step 2: Add the Code (2 min)

### Option A: Manual Copy (Recommended for first time)

1. Copy each file from this repository:
   - Click **"+"** → **"Script"** for each `.gs` file
   - Click **"+"** → **"HTML"** for each `.html` file

2. Copy these files in order:
   - `Code.gs`
   - `RubricManager.gs`
   - `LLMService.gs`
   - `CommentService.gs`
   - `Sidebar.html`
   - `Settings.html`

3. Enable manifest:
   - Click ⚙️ **Project Settings**
   - Check **"Show appsscript.json manifest file in editor"**
   - Replace manifest content with `appsscript.json`

### Option B: Use clasp (For developers)

```bash
# Install clasp
npm install -g @google/clasp

# Login
clasp login

# Create new project
clasp create --type standalone --title "Rubric Feedback"

# Push code
clasp push
```

## Step 3: Test It (1 min)

1. In Apps Script editor, select `testSetup` function
2. Click **Run** (▶️)
3. Click **Review permissions** → Choose your account
4. Click **Advanced** → **Go to Rubric Feedback (unsafe)**
5. Click **Allow**

You should see "Execution completed" ✓

## Step 4: Try It Out!

### Create a Test Document

1. Open [Google Docs](https://docs.google.com)
2. Create a new document
3. Paste some sample student writing (or use the example below)

### Configure API

1. In your doc, click **Extensions** → **Rubric Feedback** → **Settings**
2. Choose provider: **OpenAI** or **Gemini**
3. Enter your API key:
   - OpenAI: Get from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
   - Gemini: Get from [makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
4. Click **Save**

### Create Your First Rubric

1. Click **Extensions** → **Rubric Feedback** → **Open Rubric Feedback**
2. Select **"Create new rubric..."**
3. Enter:
   - **Name**: "Quick Test Rubric"
   - **Criterion 1**:
     - Label: "Clarity"
     - Description: "Ideas are clearly expressed"
   - **Criterion 2**:
     - Label: "Organization"
     - Description: "Content is well organized"
4. Choose **Tone**: Supportive
5. Click **Save Rubric**

### Generate Feedback

1. Click **"Generate Feedback"**
2. Wait 10-20 seconds
3. Review the comments and summary
4. Click **Accept** on comments you like
5. Click **Insert Accepted Feedback**

Done! 🎉

## Sample Student Essay

Use this for testing:

```
The Benefits of Reading

Reading is important for many reasons. First, it helps us learn new things.
When we read books, we discover information about the world. Second, reading
improves our vocabulary. We encounter new words and learn what they mean.

Another benefit of reading is that it exercises our imagination. When we read
stories, we picture the characters and settings in our minds. This helps
develop creativity.

In conclusion, everyone should read more because it helps us learn, improves
our language skills, and stimulates our imagination.
```

## Troubleshooting

### "API key not set"
→ Go to Settings and add your key

### "Execution timeout"
→ Document too long. Try with shorter text first.

### Can't find Extensions menu
→ Refresh the document, or wait a few minutes after setup

### Authorization issues
→ Make sure you clicked "Allow" on all permissions

## Next Steps

- Create rubrics for your actual assignments
- Customize tone and comment style
- Try with real student work
- Check out example rubrics in `examples/` folder

## Pro Tips

1. **Save time**: Create rubric templates for recurring assignments
2. **Customize**: Always review and edit AI suggestions
3. **Cost control**: Use Gemini for testing (free tier)
4. **Better results**: More specific rubric criteria = better feedback

## Get Help

- Read the full [README.md](README.md)
- Check [DEVELOPMENT.md](DEVELOPMENT.md) for technical details
- Report issues on GitHub

---

**You're ready to start!** 🚀
