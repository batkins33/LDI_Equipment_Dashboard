"""
Dashboard Tab

System overview with quick stats and health score.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QGroupBox, QListWidget, QListWidgetItem,
    QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from datetime import datetime
from ..widgets.stat_card import StatCard
from ..widgets.health_score import HealthScore
from ..styles import get_color


class ScanThread(QThread):
    """Background thread for running scans"""
    finished = pyqtSignal(dict)
    progress = pyqtSignal(str)

    def __init__(self, app):
        super().__init__()
        self.app = app

    def run(self):
        """Run scan in background"""
        results = {}

        try:
            # Scan browsers
            self.progress.emit("Scanning browser profiles...")
            browser_profiles = self.app.browser_scanner.scan_all()
            browser_summary = self.app.browser_scanner.get_summary()
            results['browser'] = {
                'profiles': len(browser_profiles),
                'cache_size': browser_summary.get('total_cache_size', 'N/A'),
                'extensions': browser_summary.get('total_extensions', 0)
            }

            # Scan startup
            self.progress.emit("Scanning startup programs...")
            startup_items = self.app.startup_analyzer.scan_all()
            startup_summary = self.app.startup_analyzer.get_summary()
            results['startup'] = {
                'total': startup_summary.get('total_items', 0),
                'high_impact': startup_summary.get('high_impact_count', 0),
                'safe_to_disable': startup_summary.get('safe_to_disable_count', 0)
            }

            # Quick storage scan
            self.progress.emit("Scanning storage...")
            storage_categories = self.app.storage_sense.scan_all(quick_scan=True)
            storage_summary = self.app.storage_sense.get_summary()
            results['storage'] = {
                'total_size': storage_summary.get('total_size', 'N/A'),
                'safe_to_clean': storage_summary.get('safe_to_clean_size', 'N/A')
            }

            # Scan processes
            self.progress.emit("Scanning processes...")
            processes = self.app.process_explainer.scan_all(min_memory_mb=50)
            process_summary = self.app.process_explainer.get_summary()
            results['process'] = {
                'total': process_summary.get('total_processes', 0),
                'cpu': f"{process_summary.get('total_cpu_percent', 0):.1f}%",
                'memory': f"{process_summary.get('total_memory_gb', 0):.1f} GB"
            }

            # Calculate health score
            health_score = self.calculate_health_score(results)
            results['health_score'] = health_score

            self.progress.emit("Scan complete!")
            self.finished.emit(results)

        except Exception as e:
            self.progress.emit(f"Error: {str(e)}")
            self.finished.emit({})

    def calculate_health_score(self, results):
        """Calculate overall system health score (0-100)"""
        score = 100

        # Deduct points based on issues
        startup = results.get('startup', {})
        if startup.get('high_impact', 0) > 5:
            score -= 15
        elif startup.get('high_impact', 0) > 2:
            score -= 10

        if startup.get('safe_to_disable', 0) > 3:
            score -= 10
        elif startup.get('safe_to_disable', 0) > 0:
            score -= 5

        # Storage cleanup potential
        storage = results.get('storage', {})
        safe_to_clean = storage.get('safe_to_clean', 'N/A')
        if safe_to_clean != 'N/A':
            # Parse size (e.g., "5.2 GB" -> 5.2)
            try:
                size_str = safe_to_clean.split()[0]
                size = float(size_str)
                if 'GB' in safe_to_clean:
                    if size > 10:
                        score -= 20
                    elif size > 5:
                        score -= 15
                    elif size > 2:
                        score -= 10
                    elif size > 1:
                        score -= 5
            except:
                pass

        # Process load
        process = results.get('process', {})
        cpu_str = process.get('cpu', '0%')
        try:
            cpu = float(cpu_str.replace('%', ''))
            if cpu > 80:
                score -= 15
            elif cpu > 60:
                score -= 10
        except:
            pass

        return max(0, min(100, score))


class DashboardTab(QWidget):
    """Dashboard tab with system overview"""

    def __init__(self, app):
        """
        Initialize dashboard tab

        Args:
            app: SysPulse application instance
        """
        super().__init__()
        self.app = app
        self.scan_thread = None
        self.setup_ui()

    def setup_ui(self):
        """Setup dashboard UI"""
        # Main layout with scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        scroll.setWidget(container)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.addWidget(scroll)

        # Container layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        container.setLayout(layout)

        # Header
        header_layout = QHBoxLayout()
        layout.addLayout(header_layout)

        title = QLabel("📊 System Dashboard")
        title.setStyleSheet(f"""
            QLabel {{
                color: {get_color('primary')};
                font-size: 24px;
                font-weight: bold;
            }}
        """)
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Scan button
        self.scan_button = QPushButton("🔍 Run Full Scan")
        self.scan_button.setFixedHeight(40)
        self.scan_button.clicked.connect(self.run_scan)
        header_layout.addWidget(self.scan_button)

        # Stat cards grid
        stats_grid = QGridLayout()
        stats_grid.setSpacing(15)
        layout.addLayout(stats_grid)

        # Create stat cards
        self.browser_cache_card = StatCard("Browser Cache", "—", "info")
        stats_grid.addWidget(self.browser_cache_card, 0, 0)

        self.startup_items_card = StatCard("Startup Programs", "—", "warning")
        stats_grid.addWidget(self.startup_items_card, 0, 1)

        self.storage_cleanup_card = StatCard("Storage to Clean", "—", "success")
        stats_grid.addWidget(self.storage_cleanup_card, 0, 2)

        self.processes_card = StatCard("Background Processes", "—", "danger")
        stats_grid.addWidget(self.processes_card, 0, 3)

        # Health score
        self.health_score = HealthScore()
        layout.addWidget(self.health_score)

        # Status label
        self.status_label = QLabel("Click 'Run Full Scan' to analyze your system")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {get_color('text_light')};
                font-size: 13px;
                font-style: italic;
                padding: 10px;
            }}
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Recent scans group
        scans_group = QGroupBox("Recent Scans")
        scans_layout = QVBoxLayout()
        scans_group.setLayout(scans_layout)

        self.scans_list = QListWidget()
        self.scans_list.setMaximumHeight(150)
        scans_layout.addWidget(self.scans_list)

        layout.addWidget(scans_group)

        # Quick actions group
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QHBoxLayout()
        actions_group.setLayout(actions_layout)

        clean_browser_btn = QPushButton("🌐 Clean Browser Cache")
        clean_browser_btn.clicked.connect(self.quick_clean_browser)
        actions_layout.addWidget(clean_browser_btn)

        manage_startup_btn = QPushButton("🚀 Manage Startup")
        manage_startup_btn.clicked.connect(self.quick_manage_startup)
        actions_layout.addWidget(manage_startup_btn)

        clean_storage_btn = QPushButton("💾 Clean Storage")
        clean_storage_btn.clicked.connect(self.quick_clean_storage)
        actions_layout.addWidget(clean_storage_btn)

        layout.addWidget(actions_group)

        layout.addStretch()

        # Load recent scans from report history
        self.load_recent_scans()

    def run_scan(self):
        """Run full system scan in background"""
        if self.scan_thread and self.scan_thread.isRunning():
            return  # Scan already in progress

        self.scan_button.setEnabled(False)
        self.scan_button.setText("⏳ Scanning...")
        self.status_label.setText("Scan in progress...")

        self.scan_thread = ScanThread(self.app)
        self.scan_thread.progress.connect(self.update_progress)
        self.scan_thread.finished.connect(self.scan_finished)
        self.scan_thread.start()

    def update_progress(self, message: str):
        """Update progress message"""
        self.status_label.setText(message)

    def scan_finished(self, results: dict):
        """Handle scan completion"""
        self.scan_button.setEnabled(True)
        self.scan_button.setText("🔍 Run Full Scan")

        if not results:
            self.status_label.setText("Scan failed. Please try again.")
            return

        # Update stat cards
        browser = results.get('browser', {})
        self.browser_cache_card.set_value(browser.get('cache_size', 'N/A'))

        startup = results.get('startup', {})
        self.startup_items_card.set_value(str(startup.get('total', 0)))

        storage = results.get('storage', {})
        self.storage_cleanup_card.set_value(storage.get('safe_to_clean', 'N/A'))

        process = results.get('process', {})
        self.processes_card.set_value(str(process.get('total', 0)))

        # Update health score
        health_score = results.get('health_score', 0)
        self.health_score.set_score(health_score)

        # Update status
        self.status_label.setText(f"Last scan: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Add to recent scans
        self.add_recent_scan()

        # Store results for export
        self.app.last_scan_results = {
            'browser': {'summary': browser},
            'startup': {'summary': startup},
            'storage': {'summary': storage},
            'process': {'summary': process}
        }

    def load_recent_scans(self):
        """Load recent scans from report history"""
        self.scans_list.clear()

        try:
            reports = self.app.report_generator.list_reports()
            for report in reports[:5]:  # Show last 5
                timestamp = report.get('timestamp', 'Unknown')
                scans = ', '.join(report.get('scans', []))

                item = QListWidgetItem(f"📄 {timestamp} - {scans}")
                self.scans_list.addItem(item)
        except:
            pass

        if self.scans_list.count() == 0:
            item = QListWidgetItem("No recent scans")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.scans_list.addItem(item)

    def add_recent_scan(self):
        """Add current scan to recent scans list"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item = QListWidgetItem(f"📄 {timestamp} - Full System Scan")
        self.scans_list.insertItem(0, item)

        # Keep only last 5
        while self.scans_list.count() > 5:
            self.scans_list.takeItem(self.scans_list.count() - 1)

    def quick_clean_browser(self):
        """Quick action: Clean browser cache"""
        # Switch to browser tab
        parent = self.parent()
        while parent and not hasattr(parent, 'tabs'):
            parent = parent.parent()
        if parent:
            parent.tabs.setCurrentIndex(1)

    def quick_manage_startup(self):
        """Quick action: Manage startup"""
        # Switch to startup tab
        parent = self.parent()
        while parent and not hasattr(parent, 'tabs'):
            parent = parent.parent()
        if parent:
            parent.tabs.setCurrentIndex(2)

    def quick_clean_storage(self):
        """Quick action: Clean storage"""
        # Switch to storage tab
        parent = self.parent()
        while parent and not hasattr(parent, 'tabs'):
            parent = parent.parent()
        if parent:
            parent.tabs.setCurrentIndex(3)
