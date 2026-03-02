from pathlib import Path
import sys
import sqlite3

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from api.app import create_app


@pytest.fixture()
def db_path(tmp_path):
    return str(tmp_path / "test.sqlite")


def _create_views_and_tables(db_path: str) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE dim_equipment (equipment_id INTEGER PRIMARY KEY, equipment_code TEXT);
            CREATE TABLE dim_job (job_id INTEGER PRIMARY KEY, job_code TEXT);

            CREATE TABLE g_equipment_day_recon (
              equipment_id INTEGER NOT NULL,
              date_id DATE NOT NULL,
              gps_engine_hours NUMERIC(10,2),
              tc_hours_provisional NUMERIC(10,2),
              tc_hours_final NUMERIC(10,2),
              inspection_meter_delta NUMERIC(10,2),
              e360_meter_delta NUMERIC(10,2),
              variance_tc_vs_gps NUMERIC(10,2),
              variance_meter_vs_gps NUMERIC(10,2),
              confidence_score INT,
              flags_count INT,
              recon_state TEXT,
              last_reconciled_at TIMESTAMP,
              PRIMARY KEY (equipment_id, date_id)
            );

            CREATE TABLE g_exceptions (
              exception_id INTEGER PRIMARY KEY AUTOINCREMENT,
              equipment_id INTEGER,
              date_id DATE,
              job_id INTEGER,
              owner_employee_id INTEGER,
              status TEXT,
              priority TEXT,
              title TEXT,
              description TEXT,
              evidence_links_json TEXT,
              created_at TIMESTAMP,
              updated_at TIMESTAMP
            );

            CREATE TABLE f_timecard_header (
              timecard_id TEXT PRIMARY KEY,
              work_date DATE,
              status TEXT
            );

            CREATE TABLE f_inspection_equipment_day (
              equipment_id INTEGER,
              date_id DATE,
              issues_count INTEGER
            );

            CREATE TABLE f_telematics_equipment_day (
              equipment_id INTEGER,
              date_id DATE,
              gps_active BOOLEAN
            );
            """
        )

        conn.executescript(
            (Path(__file__).resolve().parents[1] / "src" / "views" / "dashboard_views.sql").read_text()
        )

        conn.execute("INSERT INTO dim_equipment (equipment_id, equipment_code) VALUES (1, 'EQ-001')")
        conn.execute(
            "INSERT INTO g_equipment_day_recon (equipment_id, date_id, gps_engine_hours, tc_hours_provisional, confidence_score, flags_count, recon_state, last_reconciled_at) VALUES (1, '2026-01-01', 8, 8, 90, 0, 'PROVISIONAL', '2026-01-02T00:00:00')"
        )
        conn.execute(
            "INSERT INTO g_exceptions (equipment_id, date_id, status, priority, title, description, created_at) VALUES (1, '2026-01-01', 'OPEN', 'HIGH', 't', 'd', '2026-01-02T00:00:00')"
        )
        conn.commit()


def test_overview_endpoint_returns_rows(db_path):
    _create_views_and_tables(db_path)
    app = create_app(db_path)
    client = app.test_client()

    resp = client.get("/api/dashboard/overview")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)


def test_exceptions_endpoint_returns_rows(db_path):
    _create_views_and_tables(db_path)
    app = create_app(db_path)
    client = app.test_client()

    resp = client.get("/api/dashboard/exceptions")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
