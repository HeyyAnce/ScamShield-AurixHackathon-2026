"""
Configuration settings and environment resolution for Scam Shield.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv(override=True)

# Project base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Curated dataset folder (committed to the repo so local and live behave the same)
DATASET_DIR = BASE_DIR / "data" / "dataset"

# Official domains path
OFFICIAL_DOMAINS_PATH = DATASET_DIR / "legit_domains.csv"

# Domains marked "unchecked" in legit_domains.csv are ignored unless this is True.
USE_UNCHECKED_DOMAINS = False

# Gemini AI Configuration
MODEL_NAME = "gemini-3.5-flash-lite"
REQUEST_TIMEOUT_MS = 20000  # 20 seconds
MAX_RETRIES = 0

# Reference Matching & Retrieval Configuration
DEFAULT_TOP_K_MATCHES = 3
MIN_SIMILARITY_THRESHOLD = 0.08

# Where to look for the curated dataset
DATASET_SEARCH_PATHS = [
    # 1. Optional override, for example when testing another copy of the data
    os.getenv("SCAM_SHIELD_DATASET_DIR"),
    # 2. The dataset stored inside the project (used locally and on the live site)
    str(DATASET_DIR),
]


def resolve_dataset_dir() -> Optional[Path]:
    """
    Resolves the dataset directory path from environment or standard locations.
    Returns Path if valid directory containing messages_english.csv is found, otherwise None.
    """
    for candidate in DATASET_SEARCH_PATHS:
        if not candidate:
            continue
        p = Path(candidate)
        if p.exists() and p.is_dir() and (p / "messages_english.csv").exists():
            return p
    return None
