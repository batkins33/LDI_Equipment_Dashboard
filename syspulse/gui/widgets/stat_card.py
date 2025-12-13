"""
Stat Card Widget

Displays a single statistic with label and value.
"""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from ..styles import get_color


class StatCard(QFrame):
    """Stat card widget for displaying key metrics"""

    def __init__(self, label: str, value: str = "—", color: str = "primary"):
        """
        Initialize stat card

        Args:
            label: Card label text
            value: Card value text
            color: Color name from palette (primary, success, warning, danger)
        """
        super().__init__()

        self.color = color
        self.setup_ui(label, value)

    def setup_ui(self, label: str, value: str):
        """Setup card UI"""
        # Frame styling
        self.setFrameStyle(QFrame.Shape.Box)
        self.setLineWidth(0)

        # Set background and border
        color_hex = get_color(self.color)
        self.setStyleSheet(f"""
            StatCard {{
                background-color: white;
                border: 2px solid {color_hex};
                border-radius: 8px;
                padding: 20px;
            }}
            StatCard:hover {{
                background-color: #f8f9fa;
            }}
        """)

        # Layout
        layout = QVBoxLayout()
        layout.setSpacing(10)
        self.setLayout(layout)

        # Label
        self.label_widget = QLabel(label)
        self.label_widget.setStyleSheet(f"""
            QLabel {{
                color: {get_color('text_light')};
                font-size: 13px;
                font-weight: normal;
            }}
        """)
        layout.addWidget(self.label_widget)

        # Value
        self.value_widget = QLabel(value)
        self.value_widget.setStyleSheet(f"""
            QLabel {{
                color: {color_hex};
                font-size: 32px;
                font-weight: bold;
            }}
        """)
        layout.addWidget(self.value_widget)

        layout.addStretch()

    def set_value(self, value: str):
        """
        Update the card value

        Args:
            value: New value text
        """
        self.value_widget.setText(value)

    def set_label(self, label: str):
        """
        Update the card label

        Args:
            label: New label text
        """
        self.label_widget.setText(label)
