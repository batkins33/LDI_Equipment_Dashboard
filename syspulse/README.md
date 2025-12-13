# SysPulse

```
  ____            ____        _
 / ___| _   _ ___|  _ \ _   _| |___  ___
 \___ \| | | / __| |_) | | | | / __|/ _ \
  ___) | |_| \__ \  __/| |_| | \__ \  __/
 |____/ \__, |___/_|    \__,_|_|___/\___|
        |___/
```

**Control the bullshit. Make your computer run better.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](https://github.com/batkins33/BA_Sandbox)

---

## 🎯 What is SysPulse?

SysPulse is a **lightweight system utilities dashboard** that solves a simple problem:

> *"Technical controls exist, but they're not understandable or consolidated."*

Windows gives you Task Manager, Disk Cleanup, Startup Apps, Services, and more - but each requires knowing:
1. **Where to find it**
2. **What you're looking at**
3. **What's safe to change**

**SysPulse translates technical → human** and consolidates everything into one on-demand tool.

---

## 🚀 Quick Start

### Installation

```bash
# Clone or download this repository
cd syspulse

# Install dependencies
pip install -r requirements.txt

# Run SysPulse
python syspulse.py
```

**That's it!** No installation, no background services, no bloat.

See [QUICKSTART.md](QUICKSTART.md) for detailed installation instructions.

---

## ✨ Features

### 🌐 Browser Profile Scanner

**Problem**: You have 3 Chrome profiles running. Each has gigabytes of cache. You have no idea which one is "Profile 2" or when you last used it.

**SysPulse Solution**:
```
[Chrome] Work Profile
  Cache: 4.2 GB
  Last used: 90 days ago
  Extensions: 23
  → Unused for 90 days, 4.2 GB cache - consider cleaning
```

**What it does**:
- Scans all Chrome, Edge, Firefox profiles
- Shows cache sizes per profile
- Lists installed extensions
- Identifies unused profiles
- Provides actionable recommendations

---

### 🚀 Startup Impact Analyzer

**Problem**: Task Manager shows "GoogleCrashHandler.exe" and you have no idea if you need it or if it's safe to disable.

**SysPulse Solution**:
```
[LOW] Spotify Web Helper
  Spotify auto-updater (not needed for app to work)
  → Safe to disable. Main Spotify app works fine without this.

[HIGH] Microsoft Teams
  Microsoft Teams communication platform
  → High boot impact. Safe to disable - launch manually before meetings.
```

**What it does**:
- Scans Windows registry and startup folders
- Translates cryptic names to plain English
- Shows impact level (High/Medium/Low)
- Estimates boot time delay
- Recommends what's safe to disable

---

### 💾 Storage Sense

**Problem**: Your disk is full but you don't know where to start cleaning.

**SysPulse Solution**:
```
High Priority Cleanups:

• Temp Files: 2.1 GB
  Safe to delete. Will free 2.1 GB.

• Old Downloads: 1.8 GB (45 items)
  Review 45 old files. Can free 1.8 GB.

• Recycle Bin: 3.2 GB
  Empty recycle bin to free 3.2 GB.
```

**What it does**:
- Scans temp files, downloads, recycle bin
- Identifies large old files
- Shows safe cleanup opportunities
- Provides size estimates
- Never auto-deletes (you're in control)

---

### ⚙️ Background Process Explainer

**Problem**: Task Manager shows 8 instances of "svchost.exe" using 40% CPU and you don't know if that's normal.

**SysPulse Solution**:
```
[12.4%] chrome.exe
  Google Chrome browser
  Memory: 542.3 MB
  → Safe to close. Multiple instances are normal (one per tab/extension).

[8.1%] svchost.exe
  Windows services host (runs multiple background services)
  Memory: 234.1 MB
  → DO NOT STOP. Multiple instances are normal - each hosts different Windows services.
```

**What it does**:
- Scans running processes
- Explains what each process actually does
- Shows CPU and memory usage
- Recommends what's safe to stop
- Filters noise (only shows significant processes)

---

## 📖 Usage

### Run All Scans (Recommended First Time)
```bash
python syspulse.py
```

### Run Specific Modules

```bash
# Browser profiles only
python syspulse.py --browsers

# Startup programs only
python syspulse.py --startup

# Storage analysis only
python syspulse.py --storage

# Running processes only
python syspulse.py --processes

# Quick scan (faster, less detailed)
python syspulse.py --quick
```

### Example Output

```
==============================================================
Browser Profile Scanner
==============================================================

Found 5 browser profiles
Browsers: Chrome, Edge
Total cache: 8.4 GB
Total extensions: 47
Unused profiles: 2 (5.1 GB wasted)

[Chrome] Personal
  Cache: 1.2 GB
  Last used: 2 days ago
  Extensions: 15
  → Actively used - no action needed

[Chrome] Work
  Cache: 4.2 GB
  Last used: 90 days ago
  Extensions: 23
  → Unused for 90 days, 4.2 GB cache - consider cleaning
```

---

## 🎨 Core Philosophy

1. **On-demand, not always running**
   - Launch when you need it
   - No background processes
   - No startup entries
   - No system tray icon

2. **Understandable, not technical**
   - "Chrome Work Profile" not "Profile 2"
   - "Spotify auto-updater" not "SpotifyWebHelper.exe"
   - Plain English recommendations

3. **Actionable, not just informational**
   - "Safe to disable" not "Unknown impact"
   - "Will free 2.1 GB" not "Some space available"
   - Clear next steps

4. **Focused, not bloated**
   - Top 10 things that matter
   - No registry cleaners (snake oil)
   - No driver updaters (risky)
   - No "optimization" wizards (placebo)

---

## 🛣️ Roadmap

See [ROADMAP.md](ROADMAP.md) for full details.

### ✅ Phase 1: Core Analysis (CURRENT - v1.0)
- ✅ Browser Profile Scanner
- ✅ Startup Impact Analyzer
- ✅ Storage Sense
- ✅ Background Process Explainer
- ✅ CLI Interface

### 🚧 Phase 2: Actionable Controls (NEXT)
- [ ] One-click cache clearing
- [ ] Startup item enable/disable
- [ ] Safe cleanup actions
- [ ] Report generation

### 🔮 Phase 3: Desktop GUI (FUTURE)
- [ ] Native desktop application
- [ ] Visual dashboards
- [ ] Drag-and-drop actions
- [ ] Single executable packaging

### 🌐 Phase 4: Cloud & Companion (FUTURE)
- [ ] Optional cloud insights
- [ ] Mobile/web companion
- [ ] Community recommendations

---

## 🖥️ Platform Support

| Platform | Status | Notes |
|----------|--------|-------|
| Windows 10/11 | ✅ Full Support | Primary target platform |
| Linux | ⚠️ Partial Support | Core features work, some limitations |
| macOS | ⚠️ Partial Support | Core features work, testing needed |

**Windows-specific features**:
- Registry startup scanning
- Windows Update cache
- Full process descriptions

**Cross-platform features**:
- Browser scanning (Chrome, Edge, Firefox)
- Storage analysis
- Process monitoring

---

## 🔒 Safety & Privacy

### What SysPulse Does
- ✅ Read-only analysis (v1.0)
- ✅ Local execution only
- ✅ No telemetry or tracking
- ✅ No network requests
- ✅ Open source

### What SysPulse Does NOT Do
- ❌ Auto-delete files (without explicit confirmation)
- ❌ Modify registry (unless you trigger an action)
- ❌ Send data anywhere
- ❌ Run in background
- ❌ Add startup entries

### Recommendations Safety
- **Safe to disable**: Tested and verified safe
- **DO NOT STOP**: System-critical processes
- **Review before**: Uncertain items marked clearly

---

## 📋 Requirements

- Python 3.10 or higher
- Dependencies (installed via `requirements.txt`):
  - `psutil` - Process and system info
  - `colorama` - Terminal colors
  - `pyyaml` - Configuration
  - `requests` - Future cloud features
  - `tabulate` - Report formatting

**Optional**:
- Windows: Run as Administrator for full registry access
- Linux/Mac: `sudo` for system-wide analysis

---

## 🧪 Testing

Run the test suite to verify all modules work:

```bash
python examples/test_modules.py
```

This will test:
- Browser scanner
- Startup analyzer
- Storage sense
- Process explainer

---

## 🤝 Contributing

SysPulse is in active development. Contributions welcome!

### How to Contribute
1. **Report bugs** - Open an issue
2. **Suggest features** - What would help you?
3. **Add knowledge** - Know a common startup program? Add it to the knowledge base
4. **Test platforms** - Help test on different OS versions
5. **Translate** - Help make SysPulse multilingual

### Adding to Knowledge Base

The knowledge bases are in:
- `modules/startup_analyzer.py` - Startup programs
- `modules/process_explainer.py` - Running processes

Add entries like:
```python
'spotify': {
    'description': 'Spotify music streaming client',
    'impact': StartupImpact.MEDIUM,
    'safe_to_disable': True,
    'recommendation': 'Safe to disable. Opens fast when you want to play music.'
}
```

---

## 📜 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Built with frustration from:
- CCleaner's bloat
- NirSoft's scattered tools
- Windows Settings' fragmentation
- Task Manager's cryptic names

Built with inspiration from:
- WinDirStat's clarity
- Autoruns' power
- Process Explorer's depth
- TreeSize's simplicity

---

## 📞 Support

- **Documentation**: See [QUICKSTART.md](QUICKSTART.md) and [ROADMAP.md](ROADMAP.md)
- **Issues**: Open an issue on GitHub
- **Questions**: Check existing issues first

---

## 🎯 Project Goals

The goal is simple:

> **Give people understandable control over the bullshit that actually impacts their computer.**

Not everything. Just the things that matter.

---

**Made with 🔧 and frustration at bloated utility software.**
