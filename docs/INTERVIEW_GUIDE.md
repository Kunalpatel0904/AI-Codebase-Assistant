# Technical Interview cheat sheet

This sheet summarizes the core architecture, rate-limit mitigations, and design trade-offs of the AI Codebase Assistant for software engineering interviews.

---

## ⚡ Technical Highlights

### 1. Gemini API Quota Management
* **The Problem:** The Gemini API Free Tier has a strict quota (15 RPM, and on some keys, 20 requests per day), causing default sequential scanners to fail with HTTP 429 errors.
* **The Solution:**
  * Consolidates file mapping by grouping summaries into batches of **30 files per API call**.
  * Consolidates documentation compilation by compiling all 6 chapters in **exactly 1 structured JSON call** (using standard schemas).
  * Reduced API queries for average repositories from **40+ requests down to under 5**.

### 2. Disk Prompt Caching Layer
* Implements a local file cache (`.cache/gemini_cache.json`) mapping SHA-256 hashes of system instructions and prompts.
* Repeated codebase lookups resolve immediately, consuming **0 API quota**.

### 3. Safe Workspace Management
* Executes shallow clones (`depth=1`) via GitPython to minimize disk consumption.
* Wraps pipelines in `try-finally` blocks to guarantee cloned directories are recursively deleted.
* Force-clears read-only flags on Windows/Linux to prevent directory cleanup lockouts.

---

## 🏗️ Architectural Trade-Offs

### 1. Context stuffing vs RAG
* **RAG:** Good for interactive chats and Q&A over massive codebases.
* **Context Stuffing:** We clone the codebase, scan all files, and package them directly into Gemini's large context window (which handles 1M+ tokens).
* **Trade-Off:** Context stuffing is significantly simpler, requires zero vector database infrastructure, and ensures 100% codebase visibility for writing complete multi-chapter manuals, rather than retrieving isolated code fragments.

### 2. Shallow cloning vs Git API crawling
* **API Scrapers:** Avoid cloning to disk but exhaust GitHub REST API tokens rapidly (60 requests limit).
* **Shallow Clones:** Clones files directly to disk in 3 seconds. It uses local scanners to read all files in a single pass, avoiding GitHub REST API rate limits completely.
