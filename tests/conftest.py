"""Run all tests offline and isolate developer credentials."""
import sys
from pathlib import Path
from unittest.mock import patch
import pytest
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
# Patch dotenv before project imports during collection; never load a real key.
_dotenv_patch = patch("dotenv.load_dotenv", return_value=False)
_dotenv_patch.start()
import os
os.environ["GEMINI_API_KEY"] = ""
os.environ["SCAM_SHIELD_DATASET_DIR"] = ""

@pytest.fixture(autouse=True)
def offline_environment(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "")
    monkeypatch.setenv("SCAM_SHIELD_DATASET_DIR", "")

def pytest_unconfigure(config):
    _dotenv_patch.stop()
