# Agent Setup: Automated UAT Testing for GUI Applications

**Purpose:** Complete, agent-executable instructions for setting up automated UAT testing for any GUI application (web, desktop, or hybrid).

**Target Audience:** AI development agents

**Execution Model:** Sequential setup with validation checkpoints

---

## Overview

This document provides complete instructions for setting up automated User Acceptance Testing (UAT) for GUI applications. It includes:

1. **Decision Framework** - How to choose the right testing approach
2. **Web GUI Testing** - Playwright-based automation
3. **Desktop GUI Testing** - PyAutoGUI/pytest-qt automation
4. **Hybrid Applications** - Combined testing strategies
5. **Complete Implementation** - All files, configurations, and workflows

---

## Part 1: Decision Framework - Choose Your Testing Strategy

### Step 1: Identify Your Application Type

Run this decision tree:

```
What type of GUI does your application have?

├─ Web-based (runs in browser)
│  ├─ Framework: React, Vue, Angular, Streamlit, Flask, Django, etc.
│  ├─ Access: http://localhost:PORT or https://domain.com
│  └─ **Use: Playwright** (see Part 2)
│
├─ Desktop GUI (native application)
│  ├─ Framework: tkinter, PyQt, wxPython, Kivy, etc.
│  ├─ Access: Executable file (.exe, .py, .app)
│  └─ **Use: PyAutoGUI + pytest-qt** (see Part 3)
│
├─ Hybrid (both web and desktop)
│  ├─ Example: Electron app, web app with desktop companion
│  └─ **Use: Both strategies** (see Part 4)
│
└─ CLI/API only (no GUI)
   └─ **Use: pytest + requests** (not covered here)
```

### Step 2: Determine Test Coverage Needs

For each GUI component, identify:

| Component Type | Test Approach | Tool |
|----------------|---------------|------|
| Web pages/routes | Navigation + interaction | Playwright |
| Web forms | Input validation + submission | Playwright |
| Web dashboards | Data display + updates | Playwright |
| Desktop windows | Window management + controls | PyAutoGUI |
| Desktop dialogs | Modal interactions | pytest-qt |
| Desktop menus | Menu navigation | PyAutoGUI |
| File uploads (web) | File input handling | Playwright |
| File dialogs (desktop) | Native file picker | PyAutoGUI |
| Drag & drop (web) | Mouse events | Playwright |
| Drag & drop (desktop) | Screen coordinates | PyAutoGUI |

### Step 3: Define Test Modes

Create these test modes for your application:

- **quick** - Critical pages/windows only (5-10 min)
- **full** - All GUI elements (30-60 min)
- **critical** - Production-critical paths only (15-20 min)
- **workflows** - End-to-end user journeys (20-30 min)

---

## Part 2: Web GUI Testing with Playwright

### Prerequisites Check

```bash
# Verify Node.js installed
node --version  # Should be 18+

# Verify Python installed
python --version  # Should be 3.8+

# Verify application can start
# Replace with your actual start command
python -m your_app.main  # or npm start, etc.
```

### Installation

```bash
# Create test directory structure
mkdir -p tests/e2e/playwright/{fixtures,helpers}
cd tests/e2e

# Initialize npm project
npm init -y

# Install Playwright
npm install --save-dev @playwright/test

# Install browsers
npx playwright install
```

### File 1: `tests/e2e/package.json`

```json
{
  "name": "your-app-e2e-tests",
  "version": "1.0.0",
  "description": "E2E tests using Playwright",
  "scripts": {
    "test": "playwright test",
    "test:headed": "playwright test --headed",
    "test:ui": "playwright test --ui",
    "test:debug": "playwright test --debug",
    "test:report": "playwright show-report",
    "install:browsers": "playwright install",
    "update:snapshots": "playwright test --update-snapshots"
  },
  "devDependencies": {
    "@playwright/test": "^1.58.2"
  }
}
```

