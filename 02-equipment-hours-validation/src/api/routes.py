"""API routes for dashboard views."""

import sqlite3
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, request


def _query_rows(db_path: str, sql: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
    params = params or []
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(sql, params)
        return [dict(r) for r in cur.fetchall()]


def register_routes(app: Flask) -> None:
    db_path = app.config["DB_PATH"]

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/api/dashboard/overview")
    def executive_overview():
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        sql = "SELECT * FROM v_executive_overview WHERE 1=1"
        params: List[Any] = []
        if start_date:
            sql += " AND date_id >= ?"
            params.append(start_date)
        if end_date:
            sql += " AND date_id <= ?"
            params.append(end_date)
        sql += " ORDER BY date_id DESC"

        return jsonify(_query_rows(db_path, sql, params))

    @app.get("/api/dashboard/provisional")
    def yesterday_provisional():
        # The view is already filtered to recon_state = PROVISIONAL.
        # Allow optional date filter.
        date_id = request.args.get("date")
        sql = "SELECT * FROM v_yesterday_provisional"
        params: List[Any] = []
        if date_id:
            sql += " WHERE date_id = ?"
            params.append(date_id)
        sql += " ORDER BY date_id DESC, equipment_code"

        return jsonify(_query_rows(db_path, sql, params))

    @app.get("/api/dashboard/exceptions")
    def exceptions_queue():
        return jsonify(_query_rows(db_path, "SELECT * FROM v_exceptions_queue"))

    @app.get("/api/dashboard/approval-flow")
    def approval_flow():
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        sql = "SELECT * FROM v_approval_flow_health WHERE 1=1"
        params: List[Any] = []
        if start_date:
            sql += " AND date_id >= ?"
            params.append(start_date)
        if end_date:
            sql += " AND date_id <= ?"
            params.append(end_date)
        sql += " ORDER BY date_id DESC"

        return jsonify(_query_rows(db_path, sql, params))

    @app.get("/api/dashboard/inspections")
    def inspections_compliance():
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        sql = "SELECT * FROM v_inspections_compliance WHERE 1=1"
        params: List[Any] = []
        if start_date:
            sql += " AND date_id >= ?"
            params.append(start_date)
        if end_date:
            sql += " AND date_id <= ?"
            params.append(end_date)
        sql += " ORDER BY date_id DESC"

        return jsonify(_query_rows(db_path, sql, params))

    @app.get("/api/dashboard/telematics")
    def telematics_health():
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        sql = "SELECT * FROM v_telematics_health WHERE 1=1"
        params: List[Any] = []
        if start_date:
            sql += " AND date_id >= ?"
            params.append(start_date)
        if end_date:
            sql += " AND date_id <= ?"
            params.append(end_date)
        sql += " ORDER BY date_id DESC"

        return jsonify(_query_rows(db_path, sql, params))

    @app.get("/api/dashboard/equipment")
    def equipment_drilldown():
        equipment_id = request.args.get("equipment_id")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        sql = "SELECT * FROM v_equipment_drilldown WHERE 1=1"
        params: List[Any] = []
        if equipment_id:
            sql += " AND equipment_id = ?"
            params.append(int(equipment_id))
        if start_date:
            sql += " AND date_id >= ?"
            params.append(start_date)
        if end_date:
            sql += " AND date_id <= ?"
            params.append(end_date)
        sql += " ORDER BY date_id DESC, equipment_code"

        return jsonify(_query_rows(db_path, sql, params))
