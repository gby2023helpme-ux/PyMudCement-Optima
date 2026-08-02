"""Design system for the PyMudCement-Optima Streamlit GUI.

Centralizes the page configuration, the global Plotly template, and the
full stylesheet (Inter font + Google Material Symbols webfont) so every
page renders with an identical look and feel.
"""

from pathlib import Path

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# ── Brand palette ──────────────────────────────────────────────────────
NAVY = "#0f2a43"
PRIMARY = "#1d4ed8"
PRIMARY_LIGHT = "#2563eb"
ACCENT = "#f59e0b"
BG = "#f4f6fb"

PAGE_TITLE = "PyMudCement-Optima"

FAVICON_PATH = Path(__file__).resolve().parents[2] / "assets" / "favicon.svg"

# ── Page config ────────────────────────────────────────────────────────
def setup_page_config() -> None:
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=str(FAVICON_PATH),
        layout="wide",
        initial_sidebar_state="expanded",
    )


# ── Global Plotly theme ────────────────────────────────────────────────
def setup_plotly_theme() -> None:
    pio.templates["optima"] = go.layout.Template(
        layout=go.Layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#ffffff",
            font=dict(family="Inter, -apple-system, sans-serif", size=13, color="#334155"),
            title=dict(font=dict(color=NAVY, size=18, family="Inter, sans-serif")),
            xaxis=dict(
                gridcolor="#e2e8f0",
                zerolinecolor="#cbd5e1",
                linecolor="#cbd5e1",
                title_font=dict(color=NAVY),
                tickfont=dict(color="#475569"),
            ),
            yaxis=dict(
                gridcolor="#e2e8f0",
                zerolinecolor="#cbd5e1",
                linecolor="#cbd5e1",
                title_font=dict(color=NAVY),
                tickfont=dict(color="#475569"),
            ),
            legend=dict(font=dict(color="#475569"), bgcolor="rgba(0,0,0,0)"),
            colorway=["#1d4ed8", "#0ea5e9", "#f59e0b", "#10b981", "#6366f1", "#0f2a43", "#ef4444", "#8b5cf6"],
            hoverlabel=dict(
                bgcolor=NAVY,
                font=dict(color="#ffffff", family="Inter, sans-serif"),
            ),
            margin=dict(l=60, r=30, t=70, b=50),
        )
    )
    pio.templates.default = "optima"


# ── Stylesheet ─────────────────────────────────────────────────────────
DESIGN_SYSTEM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap');

/* ── Global ─────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
.stApp {
    background:
        radial-gradient(1200px 400px at 85% -5%, rgba(14,165,233,0.10), transparent 60%),
        radial-gradient(1000px 500px at -10% 0%, rgba(245,158,11,0.07), transparent 55%),
        #f4f6fb;
}
.block-container { padding-top: 1.8rem; padding-bottom: 3rem; }

/* ── Google Material Symbols ────────────────────────────── */
.material-symbols-rounded {
    font-family: 'Material Symbols Rounded';
    font-weight: normal;
    font-style: normal;
    line-height: 1;
    letter-spacing: normal;
    text-transform: none;
    display: inline-block;
    white-space: nowrap;
    word-wrap: normal;
    direction: ltr;
    -webkit-font-smoothing: antialiased;
    vertical-align: middle;
}