### File 2: `tests/e2e/playwright/playwright.config.ts`

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: '.',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  
  reporter: [
    ['html', { outputFolder: 'artifacts/e2e/playwright-report' }],
    ['json', { outputFile: 'artifacts/e2e/playwright-results.json' }],
    ['junit', { outputFile: 'artifacts/e2e/playwright-junit.xml' }],
    process.env.CI ? ['dot'] : ['list']
  ],
  
  timeout: 30000,
  expect: { timeout: 5000 },
  
  use: {
    baseURL: 'http://localhost:8080',  // CHANGE THIS to your app's URL
    trace: 'on-first-retry',
    video: 'retain-on-failure',
    screenshot: 'only-on-failure',
    actionTimeout: 10000,
    navigationTimeout: 30000,
  },

  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],

  webServer: {
    command: 'python -m your_app.main',  // CHANGE THIS to your start command
    port: 8080,  // CHANGE THIS to your app's port
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
```

### File 3: `tests/e2e/playwright/fixtures/base.ts`

```typescript
import { test as base, expect } from '@playwright/test';
import path from 'path';

export interface TestFixtures {
  captureScreenshot: (name: string) => Promise<void>;
  waitForElement: (selector: string, timeout?: number) => Promise<void>;
}

export const test = base.extend<TestFixtures>({
  captureScreenshot: async ({ page }, use) => {
    const captureFunc = async (name: string) => {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const screenshotName = `${name}_${timestamp}`;
      
      await page.screenshot({
        path: `artifacts/e2e/screenshots/${screenshotName}.png`,
        fullPage: true,
      });
    };
    await use(captureFunc);
  },

  waitForElement: async ({ page }, use) => {
    const waitFunc = async (selector: string, timeout: number = 5000) => {
      await page.waitForSelector(selector, { timeout, state: 'visible' });
    };
    await use(waitFunc);
  },
});

export { expect };

// Centralized selectors - UPDATE THESE for your application
export const SELECTORS = {
  // Navigation
  HOME_LINK: 'a[href="/"]',
  DASHBOARD_LINK: 'a[href="/dashboard"]',
  
  // Forms
  SUBMIT_BUTTON: '#submit-btn',
  CANCEL_BUTTON: '#cancel-btn',
  
  // Common elements
  LOADING_SPINNER: '.loading-spinner',
  ERROR_MESSAGE: '.error-message',
  SUCCESS_MESSAGE: '.success-message',
  
  // ADD YOUR APPLICATION'S SELECTORS HERE
};
```

### File 4: `tests/e2e/playwright/test_critical_workflows.spec.ts`

```typescript
import { test, expect, SELECTORS } from './fixtures/base';

test.describe('Critical Workflows', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should load home page successfully', async ({ page, captureScreenshot }) => {
    // Step 1: Verify page loads
    await captureScreenshot('home_page_loaded');
    await expect(page.locator('h1')).toBeVisible();
    
    // Step 2: Verify critical elements present
    // ADD YOUR ASSERTIONS HERE
    await expect(page.locator(SELECTORS.SUBMIT_BUTTON)).toBeVisible();
    
    // Step 3: Check no errors
    await expect(page.locator(SELECTORS.ERROR_MESSAGE)).not.toBeVisible();
  });

  // ADD MORE WORKFLOW TESTS HERE
  // Template:
  test('should complete [workflow name]', async ({ page, captureScreenshot, waitForElement }) => {
    // Step 1: Navigate to starting point
    await page.goto('/your-page');
    await captureScreenshot('workflow_start');
    
    // Step 2: Perform actions
    await page.click(SELECTORS.SUBMIT_BUTTON);
    await waitForElement(SELECTORS.SUCCESS_MESSAGE);
    
    // Step 3: Verify outcome
    await captureScreenshot('workflow_complete');
    await expect(page.locator(SELECTORS.SUCCESS_MESSAGE)).toBeVisible();
  });
});
```

### File 5: `tests/e2e/playwright/test_error_scenarios.spec.ts`

```typescript
import { test, expect, SELECTORS } from './fixtures/base';

