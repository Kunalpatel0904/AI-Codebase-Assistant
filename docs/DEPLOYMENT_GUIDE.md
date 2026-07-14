# Production Deployment Guide

This guide describes how to deploy the AI Codebase Assistant application on various cloud platforms and containers.

---

## ☁️ Streamlit Community Cloud

Streamlit Community Cloud is the simplest way to host the application.

### Setup Instructions
1. Fork this repository on GitHub.
2. Sign in to [Streamlit Share](https://share.streamlit.io/).
3. Click **New app** and select your repository, branch (`main` or `feature/version-2`), and main file path (`app.py`).
4. Click **Advanced settings...** and add your Google Gemini API Key under Secrets:
   ```toml
   GEMINI_API_KEY = "AIzaSy..."
   # Optional:
   GITHUB_TOKEN = "ghp_..."
   ```
5. Click **Deploy**. Streamlit will automatically compile from [`requirements.txt`](file:///d:/AI_Map/AI-Codebase-Assistant/requirements.txt) and deploy.

---

## 🐳 Container Deployment (Docker)

A standard Docker container configuration is packaged in the root of the repository.

### Dockerfile
* Matches official Python slim bases: `python:3.12-slim`
* Installs `git` system packages (required for shallow cloning).
* Runs headlessly on port `8501`.

### Build & Run Commands
```bash
# Build the Docker image
docker build -t ai-codebase-assistant .

# Run the container (injecting credentials)
docker run -p 8501:8501 --env GEMINI_API_KEY="your_api_key_here" ai-codebase-assistant
```

---

## 🌐 Render or Heroku

### Configuration Parameters
* **Build Command:** `pip install -r requirements.txt`
* **Start Command:** `streamlit run app.py`
* **Exposed Port:** `8501`
* **Environment Variables:** Define `GEMINI_API_KEY` in the dashboard settings panel.
