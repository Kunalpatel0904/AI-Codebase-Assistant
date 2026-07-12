"""
Repository tree builder for V2.

Builds a visual text representation of a repository's directory structure,
filtering out common non-essential directories.
"""

from pathlib import Path

from utils.logger import get_logger

logger = get_logger(__name__)

# Directories to exclude from the tree output.
_EXCLUDED_DIRS: frozenset[str] = frozenset({
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    ".idea",
    ".vscode",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
})


def build_repository_tree(repository_path: str | Path) -> list[str]:
    """Build a text-based tree of the repository directory structure.

    Args:
        repository_path: Absolute path to the repository root.

    Returns:
        List of formatted tree lines (e.g. ``["📂 myrepo", "    📄 README.md"]``).
    """
    root = Path(repository_path)

    if not root.exists():
        logger.warning("Repository path does not exist: %s", repository_path)
        return []

    lines: list[str] = []
    _walk(root, root, lines)

    logger.debug("Built repository tree with %d lines", len(lines))
    return lines


def _walk(current: Path, root: Path, lines: list[str]) -> None:
    """Recursively walk the directory tree.

    Args:
        current: Current directory being processed.
        root: Top-level repository root (for computing indent depth).
        lines: Accumulator list of formatted lines.
    """
    depth = len(current.relative_to(root).parts)
    indent = "    " * depth

    # Directory header
    if depth == 0:
        lines.append(f"📂 {root.name}")
    else:
        lines.append(f"{indent}📁 {current.name}")

    # Files first (sorted), then sub-directories (sorted, filtered)
    children = sorted(current.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))

    for child in children:
        if child.is_file():
            lines.append(f"{indent}    📄 {child.name}")
        elif child.is_dir() and child.name not in _EXCLUDED_DIRS:
            _walk(child, root, lines)