test.describe('Error Scenarios', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should handle invalid input gracefully', async ({ page, captureScreenshot }) => {
    // Step 1: Enter invalid data
    await page.fill('#input-field', 'INVALID_DATA');
    await captureScreenshot('invalid_input_entered');
    
    // Step 2: Submit
    await page.click(SELECTORS.SUBMIT_BUTTON);
    
    // Step 3: Verify error message
    await expect(page.locator(SELECTORS.ERROR_MESSAGE)).toBeVisible();
    await captureScreenshot('error_displayed');
  });

  // ADD MORE ERROR SCENARIO TESTS HERE
});
```

### Validation Checkpoint

```bash
# Run tests to verify setup
cd tests/e2e
npm test

# Expected output:
# - Tests execute
# - Screenshots captured in artifacts/e2e/screenshots/
# - Report generated in artifacts/e2e/playwright-report/
```

---

## Part 3: Desktop GUI Testing with PyAutoGUI + pytest-qt

### Prerequisites Check

```bash
# Verify Python installed
python --version  # Should be 3.8+

# Verify your desktop app can launch
python your_desktop_app.py  # or ./your_app.exe
```

### Installation

```bash
# Install testing dependencies
pip install pytest pytest-qt pyautogui pillow

# For Qt applications specifically
pip install pytest-qt PyQt5  # or PyQt6, PySide2, PySide6

# Create test directory
mkdir -p tests/gui_tests
```

### File 1: `tests/gui_tests/conftest.py`

```python
"""Pytest configuration for GUI tests."""
import pytest
import pyautogui
import time
from pathlib import Path

# Configure PyAutoGUI safety
pyautogui.FAILSAFE = True  # Move mouse to corner to abort
pyautogui.PAUSE = 0.5  # Pause between actions

@pytest.fixture(scope="session")
def screenshot_dir():
    """Create screenshot directory."""
    path = Path("artifacts/gui_tests/screenshots")
    path.mkdir(parents=True, exist_ok=True)
    return path

@pytest.fixture
def capture_screenshot(screenshot_dir):
    """Fixture to capture screenshots."""
    def _capture(name: str):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = screenshot_dir / filename
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)
        return filepath
    return _capture

@pytest.fixture
def wait_for_window():
    """Wait for window to appear."""
    def _wait(title: str, timeout: int = 10):
        start = time.time()
        while time.time() - start < timeout:
            windows = pyautogui.getWindowsWithTitle(title)
            if windows:
                return windows[0]
            time.sleep(0.5)
        raise TimeoutError(f"Window '{title}' not found within {timeout}s")
    return _wait

@pytest.fixture(scope="session")
def app_launcher():
    """Launch and cleanup desktop application."""
    import subprocess
    
    # CHANGE THIS to your app's launch command
    process = subprocess.Popen(['python', 'your_desktop_app.py'])
    
    # Wait for app to start
    time.sleep(2)
    
    yield process
    
    # Cleanup
    process.terminate()
    process.wait(timeout=5)
```

### File 2: `tests/gui_tests/test_desktop_workflows.py`

```python
"""Desktop GUI workflow tests using PyAutoGUI."""
import pytest
import pyautogui
import time

