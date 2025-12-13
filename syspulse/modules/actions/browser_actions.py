"""
Browser Cleanup Actions

Safe browser cache cleanup with confirmation and dry-run mode.
"""

import shutil
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import json


class CleanupResult:
    """Result of a cleanup operation"""

    def __init__(self, profile_name: str, browser: str):
        self.profile_name = profile_name
        self.browser = browser
        self.files_deleted = 0
        self.bytes_freed = 0
        self.errors: List[str] = []
        self.success = False
        self.dry_run = False

    def to_dict(self) -> Dict:
        return {
            'profile_name': self.profile_name,
            'browser': self.browser,
            'files_deleted': self.files_deleted,
            'bytes_freed': self.bytes_freed,
            'bytes_freed_human': self._human_size(self.bytes_freed),
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


class BrowserCleaner:
    """Safe browser cache cleanup with confirmations"""

    def __init__(self):
        self.log_file = Path.home() / '.syspulse' / 'cleanup_log.json'
        self.log_file.parent.mkdir(exist_ok=True)

    def clear_profile_cache(
        self,
        profile_path: Path,
        profile_name: str,
        browser: str,
        dry_run: bool = False
    ) -> CleanupResult:
        """
        Clear cache for a single browser profile

        Args:
            profile_path: Path to browser profile directory
            profile_name: Human-readable profile name
            browser: Browser name (Chrome, Edge, Firefox)
            dry_run: If True, only calculate what would be deleted

        Returns:
            CleanupResult with details of operation
        """
        result = CleanupResult(profile_name, browser)
        result.dry_run = dry_run

        # Determine cache directory based on browser
        cache_dirs = self._get_cache_directories(profile_path, browser)

        if not cache_dirs:
            result.errors.append(f"No cache directories found for {browser}")
            return result

        # Calculate size and count files
        total_size = 0
        total_files = 0

        for cache_dir in cache_dirs:
            if not cache_dir.exists():
                continue

            # Calculate size
            try:
                for entry in cache_dir.rglob('*'):
                    if entry.is_file():
                        try:
                            size = entry.stat().st_size
                            total_size += size
                            total_files += 1
                        except:
                            pass
            except Exception as e:
                result.errors.append(f"Error scanning {cache_dir}: {e}")

        result.bytes_freed = total_size
        result.files_deleted = total_files

        # If dry run, don't actually delete
        if dry_run:
            result.success = True
            return result

        # Actually delete cache
        deleted_count = 0
        deleted_size = 0

        for cache_dir in cache_dirs:
            if not cache_dir.exists():
                continue

            try:
                # Delete cache directory contents
                for item in cache_dir.iterdir():
                    try:
                        if item.is_file():
                            size = item.stat().st_size
                            item.unlink()
                            deleted_size += size
                            deleted_count += 1
                        elif item.is_dir():
                            # Calculate size before deleting
                            dir_size = sum(
                                f.stat().st_size
                                for f in item.rglob('*')
                                if f.is_file()
                            )
                            shutil.rmtree(item, ignore_errors=True)
                            deleted_size += dir_size
                            deleted_count += 1
                    except Exception as e:
                        result.errors.append(f"Error deleting {item.name}: {e}")

            except Exception as e:
                result.errors.append(f"Error accessing {cache_dir}: {e}")

        result.files_deleted = deleted_count
        result.bytes_freed = deleted_size
        result.success = len(result.errors) == 0 or deleted_count > 0

        # Log the action
        self._log_action(result)

        return result

    def clear_multiple_profiles(
        self,
        profiles: List[Dict],
        dry_run: bool = False
    ) -> List[CleanupResult]:
        """
        Clear cache for multiple browser profiles

        Args:
            profiles: List of profile dicts from BrowserScanner
            dry_run: If True, only show what would be deleted

        Returns:
            List of CleanupResults
        """
        results = []

        for profile_data in profiles:
            result = self.clear_profile_cache(
                Path(profile_data['path']),
                profile_data['name'],
                profile_data['browser'],
                dry_run=dry_run
            )
            results.append(result)

        return results

    def _get_cache_directories(self, profile_path: Path, browser: str) -> List[Path]:
        """Get list of cache directories for a browser profile"""
        cache_dirs = []

        if browser in ['Chrome', 'Edge']:
            # Chromium-based browsers
            cache_dirs = [
                profile_path / 'Cache' / 'Cache_Data',
                profile_path / 'Code Cache',
                profile_path / 'GPUCache',
                profile_path / 'Service Worker' / 'CacheStorage',
            ]

        elif browser == 'Firefox':
            # Firefox cache
            cache_dirs = [
                profile_path / 'cache2',
                profile_path / 'startupCache',
                profile_path / 'OfflineCache',
            ]

        # Filter to only existing directories
        return [d for d in cache_dirs if d.exists()]

    def _log_action(self, result: CleanupResult):
        """Log cleanup action to audit file"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'clear_browser_cache',
            'result': result.to_dict()
        }

        # Append to log file
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

        except Exception as e:
            # Don't fail if logging fails
            pass

    def get_cleanup_summary(self, results: List[CleanupResult]) -> Dict:
        """Get summary statistics from cleanup results"""
        total_freed = sum(r.bytes_freed for r in results)
        total_files = sum(r.files_deleted for r in results)
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful

        return {
            'total_profiles': len(results),
            'successful': successful,
            'failed': failed,
            'total_bytes_freed': total_freed,
            'total_bytes_freed_human': self._human_size(total_freed),
            'total_files_deleted': total_files,
            'errors': [
                {'profile': r.profile_name, 'errors': r.errors}
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
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from browser_scanner import BrowserScanner

    scanner = BrowserScanner()
    profiles = scanner.scan_all()

    if not profiles:
        print("No browser profiles found for testing")
        exit(0)

    cleaner = BrowserCleaner()

    print("Testing DRY RUN mode:\n")

    # Test dry run on first profile
    test_profile = profiles[0].to_dict()
    result = cleaner.clear_profile_cache(
        Path(test_profile['path']),
        test_profile['name'],
        test_profile['browser'],
        dry_run=True
    )

    print(f"Profile: {result.profile_name}")
    print(f"Would delete: {result.files_deleted} files")
    print(f"Would free: {result.to_dict()['bytes_freed_human']}")
    print(f"Success: {result.success}")

    if result.errors:
        print(f"Errors: {result.errors}")
