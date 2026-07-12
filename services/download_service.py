"""
Download service — file downloads and ZIP creation.

Consolidates logic from ``backend/download.py`` with future-ready
PDF export stub.
"""

import io
import zipfile
from pathlib import Path

from utils.logger import get_logger

logger = get_logger(__name__)


def get_markdown_files(output_folder: str) -> list[Path]:
    """Return sorted list of markdown files in the output folder.

    Args:
        output_folder: Absolute path to the tutorial output directory.

    Returns:
        Sorted list of :class:`Path` objects for each ``.md`` file.
    """
    output_path = Path(output_folder)

    if not output_path.exists():
        logger.warning("Output folder not found: %s", output_folder)
        return []

    files = sorted(output_path.glob("*.md"))
    logger.debug("Found %d markdown files in %s", len(files), output_folder)

    return files


def create_tutorial_zip(output_folder: str) -> bytes:
    """Create an in-memory ZIP archive of all markdown tutorial files.

    Args:
        output_folder: Absolute path to the tutorial output directory.

    Returns:
        ZIP file contents as bytes, or empty bytes if no files found.
    """
    markdown_files = get_markdown_files(output_folder)

    if not markdown_files:
        return b""

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for md_file in markdown_files:
            zipf.write(md_file, arcname=md_file.name)

    zip_bytes = zip_buffer.getvalue()

    logger.info(
        "Created tutorial ZIP (%d files, %d bytes)",
        len(markdown_files),
        len(zip_bytes),
    )

    return zip_bytes


def export_to_pdf(output_folder: str) -> bytes:
    """Export the tutorial as a PDF document.

    .. note:: This feature is planned for Version 2.

    Raises:
        NotImplementedError: Always — PDF export is coming in V2.
    """
    raise NotImplementedError("PDF export is coming in Version 2.")
