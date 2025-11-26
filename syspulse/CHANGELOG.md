# SysPulse Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [3.0.0-alpha.1] - 2025-01-26

### Added - Phase 3.1: Basic GUI Framework
- **Desktop GUI with PyQt6**
  - Graphical user interface entry point (`syspulse_gui.py`)
  - Main window with tabbed interface
  - Complete menu bar (File, Scan, Actions, Help)
  - Status bar for operation feedback
  - Responsive window sizing (1024x768 minimum)

- **GUI Structure**
  - `gui/` package with modular organization
  - `gui/main_window.py` - Main application window
  - `gui/styles.py` - Comprehensive stylesheet and theming
  - `gui/tabs/` - Placeholder for tab widgets
  - `gui/widgets/` - Placeholder for reusable widgets
  - `gui/dialogs/` - Placeholder for modal dialogs

- **Six tab interface**
  - Dashboard tab (placeholder)
  - Browsers tab (placeholder)
  - Startup tab (placeholder)
  - Storage tab (placeholder)
  - Processes tab (placeholder)
  - Reports tab (placeholder)

- **Menu functionality**
  - File menu: Export JSON/HTML reports, Exit
  - Scan menu: Full scan, individual module scans
  - Actions menu: Clean cache, storage, manage startup
  - Help menu: About dialog, Help dialog

- **Keyboard shortcuts**
  - `F5` - Full system scan
  - `Ctrl+J` - Export JSON report
  - `Ctrl+H` - Export HTML report
  - `Ctrl+Q` - Exit application
  - `F1` - Show help

