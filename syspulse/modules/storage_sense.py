"""
Storage Sense Module

Identifies storage hogs and provides safe cleanup options:
- Temp files
- Browser cache (via browser_scanner)
- Recycle bin
- Downloads folder
- Large old files
- Duplicate files (future)
- Visual breakdown
"""

import os
import shutil
import platform
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from collections import defaultdict


class StorageCategory:
    """Represents a category of storage usage"""

    def __init__(self, name: str, description: str, path: Optional[Path] = None):
        self.name = name
        self.description = description
        self.path = path
        self.size_bytes = 0
        self.file_count = 0
        self.safe_to_clean = False
        self.recommendation = ""
        self.items: List[Dict] = []

    def add_item(self, item_path: Path, size: int):
        """Add a file/folder to this category"""
        self.items.append({
            'path': str(item_path),
            'size': size,
            'modified': datetime.fromtimestamp(item_path.stat().st_mtime)
        })
        self.size_bytes += size
        self.file_count += 1

    def to_dict(self) -> Dict:
        """Convert to dictionary for export/display"""
        return {
            'name': self.name,
            'description': self.description,
            'path': str(self.path) if self.path else None,
            'size_bytes': self.size_bytes,
            'size_human': self._human_size(self.size_bytes),
            'file_count': self.file_count,
            'safe_to_clean': self.safe_to_clean,
            'recommendation': self.recommendation,
            'top_items': sorted(
                self.items,
                key=lambda x: x['size'],
                reverse=True
            )[:10]  # Top 10 largest
        }

    def _human_size(self, size_bytes: int) -> str:
        """Convert bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"


class StorageSense:
    """Analyzes storage usage and identifies cleanup opportunities"""

    def __init__(self):
        self.system = platform.system()
        self.categories: List[StorageCategory] = []

    def scan_all(self, quick_scan: bool = False) -> List[StorageCategory]:
        """
        Scan all storage categories

        Args:
            quick_scan: If True, skip deep scans (faster but less accurate)
        """
        self.categories = []

        # Scan temp files
        self._scan_temp_files()

        # Scan recycle bin
        self._scan_recycle_bin()

        # Scan downloads folder
        self._scan_downloads()

        # Scan logs
        self._scan_log_files()

        # Scan Windows specific
        if self.system == "Windows":
            self._scan_windows_update_cache()
            self._scan_windows_installer_cache()

        # Deep scans (optional)
        if not quick_scan:
            self._scan_large_files()
            self._scan_old_files()

        return self.categories

    def _scan_temp_files(self):
        """Scan temporary files"""
        category = StorageCategory(
            "Temp Files",
            "Temporary files that can be safely deleted",
        )
        category.safe_to_clean = True

        temp_dirs = []

        if self.system == "Windows":
            temp_dirs = [
                Path(os.environ.get('TEMP', '')),
                Path(os.environ.get('TMP', '')),
                Path(os.environ.get('LOCALAPPDATA', '')) / 'Temp',
            ]
        else:
            temp_dirs = [
                Path('/tmp'),
                Path('/var/tmp'),
            ]

        for temp_dir in temp_dirs:
            if not temp_dir or not temp_dir.exists():
                continue

            try:
                for item in temp_dir.iterdir():
                    try:
                        if item.is_file():
                            size = item.stat().st_size
                            category.add_item(item, size)
                        elif item.is_dir():
                            size = self._get_dir_size(item)
                            category.add_item(item, size)
                    except:
                        pass
            except:
                pass

        if category.size_bytes > 0:
            category.recommendation = f"Safe to delete. Will free {category._human_size(category.size_bytes)}."
        else:
            category.recommendation = "Already clean."

        self.categories.append(category)

    def _scan_recycle_bin(self):
        """Scan recycle bin"""
        category = StorageCategory(
            "Recycle Bin",
            "Deleted files waiting to be permanently removed"
        )
        category.safe_to_clean = True

        if self.system == "Windows":
            # Windows Recycle Bin
            drives = []
            try:
                import string
                from ctypes import windll

                bitmask = windll.kernel32.GetLogicalDrives()
                for letter in string.ascii_uppercase:
                    if bitmask & 1:
                        drives.append(f"{letter}:")
                    bitmask >>= 1
            except:
                drives = ['C:']

            for drive in drives:
                recycle_path = Path(drive) / '$Recycle.Bin'
                if recycle_path.exists():
                    try:
                        size = self._get_dir_size(recycle_path)
                        if size > 0:
                            category.add_item(recycle_path, size)
                    except:
                        pass

        elif self.system == "Darwin":
            # macOS Trash
            trash_path = Path.home() / '.Trash'
            if trash_path.exists():
                size = self._get_dir_size(trash_path)
                if size > 0:
                    category.add_item(trash_path, size)

        else:
            # Linux Trash
            trash_path = Path.home() / '.local' / 'share' / 'Trash'
            if trash_path.exists():
                size = self._get_dir_size(trash_path)
                if size > 0:
                    category.add_item(trash_path, size)

        if category.size_bytes > 0:
            category.recommendation = f"Empty recycle bin to free {category._human_size(category.size_bytes)}."
        else:
            category.recommendation = "Already empty."

        self.categories.append(category)

    def _scan_downloads(self):
        """Scan downloads folder for old files"""
        downloads_path = Path.home() / 'Downloads'

        if not downloads_path.exists():
            return

        category = StorageCategory(
            "Old Downloads",
            "Files in Downloads folder older than 90 days",
            downloads_path
        )
        category.safe_to_clean = True

        cutoff_date = datetime.now() - timedelta(days=90)

        try:
            for item in downloads_path.iterdir():
                try:
                    mtime = datetime.fromtimestamp(item.stat().st_mtime)
                    if mtime < cutoff_date:
                        if item.is_file():
                            size = item.stat().st_size
                        else:
                            size = self._get_dir_size(item)

                        category.add_item(item, size)
                except:
                    pass
        except:
            pass

        if category.size_bytes > 0:
            category.recommendation = f"Review {category.file_count} old files. Can free {category._human_size(category.size_bytes)}."
        else:
            category.recommendation = "No old files found."

        self.categories.append(category)

    def _scan_log_files(self):
        """Scan system log files"""
        category = StorageCategory(
            "Log Files",
            "System and application log files"
        )
        category.safe_to_clean = False  # Be careful with logs

        log_dirs = []

        if self.system == "Windows":
            log_dirs = [
                Path(os.environ.get('SYSTEMROOT', 'C:\\Windows')) / 'Logs',
                Path(os.environ.get('PROGRAMDATA', '')) / 'Logs',
            ]
        else:
            log_dirs = [
                Path('/var/log'),
                Path.home() / '.local' / 'share' / 'logs',
            ]

        for log_dir in log_dirs:
            if not log_dir or not log_dir.exists():
                continue

            try:
                for item in log_dir.rglob('*.log'):
                    try:
                        size = item.stat().st_size
                        if size > 10 * 1024 * 1024:  # Only report logs > 10MB
                            category.add_item(item, size)
                    except:
                        pass
            except:
                pass

        if category.size_bytes > 0:
            category.recommendation = f"Large log files found. Review before deleting."
        else:
            category.recommendation = "No large log files."

        self.categories.append(category)

    def _scan_windows_update_cache(self):
        """Scan Windows Update cache"""
        if self.system != "Windows":
            return

        category = StorageCategory(
            "Windows Update Cache",
            "Downloaded Windows updates (can be re-downloaded if needed)"
        )
        category.safe_to_clean = True

        update_paths = [
            Path(os.environ.get('SYSTEMROOT', 'C:\\Windows')) / 'SoftwareDistribution' / 'Download',
        ]

        for path in update_paths:
            if path.exists():
                try:
                    size = self._get_dir_size(path)
                    if size > 0:
                        category.add_item(path, size)
                except:
                    pass

        if category.size_bytes > 0:
            category.recommendation = f"Safe to clean. Will free {category._human_size(category.size_bytes)}. Updates can be re-downloaded."
        else:
            category.recommendation = "Already clean."

        self.categories.append(category)

    def _scan_windows_installer_cache(self):
        """Scan Windows Installer cache"""
        if self.system != "Windows":
            return

        category = StorageCategory(
            "Windows Installer Cache",
            "Cached installation files"
        )
        category.safe_to_clean = False  # Can cause issues if cleaned

        installer_path = Path(os.environ.get('SYSTEMROOT', 'C:\\Windows')) / 'Installer'

        if installer_path.exists():
            try:
                size = self._get_dir_size(installer_path)
                if size > 0:
                    category.add_item(installer_path, size)
            except:
                pass

        if category.size_bytes > 0:
            category.recommendation = "Large but DO NOT clean. Needed for uninstalling/repairing programs."
        else:
            category.recommendation = "N/A"

        self.categories.append(category)

    def _scan_large_files(self):
        """Scan for large files across user directories"""
        category = StorageCategory(
            "Large Files",
            "Files larger than 500MB in your user folders"
        )
        category.safe_to_clean = False

        search_dirs = [
            Path.home() / 'Documents',
            Path.home() / 'Downloads',
            Path.home() / 'Desktop',
            Path.home() / 'Videos',
        ]

        threshold = 500 * 1024 * 1024  # 500MB

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            try:
                for item in search_dir.rglob('*'):
                    try:
                        if item.is_file():
                            size = item.stat().st_size
                            if size > threshold:
                                category.add_item(item, size)
                    except:
                        pass
            except:
                pass

        if category.size_bytes > 0:
            category.recommendation = f"Found {category.file_count} large files totaling {category._human_size(category.size_bytes)}. Review to see if needed."
        else:
            category.recommendation = "No large files found."

        self.categories.append(category)

    def _scan_old_files(self):
        """Scan for files not accessed in over a year"""
        category = StorageCategory(
            "Very Old Files",
            "Files not modified in over 1 year"
        )
        category.safe_to_clean = False

        search_dirs = [
            Path.home() / 'Documents',
            Path.home() / 'Desktop',
        ]

        cutoff_date = datetime.now() - timedelta(days=365)

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            try:
                for item in search_dir.rglob('*'):
                    try:
                        if item.is_file():
                            mtime = datetime.fromtimestamp(item.stat().st_mtime)
                            if mtime < cutoff_date:
                                size = item.stat().st_size
                                if size > 10 * 1024 * 1024:  # Only report files > 10MB
                                    category.add_item(item, size)
                    except:
                        pass
            except:
                pass

        if category.size_bytes > 0:
            category.recommendation = f"Found {category.file_count} old files. Consider archiving or deleting."
        else:
            category.recommendation = "No old large files found."

        self.categories.append(category)

    def _get_dir_size(self, directory: Path) -> int:
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

    def get_summary(self) -> Dict:
        """Get summary statistics"""
        total_size = sum(cat.size_bytes for cat in self.categories)
        safe_to_clean = sum(cat.size_bytes for cat in self.categories if cat.safe_to_clean)

        # Group by cleanup priority
        high_priority = [
            cat for cat in self.categories
            if cat.safe_to_clean and cat.size_bytes > 100 * 1024 * 1024  # > 100MB
        ]

        return {
            'total_categories': len(self.categories),
            'total_size': self._human_size(total_size),
            'total_size_bytes': total_size,
            'safe_to_clean_size': self._human_size(safe_to_clean),
            'safe_to_clean_bytes': safe_to_clean,
            'high_priority_cleanups': [
                {
                    'name': cat.name,
                    'size': cat._human_size(cat.size_bytes),
                    'recommendation': cat.recommendation
                }
                for cat in sorted(high_priority, key=lambda x: x.size_bytes, reverse=True)
            ]
        }

    def _human_size(self, size_bytes: int) -> str:
        """Convert bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"


if __name__ == "__main__":
    # Quick test
    storage = StorageSense()
    categories = storage.scan_all(quick_scan=True)

    print(f"Storage Analysis:\n")

    for category in categories:
        data = category.to_dict()
        if data['size_bytes'] > 0:
            print(f"[{data['name']}]")
            print(f"  Size: {data['size_human']} ({data['file_count']} items)")
            print(f"  {data['description']}")
            print(f"  → {data['recommendation']}")
            print()

    summary = storage.get_summary()
    print("\n=== Summary ===")
    print(f"Total analyzed: {summary['total_size']}")
    print(f"Safe to clean: {summary['safe_to_clean_size']}")
    print(f"\nHigh Priority Cleanups:")
    for cleanup in summary['high_priority_cleanups']:
        print(f"  • {cleanup['name']}: {cleanup['size']}")
