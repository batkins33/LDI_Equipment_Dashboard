"""Flask API app for dashboard endpoints."""

import sqlite3
from pathlib import Path

from flask import Flask

from api.routes import register_routes


def _apply_dashboard_views(db_path: str) -> None:
    views_sql_path = Path(__file__).resolve().parents[1] / "views" / "dashboard_views.sql"
    if not views_sql_path.exists():
        return

    with sqlite3.connect(db_path) as conn:
        conn.executescript(views_sql_path.read_text(encoding="utf-8"))
        conn.commit()


def create_app(db_path: str) -> Flask:
    app = Flask(__name__)
    app.config["DB_PATH"] = db_path

    _apply_dashboard_views(db_path)
    register_routes(app)

    return app


if __name__ == "__main__":
    # Local/dev runner.
    # Usage:
    #   python 02-equipment-hours-validation/src/api/app.py <path-to-db>
    import sys

    if len(sys.argv) < 2:
        raise SystemExit("Usage: python src/api/app.py <db_path>")

    app = create_app(sys.argv[1])
    app.run(host="127.0.0.1", port=5000, debug=True)
