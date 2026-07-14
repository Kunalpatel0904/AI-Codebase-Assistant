# Application User Guide

This guide provides visual, step-by-step instructions for operating the AI Codebase Assistant.

---

## 🚀 Running Repository Analysis

### Step 1: Input URL
* Open the application in your browser (e.g. `http://localhost:8501`).
* Enter a valid GitHub repository URL in the text input box.
  * *Example:* `https://github.com/pytest-dev/iniconfig`

### Step 2: Trigger Scan
* Click **🚀 Analyze Repository**.
* The loading spinner indicates clone, scanning, statistics compiling, and chapter writing phases.
* Average pipelines compile in under **20 seconds** (large projects might take up to a minute).

---

## 📊 Navigating the Dashboard & Statistics

Upon successful generation, the interface renders two main panels:

1. **Repository Dashboard:**
   * Star counts, Fork counts, primary coding language, and License metadata card grid.
2. **Codebase Statistics:**
   * Renders computed metrics showing file counts, folders, lines of code, average size, and the largest file metadata.
3. **Repository Structure Tree:**
   * Expanding the code tree visualizes recursive repository files and subdirectories.

---

## 📚 Reading and Downloading Chapters

### Sidebar Navigation
* Select a chapter in the sidebar **Chapters** radio buttons list.
* The main content area updates automatically to render the Markdown text.
* Use the **⬅️ Previous** and **Next ➡️** navigation buttons below the text block to flip chapters sequentially.

### Document Exports
* **Single Chapter:** Click **⬇️ Download This Chapter** below the reader container to save the active chapter as a `.md` file.
* **Full Handbook:** In the sidebar or main header downloads card, click **⬇️ Download Documentation ZIP** to save all 6 chapters along with an `index.md` list file as a unified ZIP archive.
