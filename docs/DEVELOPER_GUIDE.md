# Developer Setup & Contribution Guide

This guide describes how to run, modify, test, and contribute to the AI Codebase Assistant.

---

## 🛠️ Local Environment Setup

### 1. Requirements
* Python 3.12+
* Git installed locally

### 2. Sandbox Setup
Run the following commands in your terminal:
```powershell
# Clone the repository
git clone https://github.com/your-username/AI-Codebase-Assistant.git
cd AI-Codebase-Assistant

# Initialize virtual environment
python -m venv .venv

# Activate the virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install package dependencies
pip install -r requirements.txt

# Create your local environment configuration
copy .env.example .env
```

---

## 🧪 Running Unit Tests

We use Python's built-in `unittest` module to verify the analysis pipeline and caching behaviors.

### Run all tests:
```powershell
.venv\Scripts\python.exe -m unittest discover -s tests
```

---

## 🤝 Code Standards

* **PEP8 Compliance:** Ensure code satisfies standard formatting practices. Keep lines under 100 characters where possible.
* **Type Hints:** Use explicit type annotations for public parameters and return interfaces.
* **Docstrings:** All classes, modules, and functions must contain clear, descriptive docstrings.
* **SOLID Compliance:** Keep modules single-focused. E.g. avoid mixing file-scanners with UI rendering hooks.
