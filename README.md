# 🤖 AI Codebase Assistant

Analyze public GitHub repositories and generate AI-powered tutorials using PocketFlow and Google Gemini.

---

## ✨ Features

| Feature                    | Status |
| -------------------------- | ------ |
| Analyze GitHub Repository  | ✅      |
| Repository Dashboard       | ✅      |
| PocketFlow Integration     | ✅      |
| AI Tutorial Generation     | ✅      |
| Markdown Tutorial Viewer   | ✅      |
| Download Chapter           | ✅      |
| Download Tutorial ZIP      | ✅      |
| Session State (no reruns)  | ✅      |
| Structured Logging         | ✅      |
| Error Handling             | ✅      |
| Local Folder Analysis      | 🔮 V2  |
| ZIP Upload                 | 🔮 V2  |
| PDF Export                 | 🔮 V2  |
| AI Chat / RAG              | 🔮 V2  |
| Multiple LLM Providers     | 🔮 V2  |

---

## 🛠️ Tech Stack

- **Python** 3.14
- **Streamlit** — UI framework
- **PocketFlow** — Tutorial generation engine
- **Google Gemini** — AI language model
- **GitHub REST API** — Repository metadata
- **Requests** — HTTP client

---

## 📁 Project Structure

```
AI-Codebase-Assistant/
├── app.py                      # Entry point
├── config.py                   # Central configuration
├── requirements.txt            # Dependencies
├── .env.example                # Environment template
│
├── services/                   # Business logic
│   ├── github_service.py       # GitHub API + URL parsing
│   ├── analysis_service.py     # Analysis orchestration
│   ├── tutorial_service.py     # Tutorial generation + reading
│   ├── download_service.py     # Downloads + ZIP
│   ├── local_service.py        # Local folder logic (V2)
│   ├── zip_service.py          # ZIP uploads logic (V2)
│   ├── pdf_service.py          # PDF export logic (V2)
│   ├── chat_service.py         # AI Q&A Chat logic (V2)
│   └── tree_service.py         # Directory tree fetcher (V2)
│
├── frontend/                   # Streamlit UI
│   ├── home.py                 # Page orchestrator
│   ├── sidebar.py              # Sidebar navigation
│   ├── dashboard.py            # Repository dashboard
│   ├── tutorial.py             # Tutorial viewer
│   ├── downloads.py            # Download section
│   ├── components.py           # Shared UI components
│   └── state.py                # Session state management
│
├── backend/                    # Legacy wrappers / utilities
│   └── repository_tree.py      # Folder structure printer (V2)
│
├── external/                   # Third-party integrations
│   └── pocketflow.py           # PocketFlow subprocess wrapper
│
├── utils/                      # Shared utilities
│   ├── logger.py               # Rotating logger
│   └── exceptions.py           # Custom exception hierarchy
│
└── logs/                       # Runtime logs (gitignored)
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- [PocketFlow Tutorial project](https://github.com/The-Pocket/PocketFlow-Tutorial-Codebase-Knowledge) installed locally
- Google Gemini API key

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/AI-Codebase-Assistant.git
cd AI-Codebase-Assistant

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your API key and PocketFlow path
```

### Run

```bash
streamlit run app.py
```

---

## ⚙️ Configuration

All settings are managed via environment variables (`.env` file):

| Variable             | Description                          | Default                                                    |
| -------------------- | ------------------------------------ | ---------------------------------------------------------- |
| `GEMINI_API_KEY`     | Google Gemini API key                | —                                                          |
| `POCKETFLOW_PATH`    | PocketFlow project directory         | `D:\AI_Map\PocketFlow-Tutorial-Codebase-Knowledge-main`    |
| `DEFAULT_TIMEOUT`    | HTTP request timeout (seconds)       | `30`                                                       |
| `POCKETFLOW_TIMEOUT` | PocketFlow execution timeout (secs)  | `300`                                                      |

---

## 📋 Usage

1. Open the app in your browser (`http://localhost:8501`)
2. Paste a **public GitHub repository URL**
3. Click **🚀 Analyze Repository**
4. Browse the generated tutorial using the sidebar chapter list
5. Download individual chapters or the complete ZIP

---

## 🔮 Version 2 Roadmap

- 📂 Local folder analysis
- 📦 ZIP file upload
- 📄 PDF export
- 🤖 AI Chat with RAG
- 🔍 Repository tree view and search
- 🔀 Multiple LLM providers

---

## 📄 License

This project is for educational and personal use.
