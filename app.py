"""
AI Codebase Assistant — Application entry point.

Run with:
    streamlit run app.py
"""

import streamlit as st

import config
from frontend.home import render_home
from frontend.state import init_session_state
from utils.logger import setup_logging


def main() -> None:
    """Configure the Streamlit page and launch the app.

    ``st.set_page_config`` must be the very first Streamlit call.
    Logging is initialised immediately after so that all subsequent
    modules have access to the configured logger.
    """
    st.set_page_config(
        page_title=config.APP_TITLE,
        page_icon=config.APP_ICON,
        layout=config.APP_LAYOUT,
    )

    setup_logging()
    init_session_state()
    render_home()


if __name__ == "__main__":
    main()