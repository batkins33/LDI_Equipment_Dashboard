import json
from pathlib import Path
from typing import Any, Dict, List

BASE = Path(__file__).resolve().parent / "fixtures"

def load_fixture(name: str) -> Any:
    p = BASE / name
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)

def list_fixture(name: str) -> List[Dict]:
    data = load_fixture(name)
    assert isinstance(data, list)
    return data
