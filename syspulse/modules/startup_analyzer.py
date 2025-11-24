"""
Startup Impact Analyzer Module

Scans startup programs and translates them into human language:
- What the program actually does
- Impact on boot time (High/Medium/Low)
- Safe to disable or not
- Recommendations
"""

import os
import platform
import winreg
from pathlib import Path
from typing import List, Dict, Optional
from enum import Enum


class StartupImpact(Enum):
    """Startup impact levels"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    UNKNOWN = "Unknown"


class StartupItem:
    """Represents a single startup program"""

    def __init__(self, name: str, command: str, location: str):
        self.name = name
        self.command = command
        self.location = location  # Registry, Startup folder, Task Scheduler, etc.
        self.impact = StartupImpact.UNKNOWN
        self.description = ""
        self.safe_to_disable = None
        self.recommendation = ""

        # Analyze the startup item
        self._analyze()

    def _analyze(self):
        """Analyze startup item and determine impact/description"""
        lower_name = self.name.lower()
        lower_cmd = self.command.lower()

        # Apply knowledge base
        self._apply_knowledge_base(lower_name, lower_cmd)

        # If not in knowledge base, make educated guess
        if not self.description:
            self._infer_description()

    def _apply_knowledge_base(self, name: str, cmd: str):
        """Apply known startup programs knowledge base"""

        # Common startup programs with translations
        knowledge_base = {
            # Cloud storage
            'onedrive': {
                'description': 'Microsoft OneDrive cloud storage sync',
                'impact': StartupImpact.MEDIUM,
                'safe_to_disable': True,
                'recommendation': 'Safe to disable if you don\'t use OneDrive. You can launch it manually when needed.'
            },
            'dropbox': {
                'description': 'Dropbox cloud storage sync',
                'impact': StartupImpact.MEDIUM,
                'safe_to_disable': True,
                'recommendation': 'Safe to disable if you don\'t actively sync files. Launch manually when needed.'
            },
            'googledrivesync': {
                'description': 'Google Drive cloud storage sync',
                'impact': StartupImpact.MEDIUM,
                'safe_to_disable': True,
                'recommendation': 'Safe to disable. Drive will still work in browser; launch manually for sync.'
            },

            # Communication
            'slack': {
                'description': 'Slack messaging client',
                'impact': StartupImpact.MEDIUM,
                'safe_to_disable': True,
                'recommendation': 'Safe to disable. Launch Slack manually when you start work.'
            },
            'discord': {
                'description': 'Discord messaging/voice chat',
                'impact': StartupImpact.MEDIUM,
                'safe_to_disable': True,
                'recommendation': 'Safe to disable. Open Discord when you need it.'
            },
            'teams': {
                'description': 'Microsoft Teams communication platform',
                'impact': StartupImpact.HIGH,
                'safe_to_disable': True,
                'recommendation': 'High boot impact. Safe to disable - launch manually before meetings.'
            },

            # Media
            'spotify': {
                'description': 'Spotify music streaming client',
                'impact': StartupImpact.MEDIUM,
                'safe_to_disable': True,
                'recommendation': 'Safe to disable. Opens fast when you want to play music.'
            },
            'spotifywebhelper': {
                'description': 'Spotify web helper/updater (not needed for app to work)',
                'impact': StartupImpact.LOW,
                'safe_to_disable': True,
                'recommendation': 'Safe to disable. Main Spotify app works fine without this.'
            },
            'itunes': {
                'description': 'Apple iTunes media player',
                'impact': StartupImpact.MEDIUM,
                'safe_to_disable': True,
                'recommendation': 'Safe to disable unless you actively sync devices.'
            },

            # Updaters
            'googleupdate': {
                'description': 'Google software updater (Chrome, Drive, etc.)',
                'impact': StartupImpact.LOW,
                'safe_to_disable': True,
                'recommendation': 'Safe to disable. Apps will still update, just not in background.'
            },
            'adobearm': {
                'description': 'Adobe Acrobat update service',
                'impact': StartupImpact.LOW,
                'safe_to_disable': True,
                'recommendation': 'Safe to disable. Adobe products will still work and prompt for updates.'
            },
            'ccleaner': {
                'description': 'CCleaner monitoring service',
                'impact': StartupImpact.LOW,
                'safe_to_disable': True,
                'recommendation': 'Safe to disable. Run CCleaner manually when you want to clean.'
            },

            # Gaming
            'steam': {
                'description': 'Steam gaming platform',
                'impact': StartupImpact.HIGH,
                'safe_to_disable': True,
                'recommendation': 'High boot impact. Safe to disable - launch when you want to game.'
            },
            'epicgameslauncher': {
                'description': 'Epic Games launcher',
                'impact': StartupImpact.MEDIUM,
                'safe_to_disable': True,
                'recommendation': 'Safe to disable. Opens quickly when you launch a game.'
            },
            'nvidia': {
                'description': 'NVIDIA graphics control panel/updater',
                'impact': StartupImpact.LOW,
                'safe_to_disable': False,
                'recommendation': 'Keep enabled. Needed for graphics driver features.'
            },

            # Utilities
            'evernote': {
                'description': 'Evernote note-taking app sync',
                'impact': StartupImpact.MEDIUM,
                'safe_to_disable': True,
                'recommendation': 'Safe to disable. Launch manually when you need notes.'
            },
            'skype': {
                'description': 'Skype communication app',
                'impact': StartupImpact.MEDIUM,
                'safe_to_disable': True,
                'recommendation': 'Safe to disable. Launch before calls.'
            },

            # System critical (don't disable)
            'windows defender': {
                'description': 'Windows security/antivirus protection',
                'impact': StartupImpact.LOW,
                'safe_to_disable': False,
                'recommendation': 'DO NOT DISABLE. Critical for system security.'
            },
            'realtek': {
                'description': 'Realtek audio driver controls',
                'impact': StartupImpact.LOW,
                'safe_to_disable': False,
                'recommendation': 'Keep enabled. Needed for audio to work properly.'
            },
            'intel': {
                'description': 'Intel graphics/chipset utilities',
                'impact': StartupImpact.LOW,
                'safe_to_disable': False,
                'recommendation': 'Keep enabled. System hardware management.'
            },
        }

        # Check knowledge base
        for key, data in knowledge_base.items():
            if key in name or key in cmd:
                self.description = data['description']
                self.impact = data['impact']
                self.safe_to_disable = data['safe_to_disable']
                self.recommendation = data['recommendation']
                return

    def _infer_description(self):
        """Infer description from name/path if not in knowledge base"""
        lower_name = self.name.lower()
        lower_cmd = self.command.lower()

        # Heuristics for common patterns
        if 'update' in lower_name or 'updater' in lower_name:
            self.description = f'{self.name} auto-updater service'
            self.impact = StartupImpact.LOW
            self.safe_to_disable = True
            self.recommendation = 'Likely safe to disable. Software will still update when launched.'

        elif 'helper' in lower_name or 'agent' in lower_name:
            self.description = f'{self.name} background helper service'
            self.impact = StartupImpact.LOW
            self.safe_to_disable = True
            self.recommendation = 'Likely safe to disable. Usually not critical for main app.'

        elif 'sync' in lower_name:
            self.description = f'{self.name} file/data synchronization'
            self.impact = StartupImpact.MEDIUM
            self.safe_to_disable = True
            self.recommendation = 'Safe to disable if you don\'t need constant syncing.'

        elif '.exe' not in lower_cmd:
            self.description = f'{self.name} (may be a script or shortcut)'
            self.impact = StartupImpact.UNKNOWN
            self.safe_to_disable = None
            self.recommendation = 'Review command to understand what this does.'

        else:
            # Generic unknown
            self.description = f'{self.name}'
            self.impact = StartupImpact.UNKNOWN
            self.safe_to_disable = None
            self.recommendation = 'Unknown program. Research before disabling.'

    def to_dict(self) -> Dict:
        """Convert to dictionary for export/display"""
        return {
            'name': self.name,
            'description': self.description,
            'command': self.command,
            'location': self.location,
            'impact': self.impact.value,
            'safe_to_disable': self.safe_to_disable,
            'recommendation': self.recommendation
        }


class StartupAnalyzer:
    """Scans and analyzes startup programs"""

    def __init__(self):
        self.system = platform.system()
        self.startup_items: List[StartupItem] = []

    def scan_all(self) -> List[StartupItem]:
        """Scan all startup locations"""
        self.startup_items = []

        if self.system == "Windows":
            self._scan_windows_registry()
            self._scan_windows_startup_folder()
        elif self.system == "Linux":
            self._scan_linux_autostart()
        elif self.system == "Darwin":
            self._scan_macos_launch_agents()

        return self.startup_items

    def _scan_windows_registry(self):
        """Scan Windows registry for startup items"""
        if self.system != "Windows":
            return

        # Registry locations to check
        registry_paths = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
        ]

        for hive, path in registry_paths:
            try:
                key = winreg.OpenKey(hive, path, 0, winreg.KEY_READ)
                index = 0

                while True:
                    try:
                        name, command, _ = winreg.EnumValue(key, index)
                        location = f"Registry: {path}"

                        item = StartupItem(name, command, location)
                        self.startup_items.append(item)

                        index += 1
                    except OSError:
                        break

                winreg.CloseKey(key)
            except Exception as e:
                # Key doesn't exist or can't be accessed
                pass

    def _scan_windows_startup_folder(self):
        """Scan Windows Startup folder"""
        if self.system != "Windows":
            return

        startup_folders = [
            Path(os.environ.get('APPDATA', '')) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup',
            Path(os.environ.get('PROGRAMDATA', '')) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup',
        ]

        for folder in startup_folders:
            if not folder.exists():
                continue

            for item in folder.iterdir():
                if item.is_file():
                    name = item.stem
                    command = str(item)
                    location = f"Startup Folder: {folder.name}"

                    startup_item = StartupItem(name, command, location)
                    self.startup_items.append(startup_item)

    def _scan_linux_autostart(self):
        """Scan Linux autostart .desktop files"""
        autostart_dirs = [
            Path.home() / '.config' / 'autostart',
            Path('/etc/xdg/autostart')
        ]

        for directory in autostart_dirs:
            if not directory.exists():
                continue

            for item in directory.glob('*.desktop'):
                # Parse .desktop file
                name = item.stem
                command = ""

                try:
                    with open(item, 'r') as f:
                        for line in f:
                            if line.startswith('Exec='):
                                command = line.split('=', 1)[1].strip()
                                break
                except:
                    pass

                location = f"Autostart: {directory}"
                startup_item = StartupItem(name, command, location)
                self.startup_items.append(startup_item)

    def _scan_macos_launch_agents(self):
        """Scan macOS Launch Agents"""
        launch_dirs = [
            Path.home() / 'Library' / 'LaunchAgents',
            Path('/Library/LaunchAgents'),
            Path('/System/Library/LaunchAgents')
        ]

        for directory in launch_dirs:
            if not directory.exists():
                continue

            for item in directory.glob('*.plist'):
                name = item.stem
                command = str(item)
                location = f"Launch Agent: {directory.name}"

                startup_item = StartupItem(name, command, location)
                self.startup_items.append(startup_item)

    def get_summary(self) -> Dict:
        """Get summary statistics"""
        high_impact = [item for item in self.startup_items if item.impact == StartupImpact.HIGH]
        medium_impact = [item for item in self.startup_items if item.impact == StartupImpact.MEDIUM]
        safe_to_disable = [item for item in self.startup_items if item.safe_to_disable]

        # Estimate boot delay (rough calculation)
        impact_delays = {
            StartupImpact.HIGH: 5,
            StartupImpact.MEDIUM: 2,
            StartupImpact.LOW: 0.5,
            StartupImpact.UNKNOWN: 1
        }

        estimated_delay = sum(impact_delays.get(item.impact, 0) for item in self.startup_items)
        potential_savings = sum(impact_delays.get(item.impact, 0) for item in safe_to_disable)

        return {
            'total_items': len(self.startup_items),
            'high_impact_count': len(high_impact),
            'medium_impact_count': len(medium_impact),
            'safe_to_disable_count': len(safe_to_disable),
            'estimated_boot_delay_seconds': round(estimated_delay),
            'potential_savings_seconds': round(potential_savings),
            'high_impact_items': [item.name for item in high_impact],
            'top_recommendations': [
                item.to_dict() for item in sorted(
                    safe_to_disable,
                    key=lambda x: ['HIGH', 'MEDIUM', 'LOW', 'UNKNOWN'].index(x.impact.value)
                )[:5]
            ]
        }


if __name__ == "__main__":
    # Quick test
    analyzer = StartupAnalyzer()
    items = analyzer.scan_all()

    print(f"Found {len(items)} startup items:\n")

    for item in items:
        data = item.to_dict()
        print(f"[{data['impact']}] {data['name']}")
        print(f"  {data['description']}")
        print(f"  → {data['recommendation']}")
        print()

    summary = analyzer.get_summary()
    print("\n=== Summary ===")
    print(f"Total startup items: {summary['total_items']}")
    print(f"High impact: {summary['high_impact_count']}")
    print(f"Safe to disable: {summary['safe_to_disable_count']}")
    print(f"Estimated boot delay: ~{summary['estimated_boot_delay_seconds']} seconds")
    print(f"Potential savings: ~{summary['potential_savings_seconds']} seconds")
