"""Telematics data normalizer - converts mock data to canonical schema."""

import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional
from connectors.mock_telematics import MockTelematicsConnector
from normalizers.crosswalk import CrosswalkManager


class TelematicsNormalizer:
    """Normalizes telematics engine hour data to canonical schema."""
    
    def __init__(self, db_path: str, use_mock: bool = True):
        """Initialize normalizer.
        
        Args:
            db_path: Path to SQLite database
            use_mock: Whether to use mock connector
        """
        self.db_path = db_path
        self.connector = MockTelematicsConnector(use_mock=use_mock)
        self.crosswalk = CrosswalkManager(db_path)
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Ensure silver layer tables exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS f_telematics_equipment_day (
                    equipment_id INTEGER NOT NULL REFERENCES dim_equipment(equipment_id),
                    date_id DATE NOT NULL REFERENCES dim_date(date_id),
                    engine_hours_start NUMERIC(10,2),
                    engine_hours_end NUMERIC(10,2),
                    engine_hours_daily NUMERIC(10,2),
                    gps_active BOOLEAN,
                    device_id TEXT,
                    source_last_modified_at TIMESTAMP,
                    snapshot_ts TIMESTAMP NOT NULL
                )
            """)
    
    def normalize(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, int]:
        """Normalize telematics data to silver layer.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Statistics: {records_processed, records_inserted, errors}
        """
        stats = {"records_processed": 0, "records_inserted": 0, "errors": 0}
        
        try:
            # Load data from connector
            readings = self.connector.get_engine_hours(start_date, end_date)
            devices = self.connector.get_devices()
            
            # Create equipment mappings if they don't exist
            self._ensure_equipment(devices)
            
            # Process readings
            for reading in readings:
                try:
                    self._process_reading(reading)
                    stats["records_inserted"] += 1
                except Exception as e:
                    print(f"Error processing reading for {reading.get('equipment_id', 'unknown')}: {e}")
                    stats["errors"] += 1
                
                stats["records_processed"] += 1
            
            # Commit changes
            with sqlite3.connect(self.db_path) as conn:
                conn.commit()
            
        except Exception as e:
            print(f"Error normalizing telematics data: {e}")
            stats["errors"] += 1
        
        return stats
    
    def _ensure_equipment(self, devices: List[Dict]):
        """Ensure equipment dimension has required data."""
        with sqlite3.connect(self.db_path) as conn:
            for device in devices:
                equipment_id = self.crosswalk.get_equipment_id("TELEMATICS", device["equipment_id"], device["device_id"])
                if equipment_id is None:
                    # Create new equipment
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO dim_equipment (equipment_code, equipment_name, equipment_type)
                        VALUES (?, ?, ?)
                    """, (device["equipment_id"], device["equipment_id"], "TELEMATICS"))
                    equipment_id = cursor.lastrowid
                    if equipment_id is None:
                        raise RuntimeError("Failed to create equipment")

                    # Create crosswalk mapping
                    self.crosswalk.create_equipment_mapping(
                        int(equipment_id), "TELEMATICS", device["equipment_id"], device["device_id"]
                    )
    
    def _process_reading(self, reading: Dict[str, Any]):
        """Process a single telematics reading."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get internal equipment ID
            equipment_id = self.crosswalk.get_equipment_id("TELEMATICS", reading["equipment_id"], reading["device_id"])
            if equipment_id is None:
                raise ValueError(f"Missing equipment mapping for {reading['equipment_id']} device {reading['device_id']}")
            
            # Insert telematics data
            cursor.execute("""
                INSERT OR REPLACE INTO f_telematics_equipment_day (
                    equipment_id, date_id, engine_hours_start, engine_hours_end,
                    engine_hours_daily, gps_active, device_id, snapshot_ts
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                equipment_id,
                reading["date"],
                reading["engine_hours_start"],
                reading["engine_hours_end"],
                reading["engine_hours_daily"],
                reading["gps_active"],
                reading["device_id"],
                datetime.now().isoformat()
            ))
    
    def get_normalized_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """Get normalized data for verification.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of telematics records
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM f_telematics_equipment_day WHERE 1=1"
            params = []
            if start_date:
                query += " AND date_id >= ?"
                params.append(start_date)
            if end_date:
                query += " AND date_id <= ?"
                params.append(end_date)
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