class TestDesktopWorkflows:
    """Test critical desktop GUI workflows."""
    
    def test_application_launches(self, app_launcher, wait_for_window, capture_screenshot):
        """Test that application launches successfully."""
        # Step 1: Wait for main window
        window = wait_for_window("Your App Title")  # CHANGE THIS
        assert window is not None
        
        # Step 2: Capture screenshot
        capture_screenshot("app_launched")
        
        # Step 3: Verify window is active
        window.activate()
        time.sleep(0.5)
        assert window.isActive
    
    def test_menu_navigation(self, app_launcher, wait_for_window, capture_screenshot):
        """Test menu navigation."""
        # Step 1: Activate window
        window = wait_for_window("Your App Title")  # CHANGE THIS
        window.activate()
        
        # Step 2: Click menu (using image recognition)
        # First, create reference images in tests/gui_tests/images/
        try:
            menu_location = pyautogui.locateOnScreen('tests/gui_tests/images/file_menu.png')
            if menu_location:
                pyautogui.click(menu_location)
                capture_screenshot("menu_opened")
        except pyautogui.ImageNotFoundException:
            pytest.skip("Menu image not found - create reference image first")
    
    def test_button_click_workflow(self, app_launcher, wait_for_window, capture_screenshot):
        """Test button click workflow."""
        # Step 1: Activate window
        window = wait_for_window("Your App Title")  # CHANGE THIS
        window.activate()
        time.sleep(0.5)
        
        # Step 2: Find and click button
        # Option A: Using image recognition
        try:
            button_location = pyautogui.locateOnScreen('tests/gui_tests/images/submit_button.png')
            if button_location:
                pyautogui.click(button_location)
                capture_screenshot("button_clicked")
                time.sleep(1)
        except pyautogui.ImageNotFoundException:
            pytest.skip("Button image not found")
        
        # Option B: Using coordinates (less reliable)
        # pyautogui.click(x=100, y=200)  # CHANGE coordinates
        
        # Step 3: Verify result
        # Check for success dialog, status change, etc.
        capture_screenshot("workflow_complete")

# ADD MORE WORKFLOW TESTS HERE
```

### File 3: `tests/gui_tests/test_qt_specific.py` (for Qt applications)

```python
"""Qt-specific GUI tests using pytest-qt."""
import pytest
from PyQt5.QtWidgets import QApplication, QPushButton, QLineEdit
from PyQt5.QtCore import Qt

# Import your application's main window
# from your_app.main_window import MainWindow

@pytest.fixture
def app(qtbot):
    """Create application instance."""
    # CHANGE THIS to your app's main window class
    # window = MainWindow()
    # qtbot.addWidget(window)
    # window.show()
    # return window
    pass

def test_button_click(app, qtbot):
    """Test button click using pytest-qt."""
    # Find button by object name
    button = app.findChild(QPushButton, "submitButton")  # CHANGE THIS
    assert button is not None
    
    # Click button
    qtbot.mouseClick(button, Qt.LeftButton)
    
    # Wait for signal or state change
    # qtbot.waitSignal(app.dataProcessed, timeout=5000)
    
    # Verify result
    # assert app.status_label.text() == "Success"

def test_text_input(app, qtbot):
    """Test text input using pytest-qt."""
    # Find input field
    input_field = app.findChild(QLineEdit, "nameInput")  # CHANGE THIS
    assert input_field is not None
    
    # Enter text
    qtbot.keyClicks(input_field, "Test Input")
    
    # Verify
    assert input_field.text() == "Test Input"

# ADD MORE QT-SPECIFIC TESTS HERE
```

### File 4: `tests/gui_tests/README.md`

```markdown
# Desktop GUI Testing Setup

## Creating Reference Images

For PyAutoGUI image recognition:

1. Launch your application
2. Take screenshots of UI elements:
   ```python
   import pyautogui
   
   # Position mouse over element, then:
   region = pyautogui.screenshot(region=(x, y, width, height))
   region.save('tests/gui_tests/images/element_name.png')
   ```

3. Store images in `tests/gui_tests/images/`

## Running Tests

```bash
# Run all GUI tests
pytest tests/gui_tests/ -v

# Run specific test
pytest tests/gui_tests/test_desktop_workflows.py::TestDesktopWorkflows::test_application_launches -v

# Run with screenshots
pytest tests/gui_tests/ -v --capture=no
```

## Troubleshooting

- **Image not found**: Recreate reference images at current screen resolution
- **Window not found**: Check window title matches exactly
- **Timing issues**: Increase sleep times or timeouts
- **Mouse/keyboard not working**: Check PyAutoGUI FAILSAFE is enabled
```

### Validation Checkpoint

```bash
# Create reference images first
python -c "import pyautogui; pyautogui.screenshot().save('test.png')"

