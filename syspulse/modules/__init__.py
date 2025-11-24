"""
SysPulse Modules

Core analysis modules for system utilities dashboard.
"""

from .browser_scanner import BrowserScanner, BrowserProfile
from .startup_analyzer import StartupAnalyzer, StartupItem, StartupImpact
from .storage_sense import StorageSense, StorageCategory
from .process_explainer import ProcessExplainer, ProcessInfo

__all__ = [
    'BrowserScanner',
    'BrowserProfile',
    'StartupAnalyzer',
    'StartupItem',
    'StartupImpact',
    'StorageSense',
    'StorageCategory',
    'ProcessExplainer',
    'ProcessInfo',
]
