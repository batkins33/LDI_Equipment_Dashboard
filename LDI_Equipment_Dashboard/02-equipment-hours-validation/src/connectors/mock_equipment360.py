"""Mock Equipment360 connector - loads fixture data instead of calling API."""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional


class MockEquipment360Connector:
    """Mock connector for Equipment360 meter readings."""
    
    def __init__(self, use_mock: bool = True):
        """Initialize connector.
        
        Args:
            use_mock: If True, load from fixtures; if False, would call real API
        """
        self.use_mock = use_mock
        self.fixture_path = Path(__file__).parent.parent.parent / "data" / "fixtures" / "mock_equipment360.json"
        self._data: Optional[Dict[str, Any]] = None
    
    def _load_fixture(self) -> Dict[str, Any]:
        """Load fixture data from JSON file."""
        if self._data is None:
            with open(self.fixture_path, 'r') as f:
                self._data = json.load(f)
        return self._data
    
    def get_meter_readings(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get meter readings for date range.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of meter reading records
        """
        if not self.use_mock:
            raise NotImplementedError("Real API connector not implemented in P0.5")
        
        data = self._load_fixture()
        readings = data.get("readings", [])
        
        if start_date:
            readings = [r for r in readings if r["reading_date"] >= start_date]
        if end_date:
            readings = [r for r in readings if r["reading_date"] <= end_date]
        
        return readings