# Run tests
pytest tests/gui_tests/ -v

# Expected output:
# - Tests execute
# - Screenshots captured in artifacts/gui_tests/screenshots/
# - Pass/fail results displayed
```

---

## Part 4: Hybrid Applications (Web + Desktop)

For applications with both web and desktop components:

### Strategy

1. **Separate test suites** - Keep web and desktop tests separate
2. **Shared fixtures** - Use common setup/teardown
3. **Unified reporting** - Combine results

### File: `tests/conftest.py` (shared)

```python
"""Shared pytest configuration."""
import pytest
from pathlib import Path

@pytest.fixture(scope="session")
def artifacts_dir():
    """Create artifacts directory."""
    path = Path("artifacts/tests")
    path.mkdir(parents=True, exist_ok=True)
    return path

@pytest.fixture(scope="session")
def test_data_dir():
    """Test data directory."""
    return Path("tests/fixtures")

# Add shared fixtures here
```

### Running Combined Tests

```bash
# Run all tests (web + desktop)
pytest tests/ -v

# Run only web tests
pytest tests/e2e/ -v

# Run only desktop tests
pytest tests/gui_tests/ -v

# Generate combined report
pytest tests/ --html=artifacts/tests/combined_report.html
```

---

## Part 5: Complete UAT Automation Framework

### File: `tools/uat/uat_automation.py`

```python
"""UAT Automation Framework - Universal GUI Testing."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestStatus(Enum):
    """Test execution status."""
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"

class TestSeverity(Enum):
    """Test severity levels."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class GUIType(Enum):
    """GUI application type."""
    WEB = "WEB"
    DESKTOP = "DESKTOP"
    HYBRID = "HYBRID"

@dataclass
class TestResult:
    """Result of a single test execution."""
    test_id: str
    test_name: str
    category: str
    gui_type: GUIType
    status: TestStatus
    duration: float
    screenshot_path: str | None = None
    error_message: str | None = None
    severity: TestSeverity = TestSeverity.MEDIUM
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class UATReport:
    """Complete UAT test run report."""
    test_run_id: str
    start_time: datetime
    end_time: datetime
    total_duration: float
    summary: dict[str, int]
    results: list[TestResult]
    critical_failures: list[TestResult] = field(default_factory=list)

