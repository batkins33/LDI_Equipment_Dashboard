"""Exceptions helpers (spec path).

In this P0.5 POC, exceptions are generated within GoldReconciler.
This module exists so later phases can expand exception routing/assignment.
"""

EXCEPTION_STATUS_OPEN = "OPEN"
EXCEPTION_STATUS_CLOSED = "CLOSED"

PRIORITY_LOW = "LOW"
PRIORITY_MED = "MED"
PRIORITY_HIGH = "HIGH"
