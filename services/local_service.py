"""
Local folder service — validation and metadata extraction for local directories.
"""

import os
from collections import Counter
from pathlib import Path
from typing import Any

from utils.logger import get_logger

logger = get_logger(__name__)

# Common code file extensions for language detection.
_LANGUAGE_MAP: dict[str, str] = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".jsx": "React JSX",
    ".tsx": "React TSX",
    ".java": "Java",
    ".go": "Go",
    ".rs": "Rust",
    ".c": "C",
    ".cpp": "C++",
    ".h": "C/C++ Header",
    ".cs": "C#",
    ".rb": "Ruby",
    ".php": "PHP",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".dart": "Dart",
    ".r": "R",
    ".scala": "Scala",
    ".html": "HTML",
    ".css": "CSS",
    ".md": "Markdown",
    ".yml": "YAML",
    ".yaml": "YAML",
    ".json": "JSON",
    ".toml": "TOML",
    ".sh": "Shell",
}

_EXCLUDED_DIRS: frozenset[str] = frozenset({
    ".git", "__pycache__", ".venv", "venv", "node_modules",
    ".idea", ".vscode", ".mypy_cache", ".pytest_cache",
    "dist", "build", ".next",
})


def validate_local_folder(folder_path: str) -> Path:
    """Validate that the given path is an existing directory.

    Args:
        folder_path: Path to the local folder.

    Returns:
        Resolved :class:`Path` object.

    Raises:
        ValueError: If the path doesn't exist or isn't a directory.
    """
    path = Path(folder_path).resolve()

    if not path.exists():
        raise ValueError(f"Path does not exist: {folder_path}")

    if not path.is_dir():
        raise ValueError(f"Path is not a directory: {folder_path}")

    logger.info("Validated local folder: %s", path)
    return path


def get_folder_metadata(folder_path: str) -> dict[str, Any]:
    """Extract metadata from a local folder for the dashboard.

    Args:
        folder_path: Path to the local folder.

    Returns:
        Dict with metadata fields matching the GitHub details format.
    """
    path = Path(folder_path).resolve()
    file_count = 0
    total_size = 0
    extensions: Counter[str] = Counter()

    for root, dirs, files in os.walk(path):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in _EXCLUDED_DIRS]

        for f in files:
            fp = Path(root) / f
            file_count += 1
            try:
                total_size += fp.stat().st_size
            except OSError:
                pass
            ext = fp.suffix.lower()
            if ext in _LANGUAGE_MAP:
                extensions[ext] += 1

    # Detect primary language
    primary_lang = "Unknown"
    if extensions:
        top_ext = extensions.most_common(1)[0][0]
        primary_lang = _LANGUAGE_MAP.get(top_ext, "Unknown")

    size_mb = total_size / (1024 * 1024)

    details: dict[str, Any] = {
        "name": path.name,
        "owner": "Local",
        "description": f"Local folder with {file_count} files ({size_mb:.1f} MB)",
        "language": primary_lang,
        "stars": "N/A",
        "forks": "N/A",
        "open_issues": "N/A",
        "license": "N/A",
        "updated": "N/A",
        "html_url": str(path),
    }

    logger.info(
        "Folder metadata: %s — %d files, %.1f MB, primary=%s",
        path.name, file_count, size_mb, primary_lang,
    )

    return details
