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
SUPPORTED_SOURCES: list[str] = ["GitHub Repository"]  # Active sources in v1.0.0

V2_SOURCES: list[str] = ["Local Folder", "ZIP Upload"]  # Planned for next release (v2.0.0)

# ---------------------------------------------------------------------------
# ZIP Uploads
# ---------------------------------------------------------------------------
MAX_ZIP_SIZE_MB: int = 50  # Maximum upload limit for ZIP archives in MB


