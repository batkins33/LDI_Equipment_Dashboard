# SysPulse GUI

**Desktop GUI for SysPulse System Utilities Dashboard**

Version: 3.0.0-alpha.1 (Phase 3.1)

---

## Overview

The SysPulse GUI provides a graphical interface for the system utilities dashboard, making it easier to visualize and manage your system's performance.

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Install GUI Dependencies

```bash
cd syspulse
pip install -r requirements-gui.txt
```

This will install:
- PyQt6 (GUI framework)
- PyQt6-Charts (for visualizations)
- matplotlib (for advanced charts)
- Pillow (for image handling)

---

## Launching the GUI

```bash
# From the syspulse directory
python syspulse_gui.py
```

Or make it executable (Linux/macOS):

```bash
chmod +x syspulse_gui.py
./syspulse_gui.py
```

---

## Features (Phase 3.1)

### ✅ Implemented
- **Main Window** with tabbed interface
- **Menu Bar** with File, Scan, Actions, and Help menus
- **Status Bar** for operation feedback
- **6 Tabs**: Dashboard, Browsers, Startup, Storage, Processes, Reports
- **Keyboard Shortcuts**:
  - `F5` - Full system scan
  - `Ctrl+J` - Export JSON report
  - `Ctrl+H` - Export HTML report
  - `Ctrl+Q` - Exit application
  - `F1` - Help

### 🚧 Coming Soon (Phase 3.2-3.9)
- Dashboard with system overview and quick stats
- Browser profiles table and cache visualization
- Startup programs management with toggles
- Storage treemap and cleanup controls
- Real-time process monitoring
- Report history and export
- Settings and preferences
- Packaging as standalone executable

---

## Current Status

**Phase 3.1 - Basic GUI Framework: COMPLETE** ✅

The GUI framework is now in place. Tab content will be implemented in upcoming phases:

| Phase | Feature | Status |
|-------|---------|--------|
| 3.1 | Basic GUI Framework | ✅ Complete |
| 3.2 | Dashboard Tab | ⏳ Pending |
| 3.3 | Browser Tab | ⏳ Pending |
| 3.4 | Startup Tab | ⏳ Pending |
| 3.5 | Storage Tab | ⏳ Pending |
| 3.6 | Processes Tab | ⏳ Pending |
| 3.7 | Reports Tab | ⏳ Pending |
| 3.8 | Settings | ⏳ Pending |
| 3.9 | Packaging | ⏳ Pending |

---

## Using the GUI

### Menu Bar

**File Menu:**
- Export JSON Report (`Ctrl+J`)
- Export HTML Report (`Ctrl+H`)
- Exit (`Ctrl+Q`)

**Scan Menu:**
- Full System Scan (`F5`)
- Scan Browsers
- Scan Startup
- Scan Storage
- Scan Processes

**Actions Menu:**
- Clean Browser Cache
- Clean Storage
- Manage Startup Programs

**Help Menu:**
- About SysPulse
- Help (`F1`)

### Tabs

Navigate between tabs to access different modules:
- **Dashboard** - System overview
- **Browsers** - Browser profile management
- **Startup** - Startup program control
- **Storage** - Storage analysis
- **Processes** - Process monitoring
- **Reports** - Report history

---

## Design

### Color Scheme
- Primary: Purple gradient (#667eea → #764ba2)
- Success: Green (#27ae60)
- Warning: Orange (#f39c12)
- Danger: Red (#e74c3c)

### Layout
- Minimum window size: 1024x768
- Tab-based navigation
- Consistent spacing and typography
- Responsive design

---

## Fallback to CLI

If PyQt6 is not available, use the CLI or interactive mode:

```bash
# Interactive mode (text-based menu)
python syspulse.py --interactive

# Direct CLI usage
python syspulse.py --browsers
python syspulse.py --startup
python syspulse.py --clean-browser-cache
```

---

## Development

### Project Structure

```
syspulse/
├── syspulse_gui.py          # GUI entry point
├── gui/
│   ├── __init__.py
│   ├── main_window.py       # Main application window
│   ├── styles.py            # Stylesheet and theming
│   ├── tabs/                # Tab widgets
│   │   └── __init__.py
│   ├── widgets/             # Reusable widgets
│   │   └── __init__.py
│   └── dialogs/             # Dialog windows
│       └── __init__.py
├── modules/                 # Backend modules
└── requirements-gui.txt     # GUI dependencies
```

### Adding New Features

1. Backend functionality goes in `modules/`
2. GUI components go in `gui/`
3. Tab-specific code goes in `gui/tabs/`
4. Reusable widgets go in `gui/widgets/`
5. Modal dialogs go in `gui/dialogs/`

---

## Troubleshooting

### PyQt6 Installation Issues

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install python3-pyqt6

# Or via pip
pip install PyQt6 PyQt6-Charts
```

**macOS:**
```bash
# Using pip
pip3 install PyQt6 PyQt6-Charts

# Or using Homebrew
brew install pyqt@6
```

**Windows:**
```bash
# Using pip
pip install PyQt6 PyQt6-Charts
```

### GUI Won't Launch

1. Check Python version: `python --version` (need 3.8+)
2. Verify PyQt6 installation: `python -c "import PyQt6; print('OK')"`
3. Check error messages in terminal
4. Fall back to CLI: `python syspulse.py --interactive`

---

## Roadmap

See `PHASE3_PLAN.md` for detailed implementation plan.

Next up: **Phase 3.2 - Dashboard Tab** with system overview and quick stats.

---

## Contributing

Report issues or suggest features via the main repository.

---

**Control the bullshit. Make your computer run better.** 🔧
