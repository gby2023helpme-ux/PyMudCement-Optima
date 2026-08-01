"""GUI page modules package.

Exposes the page router (``render_page``) and the current-page resolver
(``get_current_page``). Individual pages live in this package and register
their metadata in :mod:`src.gui.registry`.
"""

import streamlit as st

from src.gui.registry import MODULE_META
from src.gui.modules.home import render as render_home
from src.gui.modules.pressure_balance import render as render_pressure_balance
from src.gui.modules.mud_report_parser import render as render_mud_report_parser
from src.gui.modules.annular_hydraulics import render as render_annular_hydraulics
from src.gui.modules.system_hydraulics import render as render_system_hydraulics
from src.gui.modules.slurry_design import render as render_slurry_design
from src.gui.modules.procedure_sheet import render as render_procedure_sheet
from src.gui.modules.plug_design import render as render_plug_design


def get_current_page() -> str:
    """Resolve the active page name from ``st.session_state.page``."""
    page = st.session_state.get("page", "Home")
    return page if page in MODULE_META else "Home"


def render_page(page: str) -> None:
    """Dispatch rendering to the page module matching ``page``."""
    if page == "Home":
        render_home()
    elif page == "Pressure Balance":
        render_pressure_balance()
    elif page == "Mud Report Parser":
        render_mud_report_parser()
    elif page == "Annular Hydraulics & ECD":
        render_annular_hydraulics()
    elif page == "System Hydraulics":
        render_system_hydraulics()
    elif page == "Cement Slurry Design":
        render_slurry_design()
    elif page == "Cementing Procedure Sheet":
        render_procedure_sheet()
    elif page == "P&A Plug Design":
        render_plug_design()
    else:
        render_home()
