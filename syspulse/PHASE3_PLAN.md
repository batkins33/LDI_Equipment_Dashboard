# SysPulse Phase 3 Implementation Plan

**Status**: 🚧 In Progress
**Version**: 3.0.0 (in development)
**Started**: 2025-01-26

---

## Overview

Phase 3 adds a **Desktop GUI** to SysPulse. While Phase 1 was CLI analysis and Phase 2 added actions + interactive mode, Phase 3 provides a native graphical interface for better visualization and ease of use.

---

## GUI Framework Decision

After evaluating options, we're choosing **PyQt6** for the following reasons:

### Framework Comparison:

| Framework | Pros | Cons | Verdict |
|-----------|------|------|---------|
| **PyQt6** | Native Python, mature, cross-platform, rich widgets, can reuse all existing code | Licensing (GPL/Commercial), learning curve | ✅ **CHOSEN** |
| **Tkinter** | Built-in, simple, lightweight | Limited widgets, dated appearance | ❌ Too basic |
| **Electron** | Modern, web technologies | Requires JS/TS rewrite, large bundle size | ❌ Major rewrite |
| **Tauri** | Small bundle, Rust performance | Requires Rust backend setup | ❌ Added complexity |
| **PySide6** | Official Qt, LGPL license | Similar to PyQt6, slightly less mature | ⚠️ Alternative |

### Decision: **PyQt6**
- **Native Python integration** - Reuse 100% of existing code
- **Cross-platform** - Windows, macOS, Linux
- **Rich widget library** - Charts, graphs, treemaps available
- **Mature ecosystem** - Well-documented, large community
- **Qt Designer** - Visual UI design tool

---

## Implementation Order

### ✅ Phase 3.1: Basic GUI Framework Setup
**Version**: `3.0.0-alpha.1`
**Status**: Pending

**Features**:
- Install PyQt6 dependency
- Create basic main window
- Add menu bar (File, Scan, Actions, Help)
- Create tab-based interface
- Integrate with existing SysPulse backend

**Files to create**:
- `gui/__init__.py` - GUI package initialization
- `gui/main_window.py` - Main application window
- `gui/styles.py` - Stylesheet and theme
- `syspulse_gui.py` - GUI entry point

**Dependencies**:
```bash
pip install PyQt6 PyQt6-Charts
```

---

### ✅ Phase 3.2: Dashboard Tab
**Version**: `3.0.0-alpha.2`
**Status**: Pending

**Features**:
- System overview dashboard
- Quick stats cards (total cache, startup items, storage usage)
- "Run Full Scan" button
- Recent scans list
- System health score display

**Files to create**:
- `gui/tabs/dashboard.py` - Dashboard tab widget
- `gui/widgets/stat_card.py` - Reusable stat card widget
- `gui/widgets/health_score.py` - Health score gauge

**UI Layout**:
```
┌─────────────────────────────────────────┐
│ SysPulse                    [Run Scan]  │
├─────────────────────────────────────────┤
│ Dashboard │ Browsers │ Startup │ ...    │
├─────────────────────────────────────────┤
│ ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│ │ Browser │ │ Startup │ │ Storage │   │
│ │ 8.4 GB  │ │ 23 apps │ │ 124 GB  │   │
│ └─────────┘ └─────────┘ └─────────┘   │
│                                         │
│ System Health: ████████░░ 80%          │
│                                         │
│ Recent Scans:                           │
│  • 2025-01-26 14:30 - Full Scan        │
│  • 2025-01-25 09:15 - Browser Only     │
└─────────────────────────────────────────┘
```

---

### ✅ Phase 3.3: Browser Tab
**Version**: `3.0.0-alpha.3`
**Status**: Pending

**Features**:
- Browser profiles table view
- Cache size visualization (bar chart)
- Extension count per profile
- "Clean Cache" button with selection
- Profile details panel

**Files to create**:
- `gui/tabs/browser.py` - Browser tab widget
- `gui/widgets/profile_table.py` - Profile table widget
- `gui/dialogs/clean_cache_dialog.py` - Cache cleaning dialog

**UI Features**:
- Sortable table (by name, cache size, last used)
- Multi-select checkboxes for batch operations
- Right-click context menu (Clean, View Details, Export)
- Visual cache size comparison chart

---

### ✅ Phase 3.4: Startup Tab
**Version**: `3.0.0-alpha.4`
**Status**: Pending

**Features**:
- Startup items table with impact levels
- Color-coded impact (Red=High, Yellow=Medium, Green=Low)
- Toggle switches to enable/disable items
- Estimated boot time savings
- Search/filter by impact or name

**Files to create**:
- `gui/tabs/startup.py` - Startup tab widget
- `gui/widgets/startup_table.py` - Startup items table
- `gui/widgets/toggle_switch.py` - Custom toggle switch widget

**UI Features**:
- Impact column with colored badges
- One-click toggle switches
- "Optimize Now" button (disables high-impact safe items)
- Before/after boot time estimate

---

### ✅ Phase 3.5: Storage Tab
**Version**: `3.0.0-alpha.5`
**Status**: Pending

**Features**:
- Storage treemap visualization
- Category breakdown (Temp, Cache, Downloads, etc.)
- Cleanup checkboxes per category
- "Clean All Safe" button
- Space to be freed indicator

**Files to create**:
- `gui/tabs/storage.py` - Storage tab widget
- `gui/widgets/treemap.py` - Interactive treemap widget
- `gui/dialogs/cleanup_confirm.py` - Cleanup confirmation dialog

**UI Features**:
- Interactive treemap (click to drill down)
- Visual size comparison
- Estimated space savings shown in real-time
- Safety indicators (green checkmark for safe items)

