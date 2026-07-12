import streamlit as st

from frontend.components import render_app_header, render_error, render_success
from frontend.dashboard import render_dashboard
from frontend.downloads import render_downloads
from frontend.sidebar import render_sidebar
from frontend.state import is_analysis_complete, reset_state
from frontend.tutorial import render_tutorial, load_chapters_from_disk
from services.document_service import generate_documentation
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

        with st.spinner("🔍 Analyzing repository and generating documentation… This may take a few minutes."):
            result = generate_documentation(repo_url.strip())

        if result.status != "success":
            render_error(result.message)
            return

        # Load chapters from the generated output files
        chapters = load_chapters_from_disk(result.output_folder)

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
    """Render dashboard, codebase statistics, directory tree, and chapter viewer."""
    result = st.session_state.analysis_result
    chapters = st.session_state.chapters

    render_success(result.message)

    # --- Dashboard, Statistics and Tree ---
    if result.details:
        render_dashboard(
            details=result.details,
            stats=result.stats,
            tree_text=result.tree_text,
        )

    # --- Chapter viewer ---
    if chapters:
        render_tutorial(chapters)
    else:
        st.warning("📭 No tutorial chapters were generated.")

    # --- Downloads ---
    if result.output_folder:
        render_downloads(result.output_folder)