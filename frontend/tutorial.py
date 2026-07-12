"""
Tutorial viewer — renders the currently selected chapter.
"""

import streamlit as st

from services.tutorial_service import Chapter
from frontend.components import render_section_header


def render_tutorial(chapters: list[Chapter]) -> None:
    """Render the tutorial viewer for the currently selected chapter.

    The chapter is determined by ``st.session_state.selected_chapter``.
    Also provides a download button for the current chapter.

    Args:
        chapters: List of all generated chapters.
    """
    if not chapters:
        st.warning("📭 No tutorial chapters were generated.")
        return

    selected_index: int = st.session_state.get("selected_chapter", 0)

    # Guard against out-of-range index
    if selected_index >= len(chapters):
        selected_index = 0
        st.session_state.selected_chapter = 0

    chapter = chapters[selected_index]

    # --- Chapter header ---
    render_section_header("📖", chapter.title)

    # --- Markdown content ---
    with st.container(border=True):
        st.markdown(chapter.content)

    # --- Download current chapter ---
    st.download_button(
        label="⬇️ Download This Chapter",
        data=chapter.content,
        file_name=chapter.filename,
        mime="text/markdown",
        use_container_width=True,
    )

    # --- Chapter navigation (prev / next) ---
    _render_chapter_navigation(chapters, selected_index)


def _render_chapter_navigation(
    chapters: list[Chapter],
    current_index: int,
) -> None:
    """Render prev/next navigation buttons below the chapter.

    Args:
        chapters: Full chapter list.
        current_index: Index of the currently displayed chapter.
    """
    col_prev, col_info, col_next = st.columns([1, 2, 1])

    with col_prev:
        if current_index > 0:
            if st.button("⬅️ Previous", use_container_width=True):
                st.session_state.selected_chapter = current_index - 1
                st.rerun()

    with col_info:
        st.caption(
            f"Chapter {current_index + 1} of {len(chapters)}"
        )

    with col_next:
        if current_index < len(chapters) - 1:
            if st.button("Next ➡️", use_container_width=True):
                st.session_state.selected_chapter = current_index + 1
                st.rerun()
