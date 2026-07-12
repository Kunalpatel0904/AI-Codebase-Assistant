"""
Clone service — Clones public GitHub repositories locally.
"""

import time
import shutil
import tempfile
import os
import stat
from pathlib import Path
import git

from utils.exceptions import RepositoryCloneError
from utils.logger import get_logger

logger = get_logger(__name__)


def clone_repository(repo_url: str) -> Path:
    """Clones a public GitHub repository locally to a temporary directory.

    A shallow clone (depth=1) is executed to minimize bandwidth and storage.

    Args:
        repo_url: Clean canonical URL of the GitHub repository.

    Returns:
        Path: Path to the cloned repository directory.

    Raises:
        RepositoryCloneError: If the cloning process fails.
    """
    start_time = time.perf_counter()
    logger.info("Cloning repository start: url=%s", repo_url)

    try:
        # Create a unique temporary directory
        temp_dir = Path(tempfile.mkdtemp(prefix="ai_assistant_clone_"))
        
        # Clone with depth=1
        git.Repo.clone_from(
            url=repo_url,
            to_path=temp_dir,
            depth=1,
        )
        
        duration = time.perf_counter() - start_time
        logger.info("Cloning repository success: path=%s, duration=%.2fs", temp_dir, duration)
        return temp_dir

    except Exception as exc:
        duration = time.perf_counter() - start_time
        logger.error("Cloning repository failure: url=%s, error=%s, duration=%.2fs", repo_url, exc, duration)
        raise RepositoryCloneError(f"Failed to clone repository: {exc}") from exc


def cleanup_repository(repo_path: Path) -> None:
    """Deletes a cloned repository directory from local storage safely.

    Args:
        repo_path: Path to the directory to clean up.
    """
    start_time = time.perf_counter()
    logger.info("Cleanup cloned repository start: path=%s", repo_path)

    if not repo_path.exists():
        logger.debug("Cleanup skipped: path does not exist.")
        return

    try:
        # Force-delete read-only files (common in git directories on Windows)
        def _onerror(func, path, exc_info):
            os.chmod(path, stat.S_IWRITE)
            func(path)

        shutil.rmtree(repo_path, onerror=_onerror)
        duration = time.perf_counter() - start_time
        logger.info("Cleanup cloned repository success: duration=%.2fs", duration)

    except Exception as exc:
        duration = time.perf_counter() - start_time
        logger.error("Cleanup cloned repository failure: path=%s, error=%s, duration=%.2fs", repo_path, exc, duration)
