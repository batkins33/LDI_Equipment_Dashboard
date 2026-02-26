# Lindamood Slides Bot

A Playwright-based automation that creates Google Slides presentations using branding extracted from [lindamood.net](https://www.lindamood.net).

## Overview

This automation:
1. **Authenticates** to Google (one-time interactive login)
2. **Extracts** Lindamood branding (logo + color palette) from their website
3. **Builds** a Google Slides deck titled "Lindamood Automation Opportunity"
4. **Exports** PDF + screenshots as build artifacts
5. **Tests** the entire workflow end-to-end

## Prerequisites

- **Node.js** 18+ (tested with v20)
- **npm** 9+
- A **Google Account** with Google Drive/Slides access

## Installation

```bash
cd automation/lindamood-slides-bot
npm install
```

This will also download Playwright browsers automatically via the `postinstall` hook.

## One-Time Setup

### 1. Authenticate to Google

The automation needs to authenticate to Google to create slides. Run:

```bash
npm run auth
```

This will:
- Open a headed Chrome browser
- Navigate to Google Drive
- Wait for you to complete login (including any MFA)
- Save your session to `.auth/storageState.json`

**Important:** Keep `.auth/` gitignored - it contains your session credentials.

### 2. Troubleshooting Auth

| Issue | Solution |
|-------|----------|
| "Already logged in" | Clear browser cookies/data before running |
| MFA not completing | Complete MFA in the opened browser, then wait for script to detect success |
| Timeout waiting for Drive | Check console for "Drive detected" message, press Ctrl+C if stuck |
| `.auth/` not created | Create it manually: `mkdir -p .auth` |

## Usage

### Extract Branding

Extract logo and color palette from lindamood.net:

```bash
npm run brand:extract
```

Outputs:
- `brand/brand.json` - Color palette and metadata
- `brand/logo.png` - Downloaded logo
- `artifacts/screenshots/site_*.png` - Evidence screenshots

### Build Deck

Create the Google Slides presentation:

```bash
npm run deck:build
```

Outputs:
- `artifacts/deck_url.txt` - URL to the created deck
- `artifacts/screenshots/deck_final.png` - Screenshot of final deck
- Directly creates slides in your Google Drive

### Run E2E Tests

Full workflow validation (requires completed auth):

```bash
npm test
```

This runs `tests/build_deck.spec.ts` which:
- Validates `storageState.json` exists
- Extracts brand (or validates existing)
- Builds the deck
- Verifies outputs

## Project Structure

```
automation/lindamood-slides-bot/
├── .auth/                    # Gitignored - Google session storage
│   └── storageState.json     # Your authenticated Google session
├── brand/
│   ├── extract_brand.ts      # Brand extraction script
│   ├── brand.json            # Generated brand palette
│   └── logo.png              # Downloaded logo
├── content/
│   └── deck_outline.json     # Slide content source of truth
├── slides/
│   ├── auth.ts               # Google authentication script
│   └── build_deck.ts         # Deck creation script
├── tests/
│   └── build_deck.spec.ts    # E2E test suite
├── artifacts/                # Generated build outputs
│   ├── deck_url.txt          # URL to created deck
│   ├── lindamood_opportunity_deck.pdf  # Exported PDF
│   └── screenshots/          # Build screenshots
├── playwright.config.ts        # Playwright configuration
├── package.json
├── tsconfig.json
├── .gitignore
└── README.md
```

## Common Failures & Solutions

### Google UI Changes

If selectors break due to Google UI updates:

1. Check the error screenshot in `test-results/`
2. Update locators in `slides/build_deck.ts` to use role/text locators
3. Prefer keyboard shortcuts over brittle selectors

### Export/Download Blocked

If PDF export fails:

1. Ensure you're not in Incognito/Private browsing
2. Check that downloads are allowed in browser settings
3. Verify `playwright.config.ts` has proper download behavior configured

### Website Blocks Automation

If lindamood.net blocks Playwright:

1. Check `artifacts/screenshots/site_home.png` for blocking evidence
2. The script includes standard user-agent and waits for network idle
3. Review `brand/extract_brand.ts` HTML capture for debugging

## Re-Running

The automation is designed to be **re-runnable**:

- Each `deck:build` creates a **new** deck (no overwrites)
- Auth is persisted across runs
- Brand extraction can be re-run to pick up website changes

## License

MIT
