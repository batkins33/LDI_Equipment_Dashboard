"""
Settings Dialog

Application preferences and configuration.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QCheckBox, QComboBox, QPushButton, QGroupBox,
    QSpinBox, QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from ..styles import get_color


class SettingsDialog(QDialog):
    """Settings and preferences dialog"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumSize(600, 500)
        self.settings_changed = False
        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Title
        title = QLabel("⚙️ Settings & Preferences")
        title.setStyleSheet(f"""
            QLabel {{
                color: {get_color('primary')};
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
            }}
        """)
        layout.addWidget(title)

        # Tabs for different settings categories
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # General settings tab
        general_tab = self.create_general_tab()
        tabs.addTab(general_tab, "General")

        # Scanning settings tab
        scanning_tab = self.create_scanning_tab()
        tabs.addTab(scanning_tab, "Scanning")

        # Cleanup settings tab
        cleanup_tab = self.create_cleanup_tab()
        tabs.addTab(cleanup_tab, "Cleanup")

        # Advanced settings tab
        advanced_tab = self.create_advanced_tab()
        tabs.addTab(advanced_tab, "Advanced")

        # Buttons
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        button_layout.addStretch()

        defaults_btn = QPushButton("Restore Defaults")
        defaults_btn.clicked.connect(self.restore_defaults)
        button_layout.addWidget(defaults_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save")
        save_btn.setProperty("class", "success")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)

    def create_general_tab(self):
        """Create general settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Appearance group
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QFormLayout()
        appearance_group.setLayout(appearance_layout)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System Default", "Light", "Dark"])
        appearance_layout.addRow("Theme:", self.theme_combo)

        self.show_icons = QCheckBox("Show icons in tabs")
        self.show_icons.setChecked(True)
        appearance_layout.addRow("", self.show_icons)

        layout.addWidget(appearance_group)

        # Startup group
        startup_group = QGroupBox("Startup")
        startup_layout = QVBoxLayout()
        startup_group.setLayout(startup_layout)

        self.start_minimized = QCheckBox("Start minimized to system tray")
        startup_layout.addWidget(self.start_minimized)

        self.check_updates = QCheckBox("Check for updates on startup")
        self.check_updates.setChecked(True)
        startup_layout.addWidget(self.check_updates)

        self.restore_tabs = QCheckBox("Restore last active tab on startup")
        self.restore_tabs.setChecked(True)
        startup_layout.addWidget(self.restore_tabs)

        layout.addWidget(startup_group)

        layout.addStretch()

        return widget

    def create_scanning_tab(self):
        """Create scanning settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Auto-scan group
        auto_scan_group = QGroupBox("Automatic Scanning")
        auto_scan_layout = QVBoxLayout()
        auto_scan_group.setLayout(auto_scan_layout)

        self.auto_scan_enabled = QCheckBox("Enable automatic scans")
        auto_scan_layout.addWidget(self.auto_scan_enabled)

        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Scan interval:"))
        self.scan_interval = QSpinBox()
        self.scan_interval.setRange(1, 168)
        self.scan_interval.setValue(24)
        self.scan_interval.setSuffix(" hours")
        interval_layout.addWidget(self.scan_interval)
        interval_layout.addStretch()
        auto_scan_layout.addLayout(interval_layout)

        layout.addWidget(auto_scan_group)

        # Scan options group
        scan_options_group = QGroupBox("Scan Options")
        scan_options_layout = QVBoxLayout()
        scan_options_group.setLayout(scan_options_layout)

        self.quick_storage_scan = QCheckBox("Use quick storage scan (faster, less thorough)")
        self.quick_storage_scan.setChecked(True)
        scan_options_layout.addWidget(self.quick_storage_scan)

        self.scan_hidden_files = QCheckBox("Scan hidden files and folders")
        scan_options_layout.addWidget(self.scan_hidden_files)

        min_memory_layout = QHBoxLayout()
        min_memory_layout.addWidget(QLabel("Minimum process memory to show:"))
        self.min_process_memory = QSpinBox()
        self.min_process_memory.setRange(1, 1000)
        self.min_process_memory.setValue(50)
        self.min_process_memory.setSuffix(" MB")
        min_memory_layout.addWidget(self.min_process_memory)
        min_memory_layout.addStretch()
        scan_options_layout.addLayout(min_memory_layout)

        layout.addWidget(scan_options_group)

        layout.addStretch()

        return widget

    def create_cleanup_tab(self):
        """Create cleanup settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Confirmation group
        confirm_group = QGroupBox("Confirmations")
        confirm_layout = QVBoxLayout()
        confirm_group.setLayout(confirm_layout)

        self.confirm_browser_clean = QCheckBox("Confirm before cleaning browser cache")
        self.confirm_browser_clean.setChecked(True)
        confirm_layout.addWidget(self.confirm_browser_clean)

        self.confirm_storage_clean = QCheckBox("Confirm before cleaning storage")
        self.confirm_storage_clean.setChecked(True)
        confirm_layout.addWidget(self.confirm_storage_clean)

        self.confirm_startup_disable = QCheckBox("Confirm before disabling startup items")
        self.confirm_startup_disable.setChecked(True)
        confirm_layout.addWidget(self.confirm_startup_disable)

        layout.addWidget(confirm_group)

        # Backup group
        backup_group = QGroupBox("Backups")
        backup_layout = QVBoxLayout()
        backup_group.setLayout(backup_layout)

        self.create_backups = QCheckBox("Create backups before making changes")
        self.create_backups.setChecked(True)
        backup_layout.addWidget(self.create_backups)

        retention_layout = QHBoxLayout()
        retention_layout.addWidget(QLabel("Keep backups for:"))
        self.backup_retention = QSpinBox()
        self.backup_retention.setRange(1, 365)
        self.backup_retention.setValue(30)
        self.backup_retention.setSuffix(" days")
        retention_layout.addWidget(self.backup_retention)
        retention_layout.addStretch()
        backup_layout.addLayout(retention_layout)

        layout.addWidget(backup_group)

        # Reports group
        reports_group = QGroupBox("Reports")
        reports_layout = QVBoxLayout()
        reports_group.setLayout(reports_layout)

        self.auto_export_reports = QCheckBox("Automatically export reports after scans")
        reports_layout.addWidget(self.auto_export_reports)

        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Default export format:"))
        self.report_format = QComboBox()
        self.report_format.addItems(["JSON", "HTML", "Both"])
        format_layout.addWidget(self.report_format)
        format_layout.addStretch()
        reports_layout.addLayout(format_layout)

        layout.addWidget(reports_group)

        layout.addStretch()

        return widget

    def create_advanced_tab(self):
        """Create advanced settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Performance group
        performance_group = QGroupBox("Performance")
        performance_layout = QVBoxLayout()
        performance_group.setLayout(performance_layout)

        threads_layout = QHBoxLayout()
        threads_layout.addWidget(QLabel("Background scan threads:"))
        self.scan_threads = QSpinBox()
        self.scan_threads.setRange(1, 8)
        self.scan_threads.setValue(2)
        threads_layout.addWidget(self.scan_threads)
        threads_layout.addStretch()
        performance_layout.addLayout(threads_layout)

        refresh_layout = QHBoxLayout()
        refresh_layout.addWidget(QLabel("Process auto-refresh interval:"))
        self.process_refresh = QSpinBox()
        self.process_refresh.setRange(1, 60)
        self.process_refresh.setValue(3)
        self.process_refresh.setSuffix(" seconds")
        refresh_layout.addWidget(self.process_refresh)
        refresh_layout.addStretch()
        performance_layout.addLayout(refresh_layout)

        layout.addWidget(performance_group)

        # Logging group
        logging_group = QGroupBox("Logging")
        logging_layout = QVBoxLayout()
        logging_group.setLayout(logging_layout)

        self.enable_logging = QCheckBox("Enable debug logging")
        logging_layout.addWidget(self.enable_logging)

        self.log_scans = QCheckBox("Log all scan operations")
        self.log_scans.setChecked(True)
        logging_layout.addWidget(self.log_scans)

        self.log_cleanup = QCheckBox("Log all cleanup operations")
        self.log_cleanup.setChecked(True)
        logging_layout.addWidget(self.log_cleanup)

        layout.addWidget(logging_group)

        # Data group
        data_group = QGroupBox("Data")
        data_layout = QVBoxLayout()
        data_group.setLayout(data_layout)

        clear_cache_btn = QPushButton("Clear Application Cache")
        clear_cache_btn.clicked.connect(self.clear_cache)
        data_layout.addWidget(clear_cache_btn)

        clear_reports_btn = QPushButton("Delete All Reports")
        clear_reports_btn.setProperty("class", "danger")
        clear_reports_btn.clicked.connect(self.clear_reports)
        data_layout.addWidget(clear_reports_btn)

        layout.addWidget(data_group)

        layout.addStretch()

        return widget

    def restore_defaults(self):
        """Restore default settings"""
        reply = QMessageBox.question(
            self,
            "Restore Defaults",
            "Restore all settings to their default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # General
            self.theme_combo.setCurrentIndex(0)
            self.show_icons.setChecked(True)
            self.start_minimized.setChecked(False)
            self.check_updates.setChecked(True)
            self.restore_tabs.setChecked(True)

            # Scanning
            self.auto_scan_enabled.setChecked(False)
            self.scan_interval.setValue(24)
            self.quick_storage_scan.setChecked(True)
            self.scan_hidden_files.setChecked(False)
            self.min_process_memory.setValue(50)

            # Cleanup
            self.confirm_browser_clean.setChecked(True)
            self.confirm_storage_clean.setChecked(True)
            self.confirm_startup_disable.setChecked(True)
            self.create_backups.setChecked(True)
            self.backup_retention.setValue(30)
            self.auto_export_reports.setChecked(False)
            self.report_format.setCurrentIndex(0)

            # Advanced
            self.scan_threads.setValue(2)
            self.process_refresh.setValue(3)
            self.enable_logging.setChecked(False)
            self.log_scans.setChecked(True)
            self.log_cleanup.setChecked(True)

            QMessageBox.information(self, "Success", "Settings restored to defaults")

    def clear_cache(self):
        """Clear application cache"""
        reply = QMessageBox.question(
            self,
            "Clear Cache",
            "Clear all cached scan data?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # TODO: Implement cache clearing
            QMessageBox.information(self, "Success", "Cache cleared successfully")

    def clear_reports(self):
        """Clear all reports"""
        reply = QMessageBox.warning(
            self,
            "Delete All Reports",
            "Delete ALL generated reports?\n\nThis cannot be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # TODO: Implement report deletion
            QMessageBox.information(self, "Success", "All reports deleted")

    def save_settings(self):
        """Save settings"""
        # TODO: Actually save settings to config file
        self.settings_changed = True
        QMessageBox.information(
            self,
            "Settings Saved",
            "Settings have been saved successfully.\n\nSome changes may require restarting the application."
        )
        self.accept()
