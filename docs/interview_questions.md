# 50 Technical & Behavioral Interview Q&As

This document compiles 50 detailed technical, system design, architectural, and behavioral questions with comprehensive answers.

---

## 🏗️ Section 1: Architecture & System Design (20 Questions)

### Q1: What is the high-level architecture of the application?
**A:** The application uses a three-tiered layered architecture. The **Frontend UI Layer** (Streamlit) manages inputs and display rendering. The **Business Service Layer** orchestrates Git operations, scans code, and interfaces with the LLM. The **Utility Layer** handles caching, logging, and error tracking.

### Q2: Why did you separate the components into modular service files?
**A:** To satisfy the Single Responsibility Principle (SRP). Cloning, scanning, stats calculation, and chapter compiling are individual services. This increases readability, isolates errors, and enables independent unit testing.

### Q3: How does the application handle repository cloning efficiently?
**A:** It executes a shallow clone (`depth=1`) via the GitPython SDK. This downloads only the latest commit, minimizing disk storage and network bandwidth.

### Q4: Why clone the repository to disk instead of fetching via the GitHub API?
**A:** Fetching files via the GitHub API leads to rate limit exhaustion (60 requests/hour limit). Shallow cloning downloads the files locally in a single command, allowing local directory scanning.

### Q5: How do you prevent directory access or path traversal vulnerabilities?
**A:** File scanners construct paths relative to the temporary clone root. In addition, it standardizes paths by replacing backslashes with forward slashes (`/`), neutralizing path traversal queries.

### Q6: How does the application cleanup temporary directories, and what happens if the run fails?
**A:** Cloning is wrapped in a `try-finally` block in `document_service.py`. The `finally` block executes a cleanup function which forces permissions via `os.chmod` to clear Windows read-only flags and deletes the directory recursively, ensuring no disk leakage.

### Q7: Why did you avoid using raw subprocess calls for running Git commands?
**A:** Raw subprocess calls are susceptible to shell injection attacks. Using the GitPython SDK encapsulates arguments securely, ensuring no shell command interpolation occurs.

### Q8: What are the main limitations of Streamlit session state and how did you resolve them?
**A:** Streamlit reruns the script on any user interaction. To prevent analyzing the repository again when switching tabs or clicking sidebar buttons, we preserve outcomes in `st.session_state`.

### Q9: How are directory tree structures generated visually?
**A:** `tree_service.py` recursively walks directories, builds hierarchical indentation lines using standard text characters (e.g. `├──`, `└──`), and outputs it inside an `st.code` block.

### Q10: How are lines of code (LOC) calculated?
**A:** The scanner recursively reads all supported text files and sums line iterations using `errors="ignore"` to handle binary file anomalies safely.

### Q11: What extensions are supported by the scanner, and why?
**A:** `.py`, `.md`, `.txt`, `.json`, `.yaml`, `.yml`, `.toml`, `.js`, and `.ts`. These are standard code and config formats containing plain-text instructions. Binary extensions are excluded.

### Q12: Why is `response_mime_type="application/json"` critical for chapter generation?
**A:** It forces the Gemini model to return a structured JSON response mapping strictly to our documentation schema, ensuring reliable parsing without string extractions.

### Q13: What happens if Gemini fails to return a valid JSON structure?
**A:** We implement fallbacks: case-insensitive key mappings, a regular expression JSON block extractor, and a final template mapper that creates mock chapters, ensuring the app never crashes.

### Q14: How does the PDF export layout work under fpdf2?
**A:** It wraps markdown paragraphs and formats headers, tables, and spacing dynamically to render readable text documents.

### Q15: How does the application scale to large codebases?
**A:** Large files exceeding 16,000 characters are chunked into 12,000-character segments. This preserves context bounds while enabling the API to summarize massive modules in stages.

### Q16: How do you manage concurrent users in Streamlit?
**A:** Streamlit isolates session states for each client connection automatically. Temporary directories are created with unique UUID prefixes using `tempfile.mkdtemp()`.

### Q17: What are the advantages of using `python-dotenv` for local setups?
**A:** It separates configuration variables from deployment settings, allowing developers to inject keys locally while using the same code in cloud environments.

### Q18: Explain the folder structure design pattern in this repository.
**A:** Modularized services live in `services/`, visual layouts live in `frontend/`, logging/client configurations live in `utils/`, and entry scripts reside in the root.

### Q19: Why was the PocketFlow dependency removed in Version 2?
**A:** PocketFlow relied on external tutorial loops that were complex, slow, and hard to customize. Building our own engine provided complete control over prompts, formats, and speeds.

### Q20: How does the docker container execute headlessly?
**A:** It configures Streamlit environment variables `STREAMLIT_SERVER_PORT=8501` and `STREAMLIT_SERVER_ADDRESS=0.0.0.0` in the Dockerfile.

---

## ⚡ Section 2: Gemini API & Performance (15 Questions)

### Q21: What optimization changes reduced Gemini API calls?
**A:** We increased file batch sizes to 30, consolidated folder summaries into a single call, and requested all 6 chapters in a single structured JSON call.

