"""
Streamlit session state management.

Centralizes all session state keys and provides helpers to initialize,
reset, and query state. This prevents model reruns on every
Streamlit interaction (chapter click, download, radio button, etc.).
"""

from typing import Any

import streamlit as st

from utils.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Default values for every session state key.
#
# NOTE: ``repo_url`` is NOT listed here because it is managed by the
# ``st.text_input`` widget via its ``key=`` parameter.  Streamlit does
# not allow programmatic writes to widget-bound keys after the widget
# has been rendered.
#
# Mutable defaults (lists, dicts) use factory functions to avoid
# shared-mutation bugs across resets.
# ---------------------------------------------------------------------------
_IMMUTABLE_DEFAULTS: dict[str, Any] = {
    "analysis_done": False,
    "analysis_result": None,
    "selected_chapter": 0,
    "error_message": None,
}

_MUTABLE_FACTORIES: dict[str, type] = {
    "chapters": list,
}


def _get_defaults() -> dict[str, Any]:
    """Return a fresh copy of all default values."""
    defaults = dict(_IMMUTABLE_DEFAULTS)
    for key, factory in _MUTABLE_FACTORIES.items():
        defaults[key] = factory()
    return defaults


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def init_session_state() -> None:
    """Initialize all session state keys with defaults.

    Safe to call on every Streamlit rerun — only sets keys that don't
    already exist.
    """
    for key, default in _get_defaults().items():
        if key not in st.session_state:
            st.session_state[key] = default


def reset_state() -> None:
    """Clear all analysis-related state for a fresh run.

    Note: ``repo_url`` is not reset here because it is bound to the
    text_input widget.  Streamlit handles widget-key lifecycle itself.
    """
    for key, default in _get_defaults().items():
        st.session_state[key] = default

    logger.info("Session state reset.")


def is_analysis_complete() -> bool:
    """Check whether a successful analysis result is stored."""
    return bool(st.session_state.get("analysis_done", False))
