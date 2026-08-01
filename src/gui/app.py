"""PyMudCement-Optima Streamlit entry point.

Run with:  streamlit run src/gui/app.py

Orchestrates: theme setup → login gate → app shell (sidebar) → page routing.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st

from src.gui.components import (
    app_footer,
    render_login_screen,
    sidebar_brand,
    sidebar_nav,
    unit_system_selector,
    user_chip,
)
from src.gui.modules import get_current_page, render_page
from src.gui.theme import apply_theme

apply_theme()

# ══════════════════════════════════════════════════════════════════
#  AUTHENTICATION GATE
# ══════════════════════════════════════════════════════════════════
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = ""

if not st.session_state.authenticated:
    render_login_screen()

# ══════════════════════════════════════════════════════════════════
#  APP SHELL
# ══════════════════════════════════════════════════════════════════
full_name = st.session_state.get("full_name", st.session_state.username)
current_page = get_current_page()

with st.sidebar:
    sidebar_brand()
    user_chip(full_name, st.session_state.username)
    unit_system_selector()
    sidebar_nav(current_page)

    st.markdown('<div class="sidebar-footer">', unsafe_allow_html=True)
    if st.button("Logout", icon=":material/logout:", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
#  PAGE ROUTING
# ══════════════════════════════════════════════════════════════════
render_page(current_page)
app_footer()