---

### ✅ Phase 3.6: Processes Tab
**Version**: `3.0.0-alpha.6`
**Status**: Pending

**Features**:
- Real-time process list
- CPU and memory usage bars
- Process grouping by category
- Search/filter functionality
- "End Process" with confirmation

**Files to create**:
- `gui/tabs/processes.py` - Processes tab widget
- `gui/widgets/process_table.py` - Process table with live updates
- `gui/dialogs/end_process_dialog.py` - Process termination dialog

**UI Features**:
- Auto-refresh every 2 seconds
- Sort by CPU, memory, or name
- Visual usage bars in table cells
- Category grouping (System, Background, User Apps)

---

### ✅ Phase 3.7: Reports Tab
**Version**: `3.0.0-alpha.7`
**Status**: Pending

**Features**:
- Report history list
- Report preview panel
- Export buttons (JSON, HTML, PDF)
- Before/after comparison view
- Charts showing trends over time

**Files to create**:
- `gui/tabs/reports.py` - Reports tab widget
- `gui/widgets/report_preview.py` - Report preview widget
- `gui/widgets/trend_chart.py` - Trend visualization

**UI Features**:
- Timeline view of past scans
- Click to preview report details
- Export to various formats
- Compare two reports side-by-side

---

### ✅ Phase 3.8: Settings & Preferences
**Version**: `3.0.0-alpha.8`
**Status**: Pending

**Features**:
- Application preferences
- Auto-scan scheduling
- Theme selection (Light/Dark)
- Notification preferences
- About dialog

**Files to create**:
- `gui/dialogs/settings_dialog.py` - Settings dialog
- `gui/dialogs/about_dialog.py` - About dialog
- `gui/theme.py` - Theme management

---

### ✅ Phase 3.9: Packaging & Distribution
**Version**: `3.0.0-beta.1`
**Status**: Pending

**Features**:
- Build standalone executables
- Windows installer (.exe)
- macOS app bundle (.app)
- Linux AppImage
- Auto-update mechanism

**Files to create**:
- `setup.py` - PyInstaller setup
- `build_windows.py` - Windows build script
- `build_macos.py` - macOS build script
- `build_linux.py` - Linux build script
- `installer/windows.iss` - Inno Setup script

**Build Tools**:
- PyInstaller for executable creation
- Inno Setup for Windows installer
- create-dmg for macOS installer
- AppImage tools for Linux

---

## Design System

### Color Palette
```python
COLORS = {
    'primary': '#667eea',      # Purple gradient start
    'primary_dark': '#764ba2', # Purple gradient end
    'success': '#27ae60',      # Green
    'warning': '#f39c12',      # Orange
    'danger': '#e74c3c',       # Red
    'background': '#f8f9fa',   # Light gray
    'surface': '#ffffff',      # White
    'text': '#333333',         # Dark gray
    'text_light': '#666666',   # Medium gray
}
```

### Typography
- **Headers**: 16-20pt Bold
- **Body**: 12pt Regular
- **Captions**: 10pt Regular
- **Font Family**: System default (Segoe UI on Windows, SF Pro on macOS, Ubuntu on Linux)

### Spacing
- **Small**: 8px
- **Medium**: 16px
- **Large**: 24px
- **XLarge**: 32px

---

## Commit Strategy

Each feature gets **its own commit**:

```
[Phase3] Add basic GUI framework setup (v3.0.0-alpha.1)
[Phase3] Add dashboard tab (v3.0.0-alpha.2)
[Phase3] Add browser tab (v3.0.0-alpha.3)
...
```

---

## Testing Strategy

Each GUI component includes:

1. **Manual testing** - Visual verification
2. **Integration testing** - Verify backend integration
3. **Cross-platform testing** - Test on Windows, macOS, Linux
4. **Usability testing** - Easy to understand and use

---

## Requirements

### Python Packages
```
PyQt6>=6.6.0
PyQt6-Charts>=6.6.0
matplotlib>=3.8.0  # For advanced charts
Pillow>=10.0.0     # For image handling
```

### System Requirements
- **Python**: 3.8+
- **OS**: Windows 10+, macOS 10.14+, Ubuntu 20.04+
- **RAM**: 512MB minimum
- **Disk**: 100MB for application

---

## Success Metrics

- ✅ GUI launches in <2 seconds
- ✅ All CLI features accessible via GUI
- ✅ Standalone executable <50MB
- ✅ Works without admin rights (with graceful degradation)
- ✅ Responsive UI (no freezing during scans)

---

## Current Status

| Feature | Status | Version |
|---------|--------|---------|
| Phase 1 (CLI) | ✅ Complete | v1.0.0 |
| Phase 2 (Actions) | ✅ Complete | v2.0.0-alpha.5 |
| GUI Framework | ⏳ Pending | v3.0.0-alpha.1 |
| Dashboard Tab | ⏳ Pending | v3.0.0-alpha.2 |
| Browser Tab | ⏳ Pending | v3.0.0-alpha.3 |
| Startup Tab | ⏳ Pending | v3.0.0-alpha.4 |
| Storage Tab | ⏳ Pending | v3.0.0-alpha.5 |
| Processes Tab | ⏳ Pending | v3.0.0-alpha.6 |
| Reports Tab | ⏳ Pending | v3.0.0-alpha.7 |
| Settings | ⏳ Pending | v3.0.0-alpha.8 |
| Packaging | ⏳ Pending | v3.0.0-beta.1 |

---

## Next Action

Starting with **Phase 3.1: Basic GUI Framework Setup**

This creates the foundation for all future GUI work.
