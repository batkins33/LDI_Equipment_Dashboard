"""
Main Window for SysPulse GUI

Provides the main application window with menu bar and tab interface.
"""

try:
    from PyQt6.QtWidgets import (
        QMainWindow, QTabWidget, QWidget, QVBoxLayout,
        QMenuBar, QMenu, QStatusBar, QMessageBox, QLabel
    )
    from PyQt6.QtCore import Qt, QSize
    from PyQt6.QtGui import QAction, QIcon
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("PyQt6 not installed. Please run: pip install PyQt6 PyQt6-Charts")

from .styles import get_stylesheet, get_color
from .tabs import DashboardTab


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self, syspulse_app):
        """
        Initialize main window

        Args:
            syspulse_app: Instance of the main SysPulse application
        """
        super().__init__()

        self.app = syspulse_app
        self.setWindowTitle("SysPulse - System Utilities Dashboard")
        self.setMinimumSize(1024, 768)

        # Apply stylesheet
        self.setStyleSheet(get_stylesheet())

        # Create UI components
        self.create_menu_bar()
        self.create_tabs()
        self.create_status_bar()

        # Center window on screen
        self.center_on_screen()

    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("&File")

        export_json_action = QAction("Export JSON Report", self)
        export_json_action.setShortcut("Ctrl+J")
        export_json_action.triggered.connect(self.export_json_report)
        file_menu.addAction(export_json_action)

        export_html_action = QAction("Export HTML Report", self)
        export_html_action.setShortcut("Ctrl+H")
        export_html_action.triggered.connect(self.export_html_report)
        file_menu.addAction(export_html_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Scan Menu
        scan_menu = menubar.addMenu("&Scan")

        full_scan_action = QAction("Full System Scan", self)
        full_scan_action.setShortcut("F5")
        full_scan_action.triggered.connect(self.run_full_scan)
        scan_menu.addAction(full_scan_action)

        scan_menu.addSeparator()

        browser_scan_action = QAction("Scan Browsers", self)
        browser_scan_action.triggered.connect(self.scan_browsers)
        scan_menu.addAction(browser_scan_action)

        startup_scan_action = QAction("Scan Startup", self)
        startup_scan_action.triggered.connect(self.scan_startup)
        scan_menu.addAction(startup_scan_action)

        storage_scan_action = QAction("Scan Storage", self)
        storage_scan_action.triggered.connect(self.scan_storage)
        scan_menu.addAction(storage_scan_action)

        process_scan_action = QAction("Scan Processes", self)
        process_scan_action.triggered.connect(self.scan_processes)
        scan_menu.addAction(process_scan_action)

        # Actions Menu
        actions_menu = menubar.addMenu("&Actions")

        clean_browser_action = QAction("Clean Browser Cache", self)
        clean_browser_action.triggered.connect(self.clean_browser_cache)
        actions_menu.addAction(clean_browser_action)

        clean_storage_action = QAction("Clean Storage", self)
        clean_storage_action.triggered.connect(self.clean_storage)
        actions_menu.addAction(clean_storage_action)

        manage_startup_action = QAction("Manage Startup Programs", self)
        manage_startup_action.triggered.connect(self.manage_startup)
        actions_menu.addAction(manage_startup_action)

        # Help Menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("About SysPulse", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        help_action = QAction("Help", self)
        help_action.setShortcut("F1")
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

    def create_tabs(self):
        """Create tab widget"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Create placeholder tabs
        # These will be replaced with proper tab widgets in future phases
        self.create_dashboard_tab()
        self.create_browser_tab()
        self.create_startup_tab()
        self.create_storage_tab()
        self.create_processes_tab()
        self.create_reports_tab()

    def create_dashboard_tab(self):
        """Create dashboard tab"""
        tab = DashboardTab(self.app)
        self.tabs.addTab(tab, "Dashboard")

    def create_browser_tab(self):
        """Create browser tab (placeholder)"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        label = QLabel("🌐 Browser Profiles")
        label.setProperty("class", "header")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        desc = QLabel("Browser profile analysis and cache management will appear here.\n\nThis will be implemented in Phase 3.3")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setProperty("class", "caption")
        layout.addWidget(desc)

        layout.addStretch()

        self.tabs.addTab(tab, "Browsers")

    def create_startup_tab(self):
        """Create startup tab (placeholder)"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        label = QLabel("🚀 Startup Programs")
        label.setProperty("class", "header")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        desc = QLabel("Startup program management will appear here.\n\nThis will be implemented in Phase 3.4")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setProperty("class", "caption")
        layout.addWidget(desc)

        layout.addStretch()

        self.tabs.addTab(tab, "Startup")

    def create_storage_tab(self):
        """Create storage tab (placeholder)"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        label = QLabel("💾 Storage")
        label.setProperty("class", "header")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        desc = QLabel("Storage analysis and cleanup will appear here.\n\nThis will be implemented in Phase 3.5")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setProperty("class", "caption")
        layout.addWidget(desc)

        layout.addStretch()

        self.tabs.addTab(tab, "Storage")

    def create_processes_tab(self):
        """Create processes tab (placeholder)"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        label = QLabel("⚙️ Processes")
        label.setProperty("class", "header")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        desc = QLabel("Process monitoring will appear here.\n\nThis will be implemented in Phase 3.6")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setProperty("class", "caption")
        layout.addWidget(desc)

        layout.addStretch()

        self.tabs.addTab(tab, "Processes")

    def create_reports_tab(self):
        """Create reports tab (placeholder)"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        label = QLabel("📊 Reports")
        label.setProperty("class", "header")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        desc = QLabel("Report history and export will appear here.\n\nThis will be implemented in Phase 3.7")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setProperty("class", "caption")
        layout.addWidget(desc)

        layout.addStretch()

        self.tabs.addTab(tab, "Reports")

    def create_status_bar(self):
        """Create status bar"""
        self.statusBar().showMessage("Ready")

    def center_on_screen(self):
        """Center the window on screen"""
        screen = self.screen().geometry()
        window = self.frameGeometry()
        center = screen.center()
        window.moveCenter(center)
        self.move(window.topLeft())

    # Menu action handlers
    def run_full_scan(self):
        """Run full system scan"""
        self.statusBar().showMessage("Running full system scan...")
        # TODO: Implement in background thread
        # For now, show message
        QMessageBox.information(
            self,
            "Full Scan",
            "Full system scan will be implemented in Phase 3.2\n\nFor now, use the CLI version:\npython syspulse.py"
        )
        self.statusBar().showMessage("Ready")

    def scan_browsers(self):
        """Scan browser profiles"""
        self.tabs.setCurrentIndex(1)  # Switch to browser tab
        self.statusBar().showMessage("Browser scan will be implemented in Phase 3.3")

    def scan_startup(self):
        """Scan startup programs"""
        self.tabs.setCurrentIndex(2)  # Switch to startup tab
        self.statusBar().showMessage("Startup scan will be implemented in Phase 3.4")

    def scan_storage(self):
        """Scan storage"""
        self.tabs.setCurrentIndex(3)  # Switch to storage tab
        self.statusBar().showMessage("Storage scan will be implemented in Phase 3.5")

    def scan_processes(self):
        """Scan processes"""
        self.tabs.setCurrentIndex(4)  # Switch to processes tab
        self.statusBar().showMessage("Process scan will be implemented in Phase 3.6")

    def clean_browser_cache(self):
        """Clean browser cache"""
        QMessageBox.information(
            self,
            "Clean Browser Cache",
            "Browser cache cleaning will be implemented in Phase 3.3\n\nFor now, use the CLI version:\npython syspulse.py --clean-browser-cache"
        )

    def clean_storage(self):
        """Clean storage"""
        QMessageBox.information(
            self,
            "Clean Storage",
            "Storage cleaning will be implemented in Phase 3.5\n\nFor now, use the CLI version:\npython syspulse.py --clean-storage"
        )

    def manage_startup(self):
        """Manage startup programs"""
        QMessageBox.information(
            self,
            "Manage Startup",
            "Startup management will be implemented in Phase 3.4\n\nFor now, use the CLI version:\npython syspulse.py --manage-startup"
        )

    def export_json_report(self):
        """Export JSON report"""
        self.statusBar().showMessage("Exporting JSON report...")
        # TODO: Implement
        QMessageBox.information(
            self,
            "Export JSON",
            "JSON export will be integrated in Phase 3.7"
        )
        self.statusBar().showMessage("Ready")

    def export_html_report(self):
        """Export HTML report"""
        self.statusBar().showMessage("Exporting HTML report...")
        # TODO: Implement
        QMessageBox.information(
            self,
            "Export HTML",
            "HTML export will be integrated in Phase 3.7"
        )
        self.statusBar().showMessage("Ready")

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About SysPulse",
            "<h2>SysPulse v3.0.0-alpha.2</h2>"
            "<p><b>System Utilities Dashboard</b></p>"
            "<p>Control the bullshit. Make your computer run better.</p>"
            "<p>A lightweight system utilities dashboard that gives you "
            "understandable control over the things that actually impact "
            "your computer's performance.</p>"
            "<hr>"
            "<p><b>Phase 3.2:</b> Dashboard Tab with live data</p>"
            "<p>Built with PyQt6</p>"
        )

    def show_help(self):
        """Show help dialog"""
        QMessageBox.information(
            self,
            "Help",
            "<h3>SysPulse Help</h3>"
            "<p><b>Menu Actions:</b></p>"
            "<ul>"
            "<li><b>File → Export:</b> Export reports to JSON or HTML</li>"
            "<li><b>Scan:</b> Run various system scans</li>"
            "<li><b>Actions:</b> Perform cleanup operations</li>"
            "</ul>"
            "<p><b>Tabs:</b></p>"
            "<ul>"
            "<li><b>Dashboard:</b> System overview</li>"
            "<li><b>Browsers:</b> Browser profile management</li>"
            "<li><b>Startup:</b> Startup program control</li>"
            "<li><b>Storage:</b> Storage analysis and cleanup</li>"
            "<li><b>Processes:</b> Process monitoring</li>"
            "<li><b>Reports:</b> Report history</li>"
            "</ul>"
            "<p><b>Keyboard Shortcuts:</b></p>"
            "<ul>"
            "<li><b>F5:</b> Full system scan</li>"
            "<li><b>Ctrl+J:</b> Export JSON</li>"
            "<li><b>Ctrl+H:</b> Export HTML</li>"
            "<li><b>Ctrl+Q:</b> Exit</li>"
            "<li><b>F1:</b> Help</li>"
            "</ul>"
        )
