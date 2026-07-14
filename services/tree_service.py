"""
Tree service — fetches repository/directory tree structure.

Supports both GitHub repositories (via API) and local directories.
"""

from pathlib import Path
from typing import Any
import time

from services.repository_scanner import ScannedFile

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


# ---------------------------------------------------------------------------
# V2 Recursive JSON Tree Generation
# ---------------------------------------------------------------------------

def generate_recursive_tree(scanned_files: list[ScannedFile]) -> dict[str, Any]:
    """Generates a nested recursive dictionary structure representing the directory tree.

    Args:
        scanned_files: List of metadata objects for each scanned file.

    Returns:
        dict[str, Any]: Nested dictionary matching JSON tree structure.
    """
    logger.info("Generating recursive directory tree start: files=%d", len(scanned_files))
    start_time = time.perf_counter()
    tree: dict[str, Any] = {}

    try:
        for f in scanned_files:
            parts = f.relative_path.split("/")
            current = tree
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    # It's a file
                    current[part] = {
                        "name": part,
                        "type": "file",
                        "size": f.file_size,
                        "lines": f.line_count,
                        "extension": f.extension,
                    }
                else:
                    # It's a directory
                    if part not in current:
                        current[part] = {
                            "name": part,
                            "type": "directory",
                            "children": {},
                        }
                    current = current[part]["children"]

        duration = time.perf_counter() - start_time
        logger.info("Generating recursive directory tree success: duration=%.2fs", duration)
        return tree

    except Exception as exc:
        duration = time.perf_counter() - start_time
        logger.error("Generating recursive directory tree failure: error=%s, duration=%.2fs", exc, duration)
        # Return empty on failure
        return {}


def render_tree_to_text(tree: dict[str, Any], indent: str = "") -> list[str]:
    """Renders a nested directory tree into a formatted list of indented visual text lines.

    Args:
        tree: Nested dictionary matching JSON tree structure.
        indent: Character spaces representing indentation levels.

    Returns:
        list[str]: Indented tree representation lines (e.g. ['📂 src/', '    📄 main.py']).
    """
    lines: list[str] = []
    
    # Sort keys: directories first (sorted), then files (sorted)
    sorted_keys = sorted(
        tree.keys(),
        key=lambda k: (tree[k]["type"] != "directory", k.lower())
    )

    for key in sorted_keys:
        item = tree[key]
        if item["type"] == "directory":
            lines.append(f"{indent}📁 {key}/")
            # Recurse children
            lines.extend(render_tree_to_text(item["children"], indent + "    "))
        else:
            icon = get_file_icon(key)
            lines.append(f"{indent}{icon} {key}")

    return lines

