"""
GitHub service — URL parsing and GitHub REST API integration.

Consolidates the logic previously spread across ``backend/github_parser.py``,
``backend/github_api.py``, and ``backend/validator.py``.
"""

import re
from typing import Any
from urllib.parse import urlparse

import requests

import config
from utils.exceptions import (
    GitHubRateLimitError,
    GitHubURLError,
    NetworkError,
    PrivateRepoError,
    RequestTimeoutError,
)
from utils.logger import get_logger

logger = get_logger(__name__)

# Regex for validating GitHub owner/repo segments.  Must start with an
# alphanumeric character and contain only alphanumeric, hyphens, dots,
# or underscores.  This rejects path-traversal segments like ".." and
# pure-dot names.
_GITHUB_SEGMENT_RE = re.compile(r"^[a-zA-Z0-9](?:[a-zA-Z0-9._-]*[a-zA-Z0-9])?$")


# ---------------------------------------------------------------------------
# URL Parsing & Validation
# ---------------------------------------------------------------------------

def parse_github_url(url: str) -> dict[str, str]:
    """Validate and parse a GitHub repository URL.

    Args:
        url: Full GitHub URL, e.g. ``https://github.com/owner/repo``.

    Returns:
        Dict with ``owner``, ``repository``, and ``clean_url`` keys.

    Raises:
        GitHubURLError: If the URL is not a valid GitHub repository URL.
    """
    if not url or not url.strip():
        raise GitHubURLError("Please enter a GitHub repository URL.")

    try:
        parsed = urlparse(url.strip())
    except Exception as exc:
        logger.warning("URL parse error for %r: %s", url, exc)
        raise GitHubURLError() from exc

    if parsed.scheme not in ("http", "https"):
        raise GitHubURLError("URL must start with http:// or https://.")

    # Security Check: Enforce exact domain matching. This prevents host-name spoofing
    # where domains like 'notgithub.com' or 'fake-github.com' would bypass simple substring checks.
    netloc = parsed.netloc.lower()
    if netloc != "github.com" and not netloc.endswith(".github.com"):
        raise GitHubURLError("Only GitHub repository URLs are supported.")

    # Restrict path parts strictly to ['owner', 'repo']. Extra segments (like files or branches)
    # are rejected early to enforce canonical format.
    parts = parsed.path.strip("/").split("/")

    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise GitHubURLError(
            "URL must follow the format: https://github.com/owner/repository"
        )

    owner = parts[0]
    repository = parts[1].removesuffix(".git")

    # Sanitise: reject segments with unexpected characters to prevent
    # path-traversal or injection in the API URL.
    if not _GITHUB_SEGMENT_RE.match(owner):
        raise GitHubURLError(f"Invalid repository owner: {owner!r}")

    if not _GITHUB_SEGMENT_RE.match(repository):
        raise GitHubURLError(f"Invalid repository name: {repository!r}")

    logger.info("Parsed GitHub URL — owner=%s, repo=%s", owner, repository)

    # Reconstruct a clean canonical URL. This prevents query parameter/fragment
    # injection attacks from reaching the engine subprocess boundaries.
    clean_url = f"https://github.com/{owner}/{repository}"

    return {
        "owner": owner,
        "repository": repository,
        "clean_url": clean_url,
    }


# ---------------------------------------------------------------------------
# GitHub REST API
# ---------------------------------------------------------------------------

def get_repository_details(owner: str, repo: str) -> dict[str, Any]:
    """Fetch repository metadata from the GitHub REST API.

    Args:
        owner: Repository owner / organisation.
        repo: Repository name.

    Returns:
        Dict with repository metadata fields.

    Raises:
        PrivateRepoError: If the repo is private or not found.
        GitHubRateLimitError: If the rate limit is exceeded.
        NetworkError: On connection failures.
        RequestTimeoutError: If the request times out.
    """
    url = f"{config.GITHUB_API_BASE_URL}/repos/{owner}/{repo}"

    logger.info("Fetching GitHub details: %s", url)

    try:
        response = requests.get(url, timeout=config.DEFAULT_TIMEOUT)
    except requests.exceptions.Timeout as exc:
        logger.error("GitHub API timeout for %s/%s: %s", owner, repo, exc)
        raise RequestTimeoutError() from exc
    except requests.exceptions.ConnectionError as exc:
        logger.error("GitHub API connection error: %s", exc)
        raise NetworkError() from exc
    except requests.exceptions.RequestException as exc:
        logger.error("GitHub API request error: %s", exc)
        raise NetworkError(f"GitHub API error: {exc}") from exc

    if response.status_code == 404:
        raise PrivateRepoError("Repository not found. Please check the URL.")

    if response.status_code == 403:
        raise PrivateRepoError(
            "Access denied. The repository may be private."
        )

    if response.status_code == 429:
        raise GitHubRateLimitError()

    if response.status_code != 200:
        raise NetworkError(
            f"GitHub API returned status {response.status_code}."
        )

    data: dict[str, Any] = response.json()

    # Extract license name safely — the ``license`` object may exist but
    # lack a ``name`` key, or be ``None`` entirely.
    license_obj = data.get("license")
    license_name = (
        license_obj.get("name", "None") if isinstance(license_obj, dict) else "None"
    )

    details: dict[str, Any] = {
        "name": data.get("name", ""),
        "owner": data.get("owner", {}).get("login", ""),
        "description": data.get("description") or "No description available.",
        "language": data.get("language") or "Unknown",
        "stars": data.get("stargazers_count", 0),
        "forks": data.get("forks_count", 0),
        "open_issues": data.get("open_issues_count", 0),
        "license": license_name,
        "updated": (data.get("updated_at") or "")[:10],
        "html_url": data.get("html_url", ""),
    }

    logger.info(
        "Fetched details for %s/%s — stars=%s",
        owner,
        repo,
        details["stars"],
    )

    return details
