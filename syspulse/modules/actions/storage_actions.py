"""
Storage Cleanup Actions

Safe storage cleanup with confirmation and dry-run mode.
Handles temp files, recycle bin, old downloads, etc.
"""

import shutil
import os
import platform
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import json


class CleanupResult:
    """Result of a storage cleanup operation"""

    def __init__(self, category: str):
        self.category = category
        self.files_deleted = 0
        self.bytes_freed = 0
        self.errors: List[str] = []
        self.success = False
        self.dry_run = False
        self.skipped_files = 0

    def to_dict(self) -> Dict:
        return {
            'category': self.category,
            'files_deleted': self.files_deleted,
            'bytes_freed': self.bytes_freed,
            'bytes_freed_human': self._human_size(self.bytes_freed),
            'skipped_files': self.skipped_files,
            'errors': self.errors,
            'success': self.success,
            'dry_run': self.dry_run
        }

    def _human_size(self, size_bytes: int) -> str:
        """Convert bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"


class StorageCleaner:
    """Safe storage cleanup with confirmations"""

    def __init__(self):
        self.system = platform.system()
        self.log_file = Path.home() / '.syspulse' / 'cleanup_log.json'
        self.log_file.parent.mkdir(exist_ok=True)

    def clean_temp_files(self, dry_run: bool = False) -> CleanupResult:
        """
        Clean system temporary files

        Args:
            dry_run: If True, only calculate what would be deleted

        Returns:
            CleanupResult with details
        """
        result = CleanupResult("Temp Files")
        result.dry_run = dry_run

        temp_dirs = self._get_temp_directories()

        for temp_dir in temp_dirs:
            if not temp_dir.exists():
                continue

            try:
                for item in temp_dir.iterdir():
                    try:
                        # Calculate size
                        if item.is_file():
                            size = item.stat().st_size
                        elif item.is_dir():
                            size = self._get_dir_size(item)
                        else:
                            continue

                        result.bytes_freed += size
                        result.files_deleted += 1

                        # If not dry run, actually delete
                        if not dry_run:
                            try:
                                if item.is_file():
                                    item.unlink()
                                elif item.is_dir():
                                    shutil.rmtree(item, ignore_errors=True)
                            except Exception as e:
                                result.errors.append(f"Error deleting {item.name}: {e}")
                                result.bytes_freed -= size
                                result.files_deleted -= 1
                                result.skipped_files += 1

                    except PermissionError:
                        result.skipped_files += 1
                    except Exception as e:
                        result.errors.append(f"Error processing {item.name}: {e}")

            except Exception as e:
                result.errors.append(f"Error accessing {temp_dir}: {e}")

        result.success = result.files_deleted > 0 or result.skipped_files == 0

        if not dry_run:
            self._log_action(result)

        return result

    def empty_recycle_bin(self, dry_run: bool = False) -> CleanupResult:
        """
        Empty the recycle bin

        Args:
            dry_run: If True, only calculate what would be deleted

        Returns:
            CleanupResult with details
        """
        result = CleanupResult("Recycle Bin")
        result.dry_run = dry_run

        recycle_paths = self._get_recycle_bin_paths()

        for recycle_path in recycle_paths:
            if not recycle_path.exists():
                continue

            try:
                # Calculate size first
                size = self._get_dir_size(recycle_path)
                result.bytes_freed += size

                # Count files
                file_count = sum(1 for _ in recycle_path.rglob('*') if _.is_file())
                result.files_deleted += file_count

                # If not dry run, actually empty
                if not dry_run:
                    try:
                        if self.system == "Windows":
                            # On Windows, use system command for proper recycle bin emptying
                            # This is safer than manually deleting from $Recycle.Bin
                            import ctypes
                            ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0)
                        else:
                            # On Linux/Mac, delete from trash
                            shutil.rmtree(recycle_path, ignore_errors=True)
                            recycle_path.mkdir(exist_ok=True)
                    except Exception as e:
                        result.errors.append(f"Error emptying recycle bin: {e}")

            except Exception as e:
                result.errors.append(f"Error accessing recycle bin: {e}")

        result.success = len(result.errors) == 0

        if not dry_run:
            self._log_action(result)

        return result

    def clean_old_downloads(self, days_old: int = 90, dry_run: bool = False,
                           selected_files: Optional[List[str]] = None) -> CleanupResult:
        """
        Clean old files from Downloads folder

        Args:
            days_old: Files older than this many days
            dry_run: If True, only calculate what would be deleted
            selected_files: If provided, only delete these specific files

        Returns:
            CleanupResult with details
        """
        result = CleanupResult(f"Old Downloads ({days_old}+ days)")
        result.dry_run = dry_run

        downloads_path = Path.home() / 'Downloads'

        if not downloads_path.exists():
            result.errors.append("Downloads folder not found")
            return result

        cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)

        try:
            for item in downloads_path.iterdir():
                try:
                    # Skip if specific files selected and this isn't one
                    if selected_files and str(item) not in selected_files:
                        continue

                    # Check if old enough
                    mtime = item.stat().st_mtime
                    if mtime >= cutoff_time:
                        continue

                    # Calculate size
                    if item.is_file():
                        size = item.stat().st_size
                    elif item.is_dir():
                        size = self._get_dir_size(item)
                    else:
                        continue

                    result.bytes_freed += size
                    result.files_deleted += 1

                    # If not dry run, actually delete
                    if not dry_run:
                        try:
                            if item.is_file():
                                item.unlink()
                            elif item.is_dir():
                                shutil.rmtree(item, ignore_errors=True)
                        except Exception as e:
                            result.errors.append(f"Error deleting {item.name}: {e}")
                            result.bytes_freed -= size
                            result.files_deleted -= 1
                            result.skipped_files += 1

                except PermissionError:
                    result.skipped_files += 1
                except Exception as e:
                    result.errors.append(f"Error processing {item.name}: {e}")

        except Exception as e:
            result.errors.append(f"Error accessing Downloads: {e}")

        result.success = result.files_deleted > 0 or (result.files_deleted == 0 and len(result.errors) == 0)

        if not dry_run:
            self._log_action(result)

        return result

    def clean_windows_update_cache(self, dry_run: bool = False) -> CleanupResult:
        """
        Clean Windows Update download cache

        Args:
            dry_run: If True, only calculate what would be deleted

        Returns:
            CleanupResult with details
        """
        result = CleanupResult("Windows Update Cache")
        result.dry_run = dry_run

        if self.system != "Windows":
            result.errors.append("Not applicable on non-Windows systems")
            return result

        update_cache = Path(os.environ.get('SYSTEMROOT', 'C:\\Windows')) / 'SoftwareDistribution' / 'Download'

        if not update_cache.exists():
            result.errors.append("Update cache directory not found")
            return result

        try:
            # Calculate size
            size = self._get_dir_size(update_cache)
            result.bytes_freed = size

            # Count files
            file_count = sum(1 for _ in update_cache.rglob('*') if _.is_file())
            result.files_deleted = file_count

            # If not dry run, actually clean
            if not dry_run:
                try:
                    # Stop Windows Update service first (safer)
                    os.system('net stop wuauserv')

                    # Clean the directory
                    shutil.rmtree(update_cache, ignore_errors=True)
                    update_cache.mkdir(exist_ok=True)

                    # Restart Windows Update service
                    os.system('net start wuauserv')

                except Exception as e:
                    result.errors.append(f"Error cleaning update cache: {e}")
                    # Try to restart service anyway
                    os.system('net start wuauserv')

        except Exception as e:
            result.errors.append(f"Error accessing update cache: {e}")

        result.success = len(result.errors) == 0

        if not dry_run:
            self._log_action(result)

        return result

    def _get_temp_directories(self) -> List[Path]:
        """Get list of temporary directories to clean"""
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

        # Filter to only existing directories
        return [d for d in temp_dirs if d and d.exists()]

    def _get_recycle_bin_paths(self) -> List[Path]:
        """Get list of recycle bin paths"""
        paths = []

        if self.system == "Windows":
            # Windows Recycle Bin (multiple drives)
            try:
                import string
                from ctypes import windll

                bitmask = windll.kernel32.GetLogicalDrives()
                for letter in string.ascii_uppercase:
                    if bitmask & 1:
                        recycle_path = Path(f"{letter}:") / '$Recycle.Bin'
                        if recycle_path.exists():
                            paths.append(recycle_path)
                    bitmask >>= 1
            except:
                # Fallback to C: drive only
                paths = [Path('C:/$Recycle.Bin')]

        elif self.system == "Darwin":
            # macOS Trash
            paths = [Path.home() / '.Trash']

        else:
            # Linux Trash
            paths = [Path.home() / '.local' / 'share' / 'Trash']

        return [p for p in paths if p.exists()]

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

    def _log_action(self, result: CleanupResult):
        """Log cleanup action to audit file"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'clean_storage',
            'result': result.to_dict()
        }

        try:
            logs = []
            if self.log_file.exists():
                with open(self.log_file, 'r') as f:
                    logs = json.load(f)

            logs.append(log_entry)

            # Keep only last 100 entries
            logs = logs[-100:]

            with open(self.log_file, 'w') as f:
                json.dump(logs, f, indent=2)

        except Exception:
            # Don't fail if logging fails
            pass

    def get_cleanup_summary(self, results: List[CleanupResult]) -> Dict:
        """Get summary statistics from cleanup results"""
        total_freed = sum(r.bytes_freed for r in results)
        total_files = sum(r.files_deleted for r in results)
        total_skipped = sum(r.skipped_files for r in results)
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful

        return {
            'total_categories': len(results),
            'successful': successful,
            'failed': failed,
            'total_bytes_freed': total_freed,
            'total_bytes_freed_human': self._human_size(total_freed),
            'total_files_deleted': total_files,
            'total_files_skipped': total_skipped,
            'errors': [
                {'category': r.category, 'errors': r.errors}
                for r in results
                if r.errors
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
    cleaner = StorageCleaner()

    print("Testing DRY RUN mode:\n")

    # Test temp files cleanup
    result = cleaner.clean_temp_files(dry_run=True)
    print(f"Temp Files:")
    print(f"  Would delete: {result.files_deleted} files")
    print(f"  Would free: {result.to_dict()['bytes_freed_human']}")
    print(f"  Skipped: {result.skipped_files} files")
    print(f"  Success: {result.success}")

    if result.errors:
        print(f"  Errors: {len(result.errors)}")
