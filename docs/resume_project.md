# Resume Project Card Guide

Inject this project summary card directly into your software engineering or AI engineering resume.

---

## 💼 Professional Experience / Personal Projects Section

### **AI Codebase Assistant | Python, Streamlit, Google Gemini, GitPython, Docker**
* **AI Documentation Engine:** Designed and engineered a custom codebase analysis engine utilizing Google Gemini to analyze cloned Git repositories, generating structured 6-chapter Markdown guides headlessly.
* **LLM API Request Optimization:** Engineered a prompt grouping caching layer (SHA-256 hash-based local database) and consolidated chapter generation into a single structured JSON schema call, reducing total Gemini API requests by **72.7% to 100%** (resolving HTTP 429 quota exhaustion).
* **Cross-Platform Git Cloning:** Implemented shallow repository clones (`depth=1`) via GitPython and recursive force-cleanup handlers (resolving Windows read-only workspace lockouts), enabling containerized deployments on Docker, Render, and Streamlit Community Cloud.

---

## 🎯 ATS Keywords
`Python`, `Streamlit`, `Google Gemini API`, `LLM Prompt Optimization`, `GitPython`, `Docker`, `Continuous Integration (CI/CD)`, `GitHub Actions`, `API Rate-Limit Mitigations`, `JSON Structured Output`, `SHA-256 Caching`, `Subprocess Sandbox`, `Software Architecture`.

---

## 🏆 Key Accomplishments to Showcase
1. **API Call Reductions:** Previous implementation made over 40 API requests for standard codebases. The optimized version completes the entire analysis in under **5 API calls**.
2. **Robustness Under Failure:** Handles connection dropouts, missing credentials, and private repositories gracefully with fail-safe mock documentation architectures.
