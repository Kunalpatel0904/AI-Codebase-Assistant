"""
Prompt service — Centralizes all system instructions and prompt templates for Google Gemini.
"""

from typing import Any


def get_file_summary_system_instruction() -> str:
    """Return the system instruction for generating a file summary."""
    return (
        "You are an expert code analyst. Your job is to analyze the provided source code "
        "and write a concise, high-level summary of what the file does, its public interfaces "
        "(classes/functions), and its dependencies."
    )


def get_file_summary_prompt(file_path: str, content: str) -> str:
    """Generate the prompt for summarizing an individual file's source code."""
    return f"""\
Analyze the file '{file_path}' and provide a clean, bulleted summary of its functionality and roles.

Source Code:
```
{content}
```
"""


def get_folder_summary_system_instruction() -> str:
    """Return the system instruction for generating a folder summary."""
    return (
        "You are an expert software architect. Analyze the summaries of files contained in "
        "a specific folder, and write a high-level explanation of the folder's primary responsibility "
        "in the system."
    )


def get_folder_summary_prompt(folder_name: str, file_summaries: list[dict[str, str]]) -> str:
    """Generate the prompt for summarizing a folder containing multiple files."""
    summaries_text = ""
    for item in file_summaries:
        summaries_text += f"- File: {item['relative_path']}\n  Summary: {item['summary']}\n\n"

    return f"""\
Analyze the folder '{folder_name}' based on the summaries of the files it contains:

File Summaries:
{summaries_text}

Write a concise summary explaining:
1. The primary responsibility of this directory.
2. How the modules inside work together.
"""


def get_chapter_system_instruction() -> str:
    """Return the system instruction for compiling tutorial chapters."""
    return (
        "You are a technical writer and senior software architect compiling professional documentation "
        "for a software codebase. Write clear, markdown-formatted documentation based on code metadata, "
        "statistics, and module summaries."
    )


def get_repository_summary_prompt(repo_name: str, details: dict[str, Any], stats: Any, folder_summaries: dict[str, str]) -> str:
    """Generate the prompt for Chapter 1: Repository Summary."""
    folder_text = "\n".join(f"- Folder: {k}\n  Summary: {v}" for k, v in folder_summaries.items())
    
    return f"""\
Compile Chapter 1: Repository Summary for '{repo_name}'.
Format output in clean Markdown.

Repository Details:
- Name: {details.get('name', repo_name)}
- Owner: {details.get('owner', 'Unknown')}
- Description: {details.get('description', 'N/A')}
- Primary Language: {details.get('language', 'Unknown')}
- Stars: {details.get('stars', 0)}
- License: {details.get('license', 'None')}

Codebase Statistics:
- Total Files: {stats.total_files}
- Total Folders: {stats.total_folders}
- Lines of Code: {stats.total_lines_of_code}

Folder Structure Summaries:
{folder_text}

Requirements:
- Summarize the repository's purpose, scope, and metrics.
- List key features based on folder responsibilities.
- Keep the tone professional, structured, and informative.
"""


def get_architecture_prompt(repo_name: str, folder_summaries: dict[str, str]) -> str:
    """Generate the prompt for Chapter 2: Architecture."""
    folder_text = "\n".join(f"- Folder: {k}\n  Summary: {v}" for k, v in folder_summaries.items())

    return f"""\
Compile Chapter 2: Architecture Overview for '{repo_name}'.
Format output in clean Markdown.

Here is the functional map of the codebase directories:
{folder_text}

Requirements:
- Describe the high-level architecture and subsystem relationships.
- Detail the data flow through the application layers (e.g. Frontend -> Services -> Backend/External).
- Provide architectural design choices (e.g., MVC, Layered architecture, separation of concerns).
"""


def get_folder_structure_prompt(repo_name: str, tree_text: str, folder_summaries: dict[str, str]) -> str:
    """Generate the prompt for Chapter 3: Folder Structure."""
    folder_text = "\n".join(f"- Folder: {k}\n  Summary: {v}" for k, v in folder_summaries.items())

    return f"""\
Compile Chapter 3: Folder Structure for '{repo_name}'.
Format output in clean Markdown.

Codebase Directory Tree:
```text
{tree_text}
```

Folder Descriptions:
{folder_text}

Requirements:
- Embed and review the codebase directory tree.
- Explain what each folder is responsible for.
- Note any standard structural patterns (e.g. config, tests, assets, utilities).
"""


def get_core_modules_prompt(repo_name: str, file_summaries: list[dict[str, str]]) -> str:
    """Generate the prompt for Chapter 4: Core Modules."""
    file_text = "\n".join(f"- File: {f['relative_path']}\n  Summary: {f['summary']}" for f in file_summaries if f["relative_path"].endswith((".py", ".js", ".ts")))

    return f"""\
Compile Chapter 4: Core Modules for '{repo_name}'.
Format output in clean Markdown.

Code File Summaries:
{file_text}

Requirements:
- Detail the core logic files, classes, and main algorithms.
- Explain the logic separation and functional entry points.
- Illustrate relationships between core modules.
"""


def get_api_prompt(repo_name: str, file_summaries: list[dict[str, str]]) -> str:
    """Generate the prompt for Chapter 5: API Documentation."""
    # Filter for frontend orchestrators, HTTP endpoints, routing, API wrappers
    api_text = "\n".join(
        f"- File: {f['relative_path']}\n  Summary: {f['summary']}" 
        for f in file_summaries 
        if "service" in f["relative_path"] or "api" in f["relative_path"] or "route" in f["relative_path"] or "home" in f["relative_path"]
    )

    return f"""\
Compile Chapter 5: API / Public Interface Documentation for '{repo_name}'.
Format output in clean Markdown.

Subsystem Interface Summaries:
{api_text}

Requirements:
- Document public APIs, orchestrators, endpoints, and interface methods.
- Describe parameter types, returns, custom exceptions, and error boundaries.
"""


