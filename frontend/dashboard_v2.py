"""
Repository dashboard V2 — displays repository metadata and codebase statistics.
"""

from typing import Any
import streamlit as st

from frontend.components import render_metric_card, render_section_header, render_success


def render_dashboard_v2(result: Any) -> None:
    """Render the Version 2 repository dashboard with metrics, stats, and file tree.

    Args:
        result: V2AnalysisResult object containing details, stats, and tree_text.
    """
    details = result.details or {}
    stats = result.stats
    
    render_success(result.message)

    # --- Section 1: GitHub Repository Metadata ---
    render_section_header("📊", "Repository Dashboard")

    c1, c2, c3 = st.columns(3)
    with c1:
        render_metric_card("📦", "Repository", details.get("name", ""))
    with c2:
        render_metric_card("👤", "Owner", details.get("owner", ""))
    with c3:
        render_metric_card("💻", "Language", details.get("language", "Unknown"))

    c4, c5, c6 = st.columns(3)
    with c4:
        render_metric_card("⭐", "Stars", details.get("stars", 0))
    with c5:
        render_metric_card("🍴", "Forks", details.get("forks", 0))
    with c6:
        render_metric_card("📜", "License", details.get("license", "None"))

    st.info(f"📝 **Description:** {details.get('description', 'No description available.')}", icon="ℹ️")

    # --- Section 2: Codebase Statistics ---
    if stats:
        render_section_header("⚙️", "Codebase Statistics")

        s1, s2, s3 = st.columns(3)
        with s1:
            render_metric_card("📄", "Total Files", stats.total_files)
        with s2:
            render_metric_card("📁", "Total Folders", stats.total_folders)
        with s3:
            render_metric_card("🧮", "Lines of Code (LOC)", stats.total_lines_of_code)

        s4, s5, s6 = st.columns(3)
        with s4:
            render_metric_card("🐍", "Python Files", stats.total_python_files)
        with s5:
            render_metric_card("📝", "Markdown Files", stats.total_markdown_files)
        with s6:
            # Show size in KB
            avg_size_kb = stats.average_file_size / 1024.0
            render_metric_card("📊", "Avg File Size", f"{avg_size_kb:.1f} KB")

        with st.container(border=True):
            largest_size_kb = stats.largest_file_size / 1024.0
            st.markdown(f"📏 **Largest File:** `{stats.largest_file}` ({largest_size_kb:.1f} KB)")

    # --- Section 3: Directory Tree View ---
    if result.tree_text:
        render_section_header("🌳", "Repository Structure")
        with st.expander("📂 Codebase Directory Tree", expanded=True):
            tree_content = "\n".join(result.tree_text)
            st.code(tree_content, language="text")

    # --- Footer ---
    col_left, col_right = st.columns(2)
    with col_left:
        st.caption(f"📅 Last Updated: {details.get('updated', 'N/A')}")
    with col_right:
        html_url = details.get("html_url", "")
        if html_url:
            st.caption(f"🔗 [{html_url}]({html_url})")
