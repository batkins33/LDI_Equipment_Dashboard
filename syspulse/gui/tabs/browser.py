"""
Browser Tab

Browser profile management and cache visualization.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QHeaderView, QMessageBox, QProgressDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from ..styles import get_color


class BrowserScanThread(QThread):
    """Background thread for scanning browsers"""
    finished = pyqtSignal(list)

    def __init__(self, scanner):
        super().__init__()
        self.scanner = scanner

    def run(self):
        """Run browser scan"""
        profiles = self.scanner.scan_all()
        self.finished.emit(profiles)


class BrowserTab(QWidget):
    """Browser profiles tab"""

    def __init__(self, app):
        """
        Initialize browser tab

        Args:
            app: SysPulse application instance
        """
        super().__init__()
        self.app = app
        self.profiles = []
        self.setup_ui()

    def setup_ui(self):
        """Setup browser tab UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        self.setLayout(layout)

        # Header
        header_layout = QHBoxLayout()
        layout.addLayout(header_layout)

        title = QLabel("🌐 Browser Profiles")
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
        scan_btn = QPushButton("🔍 Scan Browsers")
        scan_btn.clicked.connect(self.scan_browsers)
        header_layout.addWidget(scan_btn)

        # Clean button
        self.clean_btn = QPushButton("🧹 Clean Selected Cache")
        self.clean_btn.clicked.connect(self.clean_cache)
        self.clean_btn.setEnabled(False)
        self.clean_btn.setProperty("class", "success")
        header_layout.addWidget(self.clean_btn)

        # Profiles table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Browser", "Profile", "Cache Size", "Extensions", "Last Used", "Recommendation"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.table)

        # Stats label
        self.stats_label = QLabel("Click 'Scan Browsers' to analyze browser profiles")
        self.stats_label.setStyleSheet(f"""
            QLabel {{
                color: {get_color('text_light')};
                font-style: italic;
                padding: 10px;
            }}
        """)
        layout.addWidget(self.stats_label)

    def scan_browsers(self):
        """Scan browser profiles"""
        self.table.setRowCount(0)
        self.stats_label.setText("Scanning browsers...")

        # Run scan in background
        self.scan_thread = BrowserScanThread(self.app.browser_scanner)
        self.scan_thread.finished.connect(self.scan_finished)
        self.scan_thread.start()

    def scan_finished(self, profiles):
        """Handle scan completion"""
        self.profiles = profiles

        if not profiles:
            self.stats_label.setText("No browser profiles found")
            return

        # Populate table
        self.table.setRowCount(len(profiles))

        for i, profile in enumerate(profiles):
            # Browser
            self.table.setItem(i, 0, QTableWidgetItem(profile.browser))

            # Profile name
            self.table.setItem(i, 1, QTableWidgetItem(profile.name))

            # Cache size
            cache_item = QTableWidgetItem(profile.cache_size_human)
            if profile.cache_size_bytes > 1_000_000_000:  # > 1GB
                cache_item.setForeground(Qt.GlobalColor.red)
            self.table.setItem(i, 2, cache_item)

            # Extensions
            self.table.setItem(i, 3, QTableWidgetItem(str(profile.extensions_count)))

            # Last used
            days_text = f"{profile.days_since_used} days ago" if profile.days_since_used != "Never" else "Never"
            self.table.setItem(i, 4, QTableWidgetItem(days_text))

            # Recommendation
            rec_item = QTableWidgetItem(profile.recommendation)
            if "delete" in profile.recommendation.lower():
                rec_item.setForeground(Qt.GlobalColor.red)
            elif "clean" in profile.recommendation.lower():
                rec_item.setForeground(Qt.GlobalColor.darkYellow)
            else:
                rec_item.setForeground(Qt.GlobalColor.darkGreen)
            self.table.setItem(i, 5, rec_item)

        # Update stats
        summary = self.app.browser_scanner.get_summary()
        self.stats_label.setText(
            f"Found {summary['total_profiles']} profiles | "
            f"Total cache: {summary['total_cache_size']} | "
            f"Total extensions: {summary['total_extensions']}"
        )

    def on_selection_changed(self):
        """Handle table selection change"""
        self.clean_btn.setEnabled(len(self.table.selectedItems()) > 0)

    def clean_cache(self):
        """Clean cache for selected profiles"""
        if not self.app.browser_cleaner:
            QMessageBox.warning(
                self,
                "Not Available",
                "Browser cache cleanup module is not available."
            )
            return

        selected_rows = set(item.row() for item in self.table.selectedItems())

        if not selected_rows:
            return

        # Calculate total size
        total_size = sum(self.profiles[row].cache_size_bytes for row in selected_rows)
        total_size_human = self.format_bytes(total_size)

        # Confirm
        reply = QMessageBox.question(
            self,
            "Clean Cache",
            f"Clean cache for {len(selected_rows)} profile(s)?\n\n"
            f"Total space to free: {total_size_human}\n\n"
            f"This will NOT delete bookmarks, passwords, or history.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Clean cache
        progress = QProgressDialog("Cleaning cache...", None, 0, len(selected_rows), self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)

        cleaned = 0
        for i, row in enumerate(sorted(selected_rows)):
            profile = self.profiles[row]
            try:
                self.app.browser_cleaner.clear_cache(profile)
                cleaned += 1
            except Exception as e:
                print(f"Error cleaning {profile.name}: {e}")

            progress.setValue(i + 1)

        progress.close()

        # Show result
        QMessageBox.information(
            self,
            "Cleanup Complete",
            f"Successfully cleaned {cleaned} profile(s)\n"
            f"Freed approximately {total_size_human}"
        )

        # Rescan
        self.scan_browsers()

    @staticmethod
    def format_bytes(bytes_val):
        """Format bytes to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.1f} PB"
