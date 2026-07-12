"""
ZIP service — extraction and validation for uploaded ZIP files.
"""

import shutil
import zipfile
from io import BytesIO
from pathlib import Path

import config
from utils.logger import get_logger

logger = get_logger(__name__)

# Maximum upload size in bytes (default 50 MB).
MAX_ZIP_SIZE: int = config.MAX_ZIP_SIZE_MB * 1024 * 1024


def extract_zip(uploaded_file: BytesIO, filename: str) -> Path:
    """Extract an uploaded ZIP file to a temporary directory.

    Args:
        uploaded_file: The uploaded file's bytes buffer.
        filename: Original filename of the upload.

    Returns:
        Path to the extracted directory.

    Raises:
        ValueError: If the file is too large, not a valid ZIP, or empty.
    """
    # Validate size
    uploaded_file.seek(0, 2)  # seek to end
    size = uploaded_file.tell()
    uploaded_file.seek(0)

    if size > MAX_ZIP_SIZE:
        size_mb = size / (1024 * 1024)
        raise ValueError(
            f"ZIP file is too large ({size_mb:.1f} MB). "
            f"Maximum allowed: {config.MAX_ZIP_SIZE_MB} MB."
        )

    if size == 0:
        raise ValueError("The uploaded file is empty.")

    # Validate ZIP format
    if not zipfile.is_zipfile(uploaded_file):
        raise ValueError("The uploaded file is not a valid ZIP archive.")

    uploaded_file.seek(0)

    # Create extraction directory
    stem = Path(filename).stem
    extract_dir = config.OUTPUT_DIR / "zip_uploads" / stem
    extract_dir.mkdir(parents=True, exist_ok=True)

    # Clean previous extraction
    if extract_dir.exists():
        shutil.rmtree(extract_dir)

    # Extract
    with zipfile.ZipFile(uploaded_file, "r") as zf:
        # Security: check for path traversal
        for member in zf.namelist():
            member_path = Path(member)
            if member_path.is_absolute() or ".." in member_path.parts:
                raise ValueError(
                    f"ZIP contains unsafe path: {member}. Upload rejected."
                )

        zf.extractall(extract_dir)

    # If ZIP contains a single top-level directory, use that as the root
    top_items = list(extract_dir.iterdir())
    if len(top_items) == 1 and top_items[0].is_dir():
        actual_root = top_items[0]
    else:
        actual_root = extract_dir

    logger.info(
        "Extracted ZIP '%s': %d bytes -> %s",
        filename, size, actual_root,
    )

    return actual_root


def cleanup_zip_upload(extract_dir: str) -> None:
    """Remove extracted ZIP files after analysis.

    Args:
        extract_dir: Path to the extracted directory.
    """
    path = Path(extract_dir)
    if path.exists() and "zip_uploads" in str(path):
        shutil.rmtree(path, ignore_errors=True)
        logger.info("Cleaned up ZIP extraction: %s", path)
