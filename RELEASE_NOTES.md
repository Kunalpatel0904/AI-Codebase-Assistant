# Release Notes — Version 1.0.0 (Production Ready)

Welcome to the official **v1.0.0** release of the **AI Codebase Assistant**! This release marks our transition to a fully production-ready, secure, and portable platform for analyzing public GitHub repositories and generating AI-powered markdown tutorials.

---

## 🌟 Key Highlights

### 🔒 Upgraded URL Parsing & Security Sanitization
- Rebuilt host/domain validation to ensure only official GitHub repositories (`github.com` or `*.github.com`) can be analyzed, preventing security bypasses on malicious domains.
- Implemented **Sanitization at Boundary**: Incoming repository URLs are parsed into clean components and reconstructed into canonical URLs before being passed to external API calls or shell subprocesses, mitigating parameter injection risks.

### 📦 Self-Contained Docker Packaging
- Added a production `Dockerfile` that packages the application, sets up Streamlit for containerized deployment, and clones the `PocketFlow` engine dependency during the image build phase.
- Deploying the assistant to platforms like Render, GCP Cloud Run, or AWS ECS is now a zero-configuration experience.

### 🧪 Complete Testing & Automation
- Integrated a zero-dependency standard-library unit test suite testing URL validation across 20+ edge cases.
- Created a GitHub Actions CI pipeline running compilation checks and unit tests automatically on every code contribution.

---

## 🚀 Quickstart

### Running locally
```bash
# Clone the repository and navigate inside
git clone https://github.com/<your-username>/AI-Codebase-Assistant.git
cd AI-Codebase-Assistant

# Copy and edit the environment template
copy .env.example .env

# Install requirements
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Running with Docker
```bash
# Build the self-contained container
docker build -t ai-codebase-assistant .

# Run the container (pass your environment variables)
docker run -p 8501:8501 --env GEMINI_API_KEY="your_api_key" ai-codebase-assistant
```

---

## 🛠️ Requirements & Environment Configurations
The application requires a valid **`GEMINI_API_KEY`** (configured inside your `.env` or container environment). `GITHUB_TOKEN` is optional but highly recommended to avoid GitHub API rate limiting on public metadata checks.