/* ── Scrollbar ──────────────────────────────────────────── */
::-webkit-scrollbar { width: 9px; height: 9px; }
::-webkit-scrollbar-track { background: #eef2f7; }
::-webkit-scrollbar-thumb { background: #94a3b8; border-radius: 6px; }
::-webkit-scrollbar-thumb:hover { background: #64748b; }

/* ── Hero banner ────────────────────────────────────────── */
.hero {
    background: linear-gradient(120deg, #0f2a43 0%, #1d4ed8 70%, #2563eb 100%);
    border-radius: 16px;
    padding: 1.9rem 2.2rem;
    margin-bottom: 1.6rem;
    display: flex;
    align-items: center;
    gap: 1.2rem;
    box-shadow: 0 10px 30px rgba(15,42,67,0.25);
    position: relative;
    overflow: hidden;
}
.hero::after {
    content: "";
    position: absolute; inset: 0;
    background: radial-gradient(500px 200px at 90% 0%, rgba(255,255,255,0.14), transparent 60%);
}
.hero-icon {
    font-size: 2.8rem;
    display: flex; align-items: center;
    filter: drop-shadow(0 4px 8px rgba(0,0,0,0.25));
    position: relative; z-index: 1;
}
.hero-icon .material-symbols-rounded {
    color: #ffffff !important;
}
.hero-title { color: #ffffff !important; font-size: 1.7rem; font-weight: 800; margin: 0; letter-spacing: -0.02em; position: relative; z-index: 1; }
.hero-sub { color: #c7dbf5 !important; margin: 0.2rem 0 0; font-size: 0.95rem; font-weight: 400; position: relative; z-index: 1; }

/* ── Section cards ──────────────────────────────────────── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    box-shadow: 0 2px 10px rgba(15,42,67,0.06);
    padding: 0.2rem 0.4rem;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: 0 6px 18px rgba(15,42,67,0.10);
}

.section-label {
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; color: #1d4ed8;
    margin: 1rem 0 0.2rem 0.2rem;
}

/* ── Headings ───────────────────────────────────────────── */
h1, h2, h3 { color: #0f2a43 !important; letter-spacing: -0.01em; }
h2 { font-size: 1.35rem !important; font-weight: 700 !important; }
h3 { font-size: 1.1rem !important; font-weight: 600 !important; }
p, span, .stMarkdown { color: #334155 !important; }
caption, .stCaption, .stCaption p,
[data-testid="stCaptionContainer"] p { color: #64748b !important; }

/* ── Sidebar ────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f2a43 0%, #143b63 55%, #1d4ed8 130%);
    border-right: 1px solid rgba(255,255,255,0.06);
}
section[data-testid="stSidebar"] > div { padding-top: 1.2rem; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stRadio label,
section[data-testid="stSidebar"] .stRadio > div > div,
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown span,
section[data-testid="stSidebar"] .stMarkdown li,
section[data-testid="stSidebar"] .stCaption p,
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
    color: #ffffff !important;
}
.sidebar-brand {
    display: flex; align-items: center; gap: 0.7rem;
    padding: 0.4rem 0.2rem 0.9rem; border-bottom: 1px solid rgba(255,255,255,0.15);
    margin-bottom: 0.9rem;
}
.sidebar-brand .logo {
    width: 40px; height: 40px; flex: 0 0 40px;
    border-radius: 11px; display: flex; align-items: center; justify-content: center;
    background: rgba(255,255,255,0.12);
}
.sidebar-brand .name { color: #ffffff; font-weight: 800; font-size: 1.02rem; line-height: 1.15; }
.sidebar-brand .tag { color: #9db8e8; font-size: 0.68rem; letter-spacing: 0.08em; text-transform: uppercase; }
.user-chip {
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.16);
    border-radius: 11px; padding: 0.6rem 0.8rem; margin: 0.4rem 0 1rem;
    display: flex; align-items: center; gap: 0.6rem;
}
.user-chip .avatar {
    width: 30px; height: 30px; flex: 0 0 30px; border-radius: 50%;
    background: linear-gradient(135deg, #f59e0b, #f97316);
    color: #ffffff; display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 0.85rem;
}
.user-chip .u-name { color: #ffffff; font-weight: 600; font-size: 0.85rem; line-height: 1.2; }
.user-chip .u-role { color: #9db8e8; font-size: 0.68rem; }

/* ── Sidebar navigation buttons ─────────────────────────── */
section[data-testid="stSidebar"] .stButton,
section[data-testid="stSidebar"] .stButton > div {
    width: 100%;
}
section[data-testid="stSidebar"] .stButton button {
    width: 100%;
    justify-content: flex-start !important;
    text-align: left;
    background: transparent !important;
    border: none !important;
    color: #ffffff !important;
    border-radius: 9px !important;
    padding: 0.5rem 0.7rem !important;
    margin: 2px 0 !important;
    box-shadow: none !important;
    font-weight: 500 !important;
    transition: background 0.15s ease;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(255,255,255,0.10) !important;
}
section[data-testid="stSidebar"] .stButton button p { margin: 0; width: 100%; text-align: left; }
section[data-testid="stSidebar"] .stButton button .stIconMaterial { color: #9db8e8; }
.sidebar-footer { margin-top: 1.4rem; padding-top: 0.8rem; border-top: 1px solid rgba(255,255,255,0.15); }
.sidebar-footer .stButton button {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 9px !important;
    justify-content: center !important; text-align: center;
    color: #ffffff !important; font-weight: 600 !important;
}
.sidebar-footer .stButton button .stIconMaterial { color: #ffffff !important; }

/* ── Unit system selector ───────────────────────────────── */
.sidebar-mini-label {
    margin: 0.6rem 0 0.3rem;
    font-size: 0.62rem;
    letter-spacing: 0.12em;
    font-weight: 700;
    color: #9db8e8;
}
section[data-testid="stSidebar"] [data-testid="stSegmentedControl"] label { color: #dbe7f7 !important; }
section[data-testid="stSidebar"] [data-testid="stSegmentedControl"] button {
    color: #dbe7f7 !important;
    border: 1px solid rgba(255,255,255,0.22) !important;
    background: rgba(255,255,255,0.05) !important;
    border-radius: 8px !important;
    font-size: 0.8rem !important;
    padding: 0.25rem 0.6rem !important;
}
section[data-testid="stSidebar"] [data-testid="stSegmentedControl"] button:hover {
    background: rgba(255,255,255,0.12) !important;
}
section[data-testid="stSidebar"] [data-testid="stSegmentedControl"] button[aria-checked="true"] {
    background: #1d4ed8 !important;
    border-color: #1d4ed8 !important;
    color: #ffffff !important;
}

/* ── Tabs ───────────────────────────────────────────────── */
button[data-baseweb="tab"] {
    background: #eef2f7; color: #475569 !important; font-weight: 600;
    border-radius: 9px 9px 0 0; margin-right: 4px; padding: 0.5rem 1.1rem;
}
button[data-baseweb="tab"]:hover { color: #0f2a43 !important; background: #e2e8f0; }
button[data-baseweb="tab"][aria-selected="true"] {
    color: #1d4ed8 !important; background: #ffffff !important;
    box-shadow: 0 -2px 0 #1d4ed8 inset, 0 1px 4px rgba(15,42,67,0.08);
}

/* ── Metric cards ───────────────────────────────────────── */
div[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 0.85rem 1rem;
    box-shadow: 0 2px 8px rgba(15,42,67,0.05);
    position: relative;
    overflow: hidden;
}
div[data-testid="stMetric"]::before {
    content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 4px;
    background: linear-gradient(180deg, #1d4ed8, #0ea5e9);
}
div[data-testid="stMetric"] label {
    color: #64748b !important; font-weight: 600; font-size: 0.75rem !important;
    letter-spacing: 0.02em; text-transform: uppercase;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #0f2a43 !important; font-weight: 800; font-size: 1.45rem !important;
    font-variant-numeric: tabular-nums;
}
div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {
    color: #10b981 !important; font-size: 0.75rem !important;
}

/* ── Buttons ────────────────────────────────────────────── */
button[kind="primary"],
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%) !important;
    color: #ffffff !important;
    border: none !important; border-radius: 10px !important;
    padding: 0.6rem 1.6rem !important; font-weight: 600 !important;
    box-shadow: 0 4px 12px rgba(29,78,216,0.28);
    transition: all 0.15s ease;
}
button[kind="primary"]:hover,
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #1e40af 0%, #1d4ed8 100%) !important;
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(29,78,216,0.35);
}
button[kind="primary"] p,
button[kind="primary"] span,
button[kind="primary"] [data-testid="stButtonLabel"],
.stButton > button[kind="primary"] p,
.stButton > button[kind="primary"] span,
.stButton > button[kind="primary"] [data-testid="stButtonLabel"] {
    color: #ffffff !important;
}
.stButton > button:not([kind="primary"]) {
    background: #ffffff !important;
    color: #1d4ed8 !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.15s ease;
}
.stButton > button:not([kind="primary"]):hover {
    background: #eff6ff !important;
    border-color: #93c5fd !important;
    color: #1e40af !important;
}

/* ── Module cards (dashboard) ───────────────────────────── */
div.module-grid [data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    box-shadow: 0 2px 8px rgba(15,42,67,0.05);
    padding: 1.1rem 1.2rem !important;
    transition: all 0.18s ease;
}
div.module-grid [data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-4px);
    border-color: #1d4ed8;
    box-shadow: 0 12px 26px rgba(29,78,216,0.18);
    background: linear-gradient(180deg, #ffffff, #f0f6ff);
}
div.module-grid .mc-card {
    display: flex; flex-direction: column; gap: 0.2rem;
    margin-bottom: 0.7rem;
}
div.module-grid .mc-card .mc-icon { display: flex; align-items: center; margin-bottom: 0.4rem; }
div.module-grid .mc-card .mc-title { font-size: 1.0rem; font-weight: 700; color: #0f2a43; line-height: 1.25; }
div.module-grid .mc-card .mc-desc { font-size: 0.78rem; color: #64748b; line-height: 1.4; }
div.module-grid .stButton > button { width: 100%; }

/* ── Status pills ───────────────────────────────────────── */
.pill {
    display: inline-block; padding: 0.2rem 0.7rem; border-radius: 999px;
    font-size: 0.72rem; font-weight: 600; letter-spacing: 0.02em; white-space: nowrap;
}
.pill-ok   { background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }
.pill-warn { background: #fffbeb; color: #92400e; border: 1px solid #fde68a; }
.pill-danger{background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
.pill-info { background: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; }

/* ── Alerts ─────────────────────────────────────────────── */
div[data-testid="stAlert"] { border-radius: 10px; border: none; }
div[data-testid="stAlert"][kind="error"]   { background: #fef2f2; border-left: 5px solid #ef4444; color: #7f1d1d !important; }
div[data-testid="stAlert"][kind="success"] { background: #f0fdf4; border-left: 5px solid #22c55e; color: #14532d !important; }
div[data-testid="stAlert"][kind="warning"] { background: #fffbeb; border-left: 5px solid #f59e0b; color: #78350f !important; }
div[data-testid="stAlert"][kind="info"]    { background: #eff6ff; border-left: 5px solid #3b82f6; color: #1e3a8a !important; }

/* ── Expanders ──────────────────────────────────────────── */
details { border: 1px solid #e2e8f0 !important; border-radius: 12px; background: #ffffff; }
details summary,
[data-testid="stExpander"] summary {
    background: linear-gradient(90deg, #0f2a43, #1d4ed8) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-weight: 600 !important;
    border-radius: 12px;
}
details summary:hover { filter: brightness(1.1); }
details[open] { border-color: #1d4ed8 !important; box-shadow: 0 3px 12px rgba(15,42,67,0.10); }

/* ── Form controls ──────────────────────────────────────── */
.stNumberInput label, .stSlider label, .stSelectbox label,
.stMultiSelect label, .stTextArea label, .stFileUploader label {
    color: #0f2a43 !important; font-weight: 600; font-size: 0.86rem;
}
.stNumberInput input, .stTextInput input,
[data-baseweb="input"] input, [data-baseweb="numberinput"] input {
    color: #0f2a43 !important; font-weight: 600 !important;
    background-color: #ffffff !important;
    -webkit-text-fill-color: #0f2a43 !important;
}
[data-baseweb="input"], [data-baseweb="select"], [data-baseweb="textarea"] {
    border-color: #cbd5e1 !important;
}
[data-baseweb="input"]:focus-within, [data-baseweb="select"]:focus-within,
[data-baseweb="textarea"]:focus-within {
    border-color: #1d4ed8 !important;
    box-shadow: 0 0 0 3px rgba(29,78,216,0.15) !important;
}
.stSlider [data-baseweb="thumb"] { background-color: #1d4ed8 !important; border-color: #ffffff !important; }
.stSlider [data-baseweb="thumb"] + div,
.stSlider [data-baseweb="thumb"] + div span { color: #0f2a43 !important; -webkit-text-fill-color: #0f2a43 !important; }
.stSlider [role="slider"] ~ div { background-color: #bfdbfe !important; }
.stSlider [role="slider"] { background-color: #1d4ed8 !important; }
.stRadio > div > div > label { color: #0f2a43 !important; font-weight: 500; }
.stRadio [data-baseweb="radio"] input:checked ~ div {
    background-color: #1d4ed8 !important; border-color: #1d4ed8 !important;
}
.stRadio label:has(input:checked) p,
.stRadio label:has(input:checked) span,
.stRadio [data-baseweb="radio"] input:checked ~ p,
.stRadio [data-baseweb="radio"] input:checked ~ span {
    color: #ffffff !important;
}

/* ── File uploader ──────────────────────────────────────── */
.stFileUploader [data-testid="stFileUploadDropzone"] {
    border: 2px dashed #93c5fd !important; background: #f5f9ff !important;
    border-radius: 12px !important;
}
.stFileUploader [data-testid="stFileUploadDropzone"] p,
.stFileUploader [data-testid="stFileUploadDropzone"] span,
.stFileUploader [data-testid="stFileUploadDropzone"] small,
.stFileUploader [data-testid="stFileUploadDropzone"] div,
.stFileUploader [data-testid="stFileUploadDropzone"] svg {
    color: #1e40af !important; -webkit-text-fill-color: #1e40af !important;
}
.stFileUploader [data-testid="stFileUploadDropzone"] strong { color: #0f2a43 !important; }

/* ── DataFrames ─────────────────────────────────────────── */
.stDataFrame { border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; }
.stDataFrame [role="columnheader"] {
    color: #0f2a43 !important; font-weight: 700;
    background: linear-gradient(180deg, #eff6ff, #e0edff) !important;
}

/* ── Plotly charts ──────────────────────────────────────── */
.stPlotlyChart { background: #ffffff; border-radius: 12px; padding: 4px; border: 1px solid #e2e8f0; }

/* ── Login card ─────────────────────────────────────────── */
.login-shell { max-width: 460px; margin: 0 auto; }
[data-testid="stMainBlockContainer"]:has(.login-shell) {
    max-width: 480px !important;
    margin: 0 auto !important;
    min-height: 100vh !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    padding-top: 3rem !important;
    padding-bottom: 1.5rem !important;
}
.login-card {
    background: #ffffff; border-radius: 18px; padding: 2rem 2.2rem;
    border: 1px solid #e2e8f0; box-shadow: 0 16px 44px rgba(15,42,67,0.14);
}
.login-logo {
    color:#ffffff;
    width: 62px; height: 62px; margin: 0 auto 0.9rem; border-radius: 16px;
    background: linear-gradient(135deg, #0f2a43, #1d4ed8);
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 8px 20px rgba(29,78,216,0.35);
}
.login-logo .material-symbols-rounded,
.sidebar-brand .logo .material-symbols-rounded {
    color: #ffffff !important;
}
.login-title { text-align: center; color: #0f2a43; font-weight: 800; font-size: 1.35rem; margin-bottom: 0.2rem; }
.login-sub { text-align: center; color: #64748b !important; font-size: 0.82rem; margin-bottom: 1.2rem; }

/* ── Footer ─────────────────────────────────────────────── */
.app-footer {
    margin-top: 2.5rem; padding: 1.1rem 0 0.4rem; text-align: center;
    border-top: 1px solid #e2e8f0; color: #94a3b8 !important; font-size: 0.75rem;
}
.app-footer b { color: #64748b !important; }
"""


def inject_design_system_css() -> None:
    st.markdown(f"<style>{DESIGN_SYSTEM_CSS}</style>", unsafe_allow_html=True)


def apply_theme() -> None:
    """One-shot setup: page config, Plotly theme, and stylesheet."""
    setup_page_config()
    setup_plotly_theme()
    inject_design_system_css()
