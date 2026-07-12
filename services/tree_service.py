"""
Tree service — fetches repository/directory tree structure.

Supports both GitHub repositories (via API) and local directories.
"""

from pathlib import Path
from typing import Any

import requests

import config
from utils.logger import get_logger

logger = get_logger(__name__)

_EXCLUDED_DIRS: frozenset[str] = frozenset({
    ".git", "__pycache__", ".venv", "venv", "node_modules",
    ".idea", ".vscode", ".mypy_cache", ".pytest_cache",
    "dist", "build", ".next",
})

# File extension to icon mapping.
_ICON_MAP: dict[str, str] = {
    ".py": "🐍", ".js": "📜", ".ts": "📘", ".java": "☕",
    ".go": "🔷", ".rs": "🦀", ".md": "📝", ".json": "📋",
    ".yml": "⚙️", ".yaml": "⚙️", ".toml": "⚙️",
    ".html": "🌐", ".css": "🎨",
}


def get_file_icon(filename: str) -> str:
    """Return an emoji icon for the given filename.

    Args:
        filename: File name or path.

    Returns:
        Emoji string.
    """
    ext = Path(filename).suffix.lower()
    return _ICON_MAP.get(ext, "📄")


def get_github_tree(owner: str, repo: str) -> list[dict[str, str]]:
    """Fetch repository file tree from the GitHub API.

    Uses the Git Trees API with ``recursive=1`` to get the full tree
    in a single request.

    Args:
        owner: Repository owner.
        repo: Repository name.

    Returns:
        List of dicts with ``path``, ``type`` (``tree``/``blob``), and ``icon`` keys.
    """
    url = f"{config.GITHUB_API_BASE_URL}/repos/{owner}/{repo}/git/trees/HEAD"

    logger.info("Fetching GitHub tree for %s/%s", owner, repo)

    try:
        response = requests.get(
            url,
            params={"recursive": "1"},
            timeout=config.DEFAULT_TIMEOUT,
        )
    except requests.exceptions.RequestException as exc:
        logger.error("Failed to fetch tree: %s", exc)
        return []

    if response.status_code != 200:
        logger.warning("GitHub tree API returned %d", response.status_code)
        return []

    data = response.json()
    tree_items: list[dict[str, str]] = []

    for item in data.get("tree", []):
        path = item.get("path", "")

        # Skip excluded directories and their contents
        parts = Path(path).parts
        if any(part in _EXCLUDED_DIRS for part in parts):
            continue

        item_type = item.get("type", "blob")
        icon = "📁" if item_type == "tree" else get_file_icon(path)

        tree_items.append({
            "path": path,
            "type": item_type,
            "icon": icon,
        })

    logger.info("Fetched %d tree items for %s/%s", len(tree_items), owner, repo)
    return tree_items


def get_local_tree(folder_path: str) -> list[dict[str, str]]:
    """Build a file tree from a local directory.

    Args:
        folder_path: Absolute path to the directory.

    Returns:
        List of dicts with ``path``, ``type``, and ``icon`` keys.
    """
    root = Path(folder_path)
    if not root.exists():
        return []

    items: list[dict[str, str]] = []
    _walk_local(root, root, items)

    logger.info("Built local tree: %d items from %s", len(items), folder_path)
    return items


def _walk_local(current: Path, root: Path, items: list[dict[str, str]]) -> None:
    """Recursively walk a directory and collect tree items."""
    try:
        children = sorted(current.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    except PermissionError:
        return

    for child in children:
        if child.name in _EXCLUDED_DIRS:
            continue

        rel = str(child.relative_to(root))

        if child.is_dir():
            items.append({"path": rel, "type": "tree", "icon": "📁"})
            _walk_local(child, root, items)
        else:
            items.append({"path": rel, "type": "blob", "icon": get_file_icon(child.name)})
