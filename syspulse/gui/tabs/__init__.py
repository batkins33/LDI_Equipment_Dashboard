"""
Tab widgets for SysPulse GUI

Individual tab implementations for different modules.
"""

from .dashboard import DashboardTab
from .browser import BrowserTab
from .startup import StartupTab
from .storage import StorageTab
from .processes import ProcessesTab
from .reports import ReportsTab

__all__ = [
    'DashboardTab',
    'BrowserTab',
    'StartupTab',
    'StorageTab',
    'ProcessesTab',
    'ReportsTab'
]
