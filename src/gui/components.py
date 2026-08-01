"""Reusable Streamlit UI components for the PyMudCement-Optima GUI.

Small, self-contained builders (hero banner, section labels, status pills,
module cards, footer, sidebar shell, and the login screen) shared by every
page module. Pages only use these helpers — they never touch raw CSS.
"""

import re

import streamlit as st

from src.gui.auth import authenticate, create_user
from src.gui.icons import material_icon
from src.gui.registry import MODULE_META


# ══════════════════════════════════════════════════════════════════
#  PRIMITIVES
# ══════════════════════════════════════════════════════════════════
def hero(icon_name: str, title: str, subtitle: str) -> None:
    """Render the gradient hero banner used at the top of every page."""
    st.markdown(
        f'<div class="hero">'
        f'<div class="hero-icon">{material_icon(icon_name, size="2.8rem", color="#ffffff")}</div>'
        f'<div>'
        f'<div class="hero-title">{title}</div>'
        f'<div class="hero-sub">{subtitle}</div>'
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def section_label(text: str) -> None:
    """Render a small uppercase blue label that heads each input group."""
    st.markdown(f'<div class="section-label">{text}</div>', unsafe_allow_html=True)


def status_pill(text: str, kind: str = "info") -> str:
    """Return HTML for a colored status pill (ok / warn / danger / info)."""
    return f'<span class="pill pill-{kind}">{text}</span>'


def module_card_button(key: str, icon_name: str, title: str, desc: str) -> bool:
    """Render one clickable dashboard card for a module.

    The decorative card content is emitted via ``st.markdown`` (reliable HTML),
    while the navigation action uses Streamlit's native Material icon button.
    """
    with st.container(border=True):
        st.markdown(
            f'<div class="mc-card">'
            f'<div class="mc-icon">{material_icon(icon_name, size="2.2rem", color="#1d4ed8")}</div>'
            f'<div class="mc-title">{title}</div>'
            f'<div class="mc-desc">{desc}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )
        return st.button(
            "Open Module",
            icon=":material/open_in_new:",
            key=key,
            use_container_width=True,
        )


def app_footer() -> None:
    """Render the fixed footer shown below every page."""
    st.markdown(
        '<div class="app-footer">'
        "<b>PyMudCement-Optima</b> — Intelligent Mud &amp; Cement Design Suite<br/>"
        "PENG 258 Capstone Project &nbsp;·&nbsp; University of Energy and Natural Resources"
        "</div>",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════
#  SIDEBAR SHELL
# ══════════════════════════════════════════════════════════════════
def sidebar_brand() -> None:
    """Render the app logo block at the top of the sidebar."""
    st.markdown(
        f'<div class="sidebar-brand">'
        f'<div class="logo">{material_icon("oil_barrel", size="1.35rem", color="#ffffff")}</div>'
        f'<div>'
        f'<div class="name">PyMudCement-Optima</div>'
        f'<div class="tag">PENG 258 · UENR</div>'
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def user_chip(full_name: str, username: str) -> None:
    """Render the signed-in user chip (avatar + name + handle)."""
    initials = "".join(w[0] for w in full_name.split() if w)[:2].upper() or full_name[:2].upper()
    st.markdown(
        f'<div class="user-chip">'
        f'<div class="avatar">{initials}</div>'
        f"<div>"
        f'<div class="u-name">{full_name}</div>'
        f'<div class="u-role">@{username}</div>'
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def unit_system_selector() -> None:
    """Sidebar control for switching between SI and Oilfield (Field) units.

    Persists the choice in ``st.session_state["unit_system"]``; every page
    builds its ``Units`` helper from this value.
    """
    st.markdown('<div class="sidebar-mini-label">UNIT SYSTEM</div>', unsafe_allow_html=True)
    if st.session_state.get("unit_system") not in ("SI", "Field"):
        st.session_state.unit_system = "SI"
    st.segmented_control(
        "Unit System",
        ["SI", "Field"],
        key="unit_system",
        label_visibility="collapsed",
    )


def sidebar_nav(current_page: str) -> None:
    """Render the module navigation buttons with active-page highlighting.

    Icons use Streamlit's native ``:material/...:`` shortcode (never raw HTML
    in widget labels). The active page is highlighted by injecting a scoped
    style rule targeting the widget's ``st-key-*`` class.
    """
    for title, (icon_name, _, _) in MODULE_META.items():
        active = title == current_page
        if st.button(
            title,
            icon=f":material/{icon_name}:",
            key=f"nav_{title}",
            type="primary" if active else "secondary",
            use_container_width=True,
        ):
            st.session_state.page = title
            st.rerun()

    if current_page:
        key_class = re.sub(r"[^a-zA-Z0-9_-]", "-", f"nav_{current_page}".strip())
        st.markdown(
            f"<style>"
            f'section[data-testid="stSidebar"] [class*="st-key-{key_class}"]:has(button) button, '
            f'section[data-testid="stSidebar"] button[class*="st-key-{key_class}"] {{'
            f"background: rgba(255,255,255,0.16) !important;"
            f"box-shadow: inset 3px 0 0 #f59e0b !important;"
            f"}}"
            f'section[data-testid="stSidebar"] [class*="st-key-{key_class}"] button .stIconMaterial, '
            f'section[data-testid="stSidebar"] button[class*="st-key-{key_class}"] .stIconMaterial {{'
            f"color:#f59e0b !important;"
            f"}}"
            f"</style>",
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════
#  LOGIN / REGISTRATION
# ══════════════════════════════════════════════════════════════════
def render_login_screen() -> None:
    """Render the login/register card. Calls ``st.stop()`` when not authenticated."""
    st.markdown('<div class="login-shell">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="login-card">'
        f'<div class="login-logo">{material_icon("oil_barrel", size="1.9rem", color="#ffffff")}</div>'
        f'<div class="login-title">PyMudCement-Optima</div>'
        f'<div class="login-sub">Intelligent Mud &amp; Cement Design Suite</div>'
        f"</div>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    auth_mode = st.radio(
        "Have an account?",
        ["Login", "Register"],
        horizontal=True,
        key="auth_mode",
    )

    if auth_mode == "Login":
        username = st.text_input("Username", key="login_user", placeholder="Enter your username")
        password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password")

        if st.button("Login", icon=":material/login:", key="login_btn", type="primary", use_container_width=True):
            if username and password:
                full_name = authenticate(username, password)
                if full_name:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.full_name = full_name
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
            else:
                st.warning("Please enter both username and password.")
    else:
        new_user = st.text_input("Username", key="reg_user", placeholder="Choose a username")
        new_full = st.text_input("Full Name", key="reg_name", placeholder="e.g. Kofi Mensah")
        new_pass = st.text_input("Password", type="password", key="reg_pass", placeholder="Minimum 6 characters")
        new_pass2 = st.text_input("Confirm Password", type="password", key="reg_pass2", placeholder="Repeat your password")

        if st.button("Register", icon=":material/person_add:", key="reg_btn", type="primary", use_container_width=True):
            if not (new_user and new_pass):
                st.warning("Username and password are required.")
            elif len(new_pass) < 6:
                st.warning("Password must be at least 6 characters.")
            elif new_pass != new_pass2:
                st.error("Passwords do not match.")
            else:
                if create_user(new_user, new_pass, new_full):
                    st.success(f"Account created. You can now log in as **{new_user}**.")
                else:
                    st.error("That username is already taken.")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()
