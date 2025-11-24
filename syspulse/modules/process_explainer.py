"""
Background Process Explainer Module

Translates running processes into human language:
- What the process actually does
- Why it's running
- Resource usage (CPU, RAM)
- Safe to kill or not
- Recommendations
"""

import psutil
import platform
from typing import List, Dict, Optional
from collections import defaultdict


class ProcessInfo:
    """Represents a running process with human-readable context"""

    def __init__(self, pid: int, name: str, cpu_percent: float, memory_mb: float, username: str = ""):
        self.pid = pid
        self.name = name
        self.cpu_percent = cpu_percent
        self.memory_mb = memory_mb
        self.username = username
        self.description = ""
        self.category = "Unknown"
        self.safe_to_kill = None
        self.recommendation = ""

        # Analyze the process
        self._analyze()

    def _analyze(self):
        """Analyze process and determine description/category"""
        lower_name = self.name.lower()

        # Apply knowledge base
        self._apply_knowledge_base(lower_name)

        # If not in knowledge base, infer from name
        if not self.description:
            self._infer_description(lower_name)

    def _apply_knowledge_base(self, name: str):
        """Apply known process knowledge base"""

        knowledge_base = {
            # System critical
            'system': {
                'description': 'Windows core system process',
                'category': 'System Critical',
                'safe_to_kill': False,
                'recommendation': 'DO NOT STOP. Critical Windows process.'
            },
            'csrss.exe': {
                'description': 'Windows client/server runtime',
                'category': 'System Critical',
                'safe_to_kill': False,
                'recommendation': 'DO NOT STOP. System will crash.'
            },
            'winlogon.exe': {
                'description': 'Windows login handler',
                'category': 'System Critical',
                'safe_to_kill': False,
                'recommendation': 'DO NOT STOP. Handles user login.'
            },
            'explorer.exe': {
                'description': 'Windows desktop and file explorer',
                'category': 'System Core',
                'safe_to_kill': True,
                'recommendation': 'Can restart if desktop freezes, but will close all Explorer windows.'
            },
            'dwm.exe': {
                'description': 'Desktop Window Manager (handles visual effects)',
                'category': 'System Core',
                'safe_to_kill': False,
                'recommendation': 'DO NOT STOP. Handles window rendering.'
            },

            # svchost (Windows services host)
            'svchost.exe': {
                'description': 'Windows services host (runs multiple background services)',
                'category': 'System Services',
                'safe_to_kill': False,
                'recommendation': 'DO NOT STOP. Multiple instances are normal - each hosts different Windows services.'
            },

            # Browsers
            'chrome.exe': {
                'description': 'Google Chrome browser',
                'category': 'Browser',
                'safe_to_kill': True,
                'recommendation': 'Safe to close. Multiple instances are normal (one per tab/extension).'
            },
            'firefox.exe': {
                'description': 'Mozilla Firefox browser',
                'category': 'Browser',
                'safe_to_kill': True,
                'recommendation': 'Safe to close if not using.'
            },
            'msedge.exe': {
                'description': 'Microsoft Edge browser',
                'category': 'Browser',
                'safe_to_kill': True,
                'recommendation': 'Safe to close. Multiple instances are normal.'
            },
            'brave.exe': {
                'description': 'Brave browser',
                'category': 'Browser',
                'safe_to_kill': True,
                'recommendation': 'Safe to close if not using.'
            },

            # Communication
            'slack.exe': {
                'description': 'Slack messaging app',
                'category': 'Communication',
                'safe_to_kill': True,
                'recommendation': 'Safe to close. Will stop notifications.'
            },
            'teams.exe': {
                'description': 'Microsoft Teams',
                'category': 'Communication',
                'safe_to_kill': True,
                'recommendation': 'Safe to close if not in a meeting.'
            },
            'discord.exe': {
                'description': 'Discord voice/chat app',
                'category': 'Communication',
                'safe_to_kill': True,
                'recommendation': 'Safe to close if not using.'
            },
            'zoom.exe': {
                'description': 'Zoom video conferencing',
                'category': 'Communication',
                'safe_to_kill': True,
                'recommendation': 'Safe to close if not in a meeting.'
            },

            # Development
            'code.exe': {
                'description': 'Visual Studio Code editor',
                'category': 'Development',
                'safe_to_kill': True,
                'recommendation': 'Safe to close. Save work first.'
            },
            'devenv.exe': {
                'description': 'Visual Studio IDE',
                'category': 'Development',
                'safe_to_kill': True,
                'recommendation': 'Safe to close. Save work first.'
            },
            'node.exe': {
                'description': 'Node.js JavaScript runtime (likely running a dev server)',
                'category': 'Development',
                'safe_to_kill': True,
                'recommendation': 'Safe to close. May be running a development server.'
            },
            'python.exe': {
                'description': 'Python interpreter (running a script or application)',
                'category': 'Development',
                'safe_to_kill': True,
                'recommendation': 'Safe to close if you know what script is running.'
            },

            # Cloud/Sync
            'onedrive.exe': {
                'description': 'Microsoft OneDrive cloud sync',
                'category': 'Cloud Storage',
                'safe_to_kill': True,
                'recommendation': 'Safe to close. Files will stop syncing until restarted.'
            },
            'dropbox.exe': {
                'description': 'Dropbox cloud sync',
                'category': 'Cloud Storage',
                'safe_to_kill': True,
                'recommendation': 'Safe to close. Files will stop syncing.'
            },
            'googledrivesync.exe': {
                'description': 'Google Drive sync client',
                'category': 'Cloud Storage',
                'safe_to_kill': True,
                'recommendation': 'Safe to close. Files will stop syncing.'
            },

            # Media
            'spotify.exe': {
                'description': 'Spotify music streaming',
                'category': 'Media',
                'safe_to_kill': True,
                'recommendation': 'Safe to close. Music will stop.'
            },
            'vlc.exe': {
                'description': 'VLC media player',
                'category': 'Media',
                'safe_to_kill': True,
                'recommendation': 'Safe to close.'
            },

            # Gaming
            'steam.exe': {
                'description': 'Steam gaming platform',
                'category': 'Gaming',
                'safe_to_kill': True,
                'recommendation': 'Safe to close if not gaming. May have multiple instances.'
            },
            'epicgameslauncher.exe': {
                'description': 'Epic Games launcher',
                'category': 'Gaming',
                'safe_to_kill': True,
                'recommendation': 'Safe to close if not gaming.'
            },

            # Antivirus/Security
            'msmpeng.exe': {
                'description': 'Windows Defender antivirus engine',
                'category': 'Security',
                'safe_to_kill': False,
                'recommendation': 'DO NOT STOP. Protects your computer from malware.'
            },
            'defender': {
                'description': 'Windows Defender security',
                'category': 'Security',
                'safe_to_kill': False,
                'recommendation': 'DO NOT STOP. System security.'
            },

            # Background updaters
            'googleupdate.exe': {
                'description': 'Google software updater',
                'category': 'Updater',
                'safe_to_kill': True,
                'recommendation': 'Safe to close. Google apps will still work.'
            },
            'adobearm.exe': {
                'description': 'Adobe Acrobat update service',
                'category': 'Updater',
                'safe_to_kill': True,
                'recommendation': 'Safe to close. Adobe products will still work.'
            },

            # Nvidia/Graphics
            'nvcontainer.exe': {
                'description': 'NVIDIA graphics driver service container',
                'category': 'Graphics Driver',
                'safe_to_kill': False,
                'recommendation': 'Keep running. Manages NVIDIA graphics features.'
            },
            'nvidia': {
                'description': 'NVIDIA graphics driver component',
                'category': 'Graphics Driver',
                'safe_to_kill': False,
                'recommendation': 'Keep running. Needed for graphics performance.'
            },
        }

        # Check knowledge base
        for key, data in knowledge_base.items():
            if key in name:
                self.description = data['description']
                self.category = data['category']
                self.safe_to_kill = data['safe_to_kill']
                self.recommendation = data['recommendation']
                return

    def _infer_description(self, name: str):
        """Infer description from process name if not in knowledge base"""

        if 'update' in name or 'updater' in name:
            self.description = f'{self.name} - Software updater'
            self.category = 'Updater'
            self.safe_to_kill = True
            self.recommendation = 'Likely safe to close. Software will still work.'

        elif 'helper' in name or 'agent' in name:
            self.description = f'{self.name} - Background helper service'
            self.category = 'Background Service'
            self.safe_to_kill = True
            self.recommendation = 'Likely safe to close if using too many resources.'

        elif 'service' in name or 'svc' in name:
            self.description = f'{self.name} - Background service'
            self.category = 'Service'
            self.safe_to_kill = False
            self.recommendation = 'Research before stopping. May be needed by system.'

        elif name.startswith('python') or name.startswith('node'):
            self.description = f'{self.name} - Runtime executing a script'
            self.category = 'Development/Script'
            self.safe_to_kill = True
            self.recommendation = 'Check what script is running before stopping.'

        else:
            self.description = f'{self.name}'
            self.category = 'Unknown'
            self.safe_to_kill = None
            self.recommendation = 'Unknown process. Research before stopping.'

    def to_dict(self) -> Dict:
        """Convert to dictionary for export/display"""
        return {
            'pid': self.pid,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'cpu_percent': round(self.cpu_percent, 1),
            'memory_mb': round(self.memory_mb, 1),
            'username': self.username,
            'safe_to_kill': self.safe_to_kill,
            'recommendation': self.recommendation
        }


