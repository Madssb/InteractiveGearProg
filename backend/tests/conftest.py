import importlib
import os
import sys
from pathlib import Path

import pytest


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Importing backend.db requires DATABASE_URL to exist, but tests do not need a live DB.
os.environ.setdefault(
    "DATABASE_URL", "postgresql://user:password@localhost:5432/testdb?sslmode=disable"
)

backend_main = importlib.import_module("main")


@pytest.fixture
def app_module():
    backend_main.RATE_LIMIT_SEC.clear()
    backend_main.RATE_LIMIT_MIN.clear()
    backend_main.CACHE.clear()
    return backend_main
