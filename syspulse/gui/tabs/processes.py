"""
Processes Tab

Real-time process monitoring.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QHeaderView, QLineEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from ..styles import get_color


class ProcessScanThread(QThread):
    """Background thread for scanning processes"""
    finished = pyqtSignal(list, dict)

    def __init__(self, process_explainer):
        super().__init__()
        self.process_explainer = process_explainer

    def run(self):
        """Run process scan"""
        processes = self.process_explainer.scan_all(min_memory_mb=10)
        summary = self.process_explainer.get_summary()
        self.finished.emit(processes, summary)


class ProcessesTab(QWidget):
    """Background processes tab"""

    def __init__(self, app):
        """
        Initialize processes tab

        Args:
            app: SysPulse application instance
        """
        super().__init__()
        self.app = app
        self.processes = []
        self.auto_refresh = False
        self.setup_ui()

        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.scan_processes)
        self.refresh_timer.setInterval(3000)  # 3 seconds

    def setup_ui(self):
        """Setup processes tab UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        self.setLayout(layout)

        # Header
        header_layout = QHBoxLayout()
        layout.addLayout(header_layout)

        title = QLabel("⚙️ Background Processes")
        title.setStyleSheet(f"""
            QLabel {{
                color: {get_color('primary')};
                font-size: 24px;
                font-weight: bold;
            }}
        """)
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Search processes...")
        self.search_box.textChanged.connect(self.filter_processes)
        self.search_box.setFixedWidth(250)
        header_layout.addWidget(self.search_box)

        # Scan button
        scan_btn = QPushButton("🔄 Refresh")
        scan_btn.clicked.connect(self.scan_processes)
        header_layout.addWidget(scan_btn)

        # Auto-refresh toggle
        self.auto_refresh_btn = QPushButton("▶️ Auto-Refresh")
        self.auto_refresh_btn.clicked.connect(self.toggle_auto_refresh)
        self.auto_refresh_btn.setCheckable(True)
        header_layout.addWidget(self.auto_refresh_btn)

        # Processes table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Process", "CPU %", "Memory (MB)", "Category", "Description", "Recommendation"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)

        # Stats label
        self.stats_label = QLabel("Click 'Refresh' to scan running processes")
        self.stats_label.setStyleSheet(f"""
            QLabel {{
                color: {get_color('text_light')};
                font-style: italic;
                padding: 10px;
            }}
        """)
        layout.addWidget(self.stats_label)

    def scan_processes(self):
        """Scan running processes"""
        if not hasattr(self, 'scan_thread') or not self.scan_thread.isRunning():
            self.scan_thread = ProcessScanThread(self.app.process_explainer)
            self.scan_thread.finished.connect(self.scan_finished)
            self.scan_thread.start()

    def scan_finished(self, processes, summary):
        """Handle scan completion"""
        self.processes = processes

        # Disable sorting temporarily for better performance
        self.table.setSortingEnabled(False)

        # Clear and repopulate
        self.table.setRowCount(len(processes))

        for i, proc in enumerate(processes):
            # Process name
            self.table.setItem(i, 0, QTableWidgetItem(proc.name))

            # CPU %
            cpu_item = QTableWidgetItem(f"{proc.cpu_percent:.1f}")
            if proc.cpu_percent > 50:
                cpu_item.setBackground(Qt.GlobalColor.red)
                cpu_item.setForeground(Qt.GlobalColor.white)
            elif proc.cpu_percent > 25:
                cpu_item.setBackground(Qt.GlobalColor.yellow)
            self.table.setItem(i, 1, cpu_item)

            # Memory MB
            mem_item = QTableWidgetItem(f"{proc.memory_mb:.1f}")
            if proc.memory_mb > 500:
                mem_item.setBackground(Qt.GlobalColor.red)
                mem_item.setForeground(Qt.GlobalColor.white)
            elif proc.memory_mb > 200:
                mem_item.setBackground(Qt.GlobalColor.yellow)
            self.table.setItem(i, 2, mem_item)

            # Category
            self.table.setItem(i, 3, QTableWidgetItem(proc.category))

            # Description
            self.table.setItem(i, 4, QTableWidgetItem(proc.description))

            # Recommendation
            self.table.setItem(i, 5, QTableWidgetItem(proc.recommendation))

        # Re-enable sorting
        self.table.setSortingEnabled(True)

        # Apply current filter
        self.filter_processes(self.search_box.text())

        # Update stats
        self.stats_label.setText(
            f"Total processes: {summary['total_processes']} | "
            f"CPU: {summary['total_cpu_percent']:.1f}% | "
            f"Memory: {summary['total_memory_gb']:.2f} GB"
        )

    def filter_processes(self, text):
        """Filter processes by search text"""
        for row in range(self.table.rowCount()):
            # Check if any column matches search text
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break

            # Show/hide row
            self.table.setRowHidden(row, not match)

    def toggle_auto_refresh(self):
        """Toggle auto-refresh"""
        self.auto_refresh = not self.auto_refresh

        if self.auto_refresh:
            self.auto_refresh_btn.setText("⏸️ Auto-Refresh")
            self.refresh_timer.start()
            self.scan_processes()  # Immediate scan
        else:
            self.auto_refresh_btn.setText("▶️ Auto-Refresh")
            self.refresh_timer.stop()
