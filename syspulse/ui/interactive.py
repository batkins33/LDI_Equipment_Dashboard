"""
Interactive Mode for SysPulse

Provides a menu-driven interface for easier interaction with system utilities.
Includes step-by-step guidance, confirmations, and undo capabilities.
"""

import os
import sys
from pathlib import Path
from colorama import Fore, Style, init
from typing import Optional, List, Dict, Callable

# Initialize colorama
init(autoreset=True)


class InteractiveMode:
    """Interactive menu-driven interface for SysPulse"""

    def __init__(self, syspulse_app):
        """
        Initialize interactive mode

        Args:
            syspulse_app: Instance of the main SysPulse application
        """
        self.app = syspulse_app
        self.history = []  # Track actions for undo
        self.running = True

    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('clear' if os.name != 'nt' else 'cls')

    def print_header(self):
        """Print the application header"""
        self.clear_screen()
        print(f"{Fore.MAGENTA}{Style.BRIGHT}")
        print("  ____            ____        _          ")
        print(" / ___| _   _ ___|  _ \\ _   _| |___  ___ ")
        print(" \\___ \\| | | / __| |_) | | | | / __|/ _ \\")
        print("  ___) | |_| \\__ \\  __/| |_| | \\__ \\  __/")
        print(" |____/ \\__, |___/_|    \\__,_|_|___/\\___|")
        print("        |___/                            ")
        print(f"{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Control the bullshit. Make your computer run better.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Version 2.0.0-alpha.5 - Interactive Mode{Style.RESET_ALL}")
        print()

    def print_menu(self, title: str, options: List[str], show_back: bool = False):
        """
        Print a menu with numbered options

        Args:
            title: Menu title
            options: List of menu option strings
            show_back: Whether to show a back option
        """
        print(f"{Fore.CYAN}{Style.BRIGHT}{'=' * 60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{Style.BRIGHT}{title}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{Style.BRIGHT}{'=' * 60}{Style.RESET_ALL}")
        print()

        for i, option in enumerate(options, 1):
            print(f"  {Fore.WHITE}{i}.{Style.RESET_ALL} {option}")

        if show_back:
            print(f"  {Fore.WHITE}0.{Style.RESET_ALL} {Fore.YELLOW}← Back to main menu{Style.RESET_ALL}")
        else:
            print(f"  {Fore.WHITE}0.{Style.RESET_ALL} {Fore.RED}Exit{Style.RESET_ALL}")

        print()

    def get_choice(self, max_option: int, allow_zero: bool = True) -> Optional[int]:
        """
        Get user's menu choice

        Args:
            max_option: Maximum valid option number
            allow_zero: Whether 0 is a valid choice

        Returns:
            User's choice as integer, or None if invalid
        """
        try:
            choice = input(f"{Fore.GREEN}Enter your choice: {Style.RESET_ALL}").strip()
            choice_int = int(choice)

            min_choice = 0 if allow_zero else 1
            if min_choice <= choice_int <= max_option:
                return choice_int
            else:
                print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
                input("Press Enter to continue...")
                return None
        except ValueError:
            print(f"{Fore.RED}Invalid input. Please enter a number.{Style.RESET_ALL}")
            input("Press Enter to continue...")
            return None

    def confirm_action(self, message: str, default: bool = False) -> bool:
        """
        Ask user for confirmation

        Args:
            message: Confirmation message
            default: Default choice if user just presses Enter

        Returns:
            True if user confirms, False otherwise
        """
        default_str = "Y/n" if default else "y/N"
        response = input(f"{Fore.YELLOW}{message} [{default_str}]: {Style.RESET_ALL}").strip().lower()

        if not response:
            return default

        return response in ['y', 'yes']

    def show_main_menu(self):
        """Display and handle the main menu"""
        while self.running:
            self.print_header()

            options = [
                "🔍 Scan System (Full Analysis)",
                "🌐 Scan Browser Profiles",
                "🚀 Scan Startup Programs",
                "💾 Scan Storage",
                "⚙️  Scan Background Processes",
                "🧹 Cleanup & Optimization",
                "📊 Reports & History",
                "⚙️  Settings"
            ]

            self.print_menu("Main Menu", options, show_back=False)

            choice = self.get_choice(len(options))

            if choice is None:
                continue
            elif choice == 0:
                if self.confirm_action("Are you sure you want to exit?", default=False):
                    print(f"\n{Fore.GREEN}Thank you for using SysPulse!{Style.RESET_ALL}\n")
                    self.running = False
            elif choice == 1:
                self.scan_full()
            elif choice == 2:
                self.scan_browsers()
            elif choice == 3:
                self.scan_startup()
            elif choice == 4:
                self.scan_storage()
            elif choice == 5:
                self.scan_processes()
            elif choice == 6:
                self.cleanup_menu()
            elif choice == 7:
                self.reports_menu()
            elif choice == 8:
                self.settings_menu()

    def scan_full(self):
        """Run full system scan"""
        self.print_header()
        print(f"{Fore.CYAN}Running full system scan...{Style.RESET_ALL}\n")

        quick = self.confirm_action("Use quick storage scan? (faster but less thorough)", default=True)

        print()
        self.app.run_full_scan(quick_storage=quick)

        print()
        if self.confirm_action("Would you like to export a report?", default=False):
            self.export_report_prompt()

        input(f"\n{Fore.YELLOW}Press Enter to return to main menu...{Style.RESET_ALL}")

    def scan_browsers(self):
        """Scan browser profiles"""
        self.print_header()
        print(f"{Fore.CYAN}Scanning browser profiles...{Style.RESET_ALL}\n")

        self.app.run_browser_scan()

        print()
        if self.confirm_action("Would you like to clean browser cache?", default=False):
            self.cleanup_browser_cache()

        input(f"\n{Fore.YELLOW}Press Enter to return to main menu...{Style.RESET_ALL}")

    def scan_startup(self):
        """Scan startup programs"""
        self.print_header()
        print(f"{Fore.CYAN}Scanning startup programs...{Style.RESET_ALL}\n")

        self.app.run_startup_scan()

        print()
        if self.confirm_action("Would you like to manage startup programs?", default=False):
            self.manage_startup()

        input(f"\n{Fore.YELLOW}Press Enter to return to main menu...{Style.RESET_ALL}")

    def scan_storage(self):
        """Scan storage"""
        self.print_header()
        print(f"{Fore.CYAN}Scanning storage...{Style.RESET_ALL}\n")

        quick = self.confirm_action("Use quick scan?", default=True)
        self.app.run_storage_scan(quick=quick)

        print()
        if self.confirm_action("Would you like to clean storage?", default=False):
            self.cleanup_storage()

        input(f"\n{Fore.YELLOW}Press Enter to return to main menu...{Style.RESET_ALL}")

    def scan_processes(self):
        """Scan background processes"""
        self.print_header()
        print(f"{Fore.CYAN}Scanning background processes...{Style.RESET_ALL}\n")

        self.app.run_process_scan()

        input(f"\n{Fore.YELLOW}Press Enter to return to main menu...{Style.RESET_ALL}")

    def cleanup_menu(self):
        """Display cleanup & optimization menu"""
        while True:
            self.print_header()

            options = [
                "🌐 Clean Browser Cache",
                "💾 Clean Storage (Temp files, etc.)",
                "🚀 Manage Startup Programs",
                "📋 Guided Cleanup (Step-by-step)"
            ]

            self.print_menu("Cleanup & Optimization", options, show_back=True)

            choice = self.get_choice(len(options))

            if choice is None:
                continue
            elif choice == 0:
                break
            elif choice == 1:
                self.cleanup_browser_cache()
            elif choice == 2:
                self.cleanup_storage()
            elif choice == 3:
                self.manage_startup()
            elif choice == 4:
                self.guided_cleanup()

    def cleanup_browser_cache(self):
        """Clean browser cache with confirmation"""
        self.print_header()

        if not self.app.browser_cleaner:
            print(f"{Fore.RED}Browser cleanup module not available.{Style.RESET_ALL}")
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return

        print(f"{Fore.CYAN}Browser Cache Cleanup{Style.RESET_ALL}\n")

        # Scan first to show what will be cleaned
        profiles = self.app.browser_scanner.scan_all()

        if not profiles:
            print(f"{Fore.YELLOW}No browser profiles found.{Style.RESET_ALL}")
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return

        print(f"{Fore.WHITE}Found {len(profiles)} browser profile(s):{Style.RESET_ALL}\n")

        for i, profile in enumerate(profiles, 1):
            print(f"  {i}. [{profile.browser}] {profile.name} - {profile.cache_size_human} cache")

        print()

        if self.confirm_action("Clean cache for ALL profiles?", default=False):
            dry_run = not self.confirm_action("Proceed with actual cleanup? (No = dry run only)", default=False)

            print()
            self.app.run_browser_cleanup(dry_run=dry_run)

            if not dry_run:
                self.history.append({
                    'action': 'browser_cleanup',
                    'profiles': [p.to_dict() for p in profiles]
                })

        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

    def cleanup_storage(self):
        """Clean storage with confirmation"""
        self.print_header()

        if not self.app.storage_cleaner:
            print(f"{Fore.RED}Storage cleanup module not available.{Style.RESET_ALL}")
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return

        print(f"{Fore.CYAN}Storage Cleanup{Style.RESET_ALL}\n")

        # Show what will be cleaned
        print("This will clean:")
        print("  • Temporary files")
        print("  • Recycle bin")
        print("  • System cache")
        print()

        if self.confirm_action("Proceed with storage cleanup?", default=False):
            dry_run = not self.confirm_action("Proceed with actual cleanup? (No = dry run only)", default=False)

            print()
            self.app.run_storage_cleanup(dry_run=dry_run)

            if not dry_run:
                self.history.append({
                    'action': 'storage_cleanup'
                })

        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

    def manage_startup(self):
        """Manage startup programs"""
        self.print_header()

        if not self.app.startup_manager:
            print(f"{Fore.RED}Startup manager module not available.{Style.RESET_ALL}")
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return

        print(f"{Fore.CYAN}Startup Program Management{Style.RESET_ALL}\n")

        # Scan startup items
        items = self.app.startup_analyzer.scan_all()

        if not items:
            print(f"{Fore.YELLOW}No startup items found.{Style.RESET_ALL}")
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return

        # Show high-impact items that are safe to disable
        high_impact = [item for item in items if item.impact == 'HIGH']
        safe_to_disable = [item for item in high_impact if 'safe to disable' in item.recommendation.lower()]

        if safe_to_disable:
            print(f"{Fore.WHITE}High-impact items that are safe to disable:{Style.RESET_ALL}\n")
            for i, item in enumerate(safe_to_disable, 1):
                print(f"  {i}. {item.name} - {item.description}")
            print()

            if self.confirm_action("Would you like to see disable options?", default=True):
                dry_run = not self.confirm_action("Proceed with actual changes? (No = dry run only)", default=False)

                print()
                self.app.run_startup_management(dry_run=dry_run)

                if not dry_run:
                    self.history.append({
                        'action': 'startup_management',
                        'items': [item.to_dict() for item in safe_to_disable]
                    })
        else:
            print(f"{Fore.GREEN}No high-impact startup items that need attention.{Style.RESET_ALL}")

        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

    def guided_cleanup(self):
        """Step-by-step guided cleanup wizard"""
        self.print_header()
        print(f"{Fore.CYAN}Guided Cleanup Wizard{Style.RESET_ALL}\n")
        print("This wizard will walk you through optimizing your system step-by-step.\n")

        if not self.confirm_action("Start guided cleanup?", default=True):
            return

        steps_completed = []

        # Step 1: Browser cache
        self.print_header()
        print(f"{Fore.CYAN}Step 1/3: Browser Cache{Style.RESET_ALL}\n")
        print("Browser cache can accumulate gigabytes of data over time.")
        print("Clearing it can free up space without affecting your bookmarks or passwords.\n")

        if self.confirm_action("Scan browser profiles?", default=True):
            self.app.run_browser_scan()
            print()

            if self.confirm_action("Clean browser cache?", default=False):
                if self.app.browser_cleaner:
                    self.app.run_browser_cleanup(dry_run=False)
                    steps_completed.append("Browser cache cleaned")

        input(f"\n{Fore.YELLOW}Press Enter to continue to next step...{Style.RESET_ALL}")

        # Step 2: Storage cleanup
        self.print_header()
        print(f"{Fore.CYAN}Step 2/3: Storage Cleanup{Style.RESET_ALL}\n")
        print("Temporary files, recycle bin, and system cache can take up valuable space.")
        print("Cleaning these is safe and can free up gigabytes.\n")

        if self.confirm_action("Scan storage?", default=True):
            self.app.run_storage_scan(quick=True)
            print()

            if self.confirm_action("Clean storage?", default=False):
                if self.app.storage_cleaner:
                    self.app.run_storage_cleanup(dry_run=False)
                    steps_completed.append("Storage cleaned")

        input(f"\n{Fore.YELLOW}Press Enter to continue to next step...{Style.RESET_ALL}")

        # Step 3: Startup optimization
        self.print_header()
        print(f"{Fore.CYAN}Step 3/3: Startup Optimization{Style.RESET_ALL}\n")
        print("Many programs start automatically when your computer boots,")
        print("slowing down startup time. Some can be safely disabled.\n")

        if self.confirm_action("Scan startup programs?", default=True):
            self.app.run_startup_scan()
            print()

            if self.confirm_action("Manage startup programs?", default=False):
                if self.app.startup_manager:
                    self.app.run_startup_management(dry_run=False)
                    steps_completed.append("Startup programs optimized")

        # Summary
        self.print_header()
        print(f"{Fore.GREEN}{Style.BRIGHT}Guided Cleanup Complete!{Style.RESET_ALL}\n")

        if steps_completed:
            print(f"{Fore.WHITE}Steps completed:{Style.RESET_ALL}")
            for step in steps_completed:
                print(f"  ✓ {step}")
        else:
            print(f"{Fore.YELLOW}No cleanup actions were performed.{Style.RESET_ALL}")

        print()
        input(f"{Fore.YELLOW}Press Enter to return to main menu...{Style.RESET_ALL}")

    def reports_menu(self):
        """Display reports & history menu"""
        while True:
            self.print_header()

            options = [
                "📄 Export Current Scan (JSON)",
                "📊 Export Current Scan (HTML)",
                "📂 View Report History",
                "🔄 View Action History (for undo)"
            ]

            self.print_menu("Reports & History", options, show_back=True)

            choice = self.get_choice(len(options))

            if choice is None:
                continue
            elif choice == 0:
                break
            elif choice == 1:
                self.export_report('json')
            elif choice == 2:
                self.export_report('html')
            elif choice == 3:
                self.view_report_history()
            elif choice == 4:
                self.view_action_history()

    def export_report_prompt(self):
        """Prompt for report export format"""
        print()
        print("Export format:")
        print("  1. JSON (for programmatic access)")
        print("  2. HTML (for viewing in browser)")
        print()

        choice = self.get_choice(2, allow_zero=False)

        if choice == 1:
            self.export_report('json')
        elif choice == 2:
            self.export_report('html')

    def export_report(self, format: str):
        """Export report in specified format"""
        self.print_header()
        print(f"{Fore.CYAN}Exporting {format.upper()} Report{Style.RESET_ALL}\n")

        self.app.export_report(format=format)

        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

    def view_report_history(self):
        """View list of previously generated reports"""
        self.print_header()
        print(f"{Fore.CYAN}Report History{Style.RESET_ALL}\n")

        reports = self.app.report_generator.list_reports()

        if not reports:
            print(f"{Fore.YELLOW}No reports found.{Style.RESET_ALL}")
        else:
            print(f"{Fore.WHITE}Found {len(reports)} report(s):{Style.RESET_ALL}\n")
            for i, report in enumerate(reports[:10], 1):  # Show last 10
                print(f"  {i}. {report['timestamp']} - {', '.join(report['scans'])}")
                print(f"     File: {report['file']}")
                print()

        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

    def view_action_history(self):
        """View action history for potential undo"""
        self.print_header()
        print(f"{Fore.CYAN}Action History{Style.RESET_ALL}\n")

        if not self.history:
            print(f"{Fore.YELLOW}No actions have been performed in this session.{Style.RESET_ALL}")
        else:
            print(f"{Fore.WHITE}Actions performed in this session:{Style.RESET_ALL}\n")
            for i, action in enumerate(self.history, 1):
                print(f"  {i}. {action['action']}")

            print()
            print(f"{Fore.YELLOW}Note: Undo functionality is not yet implemented.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Action history is tracked for future undo support.{Style.RESET_ALL}")

        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

    def settings_menu(self):
        """Display settings menu"""
        while True:
            self.print_header()

            options = [
                "📁 View Reports Directory",
                "🔧 About SysPulse",
                "❓ Help"
            ]

            self.print_menu("Settings", options, show_back=True)

            choice = self.get_choice(len(options))

            if choice is None:
                continue
            elif choice == 0:
                break
            elif choice == 1:
                self.view_reports_directory()
            elif choice == 2:
                self.show_about()
            elif choice == 3:
                self.show_help()

    def view_reports_directory(self):
        """Show reports directory location"""
        self.print_header()
        print(f"{Fore.CYAN}Reports Directory{Style.RESET_ALL}\n")

        reports_dir = self.app.report_generator.reports_dir
        print(f"{Fore.WHITE}Reports are saved to:{Style.RESET_ALL}")
        print(f"  {reports_dir}")
        print()

        if reports_dir.exists():
            report_count = len(list(reports_dir.glob('*.json'))) + len(list(reports_dir.glob('*.html')))
            print(f"{Fore.WHITE}Total reports: {report_count}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Directory will be created when first report is generated.{Style.RESET_ALL}")

        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

    def show_about(self):
        """Show about information"""
        self.print_header()
        print(f"{Fore.CYAN}About SysPulse{Style.RESET_ALL}\n")

        print(f"{Fore.WHITE}Version:{Style.RESET_ALL} 2.0.0-alpha.5")
        print(f"{Fore.WHITE}Phase:{Style.RESET_ALL} Phase 2 - Actionable Controls")
        print()
        print(f"{Fore.WHITE}Description:{Style.RESET_ALL}")
        print("  A lightweight system utilities dashboard that gives you")
        print("  understandable control over the things that actually impact")
        print("  your computer's performance.")
        print()
        print(f"{Fore.WHITE}Features:{Style.RESET_ALL}")
        print("  • Browser profile analysis and cache cleanup")
        print("  • Startup program management")
        print("  • Storage analysis and cleanup")
        print("  • Background process monitoring")
        print("  • JSON and HTML report generation")
        print("  • Interactive guided cleanup")
        print()
        print(f"{Fore.CYAN}Control the bullshit. Make your computer run better.{Style.RESET_ALL}")

        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

    def show_help(self):
        """Show help information"""
        self.print_header()
        print(f"{Fore.CYAN}Help{Style.RESET_ALL}\n")

        print(f"{Fore.WHITE}Navigation:{Style.RESET_ALL}")
        print("  • Enter the number of your choice and press Enter")
        print("  • Enter 0 to go back or exit")
        print()
        print(f"{Fore.WHITE}Confirmations:{Style.RESET_ALL}")
        print("  • Y/n means default is Yes (just press Enter)")
        print("  • y/N means default is No (just press Enter)")
        print()
        print(f"{Fore.WHITE}Dry Run Mode:{Style.RESET_ALL}")
        print("  • Shows what would happen without actually doing it")
        print("  • Always available before performing actions")
        print()
        print(f"{Fore.WHITE}Safety:{Style.RESET_ALL}")
        print("  • All destructive actions require confirmation")
        print("  • Backups are created when possible")
        print("  • You can always run in dry-run mode first")
        print()
        print(f"{Fore.WHITE}Tips:{Style.RESET_ALL}")
        print("  • Use 'Guided Cleanup' for step-by-step optimization")
        print("  • Export reports to track changes over time")
        print("  • Start with scans before performing cleanups")

        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

    def run(self):
        """Start interactive mode"""
        self.show_main_menu()


if __name__ == "__main__":
    print("This module should be run through syspulse.py with --interactive flag")
