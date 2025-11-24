"""
Browser Profile Scanner Module

Scans Chrome, Edge, Firefox profiles to show:
- Profile names (translated from cryptic folder names)
- Cache sizes
- Last used date
- Installed extensions
- Actionable recommendations
"""

import os
import json
import platform
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class BrowserProfile:
    """Represents a single browser profile with its metadata"""

    def __init__(self, browser: str, name: str, path: Path):
        self.browser = browser
        self.name = name
        self.path = path
        self.cache_size = 0
        self.last_used = None
        self.extensions = []
        self.is_default = False

    def to_dict(self) -> Dict:
        return {
            'browser': self.browser,
            'name': self.name,
            'path': str(self.path),
            'cache_size_mb': round(self.cache_size / (1024 * 1024), 2),
            'cache_size_human': self._human_size(self.cache_size),
            'last_used': self.last_used.isoformat() if self.last_used else 'Never',
            'days_since_used': self._days_since_used(),
            'extensions_count': len(self.extensions),
            'extensions': self.extensions,
            'is_default': self.is_default,
            'recommendation': self._get_recommendation()
        }

    def _human_size(self, size_bytes: int) -> str:
        """Convert bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def _days_since_used(self) -> Optional[int]:
        """Calculate days since profile was last used"""
        if not self.last_used:
            return None
        delta = datetime.now() - self.last_used
        return delta.days

    def _get_recommendation(self) -> str:
        """Generate human-readable recommendation"""
        days = self._days_since_used()
        cache_mb = self.cache_size / (1024 * 1024)

        if days is None:
            return "Profile never used - safe to delete"
        elif days > 90 and cache_mb > 100:
            return f"Unused for {days} days, {self._human_size(self.cache_size)} cache - consider cleaning"
        elif days > 30 and cache_mb > 500:
            return f"Large cache ({self._human_size(self.cache_size)}) - clear cache to free space"
        elif cache_mb > 1000:
            return f"Very large cache ({self._human_size(self.cache_size)}) - recommend clearing"
        elif days > 180:
            return f"Unused for {days} days - safe to delete"
        else:
            return "Actively used - no action needed"


class BrowserScanner:
    """Scans system for browser profiles and analyzes them"""

    def __init__(self):
        self.system = platform.system()
        self.profiles: List[BrowserProfile] = []

    def scan_all(self) -> List[BrowserProfile]:
        """Scan all supported browsers"""
        self.profiles = []

        # Scan Chromium-based browsers
        self._scan_chrome()
        self._scan_edge()

        # Scan Firefox
        self._scan_firefox()

        return self.profiles

    def _get_chrome_base_path(self) -> Optional[Path]:
        """Get Chrome user data directory based on OS"""
        if self.system == "Windows":
            base = Path(os.environ.get('LOCALAPPDATA', '')) / 'Google' / 'Chrome' / 'User Data'
        elif self.system == "Darwin":  # macOS
            base = Path.home() / 'Library' / 'Application Support' / 'Google' / 'Chrome'
        else:  # Linux
            base = Path.home() / '.config' / 'google-chrome'

        return base if base.exists() else None

    def _get_edge_base_path(self) -> Optional[Path]:
        """Get Edge user data directory based on OS"""
        if self.system == "Windows":
            base = Path(os.environ.get('LOCALAPPDATA', '')) / 'Microsoft' / 'Edge' / 'User Data'
        elif self.system == "Darwin":  # macOS
            base = Path.home() / 'Library' / 'Application Support' / 'Microsoft Edge'
        else:  # Linux
            base = Path.home() / '.config' / 'microsoft-edge'

        return base if base.exists() else None

    def _get_firefox_base_path(self) -> Optional[Path]:
        """Get Firefox profiles directory based on OS"""
        if self.system == "Windows":
            base = Path(os.environ.get('APPDATA', '')) / 'Mozilla' / 'Firefox' / 'Profiles'
        elif self.system == "Darwin":  # macOS
            base = Path.home() / 'Library' / 'Application Support' / 'Firefox' / 'Profiles'
        else:  # Linux
            base = Path.home() / '.mozilla' / 'firefox'

        return base if base.exists() else None

    def _scan_chrome(self):
        """Scan Chrome profiles"""
        base_path = self._get_chrome_base_path()
        if not base_path:
            return

        self._scan_chromium_browser('Chrome', base_path)

    def _scan_edge(self):
        """Scan Edge profiles"""
        base_path = self._get_edge_base_path()
        if not base_path:
            return

        self._scan_chromium_browser('Edge', base_path)

    def _scan_chromium_browser(self, browser_name: str, base_path: Path):
        """Scan Chromium-based browser profiles"""
        # Read Local State to get profile info
        local_state_file = base_path / 'Local State'
        profile_names = {}

        if local_state_file.exists():
            try:
                with open(local_state_file, 'r', encoding='utf-8') as f:
                    local_state = json.load(f)
                    profile_info = local_state.get('profile', {}).get('info_cache', {})

                    for profile_key, info in profile_info.items():
                        profile_names[profile_key] = info.get('name', profile_key)
            except Exception as e:
                print(f"Warning: Could not read {browser_name} Local State: {e}")

        # Scan for Default and Profile * directories
        for profile_dir in base_path.iterdir():
            if not profile_dir.is_dir():
                continue

            dir_name = profile_dir.name
            if dir_name == 'Default' or dir_name.startswith('Profile '):
                # Get human-readable name
                profile_name = profile_names.get(dir_name, dir_name)

                # Create profile object
                profile = BrowserProfile(browser_name, profile_name, profile_dir)
                profile.is_default = (dir_name == 'Default')

                # Calculate cache size
                cache_dir = profile_dir / 'Cache' / 'Cache_Data'
                if cache_dir.exists():
                    profile.cache_size = self._calculate_dir_size(cache_dir)

                # Get last used date from Preferences
                prefs_file = profile_dir / 'Preferences'
                if prefs_file.exists():
                    try:
                        profile.last_used = datetime.fromtimestamp(prefs_file.stat().st_mtime)
                    except:
                        pass

                # Get extensions
                extensions_dir = profile_dir / 'Extensions'
                if extensions_dir.exists():
                    profile.extensions = self._get_chrome_extensions(extensions_dir)

                self.profiles.append(profile)

    def _scan_firefox(self):
        """Scan Firefox profiles"""
        base_path = self._get_firefox_base_path()
        if not base_path:
            return

        # Read profiles.ini to get profile info
        profiles_ini = base_path.parent / 'profiles.ini' if self.system != "Windows" else base_path.parent / 'profiles.ini'

        # Scan profile directories
        for profile_dir in base_path.iterdir():
            if not profile_dir.is_dir():
                continue

            # Firefox profiles are named like "xxxxxxxx.default-release"
            profile_name = profile_dir.name.split('.')[-1] if '.' in profile_dir.name else profile_dir.name

            profile = BrowserProfile('Firefox', profile_name, profile_dir)

            # Calculate cache size
            cache_dir = profile_dir / 'cache2'
            if cache_dir.exists():
                profile.cache_size = self._calculate_dir_size(cache_dir)

            # Get last used date
            prefs_file = profile_dir / 'prefs.js'
            if prefs_file.exists():
                try:
                    profile.last_used = datetime.fromtimestamp(prefs_file.stat().st_mtime)
                except:
                    pass

            # Get extensions (simplified)
            extensions_file = profile_dir / 'extensions.json'
            if extensions_file.exists():
                try:
                    with open(extensions_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        addons = data.get('addons', [])
                        profile.extensions = [
                            addon.get('defaultLocale', {}).get('name', addon.get('id', 'Unknown'))
                            for addon in addons
                            if addon.get('type') == 'extension' and addon.get('active', False)
                        ]
                except:
                    pass

            self.profiles.append(profile)

    def _calculate_dir_size(self, directory: Path) -> int:
        """Calculate total size of directory in bytes"""
        total_size = 0
        try:
            for entry in directory.rglob('*'):
                if entry.is_file():
                    try:
                        total_size += entry.stat().st_size
                    except:
                        pass
        except:
            pass
        return total_size

    def _get_chrome_extensions(self, extensions_dir: Path) -> List[str]:
        """Get list of installed Chrome extensions"""
        extensions = []

        try:
            for ext_dir in extensions_dir.iterdir():
                if not ext_dir.is_dir():
                    continue

                # Find the manifest.json in version subdirectory
                for version_dir in ext_dir.iterdir():
                    if version_dir.is_dir():
                        manifest_file = version_dir / 'manifest.json'
                        if manifest_file.exists():
                            try:
                                with open(manifest_file, 'r', encoding='utf-8') as f:
                                    manifest = json.load(f)
                                    name = manifest.get('name', ext_dir.name)

                                    # Chrome uses __MSG_extensionName__ format
                                    if name.startswith('__MSG_'):
                                        # Try to get from messages
                                        messages_file = version_dir / '_locales' / 'en' / 'messages.json'
                                        if not messages_file.exists():
                                            messages_file = version_dir / '_locales' / 'en_US' / 'messages.json'

                                        if messages_file.exists():
                                            try:
                                                with open(messages_file, 'r', encoding='utf-8') as mf:
                                                    messages = json.load(mf)
                                                    key = name.replace('__MSG_', '').replace('__', '')
                                                    name = messages.get(key, {}).get('message', name)
                                            except:
                                                pass

                                    extensions.append(name)
                                    break
                            except:
                                pass
        except:
            pass

        return extensions

    def get_summary(self) -> Dict:
        """Get summary statistics of all profiles"""
        total_cache = sum(p.cache_size for p in self.profiles)
        total_extensions = sum(len(p.extensions) for p in self.profiles)

        unused_profiles = [p for p in self.profiles if (p._days_since_used() or 0) > 90]

        return {
            'total_profiles': len(self.profiles),
            'total_cache_size': self._human_size(total_cache),
            'total_extensions': total_extensions,
            'unused_profiles_count': len(unused_profiles),
            'unused_cache_size': self._human_size(sum(p.cache_size for p in unused_profiles)),
            'browsers_found': list(set(p.browser for p in self.profiles))
        }

    def _human_size(self, size_bytes: int) -> str:
        """Convert bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"


if __name__ == "__main__":
    # Quick test
    scanner = BrowserScanner()
    profiles = scanner.scan_all()

    print(f"Found {len(profiles)} browser profiles:\n")

    for profile in profiles:
        data = profile.to_dict()
        print(f"[{data['browser']}] {data['name']}")
        print(f"  Cache: {data['cache_size_human']}")
        print(f"  Last used: {data['days_since_used']} days ago" if data['days_since_used'] else "  Never used")
        print(f"  Extensions: {data['extensions_count']}")
        print(f"  → {data['recommendation']}")
        print()

    summary = scanner.get_summary()
    print("\n=== Summary ===")
    print(f"Total profiles: {summary['total_profiles']}")
    print(f"Total cache: {summary['total_cache_size']}")
    print(f"Total extensions: {summary['total_extensions']}")
    print(f"Unused profiles: {summary['unused_profiles_count']} ({summary['unused_cache_size']} wasted)")
