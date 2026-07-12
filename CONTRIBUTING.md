# Contributing to AI Codebase Assistant

Thank you for your interest in contributing! We welcome bug reports, feature requests, documentation enhancements, and code contributions.

Please follow these guidelines to ensure a smooth collaboration process.

---

## 🛠️ Local Development Setup

### 1. Prerequisites
- Python 3.11+
- Git

### 2. Setup Instructions
```bash
# Clone the repository
git clone https://github.com/<your-username>/AI-Codebase-Assistant.git
cd AI-Codebase-Assistant

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install package dependencies
pip install -r requirements.txt
```

### 3. Setting Up Environment Variables
Create a local `.env` file from the template:
```bash
cp .env.example .env
```
Ensure you add a valid `GEMINI_API_KEY` for AI tutorial generation.

---

## 🧪 Running Tests & Quality Checks

Before committing code, make sure all tests pass and your syntax compiles.

### Run Unit Tests
We use Python's built-in `unittest` module. Tests reside in the `tests/` directory:
```bash
python -m unittest discover -s tests
```

### Run Compile Checks
Verify there are no syntax or compile-time failures:
```bash
python -m py_compile app.py config.py backend/repository_tree.py external/pocketflow.py frontend/*.py services/*.py utils/*.py tests/*.py
```

---

## 🔀 Contribution Workflow

1. **Fork the Repository** on GitHub.
2. **Create a Feature Branch** from `main`:
   ```bash
   git checkout -b feature/your-awesome-feature
   ```
3. **Commit your Changes** with descriptive messages conforming to standard semantic formats (e.g. `feat: add local RAG integration`, `fix: sanitize path segments`).
4. **Push to your Fork**:
   ```bash
   git push origin feature/your-awesome-feature
   ```
5. **Open a Pull Request** targeting the `main` branch.

---

## 📋 coding Standards & Code Style

To maintain code quality, contributions must adhere to the following:
* **PEP8 Compliance:** Follow standard Python spacing, naming conventions, and code formatting rules.
* **Type Hints:** All new functions and classes must include Python type annotations.
* **Docstrings:** Standard modules, classes, and methods should contain comprehensive Google-style docstrings explaining arguments and return values.
* **No Hardcoded Secrets:** Never commit API keys or paths. Use `.env` and `config.py` overrides.
