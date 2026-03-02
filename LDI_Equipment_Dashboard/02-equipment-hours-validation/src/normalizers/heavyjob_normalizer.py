"""HeavyJob data normalizer - converts mock data to canonical schema."""

import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional
from connectors.mock_heavyjob import MockHeavyJobConnector
from normalizers.crosswalk import CrosswalkManager


class HeavyJobNormalizer:
    """Normalizes HeavyJob timecard data to canonical schema."""
    
    def __init__(self, db_path: str, use_mock: bool = True):
        """Initialize normalizer.
        
        Args:
            db_path: Path to SQLite database
            use_mock: Whether to use mock connector
        """
        self.db_path = db_path
        self.connector = MockHeavyJobConnector(use_mock=use_mock)
        self.crosswalk = CrosswalkManager(db_path)
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Ensure silver layer tables exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS f_timecard_header (
                    timecard_id TEXT PRIMARY KEY,
                    business_unit_id INTEGER REFERENCES dim_business_unit(business_unit_id),
                    job_id INTEGER REFERENCES dim_job(job_id),
                    foreman_employee_id INTEGER REFERENCES dim_employee(employee_id),
                    work_date DATE NOT NULL REFERENCES dim_date(date_id),
                    status TEXT,
                    submitted_at TIMESTAMP,
                    approved_at TIMESTAMP,
                    source_last_modified_at TIMESTAMP,
                    snapshot_ts TIMESTAMP NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS f_timecard_equipment_hours (
                    timecard_id TEXT NOT NULL REFERENCES f_timecard_header(timecard_id),
                    equipment_id INTEGER NOT NULL REFERENCES dim_equipment(equipment_id),
                    cost_code_id INTEGER REFERENCES dim_cost_code(cost_code_id),
                    hours NUMERIC(10,2) NOT NULL,
                    is_provisional BOOLEAN DEFAULT TRUE,
                    snapshot_ts TIMESTAMP NOT NULL
                )
            """)
    
    def normalize(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, int]:
        """Normalize HeavyJob data to silver layer.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Statistics: {records_processed, records_inserted, errors}
        """
        stats = {"records_processed": 0, "records_inserted": 0, "errors": 0}
        
        try:
            # Load data from connector
            timecards = self.connector.get_timecards(start_date, end_date)
            jobs = self.connector.get_jobs()
            equipment = self.connector.get_equipment()
            foremen = self.connector.get_foremen()
            
            # Create dimension mappings if they don't exist
            self._ensure_dimensions(jobs, equipment, foremen)
            
            # Process timecards
            for timecard in timecards:
                try:
                    self._process_timecard(timecard)
                    stats["records_inserted"] += 1
                except Exception as e:
                    print(f"Error processing timecard {timecard.get('timecard_id', 'unknown')}: {e}")
                    stats["errors"] += 1
                
                stats["records_processed"] += 1
            
            # Commit changes
            with sqlite3.connect(self.db_path) as conn:
                conn.commit()
            
        except Exception as e:
            print(f"Error normalizing HeavyJob data: {e}")
            stats["errors"] += 1
        
        return stats
    
    def _ensure_dimensions(self, jobs: List[Dict], equipment: List[Dict], foremen: List[Dict]):
        """Ensure dimension tables have required data."""
        with sqlite3.connect(self.db_path) as conn:
            # Insert jobs
            for job in jobs:
                job_id = self.crosswalk.get_job_id("HEAVYJOB", job["job_id"])
                if job_id is None:
                    # Create new job
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO dim_job (business_unit_id, job_code, job_name)
                        VALUES (?, ?, ?)
                    """, (1, job["job_id"], job["job_name"]))
                    job_id = cursor.lastrowid
                    if job_id is None:
                        raise RuntimeError("Failed to create job")
                    
                    # Create crosswalk mapping
                    self.crosswalk.create_job_mapping(job_id, "HEAVYJOB", job["job_id"])
            
            # Insert equipment
            for equip in equipment:
                equipment_id = self.crosswalk.get_equipment_id("HEAVYJOB", equip["equipment_id"])
                if equipment_id is None:
                    # Create new equipment
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO dim_equipment (equipment_code, equipment_name, equipment_type)
                        VALUES (?, ?, ?)
                    """, (equip["equipment_id"], equip["equipment_id"], equip["type"]))
                    equipment_id = cursor.lastrowid
                    if equipment_id is None:
                        raise RuntimeError("Failed to create equipment")
                    
                    # Create crosswalk mapping
                    self.crosswalk.create_equipment_mapping(equipment_id, "HEAVYJOB", equip["equipment_id"])
            
            # Insert foremen as employees
            for foreman in foremen:
                employee_id = self.crosswalk.get_employee_id("HEAVYJOB", foreman["foreman_id"])
                if employee_id is None:
                    # Create new employee
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO dim_employee (employee_code, employee_name)
                        VALUES (?, ?)
                    """, (foreman["foreman_id"], foreman["foreman_name"]))
                    employee_id = cursor.lastrowid
                    if employee_id is None:
                        raise RuntimeError("Failed to create employee")
                    
                    # Create crosswalk mapping
                    self.crosswalk.create_employee_mapping(employee_id, "HEAVYJOB", foreman["foreman_id"])
    
    def _process_timecard(self, timecard: Dict[str, Any]):
        """Process a single timecard record."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get internal IDs
            job_id = self.crosswalk.get_job_id("HEAVYJOB", timecard["job_id"])
            equipment_id = self.crosswalk.get_equipment_id("HEAVYJOB", timecard["equipment_id"])
            foreman_id = self.crosswalk.get_employee_id("HEAVYJOB", timecard["foreman_id"])
            
            if job_id is None or equipment_id is None or foreman_id is None:
                raise ValueError(f"Missing crosswalk mappings for timecard {timecard['timecard_id']}")
            
            # Insert timecard header
            cursor.execute("""
                INSERT OR REPLACE INTO f_timecard_header (
                    timecard_id, business_unit_id, job_id, foreman_employee_id,
                    work_date, status, submitted_at, approved_at, snapshot_ts
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timecard["timecard_id"],
                1,  # business_unit_id - hardcoded for demo
                job_id,
                foreman_id,
                timecard["work_date"],
                timecard["status"],
                timecard["submitted_at"],
                timecard["approved_at"],
                datetime.now().isoformat()
            ))
            
            # Insert equipment hours
            cursor.execute("""
                INSERT OR REPLACE INTO f_timecard_equipment_hours (
                    timecard_id, equipment_id, hours, is_provisional, snapshot_ts
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                timecard["timecard_id"],
                equipment_id,
                timecard["hours"],
                True,  # provisional
                datetime.now().isoformat()
            ))
    
    def get_normalized_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, List[Dict]]:
        """Get normalized data for verification.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Dictionary with headers and hours data
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get headers
            query = "SELECT * FROM f_timecard_header WHERE 1=1"
            params = []
            if start_date:
                query += " AND work_date >= ?"
                params.append(start_date)
            if end_date:
                query += " AND work_date <= ?"
                params.append(end_date)
            
            cursor.execute(query, params)
            headers = [dict(row) for row in cursor.fetchall()]
            
            # Get hours
            query = "SELECT * FROM f_timecard_equipment_hours WHERE 1=1"
            params = []
            if start_date:
                query += " AND timecard_id IN (SELECT timecard_id FROM f_timecard_header WHERE work_date >= ?)"
                params.append(start_date)
            if end_date:
                query += " AND timecard_id IN (SELECT timecard_id FROM f_timecard_header WHERE work_date <= ?)"
                params.append(end_date)
            
            cursor.execute(query, params)
            hours = [dict(row) for row in cursor.fetchall()]
            
            return {
                "headers": headers,
                "hours": hours
            }
