"""Gold layer reconciliation and flag generation.

Reconciles hours at the Equipment × Day grain.

Inputs (silver):
- f_timecard_header
- f_timecard_equipment_hours
- f_telematics_equipment_day
- f_inspection_equipment_day
- f_e360_meter_reading OR f_equipment360_meter_reading (POC normalizer)

Outputs (gold):
- g_equipment_day_recon
- g_equipment_day_flags
- g_exceptions
"""

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class ReconThresholds:
    """Thresholds for flagging."""

    # Variance is stored/computed as ratio: abs(a-b)/b.
    high_variance_ratio: float = 0.25
    approval_delay_days: int = 2
    missing_data_penalty: int = 20


class GoldReconciler:
    """Computes daily reconciliation metrics, flags, and exceptions."""

    def __init__(self, db_path: str, thresholds: Optional[ReconThresholds] = None):
        self.db_path = db_path
        self.thresholds = thresholds or ReconThresholds()
        self._ensure_gold_tables_exist()

    def _ensure_gold_tables_exist(self) -> None:
        """Ensure gold tables exist (for safety in SQLite POC)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS g_equipment_day_recon (
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
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS g_equipment_day_flags (
                  equipment_id INTEGER NOT NULL,
                  date_id DATE NOT NULL,
                  flag_code TEXT NOT NULL,
                  severity TEXT NOT NULL,
                  details_json TEXT,
                  created_at TIMESTAMP NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS g_exceptions (
                  exception_id INTEGER PRIMARY KEY AUTOINCREMENT,
                  equipment_id INTEGER,
                  date_id DATE,
                  job_id INTEGER,
                  owner_employee_id INTEGER,
                  status TEXT DEFAULT 'OPEN',
                  priority TEXT DEFAULT 'MED',
                  title TEXT,
                  description TEXT,
                  evidence_links_json TEXT,
                  created_at TIMESTAMP NOT NULL,
                  updated_at TIMESTAMP
                )
                """
            )

    def reconcile(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, int]:
        """Run reconciliation and write gold outputs.

        Args:
            start_date: inclusive YYYY-MM-DD
            end_date: inclusive YYYY-MM-DD

        Returns:
            Stats dict.
        """
        stats = {"equipment_days": 0, "flags": 0, "exceptions": 0}

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            equipment_days = self._get_equipment_days(conn, start_date, end_date)
            for equipment_id, date_id in equipment_days:
                recon_row, flags = self._compute_recon_for_day(conn, equipment_id, date_id)

                conn.execute(
                    """
                    INSERT OR REPLACE INTO g_equipment_day_recon (
                        equipment_id, date_id,
                        gps_engine_hours, tc_hours_provisional, tc_hours_final,
                        inspection_meter_delta, e360_meter_delta,
                        variance_tc_vs_gps, variance_meter_vs_gps,
                        confidence_score, flags_count,
                        recon_state, last_reconciled_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        recon_row["equipment_id"],
                        recon_row["date_id"],
                        recon_row["gps_engine_hours"],
                        recon_row["tc_hours_provisional"],
                        recon_row["tc_hours_final"],
                        recon_row["inspection_meter_delta"],
                        recon_row["e360_meter_delta"],
                        recon_row["variance_tc_vs_gps"],
                        recon_row["variance_meter_vs_gps"],
                        recon_row["confidence_score"],
                        recon_row["flags_count"],
                        recon_row["recon_state"],
                        recon_row["last_reconciled_at"],
                    ),
                )

                # Replace flags for this equipment-day to keep idempotent.
                conn.execute(
                    "DELETE FROM g_equipment_day_flags WHERE equipment_id = ? AND date_id = ?",
                    (equipment_id, date_id),
                )
                for flag in flags:
                    conn.execute(
                        """
                        INSERT INTO g_equipment_day_flags (
                            equipment_id, date_id, flag_code, severity, details_json, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            equipment_id,
                            date_id,
                            flag["flag_code"],
                            flag["severity"],
                            json.dumps(flag.get("details", {})),
                            datetime.now().isoformat(),
                        ),
                    )

                # Basic exception rule: any HIGH severity flag creates/updates an OPEN exception.
                high_flags = [f for f in flags if f["severity"] in ("HIGH", "CRIT")]
                if high_flags:
                    self._upsert_exception(conn, equipment_id, date_id, high_flags)
                    stats["exceptions"] += 1

                stats["equipment_days"] += 1
                stats["flags"] += len(flags)

            conn.commit()

        return stats

    def _get_equipment_days(
        self, conn: sqlite3.Connection, start_date: Optional[str], end_date: Optional[str]
    ) -> List[Tuple[int, str]]:
        """Union equipment-days present in any silver source."""
        where = ""
        params: List[Any] = []
        if start_date:
            where += " AND date_id >= ?"
            params.append(start_date)
        if end_date:
            where += " AND date_id <= ?"
            params.append(end_date)

        # Build union from telematics + inspections + timecards.
        query = f"""
            SELECT equipment_id, date_id FROM (
                SELECT equipment_id, date_id FROM f_telematics_equipment_day WHERE 1=1 {where}
                UNION
                SELECT equipment_id, date_id FROM f_inspection_equipment_day WHERE 1=1 {where}
                UNION
                SELECT h.equipment_id, h.work_date AS date_id
                FROM f_timecard_equipment_hours eh
                JOIN f_timecard_header h ON h.timecard_id = eh.timecard_id
                WHERE 1=1
                {where.replace('date_id', 'h.work_date')}
            )
            GROUP BY equipment_id, date_id
            ORDER BY date_id, equipment_id
        """
        cur = conn.execute(query, params + params + params)
        return [(int(r["equipment_id"]), str(r["date_id"])) for r in cur.fetchall()]

    def _table_has_column(self, conn: sqlite3.Connection, table: str, column: str) -> bool:
        cur = conn.execute(f"PRAGMA table_info({table})")
        cols = {row[1] for row in cur.fetchall()}
        return column in cols

    def _compute_recon_for_day(
        self, conn: sqlite3.Connection, equipment_id: int, date_id: str
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Compute reconciliation values and flags for a single equipment-day."""

        gps_hours = self._get_gps_engine_hours(conn, equipment_id, date_id)
        tc_prov, tc_final = self._get_timecard_hours(conn, equipment_id, date_id)
        insp_delta = self._get_inspection_meter_delta(conn, equipment_id, date_id)
        e360_delta = self._get_e360_meter_delta(conn, equipment_id, date_id)

        variance_tc_vs_gps = None
        if gps_hours is not None and tc_prov is not None and float(gps_hours) != 0.0:
            variance_tc_vs_gps = abs(float(tc_prov) - float(gps_hours)) / float(gps_hours)

        variance_meter_vs_gps = None
        # Prefer inspection delta, fallback to e360 delta.
        meter_delta = insp_delta if insp_delta is not None else e360_delta
        if gps_hours is not None and meter_delta is not None and float(gps_hours) != 0.0:
            variance_meter_vs_gps = abs(float(meter_delta) - float(gps_hours)) / float(gps_hours)

        flags: List[Dict[str, Any]] = []

        # Missing data flags
        if gps_hours is None:
            flags.append({"flag_code": "MISSING_TELEMATICS", "severity": "MED", "details": {}})
        if tc_prov is None:
            flags.append({"flag_code": "MISSING_TIMECARD", "severity": "MED", "details": {}})
        if insp_delta is None:
            flags.append({"flag_code": "MISSING_INSPECTION", "severity": "LOW", "details": {}})

        # Variance flags
        if variance_tc_vs_gps is not None and abs(variance_tc_vs_gps) >= self.thresholds.high_variance_ratio:
            flags.append(
                {
                    "flag_code": "HIGH_VARIANCE",
                    "severity": "HIGH",
                    "details": {"variance_ratio": variance_tc_vs_gps, "threshold_ratio": self.thresholds.high_variance_ratio},
                }
            )

        if variance_meter_vs_gps is not None and abs(variance_meter_vs_gps) >= self.thresholds.high_variance_ratio:
            flags.append(
                {
                    "flag_code": "HIGH_VARIANCE",
                    "severity": "HIGH",
                    "details": {"variance_ratio": variance_meter_vs_gps, "threshold_ratio": self.thresholds.high_variance_ratio},
                }
            )

        approval_delay_days = self._get_timecard_approval_delay_days(conn, equipment_id, date_id)
        if approval_delay_days is not None and approval_delay_days >= self.thresholds.approval_delay_days:
            flags.append(
                {
                    "flag_code": "APPROVAL_DELAY",
                    "severity": "MED",
                    "details": {"approval_delay_days": approval_delay_days, "threshold_days": self.thresholds.approval_delay_days},
                }
            )

        distinct_jobs = self._get_distinct_jobs_for_equipment_day(conn, equipment_id, date_id)
        if distinct_jobs is not None and distinct_jobs > 1:
            flags.append(
                {
                    "flag_code": "MULTI_JOB_ALLOCATION",
                    "severity": "MED",
                    "details": {"distinct_job_count": distinct_jobs},
                }
            )

        confidence = self._compute_confidence(gps_hours, tc_prov, meter_delta, flags)
        recon_state = self._compute_recon_state(flags, tc_final)

        recon_row = {
            "equipment_id": equipment_id,
            "date_id": date_id,
            "gps_engine_hours": gps_hours,
            "tc_hours_provisional": tc_prov,
            "tc_hours_final": tc_final,
            "inspection_meter_delta": insp_delta,
            "e360_meter_delta": e360_delta,
            "variance_tc_vs_gps": variance_tc_vs_gps,
            "variance_meter_vs_gps": variance_meter_vs_gps,
            "confidence_score": confidence,
            "flags_count": len(flags),
            "recon_state": recon_state,
            "last_reconciled_at": datetime.now().isoformat(),
        }

        return recon_row, flags

    def _get_timecard_approval_delay_days(
        self, conn: sqlite3.Connection, equipment_id: int, date_id: str
    ) -> Optional[int]:
        """Compute max approval delay (days) for timecards on this equipment-day."""
        cur = conn.execute(
            """
            SELECT h.submitted_at, h.approved_at
            FROM f_timecard_equipment_hours eh
            JOIN f_timecard_header h ON h.timecard_id = eh.timecard_id
            WHERE eh.equipment_id = ? AND h.work_date = ?
            """,
            (equipment_id, date_id),
        )
        max_delay: Optional[int] = None
        for row in cur.fetchall():
            submitted_at = row[0]
            approved_at = row[1]
            if not submitted_at or not approved_at:
                continue
            try:
                submitted = datetime.fromisoformat(str(submitted_at))
                approved = datetime.fromisoformat(str(approved_at))
            except ValueError:
                # If timestamps are not ISO strings, skip for POC.
                continue
            delay = (approved.date() - submitted.date()).days
            if max_delay is None or delay > max_delay:
                max_delay = delay
        return max_delay

    def _get_distinct_jobs_for_equipment_day(
        self, conn: sqlite3.Connection, equipment_id: int, date_id: str
    ) -> Optional[int]:
        """Count distinct jobs for a given equipment-day from timecards."""
        cur = conn.execute(
            """
            SELECT COUNT(DISTINCT h.job_id) AS c
            FROM f_timecard_equipment_hours eh
            JOIN f_timecard_header h ON h.timecard_id = eh.timecard_id
            WHERE eh.equipment_id = ? AND h.work_date = ?
            """,
            (equipment_id, date_id),
        )
        row = cur.fetchone()
        if not row:
            return None
        return int(row[0]) if row[0] is not None else None

    def _get_gps_engine_hours(self, conn: sqlite3.Connection, equipment_id: int, date_id: str) -> Optional[float]:
        # Support both canonical column `engine_hours` and POC columns `engine_hours_daily`.
        if self._table_has_column(conn, "f_telematics_equipment_day", "engine_hours"):
            cur = conn.execute(
                """
                SELECT engine_hours AS v
                FROM f_telematics_equipment_day
                WHERE equipment_id = ? AND date_id = ?
                LIMIT 1
                """,
                (equipment_id, date_id),
            )
        else:
            cur = conn.execute(
                """
                SELECT engine_hours_daily AS v
                FROM f_telematics_equipment_day
                WHERE equipment_id = ? AND date_id = ?
                LIMIT 1
                """,
                (equipment_id, date_id),
            )
        row = cur.fetchone()
        return float(row["v"]) if row and row["v"] is not None else None

    def _get_timecard_hours(self, conn: sqlite3.Connection, equipment_id: int, date_id: str) -> Tuple[Optional[float], Optional[float]]:
        # Provisional: non-approved OR marked provisional.
        cur = conn.execute(
            """
            SELECT
                SUM(CASE WHEN (eh.is_provisional = 1 OR h.status != 'APPROVED') THEN eh.hours ELSE 0 END) AS prov,
                SUM(CASE WHEN h.status = 'APPROVED' THEN eh.hours ELSE 0 END) AS final
            FROM f_timecard_equipment_hours eh
            JOIN f_timecard_header h ON h.timecard_id = eh.timecard_id
            WHERE eh.equipment_id = ? AND h.work_date = ?
            """,
            (equipment_id, date_id),
        )
        row = cur.fetchone()
        prov = float(row["prov"]) if row and row["prov"] is not None and row["prov"] != 0 else None
        final = float(row["final"]) if row and row["final"] is not None and row["final"] != 0 else None
        return prov, final

    def _get_inspection_meter_delta(self, conn: sqlite3.Connection, equipment_id: int, date_id: str) -> Optional[float]:
        if not self._table_has_column(conn, "f_inspection_equipment_day", "meter_delta"):
            return None
        cur = conn.execute(
            """
            SELECT meter_delta
            FROM f_inspection_equipment_day
            WHERE equipment_id = ? AND date_id = ?
            LIMIT 1
            """,
            (equipment_id, date_id),
        )
        row = cur.fetchone()
        return float(row["meter_delta"]) if row and row["meter_delta"] is not None else None

    def _get_e360_meter_delta(self, conn: sqlite3.Connection, equipment_id: int, date_id: str) -> Optional[float]:
        """Compute delta from meter readings.

        Canonical table: f_e360_meter_reading(equipment_id, reading_at, meter_value)
        POC table: f_equipment360_meter_reading(equipment_id, reading_date, meter_reading)
        """
        if self._table_exists(conn, "f_e360_meter_reading"):
            # Delta = last reading of day - previous reading before end of day.
            end_ts = f"{date_id}T23:59:59"
            cur = conn.execute(
                """
                SELECT meter_value, reading_at
                FROM f_e360_meter_reading
                WHERE equipment_id = ? AND reading_at <= ?
                ORDER BY reading_at DESC
                LIMIT 2
                """,
                (equipment_id, end_ts),
            )
            rows = cur.fetchall()
            if len(rows) >= 2 and rows[0]["meter_value"] is not None and rows[1]["meter_value"] is not None:
                return float(rows[0]["meter_value"]) - float(rows[1]["meter_value"])
            return None

        if self._table_exists(conn, "f_equipment360_meter_reading"):
            cur = conn.execute(
                """
                SELECT meter_reading
                FROM f_equipment360_meter_reading
                WHERE equipment_id = ? AND reading_date <= ?
                ORDER BY reading_date DESC
                LIMIT 2
                """,
                (equipment_id, date_id),
            )
            rows = cur.fetchall()
            if len(rows) >= 2 and rows[0]["meter_reading"] is not None and rows[1]["meter_reading"] is not None:
                return float(rows[0]["meter_reading"]) - float(rows[1]["meter_reading"])
            return None

        return None

    def _table_exists(self, conn: sqlite3.Connection, table: str) -> bool:
        cur = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name = ?",
            (table,),
        )
        return cur.fetchone() is not None

    def _compute_confidence(
        self,
        gps_hours: Optional[float],
        tc_hours: Optional[float],
        meter_delta: Optional[float],
        flags: List[Dict[str, Any]],
    ) -> int:
        score = 100
        if gps_hours is None:
            score -= self.thresholds.missing_data_penalty
        if tc_hours is None:
            score -= self.thresholds.missing_data_penalty
        if meter_delta is None:
            score -= int(self.thresholds.missing_data_penalty / 2)

        for flag in flags:
            if flag["severity"] == "HIGH":
                score -= 15
            elif flag["severity"] == "MED":
                score -= 7

        if score < 0:
            score = 0
        return score

    def _compute_recon_state(self, flags: List[Dict[str, Any]], tc_final: Optional[float]) -> str:
        if any(f["severity"] in ("HIGH", "CRIT") for f in flags):
            return "EXCEPTION"
        if tc_final is not None:
            return "FINAL"
        return "PROVISIONAL"

    def _upsert_exception(
        self, conn: sqlite3.Connection, equipment_id: int, date_id: str, high_flags: List[Dict[str, Any]]
    ) -> None:
        # Simple idempotent pattern: delete existing open exception for that grain and recreate.
        conn.execute(
            "DELETE FROM g_exceptions WHERE equipment_id = ? AND date_id = ? AND status = 'OPEN'",
            (equipment_id, date_id),
        )

        title = f"Reconciliation exception for equipment {equipment_id} on {date_id}"
        description = "High severity variance detected: " + ", ".join([f["flag_code"] for f in high_flags])
        evidence = {"flags": high_flags}

        conn.execute(
            """
            INSERT INTO g_exceptions (
                equipment_id, date_id, status, priority, title, description,
                evidence_links_json, created_at, updated_at
            ) VALUES (?, ?, 'OPEN', 'HIGH', ?, ?, ?, ?, ?)
            """,
            (
                equipment_id,
                date_id,
                title,
                description,
                json.dumps(evidence),
                datetime.now().isoformat(),
                datetime.now().isoformat(),
            ),
        )
