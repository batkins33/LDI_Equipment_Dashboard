import sqlite3
from datetime import datetime
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gold.reconciliation import GoldReconciler, ReconThresholds


@pytest.fixture()
def db_path(tmp_path):
    return str(tmp_path / "test.sqlite")


def _create_min_tables(conn: sqlite3.Connection) -> None:
    conn.execute("CREATE TABLE dim_equipment (equipment_id INTEGER PRIMARY KEY, equipment_code TEXT)")
    conn.execute("CREATE TABLE dim_date (date_id DATE PRIMARY KEY)")

    conn.execute(
        """
        CREATE TABLE f_telematics_equipment_day (
            equipment_id INTEGER NOT NULL,
            date_id DATE NOT NULL,
            engine_hours_daily NUMERIC(10,2),
            snapshot_ts TEXT NOT NULL
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE f_timecard_header (
            timecard_id TEXT PRIMARY KEY,
            job_id INTEGER,
            work_date DATE NOT NULL,
            status TEXT,
            submitted_at TEXT,
            approved_at TEXT,
            snapshot_ts TEXT NOT NULL
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE f_timecard_equipment_hours (
            timecard_id TEXT NOT NULL,
            equipment_id INTEGER NOT NULL,
            hours NUMERIC(10,2) NOT NULL,
            is_provisional BOOLEAN DEFAULT TRUE,
            snapshot_ts TEXT NOT NULL
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE f_inspection_equipment_day (
            equipment_id INTEGER NOT NULL,
            date_id DATE NOT NULL,
            meter_delta NUMERIC(10,2),
            snapshot_ts TEXT NOT NULL
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE f_equipment360_meter_reading (
            reading_id TEXT PRIMARY KEY,
            equipment_id INTEGER NOT NULL,
            reading_date DATE NOT NULL,
            meter_reading NUMERIC(10,2),
            snapshot_ts TEXT NOT NULL
        )
        """
    )


def test_gold_recon_creates_high_variance_flag(db_path):
    with sqlite3.connect(db_path) as conn:
        _create_min_tables(conn)
        conn.execute("INSERT INTO dim_equipment (equipment_id, equipment_code) VALUES (1, 'EQ-001')")
        conn.execute("INSERT INTO dim_date (date_id) VALUES ('2026-01-01')")

        # GPS says 8 hrs
        conn.execute(
            "INSERT INTO f_telematics_equipment_day (equipment_id, date_id, engine_hours_daily, snapshot_ts) VALUES (1, '2026-01-01', 8, ?)",
            (datetime.now().isoformat(),),
        )

        # Timecard says 4 hrs -> variance ratio abs(4-8)/8 = 0.5
        conn.execute(
            "INSERT INTO f_timecard_header (timecard_id, job_id, work_date, status, submitted_at, approved_at, snapshot_ts) VALUES ('TC1', 10, '2026-01-01', 'PENDING', ?, NULL, ?)",
            (datetime.now().isoformat(), datetime.now().isoformat()),
        )
        conn.execute(
            "INSERT INTO f_timecard_equipment_hours (timecard_id, equipment_id, hours, is_provisional, snapshot_ts) VALUES ('TC1', 1, 4, 1, ?)",
            (datetime.now().isoformat(),),
        )
        conn.commit()

    reconciler = GoldReconciler(db_path=db_path, thresholds=ReconThresholds(high_variance_ratio=0.25))
    stats = reconciler.reconcile(start_date='2026-01-01', end_date='2026-01-01')

    assert stats["equipment_days"] == 1
    assert stats["flags"] >= 1

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        flags = conn.execute(
            "SELECT flag_code, severity FROM g_equipment_day_flags WHERE equipment_id = 1 AND date_id = '2026-01-01'"
        ).fetchall()
        assert any(f["flag_code"] == "HIGH_VARIANCE" for f in flags)


def test_gold_recon_creates_approval_delay_flag(db_path):
    with sqlite3.connect(db_path) as conn:
        _create_min_tables(conn)
        conn.execute("INSERT INTO dim_equipment (equipment_id, equipment_code) VALUES (1, 'EQ-001')")
        conn.execute("INSERT INTO dim_date (date_id) VALUES ('2026-01-01')")

        conn.execute(
            "INSERT INTO f_telematics_equipment_day (equipment_id, date_id, engine_hours_daily, snapshot_ts) VALUES (1, '2026-01-01', 8, ?)",
            (datetime.now().isoformat(),),
        )

        conn.execute(
            "INSERT INTO f_timecard_header (timecard_id, job_id, work_date, status, submitted_at, approved_at, snapshot_ts) VALUES ('TC1', 10, '2026-01-01', 'APPROVED', '2026-01-01T18:00:00', '2026-01-04T09:00:00', ?)",
            (datetime.now().isoformat(),),
        )
        conn.execute(
            "INSERT INTO f_timecard_equipment_hours (timecard_id, equipment_id, hours, is_provisional, snapshot_ts) VALUES ('TC1', 1, 8, 0, ?)",
            (datetime.now().isoformat(),),
        )
        conn.commit()

    reconciler = GoldReconciler(db_path=db_path, thresholds=ReconThresholds(approval_delay_days=2))
    reconciler.reconcile(start_date='2026-01-01', end_date='2026-01-01')

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        flags = conn.execute(
            "SELECT flag_code FROM g_equipment_day_flags WHERE equipment_id = 1 AND date_id = '2026-01-01'"
        ).fetchall()
        assert any(f["flag_code"] == "APPROVAL_DELAY" for f in flags)
