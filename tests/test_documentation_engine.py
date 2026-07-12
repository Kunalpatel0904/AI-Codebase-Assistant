"""
Unit tests for the custom Gemini AI Documentation Engine.
"""

import unittest
from unittest.mock import patch, MagicMock
import tempfile
from pathlib import Path

from services import summary_service, chapter_service, markdown_service
from services.statistics_service import CodebaseStatistics
from utils.exceptions import GeminiAPIError


class TestDocumentationEngine(unittest.TestCase):

    def setUp(self) -> None:
        """Mock time.sleep to run tests instantaneously without delays."""
        self.sleep_patcher = patch("time.sleep")
        self.mock_sleep = self.sleep_patcher.start()

    def tearDown(self) -> None:
        """Stop time.sleep mock."""
        self.sleep_patcher.stop()

    @patch("google.genai.Client")
    def test_summary_service_small_file(self, mock_client_class) -> None:
        """Verify summary_service calls Gemini once for normal sized files."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = "This is a small file summary."
        mock_client.models.generate_content.return_value = mock_response

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "helper.py"
            file_path.write_text("def helper(): pass", encoding="utf-8")

            summary = summary_service.summarize_file(
                file_path=file_path,
                relative_path="helper.py",
                api_key="fake_api_key",
                model_name="gemini-2.5-flash",
            )

            self.assertEqual(summary, "This is a small file summary.")
            mock_client.models.generate_content.assert_called_once()

    @patch("google.genai.Client")
    def test_summary_service_large_file_chunking(self, mock_client_class) -> None:
        """Verify summary_service splits large files into chunks and combines them."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # We need mock responses for chunk 1, chunk 2, and the combined summary
        mock_response_chunk = MagicMock()
        mock_response_chunk.text = "Chunk summary."
        mock_client.models.generate_content.return_value = mock_response_chunk

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "large.py"
            # Write more than 16,000 characters to trigger chunking
            large_content = "x" * 20000
            file_path.write_text(large_content, encoding="utf-8")

            summary = summary_service.summarize_file(
                file_path=file_path,
                relative_path="large.py",
                api_key="fake_api_key",
                model_name="gemini-2.5-flash",
            )

            self.assertEqual(summary, "Chunk summary.")
            # It should call generate_content 3 times: 2 for chunks, 1 for final summary compilation
            self.assertEqual(mock_client.models.generate_content.call_count, 3)

    @patch("google.genai.Client")
    def test_summary_service_folder_grouping(self, mock_client_class) -> None:
        """Verify folder summary groups files correctly by directories."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = "Folder summary details."
        mock_client.models.generate_content.return_value = mock_response

        file_summaries = [
            {"relative_path": "src/api/auth.py", "summary": "Auth module"},
            {"relative_path": "src/api/users.py", "summary": "Users module"},
            {"relative_path": "src/utils/logger.py", "summary": "Logger module"},
        ]

        folders = summary_service.summarize_folders(
            scanned_files_with_summaries=file_summaries,
            api_key="fake_api_key",
        )

        # Should group into 2 folders: 'src/api' and 'src/utils'
        self.assertEqual(len(folders), 2)
        self.assertIn("src/api", folders)
        self.assertIn("src/utils", folders)
        self.assertEqual(mock_client.models.generate_content.call_count, 1)

    @patch("google.genai.Client")
    def test_chapter_service_generates_six_chapters(self, mock_client_class) -> None:
        """Verify chapter_service calls Gemini to generate exactly 6 documentation files."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = "Sample markdown documentation content."
        mock_client.models.generate_content.return_value = mock_response

        stats = CodebaseStatistics(
            total_files=4,
            total_folders=2,
            total_python_files=2,
            total_markdown_files=1,
            total_lines_of_code=100,
            largest_file="main.py",
            largest_file_size=2000,
            average_file_size=500.0,
        )

        chapters = chapter_service.generate_chapters(
            repo_name="my-repo",
            details={"name": "my-repo", "owner": "user", "stars": 10},
            stats=stats,
            file_summaries=[],
            folder_summaries={},
            tree_text="tree-text",
            api_key="fake_api_key",
        )

        self.assertEqual(len(chapters), 6)
        self.assertIn("01_repository_summary.md", chapters)
        self.assertIn("02_architecture.md", chapters)
        self.assertIn("03_folder_structure.md", chapters)
        self.assertIn("04_core_modules.md", chapters)
        self.assertIn("05_api.md", chapters)
        self.assertIn("06_utilities.md", chapters)
        self.assertEqual(mock_client.models.generate_content.call_count, 6)

    def test_markdown_service_saves_and_indexes(self) -> None:
        """Verify markdown_service writes chapters and compiles index.md correctly."""
        chapters = {
            "01_repository_summary.md": "# Repository Summary",
            "02_architecture.md": "# Architecture Overview",
        }

        with patch("services.markdown_service.Path") as mock_path_class:
            mock_output_dir = MagicMock()
            mock_path_class.return_value = mock_output_dir
            
            # Mock Path("output") / repo_name structure
            mock_output_dir.__truediv__.return_value = mock_output_dir

            markdown_service.save_chapters_to_disk("my-repo", chapters)

            # Ensure directories are created
            mock_output_dir.mkdir.assert_called()
            
            # Ensure files are written (01_repository_summary.md, 02_architecture.md, and index.md)
            self.assertEqual(mock_output_dir.write_text.call_count, 3)


if __name__ == "__main__":
    unittest.main()
