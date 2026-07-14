"""
Markdown service — Formats and writes generated chapters to disk.
"""

import time
from pathlib import Path

from utils.logger import get_logger

logger = get_logger(__name__)


def save_chapters_to_disk(repo_name: str, chapters: dict[str, str]) -> Path:
    """Saves generated markdown chapters and index.md to the output folder.

    Args:
        repo_name: Safe name of the repository.
        chapters: Dict mapping filename (e.g., '01_repository_summary.md') to content.

    Returns:
        Path: Output directory path.
    """
    logger.info("Saving chapters to disk start: repo=%s", repo_name)
    start_time = time.perf_counter()

    # Determine safe output directory
    output_dir = Path("output") / repo_name
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save each chapter file
    for filename, content in chapters.items():
        file_path = output_dir / filename
        file_path.write_text(content, encoding="utf-8")
        logger.debug("Wrote chapter file: %s", file_path)

    # Generate and write index.md
    index_content = f"# {repo_name} Codebase Documentation Index\n\n"
    index_content += "Welcome to the AI-generated documentation for the codebase. Below is the list of chapters:\n\n"
    
    # Sort files to match numerical order
    for filename in sorted(chapters.keys()):
        # Turn filename into readable title: '01_repository_summary.md' -> 'Repository Summary'
        title = filename.replace(".md", "").split("_", 1)[-1].replace("_", " ").title()
        index_content += f"- [{title}]({filename})\n"

    index_path = output_dir / "index.md"
    index_path.write_text(index_content, encoding="utf-8")
    logger.debug("Wrote index file: %s", index_path)

    duration = time.perf_counter() - start_time
    logger.info("Saving chapters to disk success: path=%s, duration=%.2fs", output_dir, duration)
    return output_dir
