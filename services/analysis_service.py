"""
Analysis service — orchestrates the full repository analysis pipeline.

This is the single entry point that the frontend calls. It coordinates
GitHub parsing, metadata fetching, and PocketFlow tutorial generation.
"""

import time
from dataclasses import dataclass
from typing import Any, Optional

from services import github_service, tutorial_service
from utils.exceptions import AppError
from utils.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Data Class
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AnalysisResult:
    """Complete result of a repository analysis.

    Frozen to prevent accidental mutation after creation.
    """

    status: str
    message: str
    repo_info: Optional[dict[str, str]] = None
    details: Optional[dict[str, Any]] = None
    output_folder: str = ""


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def analyze_repository(repo_url: str) -> AnalysisResult:
    """Run the full analysis pipeline for a public GitHub repository.

    Steps:
        1. Parse and validate the GitHub URL.
        2. Fetch repository metadata from the GitHub API.
        3. Run PocketFlow to generate the tutorial.

    Args:
        repo_url: Public GitHub repository URL.

    Returns:
        An :class:`AnalysisResult` containing status, details, and output path.

    Note:
        All exceptions from sub-services are caught and wrapped into a
        failed ``AnalysisResult`` so the frontend never sees raw exceptions
        from this function.
    """
    start = time.perf_counter()

    try:
        # Step 1 — Parse URL
        repo_info = github_service.parse_github_url(repo_url)

        # Step 2 — Fetch metadata
        details = github_service.get_repository_details(
            owner=repo_info["owner"],
            repo=repo_info["repository"],
        )

        # Step 3 — Generate tutorial
        tutorial_result = tutorial_service.generate_tutorial(repo_info["clean_url"])

        elapsed = time.perf_counter() - start

        logger.info(
            "Analysis complete for %s/%s in %.2fs",
            repo_info["owner"],
            repo_info["repository"],
            elapsed,
        )

        return AnalysisResult(
            status="success",
            message="Repository analyzed and tutorial generated successfully.",
            repo_info=repo_info,
            details=details,
            output_folder=tutorial_result.output_folder,
        )

    except AppError as exc:
        elapsed = time.perf_counter() - start
        logger.warning("Analysis failed after %.2fs: %s", elapsed, exc.message)

        return AnalysisResult(
            status="error",
            message=exc.message,
        )

    except Exception as exc:
        elapsed = time.perf_counter() - start
        logger.exception("Unexpected error during analysis after %.2fs", elapsed)

        return AnalysisResult(
            status="error",
            message=f"An unexpected error occurred: {exc}",
        )
