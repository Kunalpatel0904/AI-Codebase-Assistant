"""
Scanner service — Recursively scans cloned repositories for relevant code files.
"""

import time
import os
from dataclasses import dataclass
from pathlib import Path

from utils.exceptions import RepositoryScanError
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class ScannedFile:
    """Dataclass holding metadata of a scanned file.

    Frozen to ensure immutability of the metadata.
    """

    file_path: Path
    relative_path: str
    extension: str
    file_size: int
    line_count: int


# List of directories to ignore during scan
_IGNORED_DIRS: frozenset[str] = frozenset({
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "dist",
    "build",
    "__pycache__",
    ".idea",
    ".vscode",
    "coverage",
    "logs",
})

# List of extensions to process
_SUPPORTED_EXTENSIONS: frozenset[str] = frozenset({
    ".py",
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".js",
    ".ts",
})


def _count_lines(file_path: Path) -> int:
    """Count the total number of lines in a file safely.

    Attempts to read as UTF-8, ignores errors for binary or invalid encodings.

    Args:
        file_path: Path to the target file.

    Returns:
        int: Number of lines in the file.
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for _ in f)
    except Exception as exc:
        logger.debug("Failed to count lines for %s: %s", file_path, exc)
        return 0


def scan_repository(repo_path: Path) -> list[ScannedFile]:
    """Recursively scan a repository path and return a list of ScannedFile objects.

    Filters files by supported extensions and ignores excluded directories.

    Args:
        repo_path: Absolute Path to the repository root directory.

    Returns:
        list[ScannedFile]: List of metadata objects for each scanned file.

    Raises:
        RepositoryScanError: If scanning fails.
    """
    start_time = time.perf_counter()
    logger.info("Scanning repository start: path=%s", repo_path)

    if not repo_path.exists() or not repo_path.is_dir():
        logger.error("Scanning repository failure: invalid path %s", repo_path)
        raise RepositoryScanError(f"Directory path does not exist or is not a directory: {repo_path}")

    scanned_files: list[ScannedFile] = []

    try:
        for root, dirs, files in os.walk(repo_path):
            # Prune ignored directories in-place to avoid descending into them
            dirs[:] = [d for d in dirs if d not in _IGNORED_DIRS]

            for file_name in files:
                file_path = Path(root) / file_name
                ext = file_path.suffix.lower()

                if ext in _SUPPORTED_EXTENSIONS:
                    try:
                        stat_result = file_path.stat()
                        size = stat_result.st_size
                        rel_path = str(file_path.relative_to(repo_path))
                        
                        # Replace backslashes with forward slashes for unified JSON tree & cross-platform compatibility
                        rel_path = rel_path.replace("\\", "/")

                        line_count = _count_lines(file_path)

                        scanned_files.append(
                            ScannedFile(
                                file_path=file_path,
                                relative_path=rel_path,
                                extension=ext,
                                file_size=size,
                                line_count=line_count,
                            )
                        )
                    except OSError as exc:
                        logger.warning("Skipping file %s due to OSError: %s", file_path, exc)

        duration = time.perf_counter() - start_time
        logger.info(
            "Scanning repository success: files_found=%d, duration=%.2fs",
            len(scanned_files),
            duration,
        )
        return scanned_files

    except Exception as exc:
        duration = time.perf_counter() - start_time
        logger.error("Scanning repository failure: path=%s, error=%s, duration=%.2fs", repo_path, exc, duration)
        raise RepositoryScanError(f"Unexpected error during repository scan: {exc}") from exc
