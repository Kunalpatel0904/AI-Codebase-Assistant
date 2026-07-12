"""
Tutorial service — PocketFlow execution and chapter reading.

Consolidates logic from ``backend/pocketflow_runner.py``,
``backend/tutorial_reader.py``, ``backend/markdown_reader.py``,
and ``core/tutorial.py``.
"""

from dataclasses import dataclass
from pathlib import Path

from external.pocketflow import PocketFlowEngine
from utils.exceptions import PocketFlowError
from utils.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Chapter:
    """A single tutorial chapter."""

    title: str
    content: str
    filename: str


@dataclass(frozen=True)
class TutorialResult:
    """Result of a PocketFlow tutorial generation run."""

    status: str
    message: str
    output_folder: str = ""


# ---------------------------------------------------------------------------
# Tutorial Generation
# ---------------------------------------------------------------------------

def generate_tutorial(repo_url: str) -> TutorialResult:
    """Run the PocketFlow engine to generate a tutorial.

    Args:
        repo_url: Public GitHub repository URL.

    Returns:
        A :class:`TutorialResult` with status and output folder.

    Raises:
        PocketFlowError: If PocketFlow is unavailable or fails.
    """
    engine = PocketFlowEngine()

    if not engine.is_available():
        raise PocketFlowError(
            "PocketFlow project not found. "
            "Please check the POCKETFLOW_PATH configuration."
        )

    logger.info("Starting PocketFlow tutorial generation for: %s", repo_url)

    result = engine.run_repository(repo_url)


    if result.returncode != 0:
        raw_error = result.stderr.strip()
        user_msg = _extract_pocketflow_error(raw_error)
        logger.error("PocketFlow failed (rc=%d): %s", result.returncode, raw_error)
        raise PocketFlowError(user_msg)

    # Derive repo name from URL to locate the output folder
    repo_name = repo_url.rstrip("/").split("/")[-1].removesuffix(".git")
    output_folder = str(engine.output_path / repo_name)

    logger.info("Tutorial generated successfully: %s", output_folder)

    return TutorialResult(
        status="success",
        message="Tutorial generated successfully.",
        output_folder=output_folder,
    )


# ---------------------------------------------------------------------------
# Chapter Reading
# ---------------------------------------------------------------------------

def get_chapters(output_folder: str) -> list[Chapter]:
    """Read generated markdown files from the output folder.

    Args:
        output_folder: Absolute path to the PocketFlow output directory.

    Returns:
        Sorted list of :class:`Chapter` objects (excluding ``index.md``).
    """
    output_path = Path(output_folder)

    if not output_path.exists():
        logger.warning("Output folder does not exist: %s", output_folder)
        return []

    chapters: list[Chapter] = []

    for md_file in sorted(output_path.glob("*.md")):
        if md_file.name.lower() == "index.md":
            continue

        try:
            content = md_file.read_text(encoding="utf-8")
        except OSError as exc:
            logger.error("Failed to read %s: %s", md_file, exc)
            continue

        chapters.append(
            Chapter(
                title=md_file.stem.replace("_", " ").title(),
                content=content,
                filename=md_file.name,
            )
        )

    logger.info("Loaded %d chapters from %s", len(chapters), output_folder)

    return chapters


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

# Map known PocketFlow error fragments to user-friendly messages.
_ERROR_MAP: dict[str, str] = {
    "Failed to fetch files": (
        "Could not fetch repository files. "
        "Please check that your GITHUB_TOKEN is set and the repository is public."
    ),
    "GEMINI_API_KEY must be set": (
        "Gemini API key is missing. "
        "Please set GEMINI_API_KEY in your .env file."
    ),
    "GEMINI_PROJECT_ID": (
        "Gemini API key is missing. "
        "Please set GEMINI_API_KEY in your .env file."
    ),
}


def _extract_pocketflow_error(stderr: str) -> str:
    """Extract a user-friendly error message from PocketFlow stderr.

    Scans the raw traceback for known error patterns and returns a
    helpful message.  Falls back to the last line of the traceback.

    Args:
        stderr: Raw stderr output from the PocketFlow subprocess.

    Returns:
        A clean, user-friendly error message.
    """
    if not stderr:
        return "Tutorial generation failed with an unknown error."

    # Check for known error patterns
    for fragment, friendly_msg in _ERROR_MAP.items():
        if fragment in stderr:
            return friendly_msg

    # Fallback: extract just the last meaningful line
    last_line = stderr.strip().splitlines()[-1].strip()
    return f"Tutorial generation failed: {last_line}"

