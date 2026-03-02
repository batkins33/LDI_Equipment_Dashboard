"""Equipment360 data normalizer - converts mock data to canonical schema."""

import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional
from connectors.mock_equipment360 import MockEquipment360Connector
from normalizers.crosswalk import CrosswalkManager


class Equipment360Normalizer:
    """Normalizes Equipment360 meter reading data to canonical schema."""
    
    def __init__(self, db_path: str, use_mock: bool = True):
        """Initialize normalizer.
        
        Args:
            db_path: Path to SQLite database
            use_mock: Whether to use mock connector
        """
        self.db_path = db_path
        self.connector = MockEquipment360Connector(use_mock=use_mock)
        self.crosswalk = CrosswalkManager(db_path)
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Ensure silver layer tables exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS f_equipment360_meter_reading (
                    reading_id TEXT PRIMARY KEY,
                    equipment_id INTEGER NOT NULL REFERENCES dim_equipment(equipment_id),
                    reading_date DATE NOT NULL REFERENCES dim_date(date_id),
                    meter_reading NUMERIC(10,2),
                    reading_type TEXT,
                    source_last_modified_at TIMESTAMP,
                    snapshot_ts TIMESTAMP NOT NULL
                )
            """)
    
    def normalize(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, int]:
        """Normalize Equipment360 data to silver layer.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Statistics: {records_processed, records_inserted, errors}
        """
        stats = {"records_processed": 0, "records_inserted": 0, "errors": 0}
        
        try:
            # Load data from connector
            readings = self.connector.get_meter_readings(start_date, end_date)
            
            # Process readings
            for reading in readings:
                try:
                    self._process_reading(reading)
                    stats["records_inserted"] += 1
                except Exception as e:
                    print(f"Error processing reading {reading.get('reading_id', 'unknown')}: {e}")
                    stats["errors"] += 1
                
                stats["records_processed"] += 1
            
            # Commit changes
            with sqlite3.connect(self.db_path) as conn:
                conn.commit()
            
        except Exception as e:
            print(f"Error normalizing Equipment360 data: {e}")
            stats["errors"] += 1
        
        return stats
    
    def _process_reading(self, reading: Dict[str, Any]):
        """Process a single meter reading."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get internal equipment ID
            equipment_id = self.crosswalk.get_equipment_id("EQUIP360", reading["equipment_id"])
            if equipment_id is None:
                raise ValueError(f"Missing equipment mapping for {reading['equipment_id']}")
            
            # Insert meter reading
            cursor.execute("""
                INSERT OR REPLACE INTO f_equipment360_meter_reading (
                    reading_id, equipment_id, reading_date, meter_reading,
                    reading_type, snapshot_ts
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                reading["reading_id"],
                equipment_id,
                reading["reading_date"],
                reading["meter_reading"],
                reading["reading_type"],
                datetime.now().isoformat()
            ))
    
    def get_normalized_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """Get normalized data for verification.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of meter reading records
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM f_equipment360_meter_reading WHERE 1=1"
            params = []
            if start_date:
                query += " AND reading_date >= ?"
                params.append(start_date)
            if end_date:
                query += " AND reading_date <= ?"
                params.append(end_date)
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
