"""
Sidebar — navigation, repository info, chapter list, and settings.
"""

import streamlit as st

import config
from frontend.components import render_coming_soon, render_section_header
from frontend.state import is_analysis_complete


def render_sidebar() -> None:
    """Render the full sidebar."""
    with st.sidebar:
        # --- Branding ---
        st.title(f"{config.APP_ICON} {config.APP_TITLE}")
        st.caption(f"v{config.APP_VERSION}")

        st.divider()

        # --- Repository info (shown after analysis) ---
        if is_analysis_complete():
            result = st.session_state.get("analysis_result")
            details = result.details if result else None

            if details:
                render_section_header("📂", "Repository")

                st.markdown(f"**{details['name']}**")
                st.caption(f"by {details['owner']}")

                if details.get("html_url"):
                    st.markdown(
                        f"[🔗 Open on GitHub]({details['html_url']})"
                    )

                st.divider()

            # --- Chapter navigation ---
            chapters = st.session_state.get("chapters", [])

            if chapters:
                render_section_header("📚", "Chapters")

                chapter_titles = [ch.title for ch in chapters]

                selected = st.radio(
                    "Select Chapter",
                    chapter_titles,
                    index=st.session_state.get("selected_chapter", 0),
                    label_visibility="collapsed",
                )

                st.session_state.selected_chapter = chapter_titles.index(
                    selected
                )

                st.divider()

            # --- Downloads section ---
            render_section_header("⬇️", "Downloads")
            st.caption("Use the download buttons in the main area.")

            st.divider()

        # --- Settings / V2 previews ---
        with st.expander("⚙️ Settings", expanded=False):
            st.caption("Configuration options will appear here.")
            render_coming_soon("Custom LLM Provider")
            render_coming_soon("Theme Settings")

        st.divider()

        # --- Coming in V2 ---
        with st.expander("🚧 Version 2 Roadmap", expanded=False):
            for feature in config.V2_SOURCES:
                render_coming_soon(feature)

            render_coming_soon("PDF Export")
            render_coming_soon("AI Chat / RAG")
            render_coming_soon("Repository Tree View")
            render_coming_soon("Search")
