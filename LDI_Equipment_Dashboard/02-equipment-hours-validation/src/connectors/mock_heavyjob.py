"""Mock HeavyJob connector - loads fixture data instead of calling API."""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional


class MockHeavyJobConnector:
    """Mock connector for HeavyJob timecard system."""
    
    def __init__(self, use_mock: bool = True):
        """Initialize connector.
        
        Args:
            use_mock: If True, load from fixtures; if False, would call real API
        """
        self.use_mock = use_mock
        self.fixture_path = Path(__file__).parent.parent.parent / "data" / "fixtures" / "mock_heavyjob.json"
        self._data: Optional[Dict[str, Any]] = None
    
    def _load_fixture(self) -> Dict[str, Any]:
        """Load fixture data from JSON file."""
        if self._data is None:
            with open(self.fixture_path, 'r') as f:
                self._data = json.load(f)
        return self._data
    
    def get_timecards(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get timecards for date range.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of timecard records
        """
        if not self.use_mock:
            raise NotImplementedError("Real API connector not implemented in P0.5")
        
        data = self._load_fixture()
        timecards = data.get("timecards", [])
        
        if start_date:
            timecards = [tc for tc in timecards if tc["work_date"] >= start_date]
        if end_date:
            timecards = [tc for tc in timecards if tc["work_date"] <= end_date]
        
        return timecards
    
    def get_jobs(self) -> List[Dict[str, Any]]:
        """Get all jobs."""
        if not self.use_mock:
            raise NotImplementedError("Real API connector not implemented in P0.5")
        
        data = self._load_fixture()
        return data.get("jobs", [])
    
    def get_equipment(self) -> List[Dict[str, Any]]:
        """Get all equipment."""
        if not self.use_mock:
            raise NotImplementedError("Real API connector not implemented in P0.5")
        
        data = self._load_fixture()
        return data.get("equipment", [])
    
    def get_foremen(self) -> List[Dict[str, Any]]:
        """Get all foremen."""
        if not self.use_mock:
            raise NotImplementedError("Real API connector not implemented in P0.5")
        
        data = self._load_fixture()
        return data.get("foremen", [])
