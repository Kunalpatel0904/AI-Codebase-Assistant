"""
Chapter service — Generates codebase documentation chapters using Google Gemini.
"""

import json
import re
import time
from typing import Any
from google import genai

from services import prompt_service
from utils.exceptions import GeminiAPIError
from utils.logger import get_logger
from utils.gemini_client import generate_content_with_retry

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
    """Generates the 6 structured markdown chapters in a single batched Gemini API call.

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

        # Compile master prompt and call Gemini with structured JSON output configuration
        master_prompt = prompt_service.get_chapters_master_prompt(
            repo_name=repo_name,
            details=details,
            stats=stats,
            file_summaries=file_summaries,
            folder_summaries=folder_summaries,
            tree_text=tree_text,
        )

        res_text = generate_content_with_retry(
            client=client,
            model=model_name,
            contents=master_prompt,
            config={
                "system_instruction": sys_instruction,
                "response_mime_type": "application/json",
                "temperature": 0.3,
            },
        )

        # Parse JSON mapping
        parsed = {}
        try:
            parsed = json.loads(res_text)
        except Exception as json_exc:
            logger.warning("JSON parsing of master chapters failed: %s. Using regex parser fallback.", json_exc)
            for key in [
                "01_repository_summary.md",
                "02_architecture.md",
                "03_folder_structure.md",
                "04_core_modules.md",
                "05_api.md",
                "06_utilities.md"
            ]:
                pattern = rf'"{key}"\s*:\s*"(.*?)"'
                match = re.search(pattern, res_text, re.DOTALL)
                if match:
                    try:
                        parsed[key] = match.group(1).encode().decode('unicode-escape', errors='ignore')
                    except Exception:
                        parsed[key] = match.group(1)

        required_keys = [
            ("01_repository_summary.md", "Repository Summary"),
            ("02_architecture.md", "Architecture Overview"),
            ("03_folder_structure.md", "Folder Structure"),
            ("04_core_modules.md", "Core Modules"),
            ("05_api.md", "API Documentation"),
            ("06_utilities.md", "Utilities and Configuration")
        ]

        for key, title in required_keys:
            content = parsed.get(key)
            if not content:
                # If key is completely missing, lookup ignoring case or whitespace
                alt_key = next((k for k in parsed.keys() if key in k or k in key), None)
                if alt_key:
                    content = parsed.get(alt_key)
            
            if not content:
                content = f"# {title}\n\nDetailed codebase documentation content currently unavailable."
            
            chapters[key] = content.strip()

        duration = time.perf_counter() - start_time
        logger.info("Generating chapters success: repo=%s, duration=%.2fs", repo_name, duration)
        return chapters

    except Exception as exc:
        duration = time.perf_counter() - start_time
        logger.error("Generating chapters failure: error=%s, duration=%.2fs", exc, duration)
        raise GeminiAPIError(f"Failed to generate documentation chapters: {exc}") from exc
