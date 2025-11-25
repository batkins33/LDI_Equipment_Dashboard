#!/usr/bin/env python3
"""
SysPulse - System Utilities Dashboard

Control the bullshit. Make your computer run better.

A lightweight, on-demand system utilities dashboard that translates
technical controls into human language and gives you actionable control
over the things that actually impact your computer's performance.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional, List

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / 'modules'))

from browser_scanner import BrowserScanner
from startup_analyzer import StartupAnalyzer
from storage_sense import StorageSense
from process_explainer import ProcessExplainer
from reporting import ReportGenerator

# Phase 2: Action modules
try:
    from actions.browser_actions import BrowserCleaner
    from actions.storage_actions import StorageCleaner
    from actions.startup_actions import StartupManager
    ACTIONS_AVAILABLE = True
except ImportError:
    ACTIONS_AVAILABLE = False
    BrowserCleaner = None
    StorageCleaner = None
    StartupManager = None

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False

    # Fallback color class
    class Fore:
        RED = GREEN = YELLOW = BLUE = CYAN = MAGENTA = WHITE = RESET = ""

    class Style:
        BRIGHT = DIM = RESET_ALL = ""


class SysPulse:
    """Main SysPulse application"""

    def __init__(self):
        self.browser_scanner = BrowserScanner()
        self.startup_analyzer = StartupAnalyzer()
        self.storage_sense = StorageSense()
        self.process_explainer = ProcessExplainer()
        self.report_generator = ReportGenerator()

        # Phase 2: Action modules
        if ACTIONS_AVAILABLE:
            self.browser_cleaner = BrowserCleaner()
            self.storage_cleaner = StorageCleaner()
            self.startup_manager = StartupManager()
        else:
            self.browser_cleaner = None
            self.storage_cleaner = None
            self.startup_manager = None

        # Storage for scan results (for reporting)
        self.last_scan_results = {}

    def print_header(self, text: str):
        """Print section header"""
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'=' * 60}")
        print(f"{text}")
        print(f"{'=' * 60}{Style.RESET_ALL}\n")

    def print_item(self, label: str, value: str, color: str = Fore.WHITE):
        """Print formatted item"""
        print(f"{color}{label}: {Style.RESET_ALL}{value}")

    def run_browser_scan(self):
        """Run browser profile scanner"""
        self.print_header("Browser Profile Scanner")

        print("Scanning browser profiles...")
        profiles = self.browser_scanner.scan_all()

        if not profiles:
            print(f"{Fore.YELLOW}No browser profiles found.{Style.RESET_ALL}")
            return

        summary = self.browser_scanner.get_summary()

        print(f"\n{Fore.GREEN}Found {summary['total_profiles']} browser profiles{Style.RESET_ALL}")
        print(f"Browsers: {', '.join(summary['browsers_found'])}")
        print(f"Total cache: {summary['total_cache_size']}")
        print(f"Total extensions: {summary['total_extensions']}")
        print(f"Unused profiles: {summary['unused_profiles_count']} ({summary['unused_cache_size']} wasted)\n")

        for profile in profiles:
            data = profile.to_dict()

            # Color code based on recommendation
            if 'consider cleaning' in data['recommendation'] or 'recommend clearing' in data['recommendation']:
                name_color = Fore.YELLOW
            elif 'safe to delete' in data['recommendation']:
                name_color = Fore.RED
            else:
                name_color = Fore.GREEN

            print(f"{name_color}{Style.BRIGHT}[{data['browser']}] {data['name']}{Style.RESET_ALL}")
            print(f"  Cache: {data['cache_size_human']}")

            if data['days_since_used'] is not None:
                print(f"  Last used: {data['days_since_used']} days ago")
            else:
                print(f"  Last used: Never")

            print(f"  Extensions: {data['extensions_count']}")
            print(f"  {Fore.CYAN}→ {data['recommendation']}{Style.RESET_ALL}")
            print()

    def run_browser_cleanup(self, dry_run: bool = False, target_profile: str = None):
        """Run browser cache cleanup with confirmation"""
        if not ACTIONS_AVAILABLE or not self.browser_cleaner:
            print(f"{Fore.RED}Error: Browser cleanup module not available{Style.RESET_ALL}")
            return

        self.print_header("Browser Cache Cleanup" + (" [DRY RUN]" if dry_run else ""))

        # Scan profiles first
        print("Scanning browser profiles...")
        profiles = self.browser_scanner.scan_all()

        if not profiles:
            print(f"{Fore.YELLOW}No browser profiles found.{Style.RESET_ALL}")
            return

        # Filter profiles that should be cleaned
        profiles_to_clean = []
        for profile in profiles:
            data = profile.to_dict()

            # If target profile specified, only clean that one
            if target_profile and data['name'] != target_profile:
                continue

            # Only suggest cleaning profiles with recommendations
            if any(keyword in data['recommendation'] for keyword in ['consider cleaning', 'recommend clearing', 'safe to delete']):
                profiles_to_clean.append(data)

        if not profiles_to_clean:
            print(f"{Fore.GREEN}No profiles need cleaning!{Style.RESET_ALL}")
            return

        # Show what will be cleaned
        print(f"\n{Fore.YELLOW}Profiles to clean:{Style.RESET_ALL}\n")

        total_to_free = 0
        for idx, profile_data in enumerate(profiles_to_clean, 1):
            print(f"{idx}. [{profile_data['browser']}] {profile_data['name']}")
            print(f"   Cache: {profile_data['cache_size_human']}")
            print(f"   {profile_data['recommendation']}")
            total_to_free += profile_data['cache_size_mb'] * 1024 * 1024

        print(f"\n{Fore.CYAN}Total space to free: {self._human_size(total_to_free)}{Style.RESET_ALL}")

        # Confirm (unless dry run)
        if not dry_run:
            print(f"\n{Fore.YELLOW}⚠ WARNING: This will delete cache files from the above profiles.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Bookmarks, passwords, history, and extensions will NOT be affected.{Style.RESET_ALL}\n")

            response = input(f"Continue? (yes/no): ").strip().lower()

            if response != 'yes':
                print(f"\n{Fore.CYAN}Cleanup cancelled.{Style.RESET_ALL}")
                return

        # Execute cleanup
        print(f"\n{Fore.CYAN}{'Simulating' if dry_run else 'Executing'} cleanup...{Style.RESET_ALL}\n")

        results = self.browser_cleaner.clear_multiple_profiles(profiles_to_clean, dry_run=dry_run)

        # Show results
        for result in results:
            data = result.to_dict()

            if data['success']:
                status_color = Fore.GREEN
                status = "✓" if not dry_run else "✓ (dry run)"
            else:
                status_color = Fore.RED
                status = "✗"

            print(f"{status_color}{status} [{data['browser']}] {data['profile_name']}{Style.RESET_ALL}")

            if dry_run:
                print(f"   Would delete: {data['files_deleted']} files")
                print(f"   Would free: {data['bytes_freed_human']}")
            else:
                print(f"   Deleted: {data['files_deleted']} files")
                print(f"   Freed: {data['bytes_freed_human']}")

            if data['errors']:
                print(f"   {Fore.YELLOW}Errors: {len(data['errors'])}{Style.RESET_ALL}")

        # Summary
        summary = self.browser_cleaner.get_cleanup_summary(results)

        print(f"\n{Fore.GREEN}{Style.BRIGHT}Summary:{Style.RESET_ALL}")
        print(f"Profiles cleaned: {summary['successful']}/{summary['total_profiles']}")

        if dry_run:
            print(f"Would free: {summary['total_bytes_freed_human']}")
        else:
            print(f"Total freed: {summary['total_bytes_freed_human']}")

        if summary['errors']:
            print(f"\n{Fore.YELLOW}Some errors occurred. Check ~/.syspulse/cleanup_log.json for details.{Style.RESET_ALL}")

    def _human_size(self, size_bytes: int) -> str:
        """Convert bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    def run_storage_cleanup(self, dry_run: bool = False, categories: Optional[List[str]] = None):
        """Run storage cleanup with confirmation"""
        if not ACTIONS_AVAILABLE or not self.storage_cleaner:
            print(f"{Fore.RED}Error: Storage cleanup module not available{Style.RESET_ALL}")
            return

        self.print_header("Storage Cleanup" + (" [DRY RUN]" if dry_run else ""))

        # Define available cleanup categories
        available_categories = {
            'temp': ('Temp Files', lambda dr: self.storage_cleaner.clean_temp_files(dry_run=dr)),
            'recycle': ('Recycle Bin', lambda dr: self.storage_cleaner.empty_recycle_bin(dry_run=dr)),
            'downloads': ('Old Downloads (90+ days)', lambda dr: self.storage_cleaner.clean_old_downloads(days_old=90, dry_run=dr)),
        }

        # Add Windows-specific category
        if self.storage_cleaner.system == "Windows":
            available_categories['winupdate'] = (
                'Windows Update Cache',
                lambda dr: self.storage_cleaner.clean_windows_update_cache(dry_run=dr)
            )

        # If no categories specified, use all
        if not categories:
            categories = list(available_categories.keys())

        # First, show what will be cleaned (always dry run first)
        print("Analyzing storage...")
        preview_results = []

        for cat_key in categories:
            if cat_key not in available_categories:
                print(f"{Fore.YELLOW}Unknown category: {cat_key}{Style.RESET_ALL}")
                continue

            cat_name, cat_func = available_categories[cat_key]
            result = cat_func(True)  # Always preview first
            preview_results.append(result)

        if not preview_results:
            print(f"{Fore.YELLOW}No categories to clean.{Style.RESET_ALL}")
            return

        # Show preview
        print(f"\n{Fore.YELLOW}Categories to clean:{Style.RESET_ALL}\n")

        total_to_free = 0
        for idx, result in enumerate(preview_results, 1):
            data = result.to_dict()

            if data['bytes_freed'] == 0:
                status = f"{Fore.GREEN}(already clean){Style.RESET_ALL}"
            else:
                status = f"{Fore.YELLOW}{data['bytes_freed_human']}{Style.RESET_ALL}"

            print(f"{idx}. {data['category']}: {status}")

            if data['files_deleted'] > 0:
                print(f"   {data['files_deleted']} files")

            if data['skipped_files'] > 0:
                print(f"   {Fore.CYAN}({data['skipped_files']} files skipped - in use or no permission){Style.RESET_ALL}")

            total_to_free += data['bytes_freed']

        print(f"\n{Fore.CYAN}Total space to free: {self._human_size(total_to_free)}{Style.RESET_ALL}")

        if total_to_free == 0:
            print(f"\n{Fore.GREEN}Nothing to clean! System is already tidy.{Style.RESET_ALL}")
            return

        # Confirm (unless dry run)
        if not dry_run:
            print(f"\n{Fore.YELLOW}⚠ WARNING: This will permanently delete the files shown above.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}This action cannot be undone (except for Recycle Bin items).{Style.RESET_ALL}\n")

            response = input(f"Continue? (yes/no): ").strip().lower()

            if response != 'yes':
                print(f"\n{Fore.CYAN}Cleanup cancelled.{Style.RESET_ALL}")
                return

        # Execute cleanup
        print(f"\n{Fore.CYAN}{'Simulating' if dry_run else 'Executing'} cleanup...{Style.RESET_ALL}\n")

        results = []
        for cat_key in categories:
            if cat_key not in available_categories:
                continue

            cat_name, cat_func = available_categories[cat_key]
            result = cat_func(dry_run)
            results.append(result)

        # Show results
        for result in results:
            data = result.to_dict()

            if data['success']:
                status_color = Fore.GREEN
                status = "✓" if not dry_run else "✓ (dry run)"
            else:
                status_color = Fore.RED
                status = "✗"

            print(f"{status_color}{status} {data['category']}{Style.RESET_ALL}")

            if dry_run:
                print(f"   Would delete: {data['files_deleted']} files")
                print(f"   Would free: {data['bytes_freed_human']}")
            else:
                print(f"   Deleted: {data['files_deleted']} files")
                print(f"   Freed: {data['bytes_freed_human']}")

            if data['skipped_files'] > 0:
                print(f"   Skipped: {data['skipped_files']} files (in use or no permission)")

            if data['errors']:
                print(f"   {Fore.YELLOW}Errors: {len(data['errors'])}{Style.RESET_ALL}")

        # Summary
        summary = self.storage_cleaner.get_cleanup_summary(results)

        print(f"\n{Fore.GREEN}{Style.BRIGHT}Summary:{Style.RESET_ALL}")
        print(f"Categories cleaned: {summary['successful']}/{summary['total_categories']}")

        if dry_run:
            print(f"Would free: {summary['total_bytes_freed_human']}")
        else:
            print(f"Total freed: {summary['total_bytes_freed_human']}")

        if summary['total_files_skipped'] > 0:
            print(f"Files skipped: {summary['total_files_skipped']} (in use or no permission)")

        if summary['errors']:
            print(f"\n{Fore.YELLOW}Some errors occurred. Check ~/.syspulse/cleanup_log.json for details.{Style.RESET_ALL}")

    def run_startup_management(self, action: str = 'list', dry_run: bool = False):
        """
        Manage startup items (disable/enable/backup/restore)

        Args:
            action: 'list', 'disable', 'enable', 'backup', or 'restore'
            dry_run: If True, only show what would be done
        """
        if not ACTIONS_AVAILABLE or not self.startup_manager:
            print(f"{Fore.RED}Error: Startup management module not available{Style.RESET_ALL}")
            return

        if self.startup_manager.system != "Windows":
            print(f"{Fore.YELLOW}Startup management currently only supported on Windows.{Style.RESET_ALL}")
            return

        self.print_header("Startup Manager" + (" [DRY RUN]" if dry_run else ""))

        # Scan startup items first
        print("Scanning startup programs...")
        items = self.startup_analyzer.scan_all()

        if not items:
            print(f"{Fore.YELLOW}No startup items found.{Style.RESET_ALL}")
            return

        # Filter to safe-to-disable items
        items_to_manage = []
        for item in items:
            data = item.to_dict()
            if data['safe_to_disable']:
                items_to_manage.append(data)

        if not items_to_manage:
            print(f"{Fore.GREEN}All startup items are necessary or unsafe to disable.{Style.RESET_ALL}")
            return

        # Show startup items with recommendations
        print(f"\n{Fore.YELLOW}Safe to disable startup items:{Style.RESET_ALL}\n")

        for idx, item_data in enumerate(items_to_manage, 1):
            impact_color = Fore.RED if item_data['impact'] == 'HIGH' else Fore.YELLOW if item_data['impact'] == 'MEDIUM' else Fore.GREEN

            print(f"{idx}. {impact_color}[{item_data['impact']}]{Style.RESET_ALL} {Style.BRIGHT}{item_data['name']}{Style.RESET_ALL}")
            print(f"   {item_data['description']}")
            print(f"   {Fore.CYAN}→ {item_data['recommendation']}{Style.RESET_ALL}")
            print()

        # Confirm (unless dry run)
        if not dry_run:
            print(f"\n{Fore.YELLOW}⚠ WARNING: This will disable the startup items shown above.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Items will not be deleted - you can re-enable them later.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}A backup will be created automatically.{Style.RESET_ALL}\n")

            response = input(f"Disable these items? (yes/no): ").strip().lower()

            if response != 'yes':
                print(f"\n{Fore.CYAN}Operation cancelled.{Style.RESET_ALL}")
                return

        # Execute disable
        print(f"\n{Fore.CYAN}{'Simulating' if dry_run else 'Disabling'} startup items...{Style.RESET_ALL}\n")

        results = []
        for item_data in items_to_manage:
            result = self.startup_manager.disable_startup_item(
                item_data['name'],
                item_data['location'],
                item_data['command'],
                dry_run=dry_run
            )
            results.append(result)

        # Show results
        successful = 0
        failed = 0

        for result in results:
            data = result.to_dict()

            if data['success']:
                status_color = Fore.GREEN
                status = "✓" if not dry_run else "✓ (dry run)"
                successful += 1
            else:
                status_color = Fore.RED
                status = "✗"
                failed += 1

            print(f"{status_color}{status} {data['item_name']}{Style.RESET_ALL}")

            if data['error']:
                print(f"   {Fore.YELLOW}Error: {data['error']}{Style.RESET_ALL}")

        # Summary
        print(f"\n{Fore.GREEN}{Style.BRIGHT}Summary:{Style.RESET_ALL}")
        print(f"Successfully {('would disable' if dry_run else 'disabled')}: {successful}")
        if failed > 0:
            print(f"Failed: {failed}")

        if not dry_run and successful > 0:
            print(f"\n{Fore.CYAN}Items have been disabled. They will not start on next boot.{Style.RESET_ALL}")
            print(f"{Fore.CYAN}To re-enable, use: python syspulse.py --enable-startup{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Backup saved to: ~/.syspulse/startup_backups/{Style.RESET_ALL}")

    def run_startup_scan(self):
        """Run startup impact analyzer"""
        self.print_header("Startup Impact Analyzer")

        print("Scanning startup programs...")
        items = self.startup_analyzer.scan_all()

        if not items:
            print(f"{Fore.YELLOW}No startup items found.{Style.RESET_ALL}")
            return

        summary = self.startup_analyzer.get_summary()

        print(f"\n{Fore.GREEN}Found {summary['total_items']} startup items{Style.RESET_ALL}")
        print(f"High impact: {summary['high_impact_count']}")
        print(f"Medium impact: {summary['medium_impact_count']}")
        print(f"Safe to disable: {summary['safe_to_disable_count']}")
        print(f"Estimated boot delay: ~{summary['estimated_boot_delay_seconds']} seconds")
        print(f"Potential savings: ~{summary['potential_savings_seconds']} seconds\n")

        # Show top recommendations
        print(f"{Fore.YELLOW}{Style.BRIGHT}Top Recommendations:{Style.RESET_ALL}\n")

        for item_data in summary['top_recommendations']:
            # Color code by impact
            if item_data['impact'] == 'HIGH':
                impact_color = Fore.RED
            elif item_data['impact'] == 'MEDIUM':
                impact_color = Fore.YELLOW
            else:
                impact_color = Fore.GREEN

            print(f"{impact_color}[{item_data['impact']}]{Style.RESET_ALL} {Style.BRIGHT}{item_data['name']}{Style.RESET_ALL}")
            print(f"  {item_data['description']}")
            print(f"  {Fore.CYAN}→ {item_data['recommendation']}{Style.RESET_ALL}")
            print()

    def run_storage_scan(self, quick: bool = False):
        """Run storage sense analyzer"""
        self.print_header("Storage Sense")

        scan_type = "quick" if quick else "full"
        print(f"Running {scan_type} storage scan...")
        categories = self.storage_sense.scan_all(quick_scan=quick)

        summary = self.storage_sense.get_summary()

        print(f"\n{Fore.GREEN}Storage Analysis Complete{Style.RESET_ALL}")
        print(f"Total analyzed: {summary['total_size']}")
        print(f"Safe to clean: {summary['safe_to_clean_size']}\n")

        # Show high priority cleanups
        if summary['high_priority_cleanups']:
            print(f"{Fore.YELLOW}{Style.BRIGHT}High Priority Cleanups:{Style.RESET_ALL}\n")
            for cleanup in summary['high_priority_cleanups']:
                print(f"{Fore.RED}• {cleanup['name']}: {cleanup['size']}{Style.RESET_ALL}")
                print(f"  {Fore.CYAN}{cleanup['recommendation']}{Style.RESET_ALL}")
                print()

        # Show all categories
        print(f"{Fore.CYAN}{Style.BRIGHT}All Categories:{Style.RESET_ALL}\n")
        for category in categories:
            data = category.to_dict()

            if data['size_bytes'] == 0:
                continue

            # Color code by safe_to_clean
            if data['safe_to_clean']:
                name_color = Fore.YELLOW
            else:
                name_color = Fore.WHITE

            print(f"{name_color}{Style.BRIGHT}{data['name']}{Style.RESET_ALL}")
            print(f"  Size: {data['size_human']} ({data['file_count']} items)")
            print(f"  {data['description']}")
            print(f"  {Fore.CYAN}→ {data['recommendation']}{Style.RESET_ALL}")
            print()

    def run_process_scan(self):
        """Run background process explainer"""
        self.print_header("Background Process Explainer")

        print("Scanning processes (this may take a moment)...")
        processes = self.process_explainer.scan_all(min_memory_mb=50)

        summary = self.process_explainer.get_summary()

        print(f"\n{Fore.GREEN}Found {summary['total_processes']} significant processes{Style.RESET_ALL}")
        print(f"Total CPU: {summary['total_cpu_percent']}%")
        print(f"Total Memory: {summary['total_memory_gb']} GB")
        print(f"CPU hogs (>10%): {summary['cpu_hogs_count']}")
        print(f"Memory hogs (>500MB): {summary['memory_hogs_count']}\n")

        # Show top CPU consumers
        print(f"{Fore.YELLOW}{Style.BRIGHT}Top CPU Consumers:{Style.RESET_ALL}\n")
        for proc_data in summary['top_cpu']:
            print(f"{Fore.RED}[{proc_data['cpu_percent']}%]{Style.RESET_ALL} {Style.BRIGHT}{proc_data['name']}{Style.RESET_ALL}")
            print(f"  {proc_data['description']}")
            print(f"  Memory: {proc_data['memory_mb']:.1f} MB")
            print(f"  {Fore.CYAN}→ {proc_data['recommendation']}{Style.RESET_ALL}")
            print()

        # Show top memory consumers
        print(f"{Fore.YELLOW}{Style.BRIGHT}Top Memory Consumers:{Style.RESET_ALL}\n")
        for proc_data in summary['top_memory']:
            print(f"{Fore.RED}[{proc_data['memory_mb']:.1f} MB]{Style.RESET_ALL} {Style.BRIGHT}{proc_data['name']}{Style.RESET_ALL}")
            print(f"  {proc_data['description']}")
            print(f"  CPU: {proc_data['cpu_percent']}%")
            print(f"  {Fore.CYAN}→ {proc_data['recommendation']}{Style.RESET_ALL}")
            print()

    def run_full_scan(self, quick_storage: bool = False, export_report: Optional[str] = None):
        """Run all scans and optionally export report"""
        print(f"{Fore.MAGENTA}{Style.BRIGHT}")
        print("  ____            ____        _          ")
        print(" / ___| _   _ ___|  _ \\ _   _| |___  ___ ")
        print(" \\___ \\| | | / __| |_) | | | | / __|/ _ \\")
        print("  ___) | |_| \\__ \\  __/| |_| | \\__ \\  __/")
        print(" |____/ \\__, |___/_|    \\__,_|_|___/\\___|")
        print("        |___/                            ")
        print()
        print("Control the bullshit. Make your computer run better.")
        print(f"{Style.RESET_ALL}")

        # Run scans and collect data
        print("Scanning browser profiles...")
        browser_profiles = self.browser_scanner.scan_all()
        browser_summary = self.browser_scanner.get_summary()
        self.last_scan_results['browser'] = {
            'summary': browser_summary,
            'profiles': [p.to_dict() for p in browser_profiles]
        }

        print("Scanning startup programs...")
        startup_items = self.startup_analyzer.scan_all()
        startup_summary = self.startup_analyzer.get_summary()
        self.last_scan_results['startup'] = {
            'summary': startup_summary,
            'top_recommendations': startup_summary['top_recommendations']
        }

        print("Scanning storage...")
        storage_categories = self.storage_sense.scan_all(quick_scan=quick_storage)
        storage_summary = self.storage_sense.get_summary()
        self.last_scan_results['storage'] = {
            'summary': storage_summary
        }

        print("Scanning processes...")
        processes = self.process_explainer.scan_all(min_memory_mb=50)
        process_summary = self.process_explainer.get_summary()
        self.last_scan_results['process'] = {
            'summary': process_summary
        }

        # Display results
        self.run_browser_scan()
        self.run_startup_scan()
        self.run_storage_scan(quick=quick_storage)
        self.run_process_scan()

        print(f"\n{Fore.GREEN}{Style.BRIGHT}Scan complete!{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Review the recommendations above to improve your system performance.{Style.RESET_ALL}\n")

        # Export report if requested
        if export_report:
            self.export_report(export_report)

    def export_report(self, format: str = 'json', output_file: Optional[Path] = None):
        """Export scan results to report"""
        self.print_header(f"Exporting Report ({format.upper()})")

        if not self.last_scan_results:
            print(f"{Fore.YELLOW}No scan results available. Run a scan first.{Style.RESET_ALL}")
            return

        try:
            if format.lower() == 'json':
                file_path = self.report_generator.generate_json_report(
                    browser_data=self.last_scan_results.get('browser'),
                    startup_data=self.last_scan_results.get('startup'),
                    storage_data=self.last_scan_results.get('storage'),
                    process_data=self.last_scan_results.get('process'),
                    output_file=output_file
                )
            elif format.lower() == 'html':
                file_path = self.report_generator.generate_html_report(
                    browser_data=self.last_scan_results.get('browser'),
                    startup_data=self.last_scan_results.get('startup'),
                    storage_data=self.last_scan_results.get('storage'),
                    process_data=self.last_scan_results.get('process'),
                    output_file=output_file
                )
            else:
                print(f"{Fore.RED}Unsupported format: {format}{Style.RESET_ALL}")
                return

            print(f"{Fore.GREEN}✓ Report exported successfully!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Location: {file_path}{Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.RED}Error exporting report: {e}{Style.RESET_ALL}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='SysPulse - System Utilities Dashboard',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  syspulse                  Run all scans
  syspulse --browsers       Scan browser profiles only
  syspulse --startup        Scan startup programs only
  syspulse --storage        Scan storage only
  syspulse --processes      Scan running processes only
  syspulse --quick          Run quick scan (faster, less detailed)
        """
    )

    # Analysis options (Phase 1)
    parser.add_argument('--browsers', action='store_true',
                        help='Scan browser profiles only')
    parser.add_argument('--startup', action='store_true',
                        help='Scan startup programs only')
    parser.add_argument('--storage', action='store_true',
                        help='Scan storage only')
    parser.add_argument('--processes', action='store_true',
                        help='Scan running processes only')
    parser.add_argument('--quick', action='store_true',
                        help='Quick scan (faster, less detailed)')

    # Action options (Phase 2)
    parser.add_argument('--clean-browser-cache', action='store_true',
                        help='Clean browser cache (interactive with confirmation)')
    parser.add_argument('--clean-storage', action='store_true',
                        help='Clean storage (temp files, recycle bin, etc.)')
    parser.add_argument('--manage-startup', action='store_true',
                        help='Disable safe-to-disable startup items (Windows only)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be done without actually doing it')

    # Report options (Phase 2.4)
    parser.add_argument('--export-json', action='store_true',
                        help='Export scan results to JSON report')
    parser.add_argument('--export-html', action='store_true',
                        help='Export scan results to HTML report')

    parser.add_argument('--version', action='version', version='SysPulse 2.0.0-alpha.4')

    args = parser.parse_args()

    app = SysPulse()

    # Determine export format
    export_format = None
    if args.export_json:
        export_format = 'json'
    elif args.export_html:
        export_format = 'html'

    # Phase 2: Action commands (take precedence)
    if args.clean_browser_cache:
        app.run_browser_cleanup(dry_run=args.dry_run)
    elif args.clean_storage:
        app.run_storage_cleanup(dry_run=args.dry_run)
    elif args.manage_startup:
        app.run_startup_management(dry_run=args.dry_run)
    # Phase 1: Analysis commands
    elif args.browsers:
        app.run_browser_scan()
        if export_format:
            app.export_report(export_format)
    elif args.startup:
        app.run_startup_scan()
        if export_format:
            app.export_report(export_format)
    elif args.storage:
        app.run_storage_scan(quick=args.quick)
        if export_format:
            app.export_report(export_format)
    elif args.processes:
        app.run_process_scan()
        if export_format:
            app.export_report(export_format)
    else:
        # Run full scan
        app.run_full_scan(quick_storage=args.quick, export_report=export_format)


if __name__ == "__main__":
    main()
