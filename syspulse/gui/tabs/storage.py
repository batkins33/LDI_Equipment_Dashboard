"""
Storage Tab

Storage analysis and cleanup.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QHeaderView, QMessageBox, QProgressDialog, QGroupBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from ..styles import get_color


class StorageScanThread(QThread):
    """Background thread for scanning storage"""
    finished = pyqtSignal(list, dict)

    def __init__(self, storage_sense):
        super().__init__()
        self.storage_sense = storage_sense

    def run(self):
        """Run storage scan"""
        categories = self.storage_sense.scan_all(quick_scan=True)
        summary = self.storage_sense.get_summary()
        self.finished.emit(categories, summary)


class StorageTab(QWidget):
    """Storage analysis tab"""

    def __init__(self, app):
        """
        Initialize storage tab

        Args:
            app: SysPulse application instance
        """
        super().__init__()
        self.app = app
        self.categories = []
        self.setup_ui()

    def setup_ui(self):
        """Setup storage tab UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        self.setLayout(layout)

        # Header
        header_layout = QHBoxLayout()
        layout.addLayout(header_layout)

        title = QLabel("💾 Storage Analysis")
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
        scan_btn = QPushButton("🔍 Scan Storage")
        scan_btn.clicked.connect(self.scan_storage)
        header_layout.addWidget(scan_btn)

        # Clean button
        self.clean_btn = QPushButton("🧹 Clean All Safe Items")
        self.clean_btn.clicked.connect(self.clean_storage)
        self.clean_btn.setEnabled(False)
        self.clean_btn.setProperty("class", "success")
        header_layout.addWidget(self.clean_btn)

        # Storage categories table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Category", "Size", "Items", "Recommendation"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        # Stats
        stats_group = QGroupBox("Summary")
        stats_layout = QVBoxLayout()
        stats_group.setLayout(stats_layout)

        self.stats_label = QLabel("Click 'Scan Storage' to analyze storage")
        self.stats_label.setStyleSheet(f"""
            QLabel {{
                color: {get_color('text')};
                padding: 10px;
            }}
        """)
        stats_layout.addWidget(self.stats_label)

        layout.addWidget(stats_group)

    def scan_storage(self):
        """Scan storage"""
        self.table.setRowCount(0)
        self.stats_label.setText("Scanning storage... (this may take a moment)")

        # Run scan in background
        self.scan_thread = StorageScanThread(self.app.storage_sense)
        self.scan_thread.finished.connect(self.scan_finished)
        self.scan_thread.start()

    def scan_finished(self, categories, summary):
        """Handle scan completion"""
        self.categories = categories

        if not categories:
            self.stats_label.setText("No storage categories found")
            return

        # Populate table
        self.table.setRowCount(len(categories))

        for i, category in enumerate(categories):
            # Category name
            self.table.setItem(i, 0, QTableWidgetItem(category.name))

            # Size
            size_item = QTableWidgetItem(category.size_human)
            if category.size_bytes > 1_000_000_000:  # > 1GB
                size_item.setForeground(Qt.GlobalColor.red)
            self.table.setItem(i, 1, size_item)

            # Items count
            self.table.setItem(i, 2, QTableWidgetItem(str(category.item_count)))

            # Recommendation
            rec_item = QTableWidgetItem(category.recommendation)
            if "safe to clean" in category.recommendation.lower():
                rec_item.setForeground(Qt.GlobalColor.darkGreen)
            else:
                rec_item.setForeground(Qt.GlobalColor.darkYellow)
            self.table.setItem(i, 3, rec_item)

        # Update stats
        self.stats_label.setText(
            f"Total analyzed: {summary['total_size']}\n"
            f"Safe to clean: {summary['safe_to_clean_size']}\n"
            f"High priority cleanups: {len(summary.get('high_priority_cleanups', []))}"
        )

        # Enable clean button
        self.clean_btn.setEnabled(True)

    def clean_storage(self):
        """Clean safe storage items"""
        if not self.app.storage_cleaner:
            QMessageBox.warning(
                self,
                "Not Available",
                "Storage cleanup module is not available."
            )
            return

        if not self.categories:
            return

        # Calculate total safe to clean
        summary = self.app.storage_sense.get_summary()
        safe_size = summary.get('safe_to_clean_size', 'Unknown')

        # Confirm
        reply = QMessageBox.question(
            self,
            "Clean Storage",
            f"Clean all safe-to-clean storage items?\n\n"
            f"Space to free: {safe_size}\n\n"
            f"This will:\n"
            f"• Empty recycle bin\n"
            f"• Delete temporary files\n"
            f"• Clean system cache\n\n"
            f"Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Clean storage
        progress = QProgressDialog("Cleaning storage...", None, 0, 0, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()

        try:
            # Run cleanup
            self.app.storage_cleaner.clean_all()

            progress.close()

            QMessageBox.information(
                self,
                "Cleanup Complete",
                f"Successfully cleaned storage!\n"
                f"Freed approximately {safe_size}"
            )

            # Rescan
            self.scan_storage()

        except Exception as e:
            progress.close()
            QMessageBox.critical(
                self,
                "Cleanup Error",
                f"Error during cleanup:\n{str(e)}"
            )
