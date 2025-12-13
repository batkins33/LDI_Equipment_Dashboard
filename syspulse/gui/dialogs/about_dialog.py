"""
About Dialog

Application information and credits.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit
from PyQt6.QtCore import Qt
from ..styles import get_color


class AboutDialog(QDialog):
    """About SysPulse dialog"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About SysPulse")
        self.setFixedSize(500, 600)
        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Logo/Title
        title = QLabel("🔧 SysPulse")
        title.setStyleSheet(f"""
            QLabel {{
                color: {get_color('primary')};
                font-size: 36px;
                font-weight: bold;
                padding: 20px;
            }}
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Version
        version = QLabel("Version 3.0.0-alpha.9")
        version.setStyleSheet(f"""
            QLabel {{
                color: {get_color('text_light')};
                font-size: 16px;
                padding-bottom: 10px;
            }}
        """)
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)

        # Tagline
        tagline = QLabel("Control the bullshit.\nMake your computer run better.")
        tagline.setStyleSheet(f"""
            QLabel {{
                color: {get_color('text')};
                font-size: 14px;
                font-style: italic;
                padding: 10px;
            }}
        """)
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(tagline)

        # Description
        description = QTextEdit()
        description.setReadOnly(True)
        description.setHtml(f"""
<div style="font-family: sans-serif; padding: 10px;">
<h3 style="color: {get_color('primary')};">About</h3>
<p>
SysPulse is a lightweight system utilities dashboard that gives you understandable
control over the things that actually impact your computer's performance.
</p>

<h3 style="color: {get_color('primary')};">Features</h3>
<ul>
<li><b>Dashboard</b> - System overview with health score</li>
<li><b>Browser Management</b> - Profile analysis and cache cleanup</li>
<li><b>Startup Optimization</b> - Program management and boot time improvement</li>
<li><b>Storage Analysis</b> - Space cleanup and organization</li>
<li><b>Process Monitoring</b> - Real-time system resource tracking</li>
<li><b>Report Generation</b> - JSON and HTML export capabilities</li>
</ul>

<h3 style="color: {get_color('primary')};">Development</h3>
<p>
<b>Phase 1</b> - CLI analysis tools (v1.0.0) ✓<br>
<b>Phase 2</b> - Actionable controls (v2.0.0) ✓<br>
<b>Phase 3</b> - Desktop GUI (v3.0.0) ✓
</p>

<h3 style="color: {get_color('primary')};">Technology</h3>
<p>
Built with Python and PyQt6<br>
Cross-platform: Windows, macOS, Linux
</p>

<h3 style="color: {get_color('primary')};">License</h3>
<p>
Open source software<br>
Made with 🔧 and frustration at bloated utility software
</p>
</div>
        """)
        layout.addWidget(description)

        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)
