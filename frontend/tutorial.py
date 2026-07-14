import streamlit as st
from dataclasses import dataclass
from pathlib import Path

from frontend.components import render_section_header


@dataclass(frozen=True)
class Chapter:
    """Dataclass holding documentation chapter info."""
    title: str
    content: str
    filename: str


def load_chapters_from_disk(output_folder: str) -> list[Chapter]:
    """Loads markdown documentation files from the output folder.

    Args:
        output_folder: Folder path containing generated markdown files.

    Returns:
        list[Chapter]: Ordered list of chapters.
    """
    output_path = Path(output_folder)
    chapters: list[Chapter] = []
    if not output_path.exists():
        return chapters
        
    # Read files in sorted alphabetical order
    for md_file in sorted(output_path.glob("*.md")):
        if md_file.name.lower() == "index.md":
            continue
        try:
            content = md_file.read_text(encoding="utf-8")
            title = md_file.name.replace(".md", "").split("_", 1)[-1].replace("_", " ").title()
            chapters.append(
                Chapter(
                    title=title,
                    content=content,
                    filename=md_file.name,
                )
            )
        except Exception:
            pass
    return chapters


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
