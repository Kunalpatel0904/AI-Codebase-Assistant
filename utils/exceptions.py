"""
Custom exception hierarchy for the AI Codebase Assistant.

Every exception carries a user-friendly ``message`` suitable for direct
display in the Streamlit UI via ``st.error()``.
"""


class AppError(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str = "An unexpected error occurred.") -> None:
        self.message = message
        super().__init__(self.message)


# ---------------------------------------------------------------------------
# GitHub Errors
# ---------------------------------------------------------------------------

class GitHubURLError(AppError):
    """Raised when the provided URL is not a valid GitHub repository URL."""

    def __init__(self, message: str = "Please enter a valid GitHub repository URL.") -> None:
        super().__init__(message)


class PrivateRepoError(AppError):
    """Raised when the repository is private or not found (403/404)."""

    def __init__(self, message: str = "This repository is private or does not exist.") -> None:
        super().__init__(message)


class GitHubRateLimitError(AppError):
    """Raised when the GitHub API rate limit is exceeded (429)."""

    def __init__(self, message: str = "GitHub API rate limit exceeded. Please try again later.") -> None:
        super().__init__(message)


# ---------------------------------------------------------------------------
# AI / Gemini Errors
# ---------------------------------------------------------------------------

class GeminiAPIError(AppError):
    """Raised when the Gemini API returns an error."""

    def __init__(self, message: str = "Gemini API error. Please check your API key and try again.") -> None:
        super().__init__(message)


# ---------------------------------------------------------------------------
# PocketFlow Errors
# ---------------------------------------------------------------------------

class PocketFlowError(AppError):
    """Raised when the PocketFlow engine fails."""

    def __init__(self, message: str = "PocketFlow execution failed.") -> None:
        super().__init__(message)


# ---------------------------------------------------------------------------
# Network Errors
# ---------------------------------------------------------------------------

class NetworkError(AppError):
    """Raised on connection or generic network failures."""

    def __init__(self, message: str = "Network error. Please check your connection and try again.") -> None:
        super().__init__(message)


class RequestTimeoutError(AppError):
    """Raised when an HTTP request times out."""

    def __init__(self, message: str = "The request timed out. Please try again later.") -> None:
        super().__init__(message)