class ProcessExplainer:
    """Scans and explains running processes"""

    def __init__(self):
        self.processes: List[ProcessInfo] = []

    def scan_all(self, min_cpu: float = 0, min_memory_mb: float = 0) -> List[ProcessInfo]:
        """
        Scan all running processes

        Args:
            min_cpu: Minimum CPU% to include (0 = all)
            min_memory_mb: Minimum memory MB to include (0 = all)
        """
        self.processes = []

        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'username']):
            try:
                pid = proc.info['pid']
                name = proc.info['name'] or 'Unknown'
                cpu = proc.info['cpu_percent'] or 0
                memory_bytes = proc.info['memory_info'].rss if proc.info['memory_info'] else 0
                memory_mb = memory_bytes / (1024 * 1024)
                username = proc.info['username'] or ''

                # Filter by thresholds
                if cpu < min_cpu and memory_mb < min_memory_mb:
                    continue

                process_info = ProcessInfo(pid, name, cpu, memory_mb, username)
                self.processes.append(process_info)

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return self.processes

    def get_top_cpu(self, count: int = 10) -> List[ProcessInfo]:
        """Get top CPU-consuming processes"""
        return sorted(self.processes, key=lambda p: p.cpu_percent, reverse=True)[:count]

    def get_top_memory(self, count: int = 10) -> List[ProcessInfo]:
        """Get top memory-consuming processes"""
        return sorted(self.processes, key=lambda p: p.memory_mb, reverse=True)[:count]

    def get_by_category(self) -> Dict[str, List[ProcessInfo]]:
        """Group processes by category"""
        categories = defaultdict(list)
        for proc in self.processes:
            categories[proc.category].append(proc)
        return dict(categories)

    def get_summary(self) -> Dict:
        """Get summary statistics"""
        total_cpu = sum(p.cpu_percent for p in self.processes)
        total_memory_mb = sum(p.memory_mb for p in self.processes)

        categories = self.get_by_category()

        # Find resource hogs
        cpu_hogs = [p for p in self.processes if p.cpu_percent > 10]
        memory_hogs = [p for p in self.processes if p.memory_mb > 500]

        return {
            'total_processes': len(self.processes),
            'total_cpu_percent': round(total_cpu, 1),
            'total_memory_mb': round(total_memory_mb, 1),
            'total_memory_gb': round(total_memory_mb / 1024, 2),
            'categories': {cat: len(procs) for cat, procs in categories.items()},
            'cpu_hogs_count': len(cpu_hogs),
            'memory_hogs_count': len(memory_hogs),
            'top_cpu': [p.to_dict() for p in self.get_top_cpu(5)],
            'top_memory': [p.to_dict() for p in self.get_top_memory(5)]
        }


