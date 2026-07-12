"""
Downloads section — ZIP download and future PDF export placeholder.

The ZIP archive is cached via ``@st.cache_data`` so it isn't rebuilt
on every Streamlit rerun.
"""

import streamlit as st

from frontend.components import render_coming_soon, render_section_header
from services.download_service import create_tutorial_zip


@st.cache_data(show_spinner=False)
def _cached_tutorial_zip(output_folder: str) -> bytes:
    """Create and cache the tutorial ZIP archive.

    Streamlit reruns the entire script on every interaction. Without
    caching, the ZIP would be rebuilt each time the user clicks
    anything on the page.

    Args:
        output_folder: Absolute path to the tutorial output directory.

    Returns:
        ZIP file contents as bytes.
    """
    return create_tutorial_zip(output_folder)


def render_downloads(output_folder: str) -> None:
    """Render the downloads section with ZIP and future PDF options.

    Args:
        output_folder: Absolute path to the tutorial output directory.
    """
    render_section_header("📦", "Downloads")

    col_zip, col_pdf = st.columns(2)

    with col_zip:
        with st.container(border=True):
            st.markdown("**📦 Complete Tutorial (ZIP)**")
            st.caption("Download all chapters as a ZIP archive.")

            zip_data = _cached_tutorial_zip(output_folder)

            if zip_data:
                st.download_button(
                    label="⬇️ Download ZIP",
                    data=zip_data,
                    file_name="tutorial.zip",
                    mime="application/zip",
                    use_container_width=True,
                )
            else:
                st.warning("No files available for download.")

    with col_pdf:
        with st.container(border=True):
            st.markdown("**📄 PDF Export**")
            render_coming_soon("PDF Export")

    st.divider()
