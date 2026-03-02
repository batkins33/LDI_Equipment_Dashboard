"""Reconciliation engine (spec path).

Delegates to GoldReconciler in src/gold/reconciliation.py.
"""

from dataclasses import dataclass
from typing import Dict, Optional

from gold.reconciliation import GoldReconciler, ReconThresholds


@dataclass(frozen=True)
class ReconConfig:
    """Configuration for reconciliation execution."""

    start_date: Optional[str] = None
    end_date: Optional[str] = None


class ReconEngine:
    """Public entrypoint for running reconciliation in the P0.5 demo."""

    def __init__(self, db_path: str, thresholds: Optional[ReconThresholds] = None):
        self._reconciler = GoldReconciler(db_path=db_path, thresholds=thresholds)

    def run(self, config: Optional[ReconConfig] = None) -> Dict[str, int]:
        config = config or ReconConfig()
        return self._reconciler.reconcile(start_date=config.start_date, end_date=config.end_date)
