"""
Central configuration for the AI Codebase Assistant.

All hardcoded values, paths, and constants are defined here.
Environment variables override defaults where applicable.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load .env file (if present)
# ---------------------------------------------------------------------------
load_dotenv(override=True)

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
APP_TITLE: str = "AI Codebase Assistant"
APP_ICON: str = "🤖"
APP_VERSION: str = "1.0.0"
APP_LAYOUT: str = "wide"

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT: Path = Path(__file__).resolve().parent

POCKETFLOW_PATH: Path = Path(
    os.getenv(
        "POCKETFLOW_PATH",
        str(PROJECT_ROOT.parent / "PocketFlow-Tutorial-Codebase-Knowledge-main"),
    )
)

POCKETFLOW_OUTPUT: Path = POCKETFLOW_PATH / "output"

LOG_DIR: Path = PROJECT_ROOT / "logs"

OUTPUT_DIR: Path = PROJECT_ROOT / "output"

# ---------------------------------------------------------------------------
# GitHub API
# ---------------------------------------------------------------------------
GITHUB_API_BASE_URL: str = "https://api.github.com"

# ---------------------------------------------------------------------------
# Timeouts (seconds)
# ---------------------------------------------------------------------------
DEFAULT_TIMEOUT: int = int(os.getenv("DEFAULT_TIMEOUT", "30"))
POCKETFLOW_TIMEOUT: int = int(os.getenv("POCKETFLOW_TIMEOUT", "300"))

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_FORMAT: str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
LOG_MAX_BYTES: int = 5 * 1024 * 1024  # 5 MB
LOG_BACKUP_COUNT: int = 3

# ---------------------------------------------------------------------------
# Supported Sources (Version 1)
# ---------------------------------------------------------------------------
SUPPORTED_SOURCES: list[str] = ["GitHub Repository"]

V2_SOURCES: list[str] = ["Local Folder", "ZIP Upload"]

# ---------------------------------------------------------------------------
# ZIP Uploads
# ---------------------------------------------------------------------------
MAX_ZIP_SIZE_MB: int = 50

