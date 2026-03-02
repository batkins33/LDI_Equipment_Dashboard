"""Safety/Inspections data normalizer - converts mock data to canonical schema."""

import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional
from connectors.mock_safety import MockSafetyConnector
from normalizers.crosswalk import CrosswalkManager


class SafetyNormalizer:
    """Normalizes safety/inspections data to canonical schema."""
    
    def __init__(self, db_path: str, use_mock: bool = True):
        """Initialize normalizer.
        
        Args:
            db_path: Path to SQLite database
            use_mock: Whether to use mock connector
        """
        self.db_path = db_path
        self.connector = MockSafetyConnector(use_mock=use_mock)
        self.crosswalk = CrosswalkManager(db_path)
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Ensure silver layer tables exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS f_inspection_equipment_day (
                    inspection_id TEXT PRIMARY KEY,
                    equipment_id INTEGER NOT NULL REFERENCES dim_equipment(equipment_id),
                    date_id DATE NOT NULL REFERENCES dim_date(date_id),
                    inspector_employee_id INTEGER REFERENCES dim_employee(employee_id),
                    meter_start NUMERIC(10,2),
                    meter_end NUMERIC(10,2),
                    meter_delta NUMERIC(10,2),
                    photo_count INTEGER,
                    issues_count INTEGER,
                    inspection_status TEXT,
                    source_last_modified_at TIMESTAMP,
                    snapshot_ts TIMESTAMP NOT NULL
                )
            """)
    
    def normalize(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, int]:
        """Normalize safety data to silver layer.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Statistics: {records_processed, records_inserted, errors}
        """
        stats = {"records_processed": 0, "records_inserted": 0, "errors": 0}
        
        try:
            # Load data from connector
            inspections = self.connector.get_inspections(start_date, end_date)
            inspectors = self.connector.get_inspectors()
            
            # Create employee mappings for inspectors
            self._ensure_employees(inspectors)
            
            # Process inspections
            for inspection in inspections:
                try:
                    self._process_inspection(inspection)
                    stats["records_inserted"] += 1
                except Exception as e:
                    print(f"Error processing inspection {inspection.get('inspection_id', 'unknown')}: {e}")
                    stats["errors"] += 1
                
                stats["records_processed"] += 1
            
            # Commit changes
            with sqlite3.connect(self.db_path) as conn:
                conn.commit()
            
        except Exception as e:
            print(f"Error normalizing safety data: {e}")
            stats["errors"] += 1
        
        return stats
    
    def _ensure_employees(self, inspectors: List[Dict]):
        """Ensure employee dimension has required data."""
        with sqlite3.connect(self.db_path) as conn:
            for inspector in inspectors:
                employee_id = self.crosswalk.get_employee_id("SAFETY", inspector["inspector_id"])
                if employee_id is None:
                    # Create new employee
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO dim_employee (employee_code, employee_name)
                        VALUES (?, ?)
                    """, (inspector["inspector_id"], inspector["inspector_name"]))
                    employee_id = cursor.lastrowid
                    if employee_id is None:
                        raise RuntimeError("Failed to create employee")

                    # Create crosswalk mapping
                    self.crosswalk.create_employee_mapping(int(employee_id), "SAFETY", inspector["inspector_id"])
    
    def _process_inspection(self, inspection: Dict[str, Any]):
        """Process a single inspection record."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get internal IDs
            equipment_id = self.crosswalk.get_equipment_id("SAFETY", inspection["equipment_id"])
            inspector_id = self.crosswalk.get_employee_id("SAFETY", inspection["inspector_id"])
            
            if equipment_id is None:
                raise ValueError(f"Missing equipment mapping for {inspection['equipment_id']}")
            
            # Insert inspection data
            cursor.execute("""
                INSERT OR REPLACE INTO f_inspection_equipment_day (
                    inspection_id, equipment_id, date_id, inspector_employee_id,
                    meter_start, meter_end, meter_delta, photo_count, issues_count,
                    inspection_status, snapshot_ts
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                inspection["inspection_id"],
                equipment_id,
                inspection["date"],
                inspector_id,
                inspection["meter_start"],
                inspection["meter_end"],
                inspection["meter_delta"],
                inspection["photo_count"],
                inspection["issues_count"],
                inspection["status"],
                datetime.now().isoformat()
            ))
    
    def get_normalized_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """Get normalized data for verification.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of inspection records
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM f_inspection_equipment_day WHERE 1=1"
            params = []
            if start_date:
                query += " AND date_id >= ?"
                params.append(start_date)
            if end_date:
                query += " AND date_id <= ?"
                params.append(end_date)
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