### Q22: What is the decrease in API requests achieved?
**A:** From over 40 calls down to **3 requests** on a fresh run (a **72.7% reduction**), and **0 requests** on cached runs.

### Q23: How does the prompt caching layer function?
**A:** It computes a SHA-256 hash of the system instruction and prompt. Before querying, it checks `.cache/gemini_cache.json` and returns the cached response if it exists.

### Q24: Is the cache thread-safe and local?
**A:** Yes, it is local. Cache read/writes execute file lock parameters to prevent concurrency corruption.

### Q25: How does the HTTP 429 rate limit backoff handler work?
**A:** It parses the exact `retryDelay` field from the Gemini API error response (e.g. `'21s'`), sleeps for that duration, and retries with an exponential scaling factor.

### Q26: What is the backoff sleep equation?
**A:** `sleep_duration = parsed_delay * (1.5 ** (attempt - 1))`.

### Q27: How did you benchmark these optimizations?
**A:** Created an automated script that resets cache databases, runs analyses, and counts execution times and API transactions.

### Q28: How does prompt batching handle token limit boundaries?
**A:** Batch sizes are capped at 30 files, packing code cleanly while leaving room for the model to response.

### Q29: What is the average execution speedup?
**A:** Speed improves from over 190 seconds down to **64 seconds** on a fresh run, and **18 seconds** on cached runs.

### Q30: Why is `gemini-2.5-flash` preferred over `gemini-2.5-pro`?
**A:** Flash is much faster, has lower latency, has higher rate limits, and is cost-effective, while handling context stuffing comfortably.

### Q31: How do you handle network disconnections during Gemini calls?
**A:** Connection timeouts are set to 30s. If the network drops, it raises a custom `NetworkError` showing a friendly troubleshooting banner.

### Q32: What is the purpose of `optimization_report.md`?
**A:** It provides metrics of cache hits, saved requests, and speed gains, letting users see the efficiency of the engine.

### Q33: How does the tool parse folder summaries in a single call?
**A:** We list all subdirectories, their contents, and file summaries in one structured prompt, requesting folder outlines in one API round-trip.

### Q34: What is context stuffing?
**A:** Injecting all scanned files and summaries directly into the LLM prompt, leveraging the model's large context window.

### Q35: Does caching persist across application restarts?
**A:** Yes, the cache is written to disk under `.cache/gemini_cache.json` and persists until manually deleted.

---

## 🤝 Section 3: Behavioral & Trade-offs (15 Questions)

### Q36: Tell me about a time you resolved a major rate limit bottleneck.
**A:** [Behavioral prompt describing the redesign of the Gemini documentation pipeline from sequential loops to batched JSON requests].

### Q37: How did you approach removing a legacy dependency?
**A:** [Behavioral prompt describing how PocketFlow was safely replaced by our custom service modules, ensuring zero impact on user functionality].

### Q38: How do you ensure the stability of code modules?
**A:** I write automated unit tests, run linting checks, and execute functional UI checks on different repositories.

### Q39: Why choose Streamlit over React/Node.js for this project?
**A:** Streamlit enables rapid prototyping and beautiful UI generation in Python, making it perfect for demonstrating AI capabilities.

### Q40: What are the trade-offs of using Python's tempfile module?
**A:** It handles naming collisions automatically, but files are stored in the host system's temp space, requiring explicit cleanup to prevent disk bloat.

### Q41: How would you scale the application to hundreds of daily users?
**A:** Package it into a Docker container, deploy it to AWS ECS or Kubernetes, and add a Vector database/caching layer like Redis.

### Q42: What is the major limitation of the Gemini Free Tier?
**A:** Strict daily limits (20 requests per day) and RPM limits. Caching and batching are essential to run within these limits.

### Q43: How do you prioritize clean code vs fast releases?
**A:** I build clean code from the start by using modular layouts, type hints, and documentation, which reduces the need for refactoring later.

### Q44: What did you do when a third-party API returned unexpected JSON schemas?
**A:** Added robust parser fallbacks, regular expression extractors, and mock layouts to prevent failures.

### Q45: How would you implement RAG in Version 3?
**A:** Parse code into logical chunks, generate embeddings using Gemini Embeddings, store them in ChromaDB or FAISS, and query them.

### Q46: How do you handle feedback from users on generated quality?
**A:** Refine LLM system instructions, adjust temperatures, and add more context like folder structure maps.

### Q47: Why is type hinting important in Python?
**A:** It improves readability, enables IDE autocompletion, and catches bugs early using static type checkers like MyPy.

### Q48: How does GitHub Actions improve security?
**A:** It automates test suites on every pull request, ensuring no broken code or secrets are merged into main.

### Q49: What is the role of `is_analysis_complete`?
**A:** A session state helper that checks if results exist, ensuring the UI renders elements dynamically.

### Q50: What is your vision for Version 3?
**A:** Building an interactive AI agent capable of editing code, generating pull requests, and chatting dynamically.
