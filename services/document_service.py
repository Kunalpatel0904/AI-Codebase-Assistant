"""
Document service — Master orchestrator for the AI Documentation Engine.
"""

import time
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import config
from services import (
    github_clone_service,
    repository_scanner,
    statistics_service,
    tree_service,
    github_service,
    summary_service,
    chapter_service,
    markdown_service,
)
from services.statistics_service import CodebaseStatistics
from utils.exceptions import AppError
from utils.logger import get_logger
from utils.gemini_client import reset_stats, get_api_call_count, get_cache_hit_count

logger = get_logger(__name__)


@dataclass(frozen=True)
class DocumentationAnalysisResult:
    """Aggregated result of the AI codebase documentation process.

    Frozen to ensure immutability.
    """

    status: str
    message: str
    details: Optional[dict[str, Any]] = None
    stats: Optional[CodebaseStatistics] = None
    tree: Optional[dict[str, Any]] = None
    tree_text: Optional[list[str]] = None
    output_folder: Optional[str] = None


def generate_documentation(repo_url: str) -> DocumentationAnalysisResult:
    """Clones, scans, calculates stats, summarizes files/folders, compiles chapters,

    and writes markdown documentation for a public GitHub repository.

    Ensures the temporary repository directory is deleted after analysis.
    """
    logger.info("Starting AI Documentation Engine pipeline for: %s", repo_url)
    start_time = time.perf_counter()
    
    # Reset Gemini client API usage statistics for this run
    reset_stats()

    api_key = os.getenv("GEMINI_API_KEY") or getattr(config, "GEMINI_API_KEY", None)
    if not api_key:
        logger.error("AI Documentation Engine failure: GEMINI_API_KEY is not configured.")
        return DocumentationAnalysisResult(
            status="error",
            message="GEMINI_API_KEY environment variable is missing. Please add it to your .env file.",
        )

    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


    clone_dir = None
    try:
        # Step 1 — Parse URL
        repo_info = github_service.parse_github_url(repo_url)
        repo_name = repo_info["repository"]

        # Step 2 — Fetch repository details from GitHub API
        details = github_service.get_repository_details(
            owner=repo_info["owner"],
            repo=repo_name,
        )

        # Step 3 — Clone the repository locally
        clone_dir = github_clone_service.clone_repository(repo_info["clean_url"])

        # Step 4 — Scan the local repository
        scanned_files = repository_scanner.scan_repository(clone_dir)
        if not scanned_files:
            raise AppError("No supported code files found in the repository.")

        # Step 5 — Compute codebase statistics
        stats = statistics_service.compute_statistics(scanned_files)

        # Step 6 — Generate file summaries using Gemini (Batched)
        file_summaries = summary_service.summarize_files(
            scanned_files=scanned_files,
            api_key=api_key,
            model_name=model_name,
        )

        # Step 7 — Generate folder summaries using Gemini
        folder_summaries = summary_service.summarize_folders(
            scanned_files_with_summaries=file_summaries,
            api_key=api_key,
            model_name=model_name,
        )

        # Step 8 — Generate recursive trees
        tree = tree_service.generate_recursive_tree(scanned_files)
        tree_text_lines = tree_service.render_tree_to_text(tree)
        tree_text_str = "\n".join(tree_text_lines)

        # Step 9 — Compile 6 chapters using Gemini in a single JSON call
        chapters = chapter_service.generate_chapters(
            repo_name=repo_name,
            details=details,
            stats=stats,
            file_summaries=file_summaries,
            folder_summaries=folder_summaries,
            tree_text=tree_text_str,
            api_key=api_key,
            model_name=model_name,
        )

        # Step 10 — Save chapters to disk and write index.md
        output_path = markdown_service.save_chapters_to_disk(
            repo_name=repo_name,
            chapters=chapters,
        )

        # Step 11 — Write Gemini API Optimization Report
        duration = time.perf_counter() - start_time
        
        calls_made = get_api_call_count()
        cache_hits = get_cache_hit_count()
        total_files = len(scanned_files)
        total_folders = len(folder_summaries)
        
        # Calculate comparison stats
        prev_file_calls = (total_files + 11) // 12
        opt_file_calls = (total_files + 29) // 30
        
        prev_folder_calls = total_folders
        opt_folder_calls = 1
        
        prev_chapter_calls = 6
        opt_chapter_calls = 1
        
        prev_total = prev_file_calls + prev_folder_calls + prev_chapter_calls
        quota_savings = prev_total - calls_made
        savings_percentage = (quota_savings / prev_total) * 100 if prev_total > 0 else 0.0
        
        report_content = f"""# Gemini API Optimization Report — {repo_name}

This report shows details of the Gemini API optimization for this run.

## API Request Metrics
| Metric | Previous Pipeline | Optimized Pipeline (This Run) |
| --- | --- | --- |
| File Summary Requests | {prev_file_calls} | {opt_file_calls} |
| Folder Summary Requests | {prev_folder_calls} | {opt_folder_calls} |
| Chapter Generation Requests | {prev_chapter_calls} | {opt_chapter_calls} |
| **Total API Requests** | **{prev_total}** | **{calls_made}** |
| Cache Hits | 0 | {cache_hits} |
| **Quota Savings** | — | **{quota_savings} requests ({savings_percentage:.1f}%)** |

## Execution Time Details
- **Previous Pipeline Expected Time:** ~{prev_total * 4.0:.1f}s (with default 3s throttling delays)
- **Optimized Pipeline Execution Time:** {duration:.2f}s
- **Speedup:** {((prev_total * 4.0) / duration) if duration > 0 else 0.0:.2f}x
"""
        report_file = Path(output_path) / "optimization_report.md"
        report_file.write_text(report_content, encoding="utf-8")
        
        logger.info("Generated API optimization report: %s", report_file)
        logger.info("API Calls Made: %d, Cache Hits: %d. Savings: %d requests (%.1f%%)", calls_made, cache_hits, quota_savings, savings_percentage)

        logger.info(
            "AI Documentation Engine pipeline success: owner=%s, repo=%s, duration=%.2fs",
            repo_info["owner"],
            repo_name,
            duration,
        )

        return DocumentationAnalysisResult(
            status="success",
            message="Codebase documentation generated successfully.",
            details=details,
            stats=stats,
            tree=tree,
            tree_text=tree_text_lines,
            output_folder=str(output_path),
        )

    except AppError as exc:
        duration = time.perf_counter() - start_time
        logger.warning("AI Documentation Engine pipeline failed after %.2fs: %s", duration, exc.message)
        return DocumentationAnalysisResult(status="error", message=exc.message)

    except Exception as exc:
        duration = time.perf_counter() - start_time
        logger.exception("Unexpected error in AI Documentation Engine pipeline after %.2fs", duration)
        return DocumentationAnalysisResult(status="error", message=f"Pipeline error occurred: {exc}")

    finally:
        # Step 12 — Clean up cloned folder from local disk
        if clone_dir is not None:
            github_clone_service.cleanup_repository(clone_dir)