class UATAutomation:
    """UAT Automation Framework."""
    
    def __init__(self, gui_type: GUIType = GUIType.WEB):
        self.gui_type = gui_type
        self.results: list[TestResult] = []
        
        # CUSTOMIZE THESE for your application
        self.WEB_PAGES = {
            "Core": [
                {"id": "home", "name": "Home Page", "url": "/", "critical": True},
                {"id": "dashboard", "name": "Dashboard", "url": "/dashboard", "critical": True},
                # ADD YOUR WEB PAGES HERE
            ],
        }
        
        self.DESKTOP_WINDOWS = {
            "Core": [
                {"id": "main_window", "name": "Main Window", "title": "Your App", "critical": True},
                # ADD YOUR DESKTOP WINDOWS HERE
            ],
        }
        
        self.WORKFLOWS = [
            {
                "id": "basic_workflow",
                "name": "Basic User Workflow",
                "gui_type": GUIType.WEB,
                "critical": True,
                "steps": [
                    "Navigate to home page",
                    "Click submit button",
                    "Verify success message",
                ]
            },
            # ADD YOUR WORKFLOWS HERE
        ]
        
        self.ERROR_SCENARIOS = [
            {
                "id": "invalid_input",
                "name": "Invalid Input Handling",
                "gui_type": GUIType.WEB,
                "severity": TestSeverity.HIGH,
                "test": "Submit form with invalid data and verify error message"
            },
            # ADD YOUR ERROR SCENARIOS HERE
        ]
    
    def get_test_plan(self, mode: str = "full") -> dict[str, Any]:
        """Generate test plan based on mode."""
        plan = {
            "mode": mode,
            "gui_type": self.gui_type.value,
            "timestamp": datetime.now().isoformat(),
            "pages": [],
            "windows": [],
            "workflows": [],
            "error_scenarios": []
        }
        
        if self.gui_type in [GUIType.WEB, GUIType.HYBRID]:
            if mode == "quick":
                plan["pages"] = [p for cat in self.WEB_PAGES.values() for p in cat if p.get("critical")]
            elif mode == "critical":
                plan["pages"] = [p for cat in self.WEB_PAGES.values() for p in cat if p.get("critical")]
                plan["workflows"] = [w for w in self.WORKFLOWS if w.get("critical") and w["gui_type"] == GUIType.WEB]
            else:  # full
                plan["pages"] = [p for cat in self.WEB_PAGES.values() for p in cat]
                plan["workflows"] = [w for w in self.WORKFLOWS if w["gui_type"] == GUIType.WEB]
                plan["error_scenarios"] = [e for e in self.ERROR_SCENARIOS if e["gui_type"] == GUIType.WEB]
        
        if self.gui_type in [GUIType.DESKTOP, GUIType.HYBRID]:
            if mode == "quick":
                plan["windows"] = [w for cat in self.DESKTOP_WINDOWS.values() for w in cat if w.get("critical")]
            elif mode == "critical":
                plan["windows"] = [w for cat in self.DESKTOP_WINDOWS.values() for w in cat if w.get("critical")]
                plan["workflows"] = [w for w in self.WORKFLOWS if w.get("critical") and w["gui_type"] == GUIType.DESKTOP]
            else:  # full
                plan["windows"] = [w for cat in self.DESKTOP_WINDOWS.values() for w in cat]
                plan["workflows"] = [w for w in self.WORKFLOWS if w["gui_type"] == GUIType.DESKTOP]
                plan["error_scenarios"] = [e for e in self.ERROR_SCENARIOS if e["gui_type"] == GUIType.DESKTOP]
        
        return plan
    
    def generate_agent_instructions(self, mode: str = "full") -> str:
        """Generate instructions for AI agent execution."""
        plan = self.get_test_plan(mode)
        
        instructions = f"""# UAT Test Execution Instructions

**Mode:** {mode}
**GUI Type:** {self.gui_type.value}
**Generated:** {plan['timestamp']}

## Test Execution Steps

"""
        
        if self.gui_type in [GUIType.WEB, GUIType.HYBRID]:
            instructions += """### Web GUI Tests (Playwright)

```bash
cd tests/e2e
npm test
```

"""
            for page in plan["pages"]:
                instructions += f"""#### Test: {page['name']}
- Navigate to: {page['url']}
- Verify page loads
- Capture screenshot: `{page['id']}_loaded.png`
- Check for errors

"""
        
        if self.gui_type in [GUIType.DESKTOP, GUIType.HYBRID]:
            instructions += """### Desktop GUI Tests (PyAutoGUI/pytest-qt)

```bash
pytest tests/gui_tests/ -v
```

"""
            for window in plan["windows"]:
                instructions += f"""#### Test: {window['name']}
- Launch application
- Wait for window: "{window['title']}"
- Verify window active
- Capture screenshot: `{window['id']}_active.png`

"""
        
        for workflow in plan["workflows"]:
            instructions += f"""### Workflow: {workflow['name']}

Steps:
"""
            for i, step in enumerate(workflow["steps"], 1):
                instructions += f"{i}. {step}\n"
            instructions += "\n"
        
        return instructions
    
    def save_test_plan(self, mode: str = "full", output_dir: str = "artifacts/uat"):
        """Save test plan to file."""
        plan = self.get_test_plan(mode)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON
        json_path = output_path / f"test_plan_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(plan, f, indent=2)
        
        # Save instructions
        instructions = self.generate_agent_instructions(mode)
        md_path = output_path / f"agent_instructions_{timestamp}.md"
        with open(md_path, 'w') as f:
            f.write(instructions)
        
        logger.info(f"Test plan saved to {json_path}")
        logger.info(f"Agent instructions saved to {md_path}")
        
        return json_path, md_path

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="UAT Automation Framework")
    parser.add_argument("--mode", choices=["quick", "full", "critical", "workflows"], default="full")
    parser.add_argument("--gui-type", choices=["web", "desktop", "hybrid"], default="web")
    parser.add_argument("--output-dir", default="artifacts/uat")
    
    args = parser.parse_args()
    
    gui_type = GUIType[args.gui_type.upper()]
    automation = UATAutomation(gui_type=gui_type)
    automation.save_test_plan(mode=args.mode, output_dir=args.output_dir)
