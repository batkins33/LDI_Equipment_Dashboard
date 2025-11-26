"""
GUI Module for SysPulse

PyQt6-based graphical user interface for system utilities dashboard.
"""

from .main_window import MainWindow
from .styles import get_stylesheet

__all__ = ['MainWindow', 'get_stylesheet']
