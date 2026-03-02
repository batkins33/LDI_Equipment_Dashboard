"""Mock Safety/Inspections connector - loads fixture data instead of calling API."""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional


class MockSafetyConnector:
    """Mock connector for Safety/inspections system."""
    
    def __init__(self, use_mock: bool = True):
        """Initialize connector.
        
        Args:
            use_mock: If True, load from fixtures; if False, would call real API
        """
        self.use_mock = use_mock
        self.fixture_path = Path(__file__).parent.parent.parent / "data" / "fixtures" / "mock_safety.json"
        self._data: Optional[Dict[str, Any]] = None
    
    def _load_fixture(self) -> Dict[str, Any]:
        """Load fixture data from JSON file."""
        if self._data is None:
            with open(self.fixture_path, 'r') as f:
                self._data = json.load(f)
        return self._data
    
    def get_inspections(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get daily inspections for date range.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of inspection records
        """
        if not self.use_mock:
            raise NotImplementedError("Real API connector not implemented in P0.5")
        
        data = self._load_fixture()
        inspections = data.get("inspections", [])
        
        if start_date:
            inspections = [i for i in inspections if i["date"] >= start_date]
        if end_date:
            inspections = [i for i in inspections if i["date"] <= end_date]
        
        return inspections
    
    def get_inspectors(self) -> List[Dict[str, Any]]:
        """Get all inspectors."""
        if not self.use_mock:
            raise NotImplementedError("Real API connector not implemented in P0.5")
        
        return [
            {"inspector_id": f"INS-{i:03d}", "inspector_name": f"Inspector {i}"}
            for i in range(1, 6)
        ]
