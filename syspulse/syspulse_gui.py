#!/usr/bin/env python3
"""
SysPulse GUI - Graphical User Interface Entry Point

Launch the PyQt6-based GUI for SysPulse system utilities dashboard.
"""

import sys
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / 'modules'))
sys.path.insert(0, str(Path(__file__).parent / 'gui'))

# Check for PyQt6
try:
    from PyQt6.QtWidgets import QApplication, QMessageBox
    from PyQt6.QtCore import Qt
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("\n❌ PyQt6 is not installed.")
    print("\nTo install PyQt6, run:")
    print("  pip install PyQt6 PyQt6-Charts")
    print("\nOr use the interactive CLI mode instead:")
    print("  python syspulse.py --interactive")
    sys.exit(1)

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

from main_window import MainWindow


class SysPulseGUI:
    """SysPulse GUI Application"""

    def __init__(self):
        """Initialize SysPulse backend"""
        # Initialize scanner modules
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

        # Storage for scan results
        self.last_scan_results = {}


def main():
    """Main entry point for GUI"""
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("SysPulse")
    app.setOrganizationName("SysPulse")
    app.setApplicationVersion("3.0.0-alpha.1")

    # Set application-wide style
    app.setStyle("Fusion")

    # Create SysPulse backend
    syspulse_app = SysPulseGUI()

    # Create and show main window
    window = MainWindow(syspulse_app)
    window.show()

    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
