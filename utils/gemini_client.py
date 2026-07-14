"""
Gemini client utility — Centralizes API requests to Gemini with caching and retry backoff.
"""

import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any
from google import genai
from utils.logger import get_logger

logger = get_logger(__name__)

CACHE_FILE = Path("d:/AI_Map/AI-Codebase-Assistant/.cache/gemini_cache.json")

# Stats counters for call report
_api_calls_made = 0
_cache_hits = 0


def get_api_call_count() -> int:
    """Return number of raw Gemini API calls made in current execution."""
    global _api_calls_made
    return _api_calls_made


def get_cache_hit_count() -> int:
    """Return number of cached prompt hits."""
    global _cache_hits
    return _cache_hits


def reset_stats() -> None:
    """Reset the API call counters."""
    global _api_calls_made, _cache_hits
    _api_calls_made = 0
    _cache_hits = 0


def parse_retry_delay(error_msg: str) -> float:
    """Extracts retry delay from 429 RESOURCE_EXHAUSTED details returned by the API.

    Args:
        error_msg: String representation of the error.

    Returns:
        float: Delay duration in seconds. Default fallback is 5.0.
    """
    # Look for 'retryDelay': '36s' or "retryDelay": "36s" or 'retryDelay': '36.96s'
    match = re.search(r"retryDelay':\s*'([\d\.]+)s'", error_msg)
    if match:
        return float(match.group(1))
    match = re.search(r'"retryDelay":\s*"([\d\.]+)s"', error_msg)
    if match:
        return float(match.group(1))
    return 5.0


def get_cached_response(prompt: str, system_instruction: str = "") -> str | None:
    """Lookup cached response for a prompt from local JSON file.

    Args:
        prompt: User query prompt.
        system_instruction: Accompanying system instruction.

    Returns:
        str | None: Cached result if found, otherwise None.
    """
    global _cache_hits
    if not CACHE_FILE.exists():
        return None
    try:
        data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        combined = f"sys:{system_instruction}\nprompt:{prompt}"
        key = hashlib.sha256(combined.encode("utf-8")).hexdigest()
        val = data.get(key)
        if val is not None:
            _cache_hits += 1
            return val
    except Exception as exc:
        logger.warning("Failed to lookup from prompt cache: %s", exc)
    return None


def save_cached_response(prompt: str, system_instruction: str, response: str) -> None:
    """Save query response to local prompt cache.

    Args:
        prompt: User query prompt.
        system_instruction: Accompanying system instruction.
        response: Output text returned by LLM.
    """
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = {}
        if CACHE_FILE.exists():
            try:
                data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass
        combined = f"sys:{system_instruction}\nprompt:{prompt}"
        key = hashlib.sha256(combined.encode("utf-8")).hexdigest()
        data[key] = response
        CACHE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as exc:
        logger.warning("Failed to write to prompt cache: %s", exc)


def generate_content_with_retry(
    client: genai.Client,
    model: str,
    contents: Any,
    config: dict[str, Any],
    max_retries: int = 3,
) -> str:
    """Wraps client generate_content with local disk caching and exponential 429 backoff.

    Args:
        client: genai.Client instance.
        model: Gemini model name.
        contents: Query prompt structure or list.
        config: GenerateContentConfig dictionary mapping.
        max_retries: Maximum number of attempts for 429.

    Returns:
        str: Gemini response text.
    """
    global _api_calls_made
    
    # We only cache string contents to keep it simple and clean
    prompt_str = str(contents)
    system_instruction = str(config.get("system_instruction", ""))
    
    cached = get_cached_response(prompt_str, system_instruction)
    if cached is not None:
        logger.info("Cache hit for Gemini prompt. Reusing response.")
        return cached

    retries = 0
    while True:
        try:
            _api_calls_made += 1
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
            res_text = (response.text or "").strip()
            
            # Cache the successful result
            save_cached_response(prompt_str, system_instruction, res_text)
            return res_text

        except Exception as exc:
            exc_str = str(exc)
            is_rate_limit = (
                "429" in exc_str
                or "RESOURCE_EXHAUSTED" in exc_str
                or "quota" in exc_str.lower()
            )
            if is_rate_limit and retries < max_retries:
                retries += 1
                delay = parse_retry_delay(exc_str)
                sleep_time = delay * (1.5 ** (retries - 1))
                logger.warning(
                    "Gemini API 429 rate limit. Retrying %d/%d in %.2fs. Error: %s",
                    retries, max_retries, sleep_time, exc
                )
                time.sleep(sleep_time)
                continue
            raise exc
