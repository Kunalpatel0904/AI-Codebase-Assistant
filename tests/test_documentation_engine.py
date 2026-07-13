"""
Unit tests for the custom Gemini AI Documentation Engine and optimization layers.
"""

import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

from services import summary_service, chapter_service, markdown_service
from services.statistics_service import CodebaseStatistics
from utils.exceptions import GeminiAPIError
from utils.gemini_client import (
    generate_content_with_retry,
    get_cached_response,
    save_cached_response,
    parse_retry_delay,
    reset_stats,
    get_api_call_count,
)

class TestDocumentationEngine(unittest.TestCase):

    def setUp(self) -> None:
        """Mock time.sleep and clear/initialize cache environment before each test."""
        self.sleep_patcher = patch("time.sleep")
        self.mock_sleep = self.sleep_patcher.start()
        reset_stats()
        # Direct prompt cache to a temp location for testing
        self.cache_dir = tempfile.TemporaryDirectory()
        self.temp_cache_file = Path(self.cache_dir.name) / "temp_cache.json"
        self.cache_path_patcher = patch("utils.gemini_client.CACHE_FILE", self.temp_cache_file)
        self.cache_path_patcher.start()

    def tearDown(self) -> None:
        """Cleanup mocks and cache environment after each test."""
        self.sleep_patcher.stop()
        self.cache_path_patcher.stop()
        self.cache_dir.cleanup()

    def test_parse_retry_delay_formats(self) -> None:
        """Verify regex parsing of the retryDelay from various format structures."""
        # Single quote dictionary format
        self.assertEqual(parse_retry_delay("{'retryDelay': '36s'}"), 36.0)
        # Double quote JSON format
        self.assertEqual(parse_retry_delay('{"retryDelay": "11.5s"}'), 11.5)
        # Fallback default value when key isn't matched
        self.assertEqual(parse_retry_delay("other random API error text"), 5.0)

    def test_caching_mechanism(self) -> None:
        """Verify get_cached_response and save_cached_response read and write correctly."""
        prompt = "Hello AI"
        sys_inst = "Translate to code"
        
        # Initial lookup must return None
        self.assertIsNone(get_cached_response(prompt, sys_inst))
        
        # Save a mock response
        save_cached_response(prompt, sys_inst, "Cached Output")
        
        # Subsequent lookup must return the cached text
        self.assertEqual(get_cached_response(prompt, sys_inst), "Cached Output")

    @patch("google.genai.Client")
    def test_retry_on_429_backoff(self, mock_client_class) -> None:
        """Verify generate_content_with_retry retries on 429 and applies backoff."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Setup mock to fail with 429 on first try, then return success text
        mock_response = MagicMock()
        mock_response.text = "Success on second attempt!"
        
        rate_limit_error = Exception("API error details: {'error': {'code': 429, 'retryDelay': '2s'}}")
        mock_client.models.generate_content.side_effect = [rate_limit_error, mock_response]
        
        config = {"system_instruction": "Be helpful"}
        result = generate_content_with_retry(
            client=mock_client,
            model="gemini-2.5-flash",
            contents="Hello",
            config=config,
            max_retries=2
        )
        
        self.assertEqual(result, "Success on second attempt!")
        self.assertEqual(mock_client.models.generate_content.call_count, 2)
        # Verify sleep was invoked exactly once with parsed delay
        self.mock_sleep.assert_called_once_with(2.0)

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
        
        mock_response_chunk = MagicMock()
        mock_response_chunk.text = "Chunk summary."
        mock_client.models.generate_content.return_value = mock_response_chunk

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "large.py"
            large_content = "x" * 20000
            file_path.write_text(large_content, encoding="utf-8")

            summary = summary_service.summarize_file(
                file_path=file_path,
                relative_path="large.py",
                api_key="fake_api_key",
                model_name="gemini-2.5-flash",
            )

            self.assertEqual(summary, "Chunk summary.")
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

        self.assertEqual(len(folders), 2)
        self.assertIn("src/api", folders)
        self.assertIn("src/utils", folders)
        self.assertEqual(mock_client.models.generate_content.call_count, 1)

    @patch("google.genai.Client")
    def test_chapter_service_generates_six_chapters(self, mock_client_class) -> None:
        """Verify chapter_service compiles all 6 chapters in a single batched structured JSON call."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "01_repository_summary.md": "# Repository Summary\nSummary info",
            "02_architecture.md": "# Architecture\nArchitecture info",
            "03_folder_structure.md": "# Folder Structure\nStructure info",
            "04_core_modules.md": "# Core Modules\nCore info",
            "05_api.md": "# API Documentation\nAPI info",
            "06_utilities.md": "# Utilities\nUtilities info"
        })
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
        self.assertEqual(chapters["01_repository_summary.md"], "# Repository Summary\nSummary info")
        self.assertEqual(chapters["02_architecture.md"], "# Architecture\nArchitecture info")
        self.assertEqual(chapters["03_folder_structure.md"], "# Folder Structure\nStructure info")
        self.assertEqual(chapters["04_core_modules.md"], "# Core Modules\nCore info")
        self.assertEqual(chapters["05_api.md"], "# API Documentation\nAPI info")
        self.assertEqual(chapters["06_utilities.md"], "# Utilities\nUtilities info")
        
        # Verify it was optimized into exactly 1 call
        self.assertEqual(mock_client.models.generate_content.call_count, 1)

    def test_markdown_service_saves_and_indexes(self) -> None:
        """Verify markdown_service writes chapters and compiles index.md correctly."""
        chapters = {
            "01_repository_summary.md": "# Repository Summary",
            "02_architecture.md": "# Architecture Overview",
        }

        with patch("services.markdown_service.Path") as mock_path_class:
            mock_output_dir = MagicMock()
            mock_path_class.return_value = mock_output_dir
            mock_output_dir.__truediv__.return_value = mock_output_dir

            markdown_service.save_chapters_to_disk("my-repo", chapters)
            mock_output_dir.mkdir.assert_called_once()
