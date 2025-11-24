"""
SysPulse Actions Modules

Actionable controls for Phase 2 - allows users to take action
on the recommendations from Phase 1 analysis.

All action modules follow safety-first principles:
- Confirmations required
- Dry-run mode available
- Backups before changes
- Graceful error handling
- Audit logging
"""

from .browser_actions import BrowserCleaner
from .storage_actions import StorageCleaner

__all__ = [
    'BrowserCleaner',
    'StorageCleaner',
]