def get_utilities_prompt(repo_name: str, file_summaries: list[dict[str, str]]) -> str:
    """Generate the prompt for Chapter 6: Utilities and Configuration."""
    # Filter for utils, config, setup, logger files
    utils_text = "\n".join(
        f"- File: {f['relative_path']}\n  Summary: {f['summary']}"
        for f in file_summaries
        if "util" in f["relative_path"] or "config" in f["relative_path"] or "logger" in f["relative_path"] or "exception" in f["relative_path"]
    )

    return f"""\
Compile Chapter 6: Utilities and Configuration for '{repo_name}'.
Format output in clean Markdown.

Utilities & Configuration File Summaries:
{utils_text}

Requirements:
- Document system utilities: loggers, custom exception definitions, configurations, and environment setups.
- Detail helper methods, fallback strategies, and log formatting definitions.
"""


def get_chapters_master_prompt(
    repo_name: str,
    details: dict[str, Any],
    stats: Any,
    file_summaries: list[dict[str, str]],
    folder_summaries: dict[str, str],
    tree_text: str,
) -> str:
    """Generate the single master prompt to compile all 6 chapters in a structured JSON response."""
    folder_text = "\n".join(f"- Folder: {k}\n  Summary: {v}" for k, v in folder_summaries.items())
    
    file_text_all = "\n".join(
        f"- File: {f['relative_path']}\n  Summary: {f['summary']}"
        for f in file_summaries
    )
    
    file_text_code = "\n".join(
        f"- File: {f['relative_path']}\n  Summary: {f['summary']}"
        for f in file_summaries
        if f["relative_path"].endswith((".py", ".js", ".ts", ".go", ".rs", ".java", ".c", ".cpp"))
    )

    api_text = "\n".join(
        f"- File: {f['relative_path']}\n  Summary: {f['summary']}"
        for f in file_summaries
        if "service" in f["relative_path"] or "api" in f["relative_path"] or "route" in f["relative_path"] or "home" in f["relative_path"]
    )

    utils_text = "\n".join(
        f"- File: {f['relative_path']}\n  Summary: {f['summary']}"
        for f in file_summaries
        if "util" in f["relative_path"] or "config" in f["relative_path"] or "logger" in f["relative_path"] or "exception" in f["relative_path"]
    )

    return f"""\
You are a technical writer and senior software architect compiling professional documentation for the codebase '{repo_name}'.
Generate the complete content for the following 6 markdown chapters. Your response MUST be a valid JSON object matching this schema:
{{
  "01_repository_summary.md": "<markdown content for chapter 1>",
  "02_architecture.md": "<markdown content for chapter 2>",
  "03_folder_structure.md": "<markdown content for chapter 3>",
  "04_core_modules.md": "<markdown content for chapter 4>",
  "05_api.md": "<markdown content for chapter 5>",
  "06_utilities.md": "<markdown content for chapter 6>"
}}

Ensure each value is a clean, comprehensive markdown document. Use markdown elements, headings, bullet points, and code blocks inside the text.

Here is the source metadata to base your chapters on:

Repository Metadata:
- Name: {details.get('name', repo_name)}
- Owner: {details.get('owner', 'Unknown')}
- Description: {details.get('description', 'N/A')}
- Primary Language: {details.get('language', 'Unknown')}
- Stars: {details.get('stars', 0)}
- License: {details.get('license', 'None')}

Codebase Statistics:
- Total Files: {stats.total_files}
- Total Folders: {stats.total_folders}
- Lines of Code: {stats.total_lines_of_code}

Directory Structure Tree:
```text
{tree_text}
```

Folder Summaries:
{folder_text}

All File Summaries:
{file_text_all}

---
CHAPTER 1: Repository Summary (01_repository_summary.md)
Requirements:
- Summarize the repository's purpose, scope, and metrics.
- List key features based on folder responsibilities.
- Keep the tone professional, structured, and informative.

---
CHAPTER 2: Architecture Overview (02_architecture.md)
Requirements:
- Describe the high-level architecture and subsystem relationships.
- Detail the data flow through the application layers (e.g. Frontend -> Services -> Backend/External).
- Provide architectural design choices (e.g., MVC, Layered architecture, separation of concerns).

---
CHAPTER 3: Folder Structure (03_folder_structure.md)
Requirements:
- Review the codebase directory tree structure.
- Explain what each folder is responsible for.
- Note any standard structural patterns (e.g. config, tests, assets, utilities).

---
CHAPTER 4: Core Modules (04_core_modules.md)
Source summaries to focus on:
{file_text_code}
Requirements:
- Detail the core logic files, classes, and main algorithms.
- Explain the logic separation and functional entry points.
- Illustrate relationships between core modules.

---
CHAPTER 5: API Documentation (05_api.md)
Source summaries to focus on:
{api_text}
Requirements:
- Document public APIs, orchestrators, endpoints, and interface methods.
- Describe parameter types, returns, custom exceptions, and error boundaries.

---
CHAPTER 6: Utilities and Configuration (06_utilities.md)
Source summaries to focus on:
{utils_text}
Requirements:
- Document system utilities: loggers, custom exception definitions, configurations, and environment setups.
- Detail helper methods, fallback strategies, and log formatting definitions.
"""

