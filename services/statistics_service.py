"""
Statistics service — Computes codebase metrics from scanned files.
"""

import time
from dataclasses import dataclass
from pathlib import Path
from services.repository_scanner import ScannedFile
from utils.exceptions import RepositoryScanError
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class CodebaseStatistics:
    """Dataclass holding calculated metrics for a codebase.

    Frozen to ensure immutability of the metrics.
    """

    total_files: int
    total_folders: int
    total_python_files: int
    total_markdown_files: int
    total_lines_of_code: int
    largest_file: str
    largest_file_size: int
    average_file_size: float


def compute_statistics(scanned_files: list[ScannedFile]) -> CodebaseStatistics:
    """Computes codebase metrics (files, folders, LOC, largest file, average size) from scanned files.

    Args:
        scanned_files: List of metadata objects for each scanned file.

    Returns:
        CodebaseStatistics: Immutably stored codebase metrics.

    Raises:
        RepositoryScanError: If computation fails.
    """
    start_time = time.perf_counter()
    logger.info("Computing codebase statistics start: file_count=%d", len(scanned_files))

    try:
        if not scanned_files:
            stats = CodebaseStatistics(
                total_files=0,
                total_folders=0,
                total_python_files=0,
                total_markdown_files=0,
                total_lines_of_code=0,
                largest_file="",
                largest_file_size=0,
                average_file_size=0.0,
            )
            duration = time.perf_counter() - start_time
            logger.info("Computing codebase statistics success (empty): duration=%.2fs", duration)
            return stats

        total_files = len(scanned_files)
        
        # Calculate unique folders in the directory hierarchy
        unique_folders: set[str] = set()
        total_python_files = 0
        total_markdown_files = 0
        total_lines_of_code = 0
        total_size = 0
        
        largest_file_path = ""
        largest_file_size = -1

        for f in scanned_files:
            # 1. Folders
            path = Path(f.relative_path)
            for parent in path.parents:
                parent_str = str(parent).replace("\\", "/")
                if parent_str != "." and parent_str != "":
                    unique_folders.add(parent_str)

            # 2. File extensions count
            if f.extension == ".py":
                total_python_files += 1
            elif f.extension == ".md":
                total_markdown_files += 1

            # 3. Lines of code and size
            total_lines_of_code += f.line_count
            total_size += f.file_size

            # 4. Find largest file
            if f.file_size > largest_file_size:
                largest_file_size = f.file_size
                largest_file_path = f.relative_path

        total_folders = len(unique_folders)
        average_file_size = float(total_size) / total_files

        stats = CodebaseStatistics(
            total_files=total_files,
            total_folders=total_folders,
            total_python_files=total_python_files,
            total_markdown_files=total_markdown_files,
            total_lines_of_code=total_lines_of_code,
            largest_file=largest_file_path,
            largest_file_size=largest_file_size,
            average_file_size=average_file_size,
        )

        duration = time.perf_counter() - start_time
        logger.info(
            "Computing codebase statistics success: files=%d, folders=%d, loc=%d, duration=%.2fs",
            total_files,
            total_folders,
            total_lines_of_code,
            duration,
        )
        return stats

    except Exception as exc:
        duration = time.perf_counter() - start_time
        logger.error("Computing codebase statistics failure: error=%s, duration=%.2fs", exc, duration)
        raise RepositoryScanError(f"Failed to calculate codebase statistics: {exc}") from exc
