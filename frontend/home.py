import streamlit as st

from frontend.components import render_app_header, render_error, render_success
from frontend.dashboard import render_dashboard
from frontend.downloads import render_downloads
from frontend.sidebar import render_sidebar
from frontend.state import is_analysis_complete, reset_state
from frontend.tutorial import render_tutorial
from services.analysis_service import analyze_repository
from services.dashboard_service import analyze_repository_v2
from services.tutorial_service import get_chapters
from utils.logger import get_logger

logger = get_logger(__name__)


def render_home() -> None:
    """Render the full home page."""

    # --- Sidebar ---
    render_sidebar()

    # --- Header ---
    render_app_header()

    # --- Input form ---
    _render_input_form()

    # --- Results (only shown after successful analysis) ---
    if is_analysis_complete():
        _render_results()


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _render_input_form() -> None:
    """Render the repository URL input and Analyze button.

    Uses a ``key=`` parameter instead of ``value=`` so Streamlit manages
    the widget state properly and doesn't overwrite user input on reruns.
    """
    repo_url = st.text_input(
        "🔗 GitHub Repository URL",
        key="repo_url",
        placeholder="https://github.com/owner/repository",
    )

    col_analyze, col_reset = st.columns([3, 1])

    with col_analyze:
        analyze_clicked = st.button(
            "🚀 Analyze Repository",
            use_container_width=True,
            type="primary",
        )

    with col_reset:
        reset_clicked = st.button(
            "🔄 Reset",
            use_container_width=True,
        )

    if reset_clicked:
        reset_state()
        st.rerun()

    if analyze_clicked:
        if not repo_url or not repo_url.strip():
            render_error("Please enter a GitHub repository URL.")
            return

        mode = st.session_state.get("app_mode", "V1")

        with st.spinner("🔍 Analyzing repository… This may take a few minutes."):
            if mode == "V2":
                result = analyze_repository_v2(repo_url.strip())
            else:
                result = analyze_repository(repo_url.strip())

        if result.status != "success":
            render_error(result.message)
            return

        if mode == "V2":
            # Version 2 does not generate chapters/tutorials (Sprint 1)
            st.session_state.analysis_done = True
            st.session_state.analysis_result = result
            st.session_state.chapters = []
            st.session_state.selected_chapter = 0
            st.session_state.error_message = None
        else:
            # Version 1 loads generated markdown chapters
            chapters = get_chapters(result.output_folder)
            st.session_state.analysis_done = True
            st.session_state.analysis_result = result
            st.session_state.chapters = chapters
            st.session_state.selected_chapter = 0
            st.session_state.error_message = None

        st.rerun()

    # Show any persisted error
    error = st.session_state.get("error_message")
    if error:
        render_error(error)

    st.divider()


def _render_results() -> None:
    """Render dashboard, tutorial, and downloads after analysis."""
    result = st.session_state.analysis_result

    if st.session_state.get("app_mode", "V1") == "V2":
        from frontend.dashboard_v2 import render_dashboard_v2
        render_dashboard_v2(result)
        return

    chapters = st.session_state.chapters

    render_success(result.message)

    # --- Dashboard ---
    if result.details:
        render_dashboard(result.details)

    # --- Tutorial viewer ---
    if chapters:
        render_tutorial(chapters)
    else:
        st.warning("📭 No tutorial chapters were generated.")

    # --- Downloads ---
    if result.output_folder:
        render_downloads(result.output_folder)