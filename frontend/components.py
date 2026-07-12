"""
Shared UI components for the AI Codebase Assistant.

Reusable rendering helpers used across the dashboard, tutorial viewer,
sidebar, and downloads pages.
"""

import streamlit as st

import config


def render_metric_card(icon: str, label: str, value: str | int) -> None:
    """Render a styled metric card inside a Streamlit container.

    Args:
        icon: Emoji icon for the metric.
        label: Metric label text.
        value: Metric value to display.
    """
    with st.container(border=True):
        st.metric(label=f"{icon} {label}", value=value)


def render_error(message: str) -> None:
    """Display a user-friendly error alert.

    Args:
        message: Error message to show.
    """
    st.error(message, icon="🚨")


def render_success(message: str) -> None:
    """Display a success alert.

    Args:
        message: Success message to show.
    """
    st.success(message, icon="✅")


def render_coming_soon(feature: str) -> None:
    """Display a 'Coming in Version 2' info badge.

    Args:
        feature: Name of the upcoming feature.
    """
    st.info(f"**{feature}** — Coming in Version 2", icon="🚧")


def render_section_header(icon: str, title: str) -> None:
    """Render a consistent section header.

    Args:
        icon: Emoji icon for the section.
        title: Section title text.
    """
    st.subheader(f"{icon} {title}")


def render_app_header() -> None:
    """Render the main application header."""
    st.title(f"{config.APP_ICON} {config.APP_TITLE}")
    st.caption(f"v{config.APP_VERSION}")
    st.write("Analyze public GitHub repositories and generate AI-powered tutorials.")
    st.divider()
