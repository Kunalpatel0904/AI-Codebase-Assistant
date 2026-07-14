# API Reference Manual

This document details the public interfaces, functions, arguments, exceptions, and data models used in the codebase.

---

## 📦 Utilities Layer

### 1. `utils.gemini_client`
Helper module coordinating rate-limit retries and prompt hashing.

#### `generate_content_with_retry(prompt: str, system_instruction: str = None, response_mime_type: str = None) -> str`
Sends a request to the Gemini API with caching and retry backoffs.
* **Arguments:**
  * `prompt` (str): Text content of the prompt query.
  * `system_instruction` (str, optional): Role instructions for the LLM.
  * `response_mime_type` (str, optional): Set to `application/json` to enforce structured responses.
* **Returns:** `str` containing the text response.
* **Raises:** `GeminiAPIError` on connection failures.

#### `reset_stats()`
Resets API call counters and cache statistics.

---

## 🛠️ Service Layer

### 1. `services.github_service`
GitHub repository scraper.

#### `parse_github_url(url: str) -> dict[str, str]`
Extracts owner and repository names from a canonical URL.
* **Arguments:** `url` (str).
* **Returns:** `dict` containing `'owner'` and `'repo'` strings.
* **Raises:** `GitHubURLError` on invalid formats.

#### `get_github_details(owner: str, repo: str) -> dict`
Queries the GitHub REST API for repository statistics.
* **Returns:** Metadata dictionary containing description, stars, forks, license, language, and update timestamps.

---

### 2. `services.github_clone_service`
Manages Git shallow clones and local workspace deletions.

#### `clone_repository(repo_url: str) -> Path`
Clones a repository into a unique temporary directory with a shallow configuration (`depth=1`).
* **Returns:** Pathlib `Path` to the workspace directory.
* **Raises:** `RepositoryCloneError`.

#### `cleanup_repository(repo_path: Path)`
Recursively deletes a directory from disk. Clears read-only flags automatically on Windows/Unix.

---

### 3. `services.repository_scanner`
Recursive text file aggregator.

#### `scan_repository(repo_path: Path) -> list[ScannedFile]`
Recursively crawls a workspace directory. Filters out binary assets and ignores folder exclusions.
* **Returns:** List of `ScannedFile` metadata objects.

---

### 4. `services.chapter_service`
Documentation engine manager.

#### `generate_chapters(repo_name: str, scanner_files: list, folder_summaries: dict) -> dict[str, str]`
Generates all 6 documentation files in a single, structured JSON API query.
* **Returns:** A dictionary mapping chapter filenames (e.g. `'02_architecture.md'`) to their compiled Markdown content.
