"""
Dashboard service — Orchestrates the Version 2 local repository analysis flow.
"""

import time
from dataclasses import dataclass
from typing import Any, Optional

from services import (
    github_clone_service,
    repository_scanner,
    statistics_service,
    tree_service,
    github_service,
)
from services.statistics_service import CodebaseStatistics
from utils.exceptions import AppError
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class V2AnalysisResult:
    """Complete result of a Version 2 repository analysis.

    Frozen to ensure immutability of the analysis outcome.
    """

    status: str
    message: str
    details: Optional[dict[str, Any]] = None
    stats: Optional[CodebaseStatistics] = None
    tree: Optional[dict[str, Any]] = None
    tree_text: Optional[list[str]] = None


def analyze_repository_v2(repo_url: str) -> V2AnalysisResult:
    """Clones, scans, parses stats, and builds directory trees for a public repository.

    Ensures local clone folders are always cleaned up via a try-finally block.

    Args:
        repo_url: Public GitHub repository URL.

    Returns:
        V2AnalysisResult: Aggregated result holding status, metadata, stats, and trees.
    """
    logger.info("Starting Version 2 analysis pipeline for: %s", repo_url)
    start_time = time.perf_counter()
    clone_dir = None

    try:
        # Step 1 — Parse URL
        repo_info = github_service.parse_github_url(repo_url)

        # Step 2 — Fetch repository details from GitHub API
        details = github_service.get_repository_details(
            owner=repo_info["owner"],
            repo=repo_info["repository"],
        )

        # Step 3 — Clone the repository locally
        clone_dir = github_clone_service.clone_repository(repo_info["clean_url"])

        # Step 4 — Scan the local repository
        scanned_files = repository_scanner.scan_repository(clone_dir)

        # Step 5 — Compute codebase statistics
        stats = statistics_service.compute_statistics(scanned_files)

        # Step 6 — Generate JSON tree and Text tree
        tree = tree_service.generate_recursive_tree(scanned_files)
        tree_text = tree_service.render_tree_to_text(tree)

        duration = time.perf_counter() - start_time
        logger.info(
            "Version 2 analysis pipeline complete: owner=%s, repo=%s, duration=%.2fs",
            repo_info["owner"],
            repo_info["repository"],
            duration,
        )

        return V2AnalysisResult(
            status="success",
            message="Repository analyzed successfully.",
            details=details,
            stats=stats,
            tree=tree,
            tree_text=tree_text,
        )

    except AppError as exc:
        duration = time.perf_counter() - start_time
        logger.warning("Version 2 analysis pipeline failed after %.2fs: %s", duration, exc.message)
        return V2AnalysisResult(status="error", message=exc.message)

    except Exception as exc:
        duration = time.perf_counter() - start_time
        logger.exception("Unexpected error in Version 2 analysis pipeline after %.2fs", duration)
        return V2AnalysisResult(status="error", message=f"An unexpected error occurred: {exc}")

    finally:
        # Step 7 — Clean up cloned folder from local disk
        if clone_dir is not None:
            github_clone_service.cleanup_repository(clone_dir)
