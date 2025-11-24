# SysPulse Quick Start

## Installation

1. **Install Python 3.10 or higher** (if not already installed)
   - Windows: Download from python.org
   - Linux: `sudo apt install python3` or `sudo yum install python3`
   - macOS: `brew install python3`

2. **Install dependencies**
   ```bash
   cd syspulse
   pip install -r requirements.txt
   ```

   Or if using virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Usage

### Run All Scans (Recommended First Time)
```bash
python syspulse.py
```

### Run Specific Scans

**Browser Profile Scanner** - See all browser profiles, cache sizes, extensions
```bash
python syspulse.py --browsers
```

**Startup Impact Analyzer** - See what's slowing your boot
```bash
python syspulse.py --startup
```

**Storage Sense** - Find storage hogs and cleanup opportunities
```bash
python syspulse.py --storage
```

**Process Explainer** - See what's running and using resources
```bash
python syspulse.py --processes
```

### Quick Scan (Faster)
```bash
python syspulse.py --quick
```

## What Each Module Does

### 🌐 Browser Profile Scanner
- Finds all Chrome, Edge, Firefox profiles
- Shows cache sizes per profile
- Lists installed extensions
- Identifies unused profiles
- **Example output**: "Chrome Work Profile: 4.2GB cache, unused for 90 days - consider cleaning"

### 🚀 Startup Impact Analyzer
- Lists all startup programs
- Translates cryptic names to human language
- Estimates boot time impact
- Recommends what's safe to disable
- **Example output**: "Spotify Web Helper: Safe to disable. Main app works fine without this."

### 💾 Storage Sense
- Scans temp files, downloads, recycle bin
- Shows large old files
- Identifies safe cleanup opportunities
- Visual breakdown of storage usage
- **Example output**: "Temp Files: 2.1GB - Safe to delete. Will free 2.1GB."

### ⚙️ Process Explainer
- Lists running processes in plain English
- Shows CPU and memory usage
- Explains what each process does
- Recommends which are safe to stop
- **Example output**: "chrome.exe: Google Chrome browser. Multiple instances normal (one per tab)."

## Understanding the Output

**Color Coding** (if terminal supports colors):
- 🔴 Red: High impact / Should review
- 🟡 Yellow: Medium impact / Consider reviewing
- 🟢 Green: Normal / No action needed
- 🔵 Cyan: Recommendations

**Impact Levels**:
- **HIGH**: Significant effect on boot/performance (5+ seconds)
- **MEDIUM**: Moderate effect (2-5 seconds)
- **LOW**: Minimal effect (<2 seconds)

## Safety Notes

⚠️ **Always read recommendations before disabling/deleting anything**

✅ **Safe to disable/clean**:
- Browser caches
- Temp files
- Most updater services
- Unused startup programs
- Old downloads

❌ **DO NOT disable/delete**:
- System processes (Windows Defender, etc.)
- Driver services (NVIDIA, Realtek, etc.)
- Anything marked "DO NOT STOP"

## Troubleshooting

**"No browser profiles found"**
- Make sure you have Chrome, Edge, or Firefox installed
- Try running with administrator/sudo privileges

**"Permission denied" errors**
- Windows: Run as Administrator
- Linux/Mac: Use `sudo python syspulse.py`

**Missing dependencies**
- Run: `pip install -r requirements.txt`

**Colors not showing**
- Install colorama: `pip install colorama`

## Next Steps

After running SysPulse:

1. **Review recommendations** - Read what each module suggests
2. **Take action manually** - For now, manually disable/delete based on recommendations
3. **Future versions** - Will include one-click actions

## Tips

- Run `--browsers` regularly to catch cache buildup
- Run `--startup` after installing new software
- Run `--storage` when disk space is low
- Run `--processes` if computer feels slow

## Platform-Specific Notes

### Windows
- Some scans require Administrator privileges for full access
- Registry startup items may need admin to view all entries

### Linux
- May need sudo for system-wide analysis
- Supports autostart .desktop files

### macOS
- Supports Launch Agents
- Some features limited compared to Windows

## Getting Help

- Check the README.md for full documentation
- Review module code for technical details
- Each module can be run standalone for testing

---

**Remember**: SysPulse is read-only. It analyzes and recommends, but doesn't automatically change anything. You're always in control.
