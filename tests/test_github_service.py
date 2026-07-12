"""
Unit tests for github_service URL parsing.
"""

import unittest

from services.github_service import parse_github_url
from utils.exceptions import GitHubURLError


class TestGitHubService(unittest.TestCase):

    def test_parse_valid_github_urls(self) -> None:
        """Verify correct parsing of valid public GitHub repository URLs."""
        valid_cases = [
            (
                "https://github.com/owner/repo",
                {
                    "owner": "owner",
                    "repository": "repo",
                    "clean_url": "https://github.com/owner/repo",
                },
            ),
            (
                "http://github.com/owner/repo-name",
                {
                    "owner": "owner",
                    "repository": "repo-name",
                    "clean_url": "https://github.com/owner/repo-name",
                },
            ),
            (
                "https://github.com/owner/repo.git",
                {
                    "owner": "owner",
                    "repository": "repo",
                    "clean_url": "https://github.com/owner/repo",
                },
            ),
            (
                "https://github.com/owner/repo.name",
                {
                    "owner": "owner",
                    "repository": "repo.name",
                    "clean_url": "https://github.com/owner/repo.name",
                },
            ),
            (
                " https://github.com/owner/repo  ",
                {
                    "owner": "owner",
                    "repository": "repo",
                    "clean_url": "https://github.com/owner/repo",
                },
            ),
            (
                "https://github.com/owner/repo?query=1",
                {
                    "owner": "owner",
                    "repository": "repo",
                    "clean_url": "https://github.com/owner/repo",
                },
            ),
            (
                "https://github.com/owner/repo#fragment",
                {
                    "owner": "owner",
                    "repository": "repo",
                    "clean_url": "https://github.com/owner/repo",
                },
            ),
            (
                "https://github.com/owner/repo;injection",
                {
                    "owner": "owner",
                    "repository": "repo",
                    "clean_url": "https://github.com/owner/repo",
                },
            ),
        ]

        for url, expected in valid_cases:
            with self.subTest(url=url):
                self.assertEqual(parse_github_url(url), expected)

    def test_parse_invalid_github_urls(self) -> None:
        """Verify exceptions are raised for invalid, empty, or unsafe URLs."""
        invalid_cases = [
            "",
            "   ",
            "https://notgithub.com/owner/repo",
            "https://fake-github.com/owner/repo",
            "ftp://github.com/owner/repo",
            "https://github.com/owner",
            "https://github.com/owner/",
            "https://github.com//repo",
            "https://github.com/owner/repo/subpath",
            "https://github.com/owner/../repo",
            "https://github.com/owner/repo.git/something",
            "https://github.com/owner<script>/repo",
            "https://github.com/owner/repo!",
        ]

        for url in invalid_cases:
            with self.subTest(url=url):
                with self.assertRaises(GitHubURLError):
                    parse_github_url(url)


if __name__ == "__main__":
    unittest.main()
