"""
Reusable widgets for SysPulse GUI

Custom widgets used across multiple tabs.
"""

from .stat_card import StatCard
from .health_score import HealthScore

# More widgets will be imported here as they are implemented
# from .profile_table import ProfileTable
# from .toggle_switch import ToggleSwitch

__all__ = ['StatCard', 'HealthScore']
