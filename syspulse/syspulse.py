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
from typing import Optional

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / 'modules'))

from browser_scanner import BrowserScanner
from startup_analyzer import StartupAnalyzer
from storage_sense import StorageSense
from process_explainer import ProcessExplainer

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

    def run_full_scan(self, quick_storage: bool = False):
        """Run all scans"""
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

        self.run_browser_scan()
        self.run_startup_scan()
        self.run_storage_scan(quick=quick_storage)
        self.run_process_scan()

        print(f"\n{Fore.GREEN}{Style.BRIGHT}Scan complete!{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Review the recommendations above to improve your system performance.{Style.RESET_ALL}\n")


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
    parser.add_argument('--version', action='version', version='SysPulse 1.0.0')

    args = parser.parse_args()

    app = SysPulse()

    # If specific scan requested, run only that
    if args.browsers:
        app.run_browser_scan()
    elif args.startup:
        app.run_startup_scan()
    elif args.storage:
        app.run_storage_scan(quick=args.quick)
    elif args.processes:
        app.run_process_scan()
    else:
        # Run full scan
        app.run_full_scan(quick_storage=args.quick)


if __name__ == "__main__":
    main()
