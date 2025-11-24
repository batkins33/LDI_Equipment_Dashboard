# SysPulse Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
