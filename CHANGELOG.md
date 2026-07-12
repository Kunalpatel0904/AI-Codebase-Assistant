# Changelog

All notable changes to the **AI Codebase Assistant** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-07-12

### Added
- **MIT License:** Added `LICENSE` file for standard open-source compliance.
- **Docker Integration:** Added `Dockerfile` to automatically package the application with self-contained `PocketFlow` cloning, ensuring out-of-the-box cloud portability.
- **Unit Test Suite:** Created `tests/test_github_service.py` to cover GitHub URL parsing and host validation.
- **Git Tracking:** Preserved empty directories (`tests/`, `ai/`, `rag/`) via `.gitkeep` files.
- **CI Pipeline:** Added GitHub Actions configuration `.github/workflows/ci.yml` for automatic compile checks and unittest execution on push/PRs.

### Changed
- **Secure URL Parsing:** Upgraded `parse_github_url` to strictly validate `github.com` and subdomains (preventing substring bypasses like `notgithub.com`) and enforce exactly 2 path segments (`owner/repository`).
- **Sanitization Boundary:** Pass a clean reconstructed canonical URL (`clean_url`) to the PocketFlow subprocess in `analysis_service.py` to prevent query parameters, fragments, or trailers from reaching execution.
- **Portability:** Configured `POCKETFLOW_PATH` fallback in `config.py` using relative directory resolve `PROJECT_ROOT.parent` instead of a hardcoded absolute Windows path.
- **Dependencies:** Added `fpdf2` (PDF generator) to `requirements.txt`.
- **Documentation:** Mapped realistic files and V2 previews in the project structure diagram in `README.md`.
