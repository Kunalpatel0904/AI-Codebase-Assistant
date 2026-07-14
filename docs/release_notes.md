# Release Notes — Version 2.0.0

We are excited to announce the production-ready release of Version 2.0.0.

---

## 🚀 Key Improvements in Version 2.0.0

### 1. Architectural Independence (PocketFlow Removal)
* Removed the dependency on the third-party PocketFlow engine.
* Replaced subprocess orchestrators with our own custom analysis pipeline.

### 2. Gemini API Call Optimization
* Implemented batching maps for file summaries (30 files/request) and folder summaries (1 request).
* Consolidated chapter generation into exactly 1 structured JSON response call, dropping total requests for standard repositories from **40+ down to under 5**.

### 3. Smart Prompt Caching
* Local disk cache hashes prompt parameters. Re-scans of identical codebases load instantly (takes under 10 seconds) and consume **0 API quota**.

### 4. Exponential Backoff Retries
* Captures HTTP 429 errors and waits for the exact time requested by the API before retrying, preventing server-side resource exhaustion blockages.

### 5. Leak-Free Workspaces
* Executes shallow clones (`depth=1`) via GitPython and force-deletes folders on exit, ensuring no temporary files persist on disk.
