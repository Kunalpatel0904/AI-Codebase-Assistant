"""
Repository dashboard — displays repository metadata in a styled card grid.
"""

from typing import Any

import streamlit as st

from frontend.components import render_metric_card, render_section_header


def render_dashboard(details: dict[str, Any]) -> None:
    """Render the repository dashboard with metric cards.

    Args:
        details: Repository metadata dict from
                 :func:`services.github_service.get_repository_details`.
    """
    render_section_header("📊", "Repository Dashboard")

    # --- Row 1: Name, Owner, Language ---
    c1, c2, c3 = st.columns(3)

    with c1:
        render_metric_card("📦", "Repository", details.get("name", ""))

    with c2:
        render_metric_card("👤", "Owner", details.get("owner", ""))

    with c3:
        render_metric_card("💻", "Language", details.get("language", "Unknown"))

    # --- Row 2: Stars, Forks, Open Issues ---
    c4, c5, c6 = st.columns(3)

    with c4:
        render_metric_card("⭐", "Stars", details.get("stars", 0))

    with c5:
        render_metric_card("🍴", "Forks", details.get("forks", 0))

    with c6:
        render_metric_card("🐛", "Open Issues", details.get("open_issues", 0))

    # --- License ---
    with st.container(border=True):
        st.markdown(
            f"📜 **License:** {details.get('license', 'None')}"
        )

    # --- Description ---
    st.info(
        f"📝 {details.get('description', 'No description available.')}",
        icon="ℹ️",
    )

    # --- Footer: Last Updated + URL ---
    col_left, col_right = st.columns(2)

    with col_left:
        st.caption(f"📅 Last Updated: {details.get('updated', 'N/A')}")

    with col_right:
        html_url = details.get("html_url", "")
        if html_url:
            st.caption(f"🔗 [{html_url}]({html_url})")

    st.divider()
