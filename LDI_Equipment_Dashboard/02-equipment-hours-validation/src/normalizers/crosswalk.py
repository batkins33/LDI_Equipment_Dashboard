"""Crosswalk mapping for external IDs to internal surrogate IDs."""

import sqlite3
from typing import Dict, List, Optional


class CrosswalkManager:
    """Manages mapping between external system IDs and internal surrogate IDs."""
    
    def __init__(self, db_path: str):
        """Initialize crosswalk manager.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Ensure crosswalk tables exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS map_equipment_external (
                    equipment_external_map_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    equipment_id INTEGER NOT NULL,
                    system TEXT NOT NULL,
                    external_equipment_id TEXT NOT NULL,
                    external_device_id TEXT,
                    is_primary BOOLEAN DEFAULT TRUE,
                    effective_start TIMESTAMP,
                    effective_end TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS map_job_external (
                    job_external_map_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id INTEGER NOT NULL,
                    system TEXT NOT NULL,
                    external_job_id TEXT NOT NULL,
                    is_primary BOOLEAN DEFAULT TRUE,
                    effective_start TIMESTAMP,
                    effective_end TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS map_employee_external (
                    employee_external_map_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    system TEXT NOT NULL,
                    external_employee_id TEXT NOT NULL,
                    is_primary BOOLEAN DEFAULT TRUE,
                    effective_start TIMESTAMP,
                    effective_end TIMESTAMP
                )
            """)
    
    def get_equipment_id(self, system: str, external_equipment_id: str, 
                        external_device_id: Optional[str] = None) -> Optional[int]:
        """Get internal equipment_id for external ID.
        
        Args:
            system: External system name (HEAVYJOB, SAFETY, EQUIP360, TELEMATICS)
            external_equipment_id: External equipment identifier
            external_device_id: Optional device ID (for telematics)
            
        Returns:
            Internal equipment_id or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT equipment_id FROM map_equipment_external
                WHERE system = ? AND external_equipment_id = ?
                AND (external_device_id IS NULL OR external_device_id = ?)
                AND effective_end IS NULL
                ORDER BY is_primary DESC, equipment_external_map_id ASC
                LIMIT 1
            """
            
            cursor.execute(query, (system, external_equipment_id, external_device_id))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def get_job_id(self, system: str, external_job_id: str) -> Optional[int]:
        """Get internal job_id for external ID.
        
        Args:
            system: External system name
            external_job_id: External job identifier
            
        Returns:
            Internal job_id or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT job_id FROM map_job_external
                WHERE system = ? AND external_job_id = ?
                AND effective_end IS NULL
                ORDER BY is_primary DESC, job_external_map_id ASC
                LIMIT 1
            """
            
            cursor.execute(query, (system, external_job_id))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def get_employee_id(self, system: str, external_employee_id: str) -> Optional[int]:
        """Get internal employee_id for external ID.
        
        Args:
            system: External system name
            external_employee_id: External employee identifier
            
        Returns:
            Internal employee_id or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT employee_id FROM map_employee_external
                WHERE system = ? AND external_employee_id = ?
                AND effective_end IS NULL
                ORDER BY is_primary DESC, employee_external_map_id ASC
                LIMIT 1
            """
            
            cursor.execute(query, (system, external_employee_id))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def create_equipment_mapping(self, equipment_id: int, system: str, 
                                 external_equipment_id: str, 
                                 external_device_id: Optional[str] = None,
                                 is_primary: bool = True) -> Optional[int]:
        """Create equipment crosswalk mapping.
        
        Args:
            equipment_id: Internal equipment_id
            system: External system name
            external_equipment_id: External equipment identifier
            external_device_id: Optional device ID
            is_primary: Whether this is the primary mapping
            
        Returns:
            Mapping ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO map_equipment_external 
                (equipment_id, system, external_equipment_id, external_device_id, is_primary)
                VALUES (?, ?, ?, ?, ?)
            """, (equipment_id, system, external_equipment_id, external_device_id, is_primary))
            
            return cursor.lastrowid
    
    def create_job_mapping(self, job_id: int, system: str, 
                          external_job_id: str, is_primary: bool = True) -> Optional[int]:
        """Create job crosswalk mapping.
        
        Args:
            job_id: Internal job_id
            system: External system name
            external_job_id: External job identifier
            is_primary: Whether this is the primary mapping
            
        Returns:
            Mapping ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO map_job_external 
                (job_id, system, external_job_id, is_primary)
                VALUES (?, ?, ?, ?)
            """, (job_id, system, external_job_id, is_primary))
            
            return cursor.lastrowid
    
    def create_employee_mapping(self, employee_id: int, system: str, 
                               external_employee_id: str, is_primary: bool = True) -> Optional[int]:
        """Create employee crosswalk mapping.
        
        Args:
            employee_id: Internal employee_id
            system: External system name
            external_employee_id: External employee identifier
            is_primary: Whether this is the primary mapping
            
        Returns:
            Mapping ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO map_employee_external 
                (employee_id, system, external_employee_id, is_primary)
                VALUES (?, ?, ?, ?)
            """, (employee_id, system, external_employee_id, is_primary))
            
            return cursor.lastrowid
    
    def get_unmapped_equipment(self, system: str) -> List[Dict[str, str]]:
        """Get equipment IDs that exist in external system but have no mapping.
        
        Args:
            system: External system name
            
        Returns:
            List of external equipment info
        """
        # This would query the external system or bronze layer
        # For now, return empty list - implementers can override
        return []
    
    def get_unmapped_jobs(self, system: str) -> List[Dict[str, str]]:
        """Get job IDs that exist in external system but have no mapping.
        
        Args:
            system: External system name
            
        Returns:
            List of external job info
        """
        # This would query the external system or bronze layer
        # For now, return empty list - implementers can override
        return []
    
    def get_unmapped_employees(self, system: str) -> List[Dict[str, str]]:
        """Get employee IDs that exist in external system but have no mapping.
        
        Args:
            system: External system name
            
        Returns:
            List of external employee info
        """
        # This would query the external system or bronze layer
        # For now, return empty list - implementers can override
        return []
