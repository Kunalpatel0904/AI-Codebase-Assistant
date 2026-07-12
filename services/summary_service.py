"""
Summary service — Queries Google Gemini to generate file and folder summaries.

Optimized with batching to avoid hitting API rate limits.
"""

import time
from pathlib import Path
from google import genai

from services import prompt_service
from utils.exceptions import GeminiAPIError, RepositoryScanError
from utils.logger import get_logger

logger = get_logger(__name__)


def summarize_file_individually(
    file_path: Path,
    relative_path: str,
    client: genai.Client,
    model_name: str,
) -> str:
    """Summarizes a single code file using Gemini with chunking if it exceeds limit.

    Args:
        file_path: Absolute Path to the source file.
        relative_path: Path relative to repository root.
        client: Initialized Gemini Client.
        model_name: Gemini model name.

    Returns:
        str: Concise file summary.
    """
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:
        logger.warning("Failed to read file %s: %s", relative_path, exc)
        return "Source code file."

    if not content.strip():
        return "Empty file."

    chunk_size = 12000
    if len(content) > 16000:
        logger.info("File %s exceeds size limit (%d chars). Chunking...", relative_path, len(content))
        chunks = [content[i : i + chunk_size] for i in range(0, len(content), chunk_size)]
        chunk_summaries = []

        for idx, chunk in enumerate(chunks, 1):
            response = client.models.generate_content(
                model=model_name,
                contents=prompt_service.get_file_summary_prompt(relative_path, chunk),
                config={
                    "system_instruction": prompt_service.get_file_summary_system_instruction(),
                    "temperature": 0.2,
                },
            )
            chunk_summaries.append(response.text or "")

        combined_summaries = "\n\n".join(
            f"### Chunk {i} Summary:\n{summ}" for i, summ in enumerate(chunk_summaries, 1)
        )
        final_prompt = (
            f"Combine the following chunk summaries for '{relative_path}' into a single, cohesive "
            f"functional summary of the entire file:\n\n{combined_summaries}"
        )
        response = client.models.generate_content(
            model=model_name,
            contents=final_prompt,
            config={
                "system_instruction": prompt_service.get_file_summary_system_instruction(),
                "temperature": 0.2,
            },
        )
        return (response.text or "Failed to summarize chunked contents.").strip()
    else:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt_service.get_file_summary_prompt(relative_path, content),
            config={
                "system_instruction": prompt_service.get_file_summary_system_instruction(),
                "temperature": 0.2,
            },
        )
        return (response.text or "No summary returned.").strip()


