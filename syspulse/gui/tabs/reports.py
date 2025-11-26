"""
Reports Tab

Report history and export.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QFileDialog, QMessageBox, QTextEdit, QSplitter
)
from PyQt6.QtCore import Qt
from pathlib import Path
from ..styles import get_color


class ReportsTab(QWidget):
    """Reports and history tab"""

    def __init__(self, app):
        """
        Initialize reports tab

        Args:
            app: SysPulse application instance
        """
        super().__init__()
        self.app = app
        self.setup_ui()
        self.load_reports()

    def setup_ui(self):
        """Setup reports tab UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        self.setLayout(layout)

        # Header
        header_layout = QHBoxLayout()
        layout.addLayout(header_layout)

        title = QLabel("📊 Reports & History")
        title.setStyleSheet(f"""
            QLabel {{
                color: {get_color('primary')};
                font-size: 24px;
                font-weight: bold;
            }}
        """)
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Export buttons
        export_json_btn = QPushButton("📄 Export JSON")
        export_json_btn.clicked.connect(lambda: self.export_report('json'))
        header_layout.addWidget(export_json_btn)

        export_html_btn = QPushButton("📊 Export HTML")
        export_html_btn.clicked.connect(lambda: self.export_report('html'))
        header_layout.addWidget(export_html_btn)

        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh List")
        refresh_btn.clicked.connect(self.load_reports)
        header_layout.addWidget(refresh_btn)

        # Splitter for list and preview
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Reports list
        list_widget = QWidget()
        list_layout = QVBoxLayout()
        list_widget.setLayout(list_layout)

        list_label = QLabel("Report History")
        list_label.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: bold;
                color: {get_color('text')};
            }}
        """)
        list_layout.addWidget(list_label)

        self.reports_list = QListWidget()
        self.reports_list.itemClicked.connect(self.on_report_selected)
        list_layout.addWidget(self.reports_list)

        splitter.addWidget(list_widget)

        # Preview panel
        preview_widget = QWidget()
        preview_layout = QVBoxLayout()
        preview_widget.setLayout(preview_layout)

        preview_label = QLabel("Report Details")
        preview_label.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: bold;
                color: {get_color('text')};
            }}
        """)
        preview_layout.addWidget(preview_label)

        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setText("Select a report to view details")
        preview_layout.addWidget(self.preview)

        # Action buttons for selected report
        action_layout = QHBoxLayout()
        preview_layout.addLayout(action_layout)

        self.open_btn = QPushButton("📂 Open in File Explorer")
        self.open_btn.clicked.connect(self.open_report_location)
        self.open_btn.setEnabled(False)
        action_layout.addWidget(self.open_btn)

        self.delete_btn = QPushButton("🗑️ Delete Report")
        self.delete_btn.clicked.connect(self.delete_report)
        self.delete_btn.setEnabled(False)
        self.delete_btn.setProperty("class", "danger")
        action_layout.addWidget(self.delete_btn)

        splitter.addWidget(preview_widget)

        # Set splitter proportions
        splitter.setSizes([400, 600])

        # Info label
        info_label = QLabel(f"Reports are saved to: {self.app.report_generator.reports_dir}")
        info_label.setStyleSheet(f"""
            QLabel {{
                color: {get_color('text_light')};
                font-size: 11px;
                font-style: italic;
                padding: 5px;
            }}
        """)
        layout.addWidget(info_label)

    def load_reports(self):
        """Load report history"""
        self.reports_list.clear()

        try:
            reports = self.app.report_generator.list_reports()

            if not reports:
                item = QListWidgetItem("No reports found")
                item.setFlags(Qt.ItemFlag.NoItemFlags)
                self.reports_list.addItem(item)
                return

            for report in reports:
                timestamp = report.get('timestamp', 'Unknown')
                scans = ', '.join(report.get('scans', []))
                size_kb = report.get('size', 0) / 1024

                item_text = f"📄 {timestamp}\n   {scans} ({size_kb:.1f} KB)"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, report)
                self.reports_list.addItem(item)

        except Exception as e:
            QMessageBox.warning(
                self,
                "Error Loading Reports",
                f"Could not load reports:\n{str(e)}"
            )

    def on_report_selected(self, item):
        """Handle report selection"""
        report = item.data(Qt.ItemDataRole.UserRole)

        if not report:
            return

        # Show report details
        details = f"""
<h3>Report Details</h3>

<p><b>Timestamp:</b> {report.get('timestamp', 'Unknown')}</p>
<p><b>Version:</b> {report.get('version', 'Unknown')}</p>
<p><b>File:</b> {report.get('file', 'Unknown')}</p>
<p><b>Size:</b> {report.get('size', 0) / 1024:.2f} KB</p>

<h4>Scans Included:</h4>
<ul>
"""

        for scan in report.get('scans', []):
            details += f"<li>{scan.title()}</li>"

        details += "</ul>"

        self.preview.setHtml(details)

        # Enable action buttons
        self.open_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)

    def export_report(self, format):
        """Export current scan results to report"""
        if not self.app.last_scan_results:
            QMessageBox.information(
                self,
                "No Scan Data",
                "No scan results available. Run a scan first from the Dashboard tab."
            )
            return

        try:
            if format == 'json':
                file_path = self.app.report_generator.generate_json_report(
                    browser_data=self.app.last_scan_results.get('browser'),
                    startup_data=self.app.last_scan_results.get('startup'),
                    storage_data=self.app.last_scan_results.get('storage'),
                    process_data=self.app.last_scan_results.get('process')
                )
            else:  # html
                file_path = self.app.report_generator.generate_html_report(
                    browser_data=self.app.last_scan_results.get('browser'),
                    startup_data=self.app.last_scan_results.get('startup'),
                    storage_data=self.app.last_scan_results.get('storage'),
                    process_data=self.app.last_scan_results.get('process')
                )

            QMessageBox.information(
                self,
                "Export Complete",
                f"Report exported successfully!\n\nLocation:\n{file_path}"
            )

            # Refresh list
            self.load_reports()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"Failed to export report:\n{str(e)}"
            )

    def open_report_location(self):
        """Open report directory in file explorer"""
        import subprocess
        import platform

        reports_dir = self.app.report_generator.reports_dir

        try:
            if platform.system() == 'Windows':
                subprocess.run(['explorer', str(reports_dir)])
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', str(reports_dir)])
            else:  # Linux
                subprocess.run(['xdg-open', str(reports_dir)])
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error",
                f"Could not open file explorer:\n{str(e)}"
            )

    def delete_report(self):
        """Delete selected report"""
        current_item = self.reports_list.currentItem()
        if not current_item:
            return

        report = current_item.data(Qt.ItemDataRole.UserRole)
        if not report:
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Delete Report",
            f"Delete this report?\n\n{report.get('file', 'Unknown')}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Delete file
        try:
            file_path = Path(report.get('file'))
            if file_path.exists():
                file_path.unlink()

            QMessageBox.information(
                self,
                "Deleted",
                "Report deleted successfully"
            )

            # Refresh list
            self.load_reports()
            self.preview.setText("Select a report to view details")
            self.open_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Delete Error",
                f"Could not delete report:\n{str(e)}"
            )
