"""Module 6 · P&A / Suspension / Sidetrack Plug Design page."""

import streamlit as st

from src.core.cementing_engine import PAPLugDesign
from src.gui.components import hero, section_label
from src.gui.units import PA_PER_PSI, get_units


def render() -> None:
    u = get_units()
    hero(
        "engineering",
        "Plug & Abandonment / Suspension / Sidetrack Design",
        "Design cement plugs for well suspension, open-hole sidetracking, "
        "or plug and abandonment (P&A) operations.",
    )

    section_label("Operation Type")
    plug_type = st.radio(
        "Select Plug Type", ["Suspension Plug", "Sidetrack Plug", "Abandonment Plug"],
        horizontal=True,
    )

    section_label("Geometry")
    c1, c2 = st.columns(2)
    with c1:
        ch = st.number_input("Open Hole Diameter (in)", 6.0, 30.0, 12.25, 0.125, key="pph")
        cc = st.number_input("Casing Outer Diameter (in)", 4.0, 20.0, 9.625, 0.125, key="ppc")
        pl_in = st.number_input(
            f"Plug Length ({u.depth})",
            u.len_from_si(5.0), u.len_from_si(500.0), u.len_from_si(50.0), 5.0, key="ppl",
        )
    with c2:
        cd_in = st.number_input(
            f"Cement Slurry Density ({u.density})",
            u.density_from_si(1500.0), u.density_from_si(2200.0), u.density_from_si(1900.0),
            0.1 if u.field else 10.0, key="pcd",
        )
        sidetrack_depth = 0.0
        abandon_top = 0.0
        abandon_bottom = 0.0
        if plug_type == "Abandonment Plug":
            abandon_top = u.len_to_si(st.number_input(
                f"Plug Top Depth ({u.depth})", 0.0, u.len_from_si(10000.0),
                u.len_from_si(1000.0), 100.0, key="ptd",
            ))
            abandon_bottom = u.len_to_si(st.number_input(
                f"Plug Bottom Depth ({u.depth})", 0.0, u.len_from_si(10000.0),
                u.len_from_si(1050.0), 100.0, key="pbd",
            ))
        if plug_type == "Sidetrack Plug":
            sidetrack_depth = u.len_to_si(st.number_input(
                f"Casing Shoe Depth ({u.depth})", 0.0, u.len_from_si(10000.0),
                u.len_from_si(1000.0), 100.0, key="psd",
            ))

    if st.button("Design Cement Plug", key="dp", type="primary"):
        with st.spinner("Designing cement plug…"):
            plug_length = u.len_to_si(pl_in)
            cement_density = u.density_to_si(cd_in)
            if plug_type == "Suspension Plug":
                result = PAPLugDesign.design_suspension_plug(ch, cc, plug_length, cement_density)
            elif plug_type == "Sidetrack Plug":
                result = PAPLugDesign.design_sidetrack_plug(ch, cc, plug_length, cement_density, sidetrack_depth)
            else:
                result = PAPLugDesign.design_abandonment_plug(
                    ch, cc, plug_length, abandon_top, abandon_bottom, cement_density,
                )

        st.subheader(f"{plug_type} — Design Results")

        def display_value(key: str, value):
            """Convert an engine result key/value into (label, display value, unit)."""
            if key.endswith("_m3"):
                return key[:-3], u.volume_from_si(value), u.volume
            if key.endswith("_m2"):
                return key[:-3], u.area_from_si(value), u.area
            if key.endswith("_kg_m3"):
                return key[:-6], u.density_from_si(value), u.density
            if key.endswith("_pa"):
                return key[:-3], u.pressure_display_from_si(value), u.pressure_display
            if key.endswith("_psi"):
                return key[:-4], u.pressure_display_from_si(value * PA_PER_PSI), u.pressure_display
            if key.endswith("_m"):
                return key[:-2], u.len_from_si(value), u.depth
            return key, value, None

        keys = list(result.items())
        for row_start in range(0, len(keys), 3):
            trio = keys[row_start:row_start + 3]
            cols = st.columns(3)
            for i, (k, v) in enumerate(trio):
                label, dval, unit = display_value(k, v)
                label = label.replace("_", " ").title()
                if unit:
                    label = f"{label} ({unit})"
                if isinstance(dval, float):
                    if dval < 1 and dval != 0:
                        value = f"{dval:.6f}"
                    elif dval > 10000:
                        value = f"{dval:,.1f}"
                    else:
                        value = f"{dval:.2f}"
                elif isinstance(dval, int):
                    value = f"{dval:,}"
                else:
                    value = str(dval)
                cols[i].metric(label, value)
