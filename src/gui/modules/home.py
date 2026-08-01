"""Home dashboard page: welcome hero + clickable module grid."""

import streamlit as st

from src.gui.components import hero, module_card_button
from src.gui.registry import MODULE_META


def render() -> None:
    full_name = st.session_state.get("full_name", "Engineer")
    first_name = full_name.split()[0] if full_name.split() else full_name

    hero(
        "home",
        f"Welcome back, {first_name}",
        "Pick a module to start your drilling engineering workflow.",
    )

    st.markdown('<div class="module-grid">', unsafe_allow_html=True)
    cols = st.columns(3)
    col_idx = 0
    for title, (icon_name, display_title, desc) in MODULE_META.items():
        if title == "Home":
            continue
        with cols[col_idx]:
            if module_card_button(f"mc_{title.replace(' ', '_')}", icon_name, display_title, desc):
                st.session_state.page = title
                st.rerun()
        col_idx = (col_idx + 1) % 3
    st.markdown("</div>", unsafe_allow_html=True)
