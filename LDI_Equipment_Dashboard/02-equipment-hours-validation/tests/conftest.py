from pathlib import Path
import sys


def pytest_configure():
    src_path = Path(__file__).resolve().parents[1] / "src"
    sys.path.insert(0, str(src_path))
