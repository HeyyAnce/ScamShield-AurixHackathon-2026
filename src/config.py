"""
Configuration settings and environment resolution for Scam Shield.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Project base directory; never discover a parent project's .env.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=False)

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

def resolve_dataset_dir() -> Optional[Path]:
    """Use a complete override folder, otherwise the bundled message files.

    Relative overrides are project-relative. CSV contents are validated by
    DatasetLoader; an existing but invalid dataset is reported as unavailable.
    An optional official-domain file is used when present; otherwise rules
    retain the bundled official-domain list.
    """
    override = os.getenv("SCAM_SHIELD_DATASET_DIR", "").strip()
    candidates = [Path(override).expanduser()] if override else []
    candidates.append(DATASET_DIR)
    for candidate in candidates:
        folder = candidate if candidate.is_absolute() else BASE_DIR / candidate
        if folder.is_dir() and all(
            (folder / name).is_file()
            for name in ("messages_english.csv", "messages_hinglish.csv")
        ):
            return folder.resolve()
    return None