```

### File: `scripts/run_uat.ps1`

```powershell
<#
.SYNOPSIS
    Run UAT tests for GUI applications
.PARAMETER Mode
    Test mode: quick, full, critical, workflows
.PARAMETER GUIType
    GUI type: web, desktop, hybrid
.PARAMETER StartServer
    Start application server before testing
.PARAMETER KeepServer
    Keep server running after tests
#>
param(
    [ValidateSet('quick', 'full', 'critical', 'workflows')]
    [string]$Mode = 'quick',
    
    [ValidateSet('web', 'desktop', 'hybrid')]
    [string]$GUIType = 'web',
    
    [switch]$StartServer,
    [switch]$KeepServer
)

Write-Host "=== UAT Automation Framework ===" -ForegroundColor Cyan
Write-Host "Mode: $Mode" -ForegroundColor Yellow
Write-Host "GUI Type: $GUIType" -ForegroundColor Yellow

# Generate test plan
Write-Host "`nGenerating test plan..." -ForegroundColor Green
python tools/uat/uat_automation.py --mode $Mode --gui-type $GUIType

# Start server if requested
$serverProcess = $null
if ($StartServer) {
    Write-Host "`nStarting application server..." -ForegroundColor Green
    # CHANGE THIS to your server start command
    $serverProcess = Start-Process python -ArgumentList "-m", "your_app.main" -PassThru -NoNewWindow
    Start-Sleep -Seconds 3
}

# Run tests based on GUI type
if ($GUIType -eq 'web' -or $GUIType -eq 'hybrid') {
    Write-Host "`nRunning Playwright tests..." -ForegroundColor Green
    Set-Location tests/e2e
    npm test
    Set-Location ../..
}

if ($GUIType -eq 'desktop' -or $GUIType -eq 'hybrid') {
    Write-Host "`nRunning desktop GUI tests..." -ForegroundColor Green
    pytest tests/gui_tests/ -v
}

# Cleanup
if ($serverProcess -and -not $KeepServer) {
    Write-Host "`nStopping server..." -ForegroundColor Yellow
    Stop-Process -Id $serverProcess.Id -Force
}

Write-Host "`n=== UAT Complete ===" -ForegroundColor Cyan
Write-Host "Results in: artifacts/" -ForegroundColor Green
```

---

## Part 6: Validation & Execution

### Final Validation Checklist

Run these commands to verify complete setup:

```bash
# 1. Verify directory structure
ls -R tests/

# Expected:
# tests/
# ├── e2e/
# │   ├── playwright/
# │   │   ├── fixtures/
# │   │   ├── helpers/
# │   │   ├── test_critical_workflows.spec.ts
# │   │   └── test_error_scenarios.spec.ts
# │   ├── package.json
# │   └── playwright.config.ts
# └── gui_tests/
#     ├── conftest.py
#     ├── test_desktop_workflows.py
#     └── test_qt_specific.py

# 2. Verify dependencies installed
cd tests/e2e && npm list @playwright/test
pip list | grep -E "pytest|pyautogui|pytest-qt"

# 3. Run quick test
python tools/uat/uat_automation.py --mode quick --gui-type web

