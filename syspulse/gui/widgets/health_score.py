"""
Health Score Widget

Displays system health score with visual gauge.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt
from ..styles import get_color


class HealthScore(QWidget):
    """Health score gauge widget"""

    def __init__(self):
        """Initialize health score widget"""
        super().__init__()
        self.score = 0
        self.setup_ui()

    def setup_ui(self):
        """Setup widget UI"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        self.setLayout(layout)

        # Header
        header = QLabel("System Health")
        header.setStyleSheet(f"""
            QLabel {{
                color: {get_color('text')};
                font-size: 16px;
                font-weight: bold;
            }}
        """)
        layout.addWidget(header)

        # Progress bar (used as gauge)
        self.gauge = QProgressBar()
        self.gauge.setMinimum(0)
        self.gauge.setMaximum(100)
        self.gauge.setValue(0)
        self.gauge.setTextVisible(True)
        self.gauge.setFormat("%v%")
        self.gauge.setFixedHeight(40)

        # Initial styling
        self.update_gauge_style(0)

        layout.addWidget(self.gauge)

        # Description
        self.description = QLabel("Run a scan to calculate health score")
        self.description.setStyleSheet(f"""
            QLabel {{
                color: {get_color('text_light')};
                font-size: 12px;
                font-style: italic;
            }}
        """)
        self.description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.description)

    def set_score(self, score: int):
        """
        Update health score

        Args:
            score: Health score (0-100)
        """
        self.score = max(0, min(100, score))
        self.gauge.setValue(self.score)
        self.update_gauge_style(self.score)
        self.update_description(self.score)

    def update_gauge_style(self, score: int):
        """Update gauge color based on score"""
        if score >= 80:
            color = get_color('success')
            bg_color = '#d4edda'
        elif score >= 60:
            color = get_color('info')
            bg_color = '#d1ecf1'
        elif score >= 40:
            color = get_color('warning')
            bg_color = '#fff3cd'
        else:
            color = get_color('danger')
            bg_color = '#f8d7da'

        self.gauge.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {color};
                border-radius: 8px;
                background-color: {bg_color};
                text-align: center;
                font-size: 18px;
                font-weight: bold;
                color: {color};
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 6px;
            }}
        """)

    def update_description(self, score: int):
        """Update description based on score"""
        if score >= 80:
            text = "✓ Excellent - Your system is running smoothly"
        elif score >= 60:
            text = "Good - Minor optimizations recommended"
        elif score >= 40:
            text = "⚠ Fair - Several issues detected"
        else:
            text = "⚠ Poor - Significant optimization needed"

        self.description.setText(text)