def summarize_files(
    scanned_files: list[Any],
    api_key: str,
    model_name: str = "gemini-2.5-flash",
) -> list[dict[str, str]]:
    """Generate file summaries. Combines small files into batches to optimize API rate limit.

    Args:
        scanned_files: List of ScannedFile objects.
        api_key: Gemini API Key.
        model_name: Gemini model name.

    Returns:
        list[dict[str, str]]: List of dicts, each with 'relative_path' and 'summary' keys.
    """
    logger.info("Summarizing codebase files start: count=%d", len(scanned_files))
    start_time = time.perf_counter()

    if not api_key:
        raise GeminiAPIError("GEMINI_API_KEY is not set.")

    client = genai.Client(api_key=api_key)
    file_summaries: list[dict[str, str]] = []

    # Filter out empty files early
    active_files = [f for f in scanned_files if f.file_size > 0]
    if not active_files:
        return []

    # Split files into large (summarized individually) and small (summarized in batches)
    large_files = []
    small_files = []

    for f in active_files:
        if f.file_size > 16000:
            large_files.append(f)
        else:
            small_files.append(f)

    # 1. Summarize large files individually
    for lf in large_files:
        try:
            summ = summarize_file_individually(lf.file_path, lf.relative_path, client, model_name)
            file_summaries.append({"relative_path": lf.relative_path, "summary": summ})
        except Exception as exc:
            logger.warning("Failed to summarize large file %s: %s", lf.relative_path, exc)
            file_summaries.append({"relative_path": lf.relative_path, "summary": "Core code module."})

    # 2. Summarize small files in batches
    batch_size = 12
    for i in range(0, len(small_files), batch_size):
        batch = small_files[i : i + batch_size]
        logger.info("Processing file summary batch %d/%d (%d files)", (i // batch_size) + 1, (len(small_files) - 1) // batch_size + 1, len(batch))

        # Build prompt containing code for all files in this batch
        prompt_lines = [
            "For each of the following files, write a concise 1-2 sentence functional summary.",
            "Format your response EXACTLY as a list of lines in the format:",
            "[relative_path]: [summary]",
            "",
            "Files list:",
            "---"
        ]
        
        for sf in batch:
            try:
                code_content = sf.file_path.read_text(encoding="utf-8", errors="ignore")
                prompt_lines.append(f"File: {sf.relative_path}")
                prompt_lines.append("Code:")
                prompt_lines.append(code_content[:8000])  # limit code content preview per file
                prompt_lines.append("---")
            except Exception:
                pass

        batch_prompt = "\n".join(prompt_lines)

        try:
            response = client.models.generate_content(
                model=model_name,
                contents=batch_prompt,
                config={
                    "system_instruction": prompt_service.get_file_summary_system_instruction(),
                    "temperature": 0.2,
                },
            )
            
            # Parse responses mapping path to summary
            batch_result = response.text or ""
            parsed_summaries = {}
            for line in batch_result.splitlines():
                if ":" in line:
                    parts = line.split(":", 1)
                    path_part = parts[0].strip().strip("*-` ")
                    summary_part = parts[1].strip()
                    parsed_summaries[path_part] = summary_part

            # Match batch files against parsed summaries
            for sf in batch:
                summary = parsed_summaries.get(sf.relative_path)
                if not summary:
                    # Fallback lookup in case of formatting mismatch (e.g. absolute paths or typos)
                    summary = next((v for k, v in parsed_summaries.items() if k in sf.relative_path or sf.relative_path in k), None)
                
                if not summary:
                    summary = f"Helper script or configuration asset supporting {sf.extension} modules."

                file_summaries.append({"relative_path": sf.relative_path, "summary": summary})
            
            time.sleep(3.0)

        except Exception as exc:
            logger.warning("Batch file summary failed: %s. Falling back to default summaries.", exc)
            for sf in batch:
                file_summaries.append({
                    "relative_path": sf.relative_path,
                    "summary": f"Source module or configuration asset handling {sf.extension} logic."
                })

    duration = time.perf_counter() - start_time
    logger.info("Summarizing codebase files success: count=%d, duration=%.2fs", len(file_summaries), duration)
    return file_summaries


def summarize_folders(
    scanned_files_with_summaries: list[dict[str, str]],
    api_key: str,
    model_name: str = "gemini-2.5-flash",
) -> dict[str, str]:
    """Generates summaries for all unique folders in a single batched Gemini request.

    Args:
        scanned_files_with_summaries: List of dicts, each with 'relative_path' and 'summary' keys.
        api_key: Gemini API Key.
        model_name: Gemini LLM model name.

    Returns:
        dict[str, str]: Maps relative folder paths to folder-wide summaries.
    """
    logger.info("Summarizing folders start: files_count=%d", len(scanned_files_with_summaries))
    start_time = time.perf_counter()

    if not api_key:
        raise GeminiAPIError("GEMINI_API_KEY is not set.")

    # Group files by parent folder
    folders_map: dict[str, list[dict[str, str]]] = {}
    for item in scanned_files_with_summaries:
        rel_path = item["relative_path"]
        parent = str(Path(rel_path).parent).replace("\\", "/")
        if parent == "." or parent == "":
            parent = "root"
        folders_map.setdefault(parent, []).append(item)

    if not folders_map:
        return {}

    try:
        client = genai.Client(api_key=api_key)
        
        # Build a single prompt mapping all folders and their files summaries
        prompt_lines = [
            "For each of the following directory folders, write a 2-3 sentence overview explaining",
            "its role in the codebase based on the files inside it.",
            "Format your response EXACTLY as a list of lines in the format:",
            "[folder_name]: [summary]",
            "",
            "Folders list:",
            "---"
        ]

        for folder_name, files in folders_map.items():
            prompt_lines.append(f"Folder: {folder_name}")
            prompt_lines.append("Contained Files:")
            for f in files:
                prompt_lines.append(f"  - File: {f['relative_path']}\n    Summary: {f['summary']}")
            prompt_lines.append("---")

        batch_prompt = "\n".join(prompt_lines)
        
        response = client.models.generate_content(
            model=model_name,
            contents=batch_prompt,
            config={
                "system_instruction": prompt_service.get_folder_summary_system_instruction(),
                "temperature": 0.2,
            },
        )

        batch_result = response.text or ""
        folder_summaries: dict[str, str] = {}
        
        for line in batch_result.splitlines():
            if ":" in line:
                parts = line.split(":", 1)
                folder_part = parts[0].strip().strip("*-` ")
                summary_part = parts[1].strip()
                folder_summaries[folder_part] = summary_part

        # Clean up mapping and add fallbacks
        final_summaries: dict[str, str] = {}
        for folder_name in folders_map.keys():
            summary = folder_summaries.get(folder_name)
            if not summary:
                summary = next((v for k, v in folder_summaries.items() if k in folder_name or folder_name in k), None)
            if not summary:
                summary = f"Contains codebase assets supporting functional {folder_name} subsystems."
            final_summaries[folder_name] = summary

        duration = time.perf_counter() - start_time
        logger.info("Summarizing folders success: folders_count=%d, duration=%.2fs", len(final_summaries), duration)
        time.sleep(3.0)
        return final_summaries


    except Exception as exc:
        duration = time.perf_counter() - start_time
        logger.error("Summarizing folders failure: error=%s, duration=%.2fs", exc, duration)
        raise GeminiAPIError(f"Gemini API failure during folder summarization: {exc}") from exc



def summarize_file(
    file_path: Path,
    relative_path: str,
    api_key: str,
    model_name: str = "gemini-2.5-flash",
) -> str:
    """Wrapper function for backward compatibility and testing individual file summaries.

    Args:
        file_path: Absolute Path to the source file.
        relative_path: Path relative to repository root.
        api_key: Gemini API Key.
        model_name: Gemini LLM model name.

    Returns:
        str: Concise file summary.
    """
    client = genai.Client(api_key=api_key)
    return summarize_file_individually(file_path, relative_path, client, model_name)

