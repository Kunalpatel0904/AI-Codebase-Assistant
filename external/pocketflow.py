"""
PocketFlow engine wrapper.

Executes the PocketFlow Tutorial project as a subprocess.
Uses centralized configuration instead of hardcoded paths.
"""

import os
import subprocess
import sys
from pathlib import Path

import config
from utils.exceptions import PocketFlowError
from utils.logger import get_logger

logger = get_logger(__name__)

# Environment variables that PocketFlow needs.  These are explicitly
# forwarded from the parent process so the subprocess can access GitHub
# and Gemini APIs.
_PASSTHROUGH_ENV_KEYS: list[str] = [
    "GITHUB_TOKEN",
    "GEMINI_API_KEY",
    "GEMINI_PROJECT_ID",
    "GEMINI_LOCATION",
    "GEMINI_MODEL",
    "GOOGLE_API_KEY",
]


class PocketFlowEngine:
    """Subprocess wrapper for the PocketFlow tutorial generator.

    Reads the PocketFlow installation path from :mod:`config` and
    runs ``main.py --repo <url>`` as a child process.
    """

    def __init__(self) -> None:
        self.project_path: Path = config.POCKETFLOW_PATH
        self.output_path: Path = config.POCKETFLOW_OUTPUT

    def is_available(self) -> bool:
        """Check whether the PocketFlow project directory exists."""
        available = self.project_path.exists()
        logger.debug("PocketFlow available: %s (path=%s)", available, self.project_path)
        return available

    @staticmethod
    def _build_env() -> dict[str, str]:
        """Build the environment dict for the subprocess.

        Starts with the current process environment and ensures all
        required API keys are forwarded.
        """
        env = os.environ.copy()

        for key in _PASSTHROUGH_ENV_KEYS:
            value = os.getenv(key)
            if value:
                env[key] = value
                logger.debug("Forwarding env var: %s", key)

        return env

    def run_repository(self, repo_url: str) -> subprocess.CompletedProcess[str]:
        """Run PocketFlow against a GitHub repository URL.

        Args:
            repo_url: Public GitHub repository URL.

        Returns:
            :class:`subprocess.CompletedProcess` with stdout, stderr, and
            return code.

        Raises:
            PocketFlowError: If the subprocess times out.
        """
        logger.info("PocketFlow Engine — starting")
        logger.info("  Python : %s", sys.executable)
        logger.info("  Path   : %s", self.project_path)
        logger.info("  Repo   : %s", repo_url)

        command = [
            sys.executable,
            "main.py",
            "--repo",
            repo_url,
        ]

        env = self._build_env()

        try:
            result = subprocess.run(
                command,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=config.POCKETFLOW_TIMEOUT,
                env=env,
            )
        except subprocess.TimeoutExpired as exc:
            logger.error(
                "PocketFlow timed out after %ds for %s",
                config.POCKETFLOW_TIMEOUT,
                repo_url,
            )
            raise PocketFlowError(
                f"Tutorial generation timed out after "
                f"{config.POCKETFLOW_TIMEOUT} seconds."
            ) from exc

        logger.info("PocketFlow return code: %d", result.returncode)
        logger.debug("PocketFlow stdout:\n%s", result.stdout)

        if result.stderr:
            logger.debug("PocketFlow stderr:\n%s", result.stderr)

        return result