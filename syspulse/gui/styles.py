"""
Styles and Theming for SysPulse GUI

Provides consistent styling across the application.
"""

# Color palette
COLORS = {
    'primary': '#667eea',
    'primary_dark': '#764ba2',
    'success': '#27ae60',
    'warning': '#f39c12',
    'danger': '#e74c3c',
    'info': '#3498db',
    'background': '#f8f9fa',
    'surface': '#ffffff',
    'text': '#333333',
    'text_light': '#666666',
    'text_lighter': '#999999',
    'border': '#dddddd',
}


def get_stylesheet() -> str:
    """
    Get the application stylesheet

    Returns:
        CSS stylesheet string for Qt application
    """
    return f"""
    /* Main Window */
    QMainWindow {{
        background-color: {COLORS['background']};
    }}

    /* Tab Widget */
    QTabWidget::pane {{
        border: 1px solid {COLORS['border']};
        background-color: {COLORS['surface']};
        border-radius: 4px;
    }}

    QTabBar::tab {{
        background-color: {COLORS['background']};
        color: {COLORS['text_light']};
        padding: 10px 20px;
        border: 1px solid {COLORS['border']};
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        margin-right: 2px;
    }}

    QTabBar::tab:selected {{
        background-color: {COLORS['surface']};
        color: {COLORS['primary']};
        font-weight: bold;
    }}

    QTabBar::tab:hover {{
        background-color: #e9ecef;
    }}

    /* Push Buttons */
    QPushButton {{
        background-color: {COLORS['primary']};
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 4px;
        font-size: 13px;
        font-weight: bold;
    }}

    QPushButton:hover {{
        background-color: {COLORS['primary_dark']};
    }}

    QPushButton:pressed {{
        background-color: #5a67d8;
    }}

    QPushButton:disabled {{
        background-color: {COLORS['border']};
        color: {COLORS['text_lighter']};
    }}

    QPushButton.success {{
        background-color: {COLORS['success']};
    }}

    QPushButton.success:hover {{
        background-color: #229954;
    }}

    QPushButton.danger {{
        background-color: {COLORS['danger']};
    }}

    QPushButton.danger:hover {{
        background-color: #c0392b;
    }}

    QPushButton.warning {{
        background-color: {COLORS['warning']};
    }}

    QPushButton.warning:hover {{
        background-color: #e67e22;
    }}

    /* Labels */
    QLabel {{
        color: {COLORS['text']};
        font-size: 13px;
    }}

    QLabel.header {{
        font-size: 20px;
        font-weight: bold;
        color: {COLORS['primary']};
    }}

    QLabel.subheader {{
        font-size: 16px;
        font-weight: bold;
        color: {COLORS['text']};
    }}

    QLabel.caption {{
        font-size: 11px;
        color: {COLORS['text_light']};
    }}

    /* Tables */
    QTableWidget {{
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        background-color: {COLORS['surface']};
        gridline-color: {COLORS['border']};
    }}

    QTableWidget::item {{
        padding: 8px;
    }}

    QTableWidget::item:selected {{
        background-color: {COLORS['primary']};
        color: white;
    }}

    QHeaderView::section {{
        background-color: {COLORS['background']};
        color: {COLORS['text']};
        padding: 10px;
        border: none;
        border-bottom: 2px solid {COLORS['primary']};
        font-weight: bold;
    }}

    /* Progress Bars */
    QProgressBar {{
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        text-align: center;
        background-color: {COLORS['background']};
    }}

    QProgressBar::chunk {{
        background-color: {COLORS['primary']};
        border-radius: 3px;
    }}

    /* Group Boxes */
    QGroupBox {{
        border: 2px solid {COLORS['border']};
        border-radius: 4px;
        margin-top: 10px;
        padding-top: 10px;
        font-weight: bold;
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 5px;
        color: {COLORS['primary']};
    }}

    /* Scroll Bars */
    QScrollBar:vertical {{
        border: none;
        background-color: {COLORS['background']};
        width: 12px;
        margin: 0px;
    }}

    QScrollBar::handle:vertical {{
        background-color: {COLORS['border']};
        min-height: 20px;
        border-radius: 6px;
    }}

    QScrollBar::handle:vertical:hover {{
        background-color: {COLORS['text_light']};
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    /* Text Edits */
    QTextEdit, QPlainTextEdit {{
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        background-color: {COLORS['surface']};
        padding: 8px;
    }}

    /* Line Edits */
    QLineEdit {{
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        padding: 8px;
        background-color: {COLORS['surface']};
    }}

    QLineEdit:focus {{
        border: 2px solid {COLORS['primary']};
    }}

    /* Combo Boxes */
    QComboBox {{
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        padding: 6px;
        background-color: {COLORS['surface']};
    }}

    QComboBox:hover {{
        border: 1px solid {COLORS['primary']};
    }}

    QComboBox::drop-down {{
        border: none;
    }}

    /* Status Bar */
    QStatusBar {{
        background-color: {COLORS['background']};
        color: {COLORS['text_light']};
    }}

    /* Menu Bar */
    QMenuBar {{
        background-color: {COLORS['surface']};
        border-bottom: 1px solid {COLORS['border']};
    }}

    QMenuBar::item {{
        padding: 8px 12px;
        background-color: transparent;
    }}

    QMenuBar::item:selected {{
        background-color: {COLORS['primary']};
        color: white;
    }}

    /* Menus */
    QMenu {{
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
    }}

    QMenu::item {{
        padding: 8px 30px 8px 20px;
    }}

    QMenu::item:selected {{
        background-color: {COLORS['primary']};
        color: white;
    }}

    /* Checkboxes */
    QCheckBox {{
        spacing: 8px;
    }}

    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 2px solid {COLORS['border']};
        border-radius: 3px;
        background-color: {COLORS['surface']};
    }}

    QCheckBox::indicator:checked {{
        background-color: {COLORS['primary']};
        border-color: {COLORS['primary']};
    }}

    /* Radio Buttons */
    QRadioButton {{
        spacing: 8px;
    }}

    QRadioButton::indicator {{
        width: 18px;
        height: 18px;
        border: 2px solid {COLORS['border']};
        border-radius: 9px;
        background-color: {COLORS['surface']};
    }}

    QRadioButton::indicator:checked {{
        background-color: {COLORS['primary']};
        border-color: {COLORS['primary']};
    }}
    """


def get_color(name: str) -> str:
    """
    Get a color from the palette

    Args:
        name: Color name from COLORS dict

    Returns:
        Hex color code
    """
    return COLORS.get(name, COLORS['text'])
