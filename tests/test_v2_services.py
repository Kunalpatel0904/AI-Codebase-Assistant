"""
Unit tests for Version 2 services: Repository Scanner, Tree Generator, and Statistics.
"""

import unittest
import tempfile
from pathlib import Path

from services.repository_scanner import scan_repository, ScannedFile
from services.statistics_service import compute_statistics, CodebaseStatistics
from services.tree_service import generate_recursive_tree, render_tree_to_text
from services.github_service import parse_github_url
from utils.exceptions import RepositoryScanError, GitHubURLError


class TestV2Services(unittest.TestCase):

    def setUp(self) -> None:
        """Create a temporary directory structure for testing scanner and statistics."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root_path = Path(self.temp_dir.name)

        # Create files and subdirectories
        # 1. Root files
        self._write_file(self.root_path / "README.md", "# Codebase\nHello World!")
        self._write_file(self.root_path / "config.json", '{"version": "1.0"}')

        # 2. Source folder
        src_dir = self.root_path / "src"
        src_dir.mkdir()
        self._write_file(src_dir / "main.py", "import sys\n\ndef main():\n    print('Hello')\n\nmain()\n")
        
        # 3. Nested folder
        utils_dir = src_dir / "utils"
        utils_dir.mkdir()
        self._write_file(utils_dir / "helpers.py", "def add(a, b):\n    return a + b\n")

        # 4. Ignored directories & unsupported extensions (should NOT be scanned)
        git_dir = self.root_path / ".git"
        git_dir.mkdir()
        self._write_file(git_dir / "config", "some git config")

        node_dir = self.root_path / "node_modules"
        node_dir.mkdir()
        self._write_file(node_dir / "package.json", "{}")

        self._write_file(src_dir / "logo.png", "binary_data")  # Unsupported extension

    def tearDown(self) -> None:
        """Clean up the temporary directory."""
        self.temp_dir.cleanup()

    def _write_file(self, file_path: Path, content: str) -> None:
        """Helper to write content to a file."""
        file_path.write_text(content, encoding="utf-8")

    def test_repository_scanner_exclusions_and_filters(self) -> None:
        """Verify the repository scanner includes supported files and excludes ignored paths."""
        scanned = scan_repository(self.root_path)

        # Expected files relative paths
        expected_paths = {
            "README.md",
            "config.json",
            "src/main.py",
            "src/utils/helpers.py",
        }

        found_paths = {f.relative_path for f in scanned}

        self.assertEqual(found_paths, expected_paths)

        # Assert no ignored files/directories are present
        for f in scanned:
            self.assertNotIn(".git", f.relative_path)
            self.assertNotIn("node_modules", f.relative_path)
            self.assertNotEqual(f.extension, ".png")

        # Assert line counts
        file_dict = {f.relative_path: f for f in scanned}
        self.assertEqual(file_dict["README.md"].line_count, 2)
        self.assertEqual(file_dict["src/main.py"].line_count, 6)
        self.assertEqual(file_dict["src/utils/helpers.py"].line_count, 2)

    def test_codebase_statistics_computation(self) -> None:
        """Verify codebase metrics are computed correctly."""
        scanned = scan_repository(self.root_path)
        stats = compute_statistics(scanned)

        self.assertEqual(stats.total_files, 4)
        self.assertEqual(stats.total_folders, 2)  # 'src' and 'src/utils'
        self.assertEqual(stats.total_python_files, 2)
        self.assertEqual(stats.total_markdown_files, 1)
        self.assertEqual(stats.total_lines_of_code, 11)  # 2 + 1 + 6 + 2
        
        # Verify largest file logic
        self.assertEqual(stats.largest_file, "src/main.py")
        self.assertTrue(stats.largest_file_size > 0)
        self.assertEqual(stats.average_file_size, sum(f.file_size for f in scanned) / 4)

    def test_statistics_empty_handling(self) -> None:
        """Verify statistics calculation is safe when no files are scanned."""
        stats = compute_statistics([])
        self.assertEqual(stats.total_files, 0)
        self.assertEqual(stats.total_folders, 0)
        self.assertEqual(stats.total_lines_of_code, 0)
        self.assertEqual(stats.average_file_size, 0.0)

    def test_recursive_tree_generator_json_and_text(self) -> None:
        """Verify nested recursive directory tree generation and string rendering."""
        scanned = scan_repository(self.root_path)
        tree = generate_recursive_tree(scanned)

        # Verify root directories and files
        self.assertIn("README.md", tree)
        self.assertIn("config.json", tree)
        self.assertIn("src", tree)

        # Verify nesting details
        self.assertEqual(tree["README.md"]["type"], "file")
        self.assertEqual(tree["src"]["type"], "directory")
        self.assertIn("main.py", tree["src"]["children"])
        self.assertIn("utils", tree["src"]["children"])
        self.assertEqual(tree["src"]["children"]["utils"]["children"]["helpers.py"]["type"], "file")

        # Verify text representation lines
        text_lines = render_tree_to_text(tree)
        text_content = "\n".join(text_lines)

        # Check directories are printed with slashes and indentation is preserved
        self.assertIn("📁 src/", text_content)
        self.assertIn("    📁 utils/", text_content)
        self.assertIn("        🐍 helpers.py", text_content)
        self.assertIn("📝 README.md", text_content)

    def test_github_url_validation_pass_fail(self) -> None:
        """Verify host and segment validation checks in parse_github_url."""
        # Valid URLs
        valid = "https://github.com/pallets/click"
        parsed = parse_github_url(valid)
        self.assertEqual(parsed["owner"], "pallets")
        self.assertEqual(parsed["repository"], "click")
        self.assertEqual(parsed["clean_url"], "https://github.com/pallets/click")

        # Invalid host name injection attempt
        with self.assertRaises(GitHubURLError):
            parse_github_url("https://notgithub.com/pallets/click")

        # Extra path component check
        with self.assertRaises(GitHubURLError):
            parse_github_url("https://github.com/pallets/click/tree/main")


if __name__ == "__main__":
    unittest.main()