# 4. Execute tests
./scripts/run_uat.ps1 -Mode quick -GUIType web
```

### Success Criteria

- ✅ Test plan generated in `artifacts/uat/`
- ✅ Agent instructions created
- ✅ Tests execute without errors
- ✅ Screenshots captured
- ✅ Reports generated

---

## Part 7: Customization Guide

### For Your Specific Application

1. **Update `playwright.config.ts`:**
   - Change `baseURL` to your app's URL
   - Change `webServer.command` to your start command
   - Change `webServer.port` to your port

2. **Update `tests/e2e/playwright/fixtures/base.ts`:**
   - Add all your application's selectors to `SELECTORS`
   - Use data-testid attributes in your HTML for stability

3. **Update `tools/uat/uat_automation.py`:**
   - Fill in `WEB_PAGES` with your routes
   - Fill in `DESKTOP_WINDOWS` with your window titles
   - Fill in `WORKFLOWS` with your user journeys
   - Fill in `ERROR_SCENARIOS` with your edge cases

4. **Create test files:**
   - Add workflow tests in `test_critical_workflows.spec.ts`
   - Add error tests in `test_error_scenarios.spec.ts`
   - Add desktop tests in `test_desktop_workflows.py`

5. **Update `scripts/run_uat.ps1`:**
   - Change server start command
   - Adjust port numbers
   - Add any pre-test setup needed

---

## Part 8: Execution Examples

### Web Application

```bash
# Generate test plan
python tools/uat/uat_automation.py --mode critical --gui-type web

# Run tests
cd tests/e2e
npm test

# View report
npm run test:report
```

### Desktop Application

```bash
# Generate test plan
python tools/uat/uat_automation.py --mode critical --gui-type desktop

# Run tests
pytest tests/gui_tests/ -v --html=artifacts/gui_tests/report.html
```

### Hybrid Application

```bash
# Generate combined test plan
python tools/uat/uat_automation.py --mode full --gui-type hybrid

# Run all tests
./scripts/run_uat.ps1 -Mode full -GUIType hybrid -StartServer
```

---

## Part 9: CI/CD Integration

### File: `.github/workflows/uat.yml`

```yaml
name: UAT Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
  workflow_dispatch:
    inputs:
      mode:
        description: 'Test mode'
        required: true
        default: 'critical'
        type: choice
        options:
          - quick
          - full
          - critical
          - workflows

jobs:
  web-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd tests/e2e
          npm install
          npx playwright install --with-deps
      
      - name: Generate test plan
        run: |
          python tools/uat/uat_automation.py --mode ${{ github.event.inputs.mode || 'critical' }} --gui-type web
      
      - name: Run Playwright tests
        run: |
          cd tests/e2e
          npm test
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: artifacts/e2e/playwright-report/
      
      - name: Upload screenshots
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: screenshots
          path: artifacts/e2e/screenshots/

  desktop-tests:
    runs-on: windows-latest  # Desktop tests need Windows
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install pytest pytest-qt pyautogui pillow
      
      - name: Generate test plan
        run: |
          python tools/uat/uat_automation.py --mode ${{ github.event.inputs.mode || 'critical' }} --gui-type desktop
      
      - name: Run desktop GUI tests
        run: |
          pytest tests/gui_tests/ -v --html=artifacts/gui_tests/report.html
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: desktop-test-report
          path: artifacts/gui_tests/
```

---

## Summary

You now have a complete, agent-executable UAT testing framework that:

1. ✅ **Decides** which testing approach to use (Playwright vs PyAutoGUI)
2. ✅ **Tests web GUIs** with Playwright (browser automation)
3. ✅ **Tests desktop GUIs** with PyAutoGUI/pytest-qt (native app automation)
4. ✅ **Supports hybrid** applications with both
5. ✅ **Generates test plans** automatically
6. ✅ **Creates agent instructions** for execution
7. ✅ **Integrates with CI/CD** via GitHub Actions
8. ✅ **Produces comprehensive reports** with screenshots

**Next Steps:**
1. Customize the files for your specific application
2. Run validation checkpoint commands
3. Execute your first test run
4. Review results and iterate

**Version:** 1.0.0  
**Last Updated:** 2026-03-01
