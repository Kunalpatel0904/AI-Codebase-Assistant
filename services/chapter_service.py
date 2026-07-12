"""
Chapter service — Generates codebase documentation chapters using Google Gemini.
"""

import time
from typing import Any
from google import genai

from services import prompt_service
from utils.exceptions import GeminiAPIError
from utils.logger import get_logger

logger = get_logger(__name__)


def generate_chapters(
    repo_name: str,
    details: dict[str, Any],
    stats: Any,
    file_summaries: list[dict[str, str]],
    folder_summaries: dict[str, str],
    tree_text: str,
    api_key: str,
    model_name: str = "gemini-2.5-flash",
) -> dict[str, str]:
    """Generates the 6 structured markdown chapters using Gemini.

    Args:
        repo_name: Repository name.
        details: Metadata details from GitHub API.
        stats: CodebaseStatistics object.
        file_summaries: List of file path to summary dicts.
        folder_summaries: Dict mapping folder path to folder summary.
        tree_text: Printed text directory tree structure.
        api_key: Gemini API Key.
        model_name: Gemini model name.

    Returns:
        dict[str, str]: Map of chapter filename to markdown content.

    Raises:
        GeminiAPIError: If Gemini request fails.
    """
    logger.info("Generating chapters start: repo=%s", repo_name)
    start_time = time.perf_counter()

    if not api_key:
        raise GeminiAPIError("GEMINI_API_KEY is not set.")

    chapters: dict[str, str] = {}

    try:
        client = genai.Client(api_key=api_key)
        
        # System instruction for technical writer role
        sys_instruction = prompt_service.get_chapter_system_instruction()

        # Helper to invoke Gemini
        def _get_chapter_content(filename: str, prompt: str) -> str:
            logger.info("Generating chapter file: %s", filename)
            ch_start = time.perf_counter()
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config={
                    "system_instruction": sys_instruction,
                    "temperature": 0.3,
                },
            )
            ch_duration = time.perf_counter() - ch_start
            logger.info("Generated chapter file success: %s, duration=%.2fs", filename, ch_duration)
            time.sleep(3.0)
            return (response.text or "").strip()


        # Chapter 1: Repository Summary
        chapters["01_repository_summary.md"] = _get_chapter_content(
            "01_repository_summary.md",
            prompt_service.get_repository_summary_prompt(repo_name, details, stats, folder_summaries)
        )

        # Chapter 2: Architecture Overview
        chapters["02_architecture.md"] = _get_chapter_content(
            "02_architecture.md",
            prompt_service.get_architecture_prompt(repo_name, folder_summaries)
        )

        # Chapter 3: Folder Structure
        chapters["03_folder_structure.md"] = _get_chapter_content(
            "03_folder_structure.md",
            prompt_service.get_folder_structure_prompt(repo_name, tree_text, folder_summaries)
        )

        # Chapter 4: Core Modules
        chapters["04_core_modules.md"] = _get_chapter_content(
            "04_core_modules.md",
            prompt_service.get_core_modules_prompt(repo_name, file_summaries)
        )

        # Chapter 5: API Documentation
        chapters["05_api.md"] = _get_chapter_content(
            "05_api.md",
            prompt_service.get_api_prompt(repo_name, file_summaries)
        )

        # Chapter 6: Utilities and Configuration
        chapters["06_utilities.md"] = _get_chapter_content(
            "06_utilities.md",
            prompt_service.get_utilities_prompt(repo_name, file_summaries)
        )

        duration = time.perf_counter() - start_time
        logger.info("Generating chapters success: repo=%s, duration=%.2fs", repo_name, duration)
        return chapters

    except Exception as exc:
        duration = time.perf_counter() - start_time
        logger.error("Generating chapters failure: error=%s, duration=%.2fs", exc, duration)
        raise GeminiAPIError(f"Failed to generate documentation chapters: {exc}") from exc