if __name__ == "__main__":
    # Quick test
    explainer = ProcessExplainer()

    print("Scanning processes (this may take a moment)...\n")
    processes = explainer.scan_all(min_memory_mb=50)  # Only show processes using > 50MB

    print(f"=== Top CPU Consumers ===\n")
    for proc in explainer.get_top_cpu(5):
        data = proc.to_dict()
        print(f"[{data['cpu_percent']}%] {data['name']}")
        print(f"  {data['description']}")
        print(f"  Memory: {data['memory_mb']:.1f} MB")
        print(f"  → {data['recommendation']}")
        print()

    print(f"\n=== Top Memory Consumers ===\n")
    for proc in explainer.get_top_memory(5):
        data = proc.to_dict()
        print(f"[{data['memory_mb']:.1f} MB] {data['name']}")
        print(f"  {data['description']}")
        print(f"  CPU: {data['cpu_percent']}%")
        print(f"  → {data['recommendation']}")
        print()

    summary = explainer.get_summary()
    print("\n=== Summary ===")
    print(f"Total processes: {summary['total_processes']}")
    print(f"Total CPU usage: {summary['total_cpu_percent']}%")
    print(f"Total memory: {summary['total_memory_gb']} GB")
    print(f"CPU hogs (>10%): {summary['cpu_hogs_count']}")
    print(f"Memory hogs (>500MB): {summary['memory_hogs_count']}")