- **Design system**
  - Purple gradient color scheme (#667eea → #764ba2)
  - Comprehensive Qt stylesheet with custom widgets
  - Fusion style for native look
  - Centered window positioning

- **Documentation**
  - `GUI_README.md` - Complete GUI documentation
  - `PHASE3_PLAN.md` - Detailed Phase 3 implementation plan
  - `requirements-gui.txt` - GUI dependencies file

### Changed
- Updated version to `3.0.0-alpha.1`
- Added PyQt6 framework decision documentation

### Technical Details
- **Framework**: PyQt6 6.6.0+
- **Charts**: PyQt6-Charts for visualizations
- **Cross-platform**: Windows, macOS, Linux support
- **Graceful fallback**: Shows instructions if PyQt6 not installed
- Tab content is placeholder - will be implemented in phases 3.2-3.7

### Requirements
```
PyQt6>=6.6.0
PyQt6-Charts>=6.6.0
matplotlib>=3.8.0
Pillow>=10.0.0
```

### Usage
```bash
# Install GUI dependencies
pip install -r requirements-gui.txt

# Launch GUI
python syspulse_gui.py

# Or continue using CLI/interactive mode
python syspulse.py --interactive
```

### Notes
- This is Phase 3.1 - basic framework only
- Tab content will be implemented in phases 3.2-3.9
- All backend functionality from Phase 1 and 2 is integrated
- GUI wraps existing SysPulse modules, no code duplication

---

## [2.0.0-alpha.5] - 2025-01-24

### Added - Phase 2.5: Interactive Mode
- **Interactive menu-driven interface**
  - `--interactive` or `-i` flag to launch interactive mode
  - User-friendly text-based menu system
  - Numbered options for easy navigation
  - Clear back/exit navigation
  - Clean screen transitions between menus

- **Main menu features**
  - Full system scan option
  - Individual module scans (browsers, startup, storage, processes)
  - Cleanup & optimization submenu
  - Reports & history submenu
  - Settings submenu

- **Guided cleanup wizard**
  - Step-by-step walkthrough (1/3, 2/3, 3/3)
  - Browser cache cleanup guidance
  - Storage cleanup guidance
  - Startup optimization guidance
  - Summary of completed actions
  - Automatic prompts after each scan

- **Enhanced user experience**
  - Smart confirmations (Y/n or y/N defaults)
  - Dry-run mode prompts before destructive actions
  - Action history tracking for future undo support
  - Report export integration from menus
  - Help and about screens
  - Reports directory information

- **New modules**
  - `ui/interactive.py` - InteractiveMode class
  - Complete menu system with submenus
  - Action history tracking (foundation for undo)

### Changed
- Updated version to `2.0.0-alpha.5`
- Interactive mode takes precedence over other CLI flags
- All scan operations can now prompt for follow-up actions

### Technical Details
- Interactive mode wraps existing SysPulse functionality
- No changes to core scanning or action modules
- Uses colorama for cross-platform colored output
- Clear screen functionality for Windows and Unix
- Action history stored in memory for session tracking

### Interactive Mode Features
- **Navigation**:
  - Number-based menu selection
  - 0 to go back or exit
  - Confirmation before exit

- **Cleanup Operations**:
  - Integrated with all Phase 2 action modules
  - Browser cache cleanup with profile selection
  - Storage cleanup with category breakdown
  - Startup management with impact display

- **Reports & History**:
  - Export current scan to JSON or HTML
  - View previously generated reports
  - View action history for potential undo
  - Reports directory location display

- **Settings**:
  - View reports directory path
  - About SysPulse information
  - Interactive help screen

### Usage Examples
```bash
# Launch interactive mode
python syspulse.py --interactive
python syspulse.py -i

# Interactive mode provides:
# - Main menu with 8 options
# - Scan options for each module
# - Cleanup & optimization submenu
# - Guided cleanup wizard
# - Report generation and history
# - Settings and help
```

### User Experience Improvements
- No need to remember CLI flags
- Clear prompts and confirmations
- Step-by-step guidance for first-time users
- Visual feedback with colored output
- Organized menus for easy discovery
- Automatic follow-up prompts after scans

### Future Enhancements (Tracked)
- Undo functionality (history tracking implemented)
- Custom profiles/presets
- Scheduled scans from interactive mode
- More detailed action history with timestamps

---

## [2.0.0-alpha.4] - 2025-01-24

### Added - Phase 2.4: Report Generation
- **JSON and HTML report generation**
  - `--export-json` flag to export scan results to JSON
  - `--export-html` flag to export scan results to HTML
  - Automatic report generation after scans
  - Beautiful HTML reports with styled sections
  - Reports saved to `~/.syspulse/reports/`

- **New modules**
  - `modules/reporting.py` - ReportGenerator class
  - JSON export with full scan data
  - HTML export with visual styling and color coding
  - Timestamp and version tracking in reports

### Changed
- Updated version to `2.0.0-alpha.4`
- Enhanced run_full_scan() to collect all scan data
- Added last_scan_results storage for reporting
- CLI now supports export flags with any scan

### Technical Details
- Reports include metadata (timestamp, version, report type)
- JSON reports: structured data for programmatic access
- HTML reports: styled with CSS, responsive design
- Report filenames include timestamp for organization
- Reports stored in ~/.syspulse/reports/ directory

### Report Features
- **JSON Reports**:
  - Complete scan data in structured format
  - Easy to parse programmatically
  - Can be used for automation or further analysis

- **HTML Reports**:
  - Beautiful gradient header design
  - Color-coded items by priority (high/medium/low)
  - Stat cards with key metrics
  - Responsive layout
  - Browser-ready, shareable

### Usage Examples
```bash
# Run full scan and export to JSON
python syspulse.py --export-json

# Run full scan and export to HTML
python syspulse.py --export-html

# Scan specific module and export
python syspulse.py --browsers --export-html
python syspulse.py --startup --export-json
```

### Report Contents
- Browser profiles with cache sizes and recommendations
- Startup items with impact levels and suggestions
- Storage analysis with cleanup opportunities
- Process information with resource usage
- All with timestamp and system context

---

## [2.0.0-alpha.3] - 2025-01-24

### Added - Phase 2.3: Startup Manager
- **Startup item management with automatic backups**
  - `--manage-startup` flag to disable safe-to-disable startup items
  - `--dry-run` flag works with startup management
  - Interactive confirmation before making changes
  - Automatic backup before any modifications
  - Items are disabled, not deleted (fully reversible)
  - Currently Windows only (registry and startup folder support)

- **New action modules**
  - `modules/actions/startup_actions.py` - StartupManager class
  - Disable/enable startup items safely
  - Backup and restore functionality
  - Registry value renaming (prefixes with `_DISABLED_`)
  - Startup folder file renaming

### Changed
- Updated version to `2.0.0-alpha.3`
- Enhanced CLI to support startup management

### Technical Details
- Only disables items marked as "safe_to_disable" by analyzer
- Registry items: renamed to `_DISABLED_{name}` (not deleted)
- Folder items: files renamed to `_DISABLED_{filename}`
- Creates backup in `~/.syspulse/startup_backups/` before changes
- Keeps last 10 backups automatically
- Fully reversible - can re-enable all items

### Safety Features
- ✅ Requires "yes" confirmation before changes
- ✅ Shows exactly which items will be disabled
- ✅ Automatic backup before any modification
- ✅ Only targets "safe to disable" items
- ✅ Never deletes registry entries or files
- ✅ Dry-run mode to preview
- ✅ Items can be re-enabled later
- ✅ Audit logging

### Usage Examples
```bash
# Preview what would be disabled (safe, no changes)
python syspulse.py --manage-startup --dry-run

# Disable safe-to-disable startup items (interactive confirmation required)
python syspulse.py --manage-startup
```

### Notes
- Windows only in this release
- Linux/macOS support planned for future releases
- Items remain disabled until manually re-enabled
- Backups stored in ~/.syspulse/startup_backups/

---

## [2.0.0-alpha.2] - 2025-01-24

### Added - Phase 2.2: Storage Cleanup Actions
- **Storage cleanup with interactive confirmation**
  - `--clean-storage` flag to trigger cleanup
  - `--dry-run` flag to preview without executing
  - Interactive confirmation before deleting files
  - Multiple cleanup categories: temp files, recycle bin, old downloads, Windows Update cache
  - Detailed summary of space freed and files deleted
  - Audit logging to `~/.syspulse/cleanup_log.json`

- **New action modules**
  - `modules/actions/storage_actions.py` - StorageCleaner class
  - Safe cleanup for temp directories, recycle bin, old downloads
  - Windows Update cache cleanup (Windows only)
  - Graceful error handling and permission checks

### Changed
- Updated version to `2.0.0-alpha.2`
- Enhanced CLI to support storage cleanup actions

### Technical Details
- Cleans temp files from system temp directories
- Empties recycle bin properly (uses Windows API on Windows)
- Removes downloads older than 90 days
- Windows Update cache cleanup (stops/restarts Windows Update service)
- Tracks skipped files (in use or no permission)
- Never deletes files without confirmation
- Preview always shown first, then confirmation required

### Safety Features
- ✅ Requires "yes" confirmation before deleting
- ✅ Shows exactly what will be cleaned and space freed
- ✅ Dry-run mode to preview
- ✅ Skips files in use or without permission
- ✅ Detailed error reporting
- ✅ Audit logging
- ✅ Cannot be undone warning

### Usage Examples
```bash
# Preview what would be cleaned (safe, no changes)
python syspulse.py --clean-storage --dry-run

# Actually clean storage (interactive confirmation required)
python syspulse.py --clean-storage
```

---

## [2.0.0-alpha.1] - 2025-01-24

### Added - Phase 2.1: Browser Cache Cleanup
- **Browser cache cleanup with interactive confirmation**
  - `--clean-browser-cache` flag to trigger cleanup
  - `--dry-run` flag to preview without executing
  - Interactive confirmation before deleting files
  - Safety warnings about what will be preserved (bookmarks, passwords, history)
  - Detailed summary of space freed and files deleted
  - Audit logging to `~/.syspulse/cleanup_log.json`

- **New action modules**
  - `modules/actions/browser_actions.py` - BrowserCleaner class
  - Safe cache deletion for Chrome, Edge, Firefox
  - Graceful error handling
  - Per-profile cleanup results

### Changed
- Updated version to `2.0.0-alpha.1`
- Main CLI now supports action commands (Phase 2)
- Import structure updated to support action modules

### Technical Details
- Only cleans cache directories (Cache, Code Cache, GPUCache, Service Worker cache)
- Never touches user data (bookmarks, passwords, history, extensions, preferences)
- Creates `~/.syspulse/` directory for logs
- Keeps last 100 log entries for audit trail

### Safety Features
- ✅ Requires "yes" confirmation before deleting
- ✅ Shows exactly what will be cleaned
- ✅ Dry-run mode to preview
- ✅ Only targets profiles with cleanup recommendations
- ✅ Detailed error reporting
- ✅ Audit logging

### Usage Examples
```bash
# Preview what would be cleaned (safe, no changes)
python syspulse.py --clean-browser-cache --dry-run

# Actually clean browser caches (interactive confirmation required)
python syspulse.py --clean-browser-cache
```

---

## [1.0.0] - 2025-01-24

### Added - Phase 1: Core Analysis (MVP)
- **Browser Profile Scanner**
  - Scans Chrome, Edge, Firefox profiles
  - Shows cache sizes, extensions, last used dates
  - Provides cleanup recommendations
  - Cross-platform support (Windows, Linux, macOS)

- **Startup Impact Analyzer**
  - Scans Windows registry and startup folders
  - Translates program names to plain English
  - Impact scoring (High/Medium/Low)
  - Boot time estimates
  - Safe-to-disable recommendations
  - Knowledge base of 30+ common programs

- **Storage Sense**
  - Temp files analysis
  - Recycle bin tracking
  - Old downloads detection
  - Large file finder
  - Windows Update cache analysis
  - Safe cleanup identification

- **Background Process Explainer**
  - Real-time process scanning
  - Human-readable descriptions
  - CPU and memory usage
  - Safe-to-kill recommendations
  - Knowledge base of 30+ common processes
  - Category grouping

- **CLI Interface**
  - Color-coded output (via colorama)
  - Module-specific scans (--browsers, --startup, --storage, --processes)
  - Full system scan mode
  - Quick scan option
  - ASCII art logo

- **Documentation**
  - Comprehensive README with examples
  - QUICKSTART guide for new users
  - ROADMAP for future development
  - MIT License
  - Platform support matrix

### Technical Details
- Python 3.10+ required
- Dependencies: psutil, colorama, pyyaml, requests, tabulate
- Cross-platform: Windows (primary), Linux, macOS
- No background processes or startup entries
- Local execution only, no network requests

### Core Philosophy
- On-demand, not always running
- Understandable, not technical
- Actionable, not just informational
- Focused, not bloated

---

## Upcoming

### [2.0.0-alpha.2] - Planned
- Phase 2.2: Storage cleanup actions
- Clean temp files, empty recycle bin
- Interactive file review for old downloads

### [2.0.0-alpha.3] - Planned
- Phase 2.3: Startup manager
- Enable/disable startup items
- Backup and restore configuration
- Boot time testing

### [2.0.0-alpha.4] - Planned
- Phase 2.4: Report generation
- JSON export
- HTML reports
- Before/after comparisons

### [2.0.0-alpha.5] - Planned
- Phase 2.5: Interactive mode
- Menu-driven interface
- Step-by-step guided cleanup
- Real-time feedback

### [2.0.0] - Planned
- Phase 2 stable release
- All actionable controls complete
- Comprehensive testing
- Documentation updates

### [3.0.0] - Future
- Phase 3: Desktop GUI
- Native application with visual dashboards
- Drag-and-drop actions
- Single executable packaging

### [4.0.0] - Future
- Phase 4: Cloud & companion
- Optional cloud insights
- Mobile/web companion
- Community recommendations

---

## Development Process

Each Phase 2 feature gets its own alpha version for:
- ✅ Clear progression tracking
- ✅ Easy rollback if needed
- ✅ Independent feature testing
- ✅ Isolated debugging

Commit format: `[Phase2] Add <feature name>`

See `PHASE2_PLAN.md` for detailed implementation plan.
