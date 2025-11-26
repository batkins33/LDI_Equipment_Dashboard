"""
Startup Tab

Startup program management with toggle controls.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QHeaderView, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from ..styles import get_color


class StartupScanThread(QThread):
    """Background thread for scanning startup"""
    finished = pyqtSignal(list)

    def __init__(self, analyzer):
        super().__init__()
        self.analyzer = analyzer

    def run(self):
        """Run startup scan"""
        items = self.analyzer.scan_all()
        self.finished.emit(items)


class StartupTab(QWidget):
    """Startup programs tab"""

    def __init__(self, app):
        """
        Initialize startup tab

        Args:
            app: SysPulse application instance
        """
        super().__init__()
        self.app = app
        self.items = []
        self.setup_ui()

    def setup_ui(self):
        """Setup startup tab UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        self.setLayout(layout)

        # Header
        header_layout = QHBoxLayout()
        layout.addLayout(header_layout)

        title = QLabel("🚀 Startup Programs")
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
        scan_btn = QPushButton("🔍 Scan Startup")
        scan_btn.clicked.connect(self.scan_startup)
        header_layout.addWidget(scan_btn)

        # Optimize button
        self.optimize_btn = QPushButton("⚡ Optimize Startup")
        self.optimize_btn.clicked.connect(self.optimize_startup)
        self.optimize_btn.setEnabled(False)
        self.optimize_btn.setProperty("class", "warning")
        header_layout.addWidget(self.optimize_btn)

        # Startup items table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Program", "Impact", "Description", "Safe to Disable", "Recommendation"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        # Stats label
        self.stats_label = QLabel("Click 'Scan Startup' to analyze startup programs")
        self.stats_label.setStyleSheet(f"""
            QLabel {{
                color: {get_color('text_light')};
                font-style: italic;
                padding: 10px;
            }}
        """)
        layout.addWidget(self.stats_label)

    def scan_startup(self):
        """Scan startup programs"""
        self.table.setRowCount(0)
        self.stats_label.setText("Scanning startup programs...")

        # Run scan in background
        self.scan_thread = StartupScanThread(self.app.startup_analyzer)
        self.scan_thread.finished.connect(self.scan_finished)
        self.scan_thread.start()

    def scan_finished(self, items):
        """Handle scan completion"""
        self.items = items

        if not items:
            self.stats_label.setText("No startup items found")
            return

        # Populate table
        self.table.setRowCount(len(items))

        safe_to_disable_count = 0

        for i, item in enumerate(items):
            # Program name
            self.table.setItem(i, 0, QTableWidgetItem(item.name))

            # Impact level (color-coded)
            impact_item = QTableWidgetItem(item.impact)
            if item.impact == "HIGH":
                impact_item.setBackground(Qt.GlobalColor.red)
                impact_item.setForeground(Qt.GlobalColor.white)
            elif item.impact == "MEDIUM":
                impact_item.setBackground(Qt.GlobalColor.yellow)
            else:
                impact_item.setBackground(Qt.GlobalColor.green)
                impact_item.setForeground(Qt.GlobalColor.white)
            self.table.setItem(i, 1, impact_item)

            # Description
            self.table.setItem(i, 2, QTableWidgetItem(item.description))

            # Safe to disable
            safe = "safe to disable" in item.recommendation.lower()
            safe_item = QTableWidgetItem("✓ Yes" if safe else "✗ No")
            if safe:
                safe_item.setForeground(Qt.GlobalColor.darkGreen)
                safe_to_disable_count += 1
            else:
                safe_item.setForeground(Qt.GlobalColor.darkRed)
            self.table.setItem(i, 3, safe_item)

            # Recommendation
            self.table.setItem(i, 4, QTableWidgetItem(item.recommendation))

        # Update stats
        summary = self.app.startup_analyzer.get_summary()
        self.stats_label.setText(
            f"Found {summary['total_items']} startup items | "
            f"High impact: {summary['high_impact_count']} | "
            f"Safe to disable: {safe_to_disable_count} | "
            f"Est. boot delay: {summary['estimated_boot_delay_seconds']}s"
        )

        # Enable optimize button if there are items to disable
        self.optimize_btn.setEnabled(safe_to_disable_count > 0)

    def optimize_startup(self):
        """Optimize startup by disabling safe items"""
        if not self.app.startup_manager:
            QMessageBox.warning(
                self,
                "Not Available",
                "Startup manager module is not available."
            )
            return

        # Count safe-to-disable items
        safe_items = [item for item in self.items if "safe to disable" in item.recommendation.lower()]

        if not safe_items:
            QMessageBox.information(
                self,
                "Nothing to Optimize",
                "No safe-to-disable startup items found."
            )
            return

        # Confirm
        reply = QMessageBox.question(
            self,
            "Optimize Startup",
            f"Disable {len(safe_items)} safe-to-disable startup item(s)?\n\n"
            f"This will:\n"
            f"• Create a backup before making changes\n"
            f"• Disable (not delete) the selected items\n"
            f"• Can be reversed if needed\n\n"
            f"Estimated boot time improvement: 5-15 seconds",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Disable items
        disabled_count = 0
        for item in safe_items:
            try:
                self.app.startup_manager.disable_item(item)
                disabled_count += 1
            except Exception as e:
                print(f"Error disabling {item.name}: {e}")

        # Show result
        QMessageBox.information(
            self,
            "Optimization Complete",
            f"Successfully disabled {disabled_count} startup item(s)\n\n"
            f"Your computer should boot faster next time!"
        )

        # Rescan
        self.scan_startup()
