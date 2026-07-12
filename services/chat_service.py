"""
Chat service — AI-powered Q&A about the analyzed codebase.

Uses Google Gemini with chapter content as context (context-stuffing).
All chapters fit comfortably within Gemini's 1M token context window.
"""

import os
from typing import Any

from utils.logger import get_logger

logger = get_logger(__name__)

_SYSTEM_PROMPT = """\
You are an expert software engineer assistant. You have been given the full \
AI-generated tutorial for a codebase. Answer the user's questions based on \
the tutorial content provided below.

Rules:
- Answer concisely and accurately based on the tutorial content.
- If the answer is not in the tutorial, say so honestly.
- Use code examples from the tutorial when relevant.
- Format responses in Markdown.

--- TUTORIAL CONTENT ---
{context}
--- END TUTORIAL ---
"""


def _build_context(chapters: list) -> str:
    """Build a single context string from all chapters.

    Args:
        chapters: List of Chapter objects.

    Returns:
        Combined chapter content as a single string.
    """
    parts: list[str] = []
    for i, ch in enumerate(chapters, 1):
        parts.append(f"## Chapter {i}: {ch.title}\n\n{ch.content}")
    return "\n\n---\n\n".join(parts)


def chat_with_codebase(
    question: str,
    chapters: list,
    chat_history: list[dict[str, str]],
) -> str:
    """Send a question about the codebase to Gemini and get a response.

    Args:
        question: The user's question.
        chapters: List of Chapter objects for context.
        chat_history: List of previous messages, each with 'role' and 'content'.

    Returns:
        The AI's response as a string.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "⚠️ GEMINI_API_KEY is not set. Please add it to your `.env` file."

    try:
        from google import genai
    except ImportError:
        return "⚠️ `google-genai` is not installed. Run: `pip install google-genai`"

    context = _build_context(chapters)
    system_prompt = _SYSTEM_PROMPT.format(context=context)

    # Build message history for Gemini
    contents: list[dict[str, Any]] = []

    for msg in chat_history:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})

    # Add the new question
    contents.append({"role": "user", "parts": [{"text": question}]})

    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    logger.info("Chat request: model=%s, history=%d msgs", model_name, len(chat_history))

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config={
                "system_instruction": system_prompt,
                "temperature": 0.3,
                "max_output_tokens": 2048,
            },
        )

        answer = response.text or "I couldn't generate a response. Please try again."

        logger.info("Chat response: %d chars", len(answer))
        return answer

    except Exception as exc:
        logger.error("Gemini chat error: %s", exc)
        return f"⚠️ AI error: {exc}"
