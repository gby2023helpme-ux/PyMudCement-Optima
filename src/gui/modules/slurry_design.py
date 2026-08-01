"""Module 4 · Cement Slurry Design page."""

import pandas as pd
import streamlit as st

from src.core.cementing_engine import ADDITIVE_DATABASE, CementingEngine, SlurryDesignRequest
from src.gui.components import hero, section_label
from src.gui.units import get_units


def render() -> None:
    u = get_units()
    hero(
        "science",
        "Cement Slurry Design",
        "Design a primary cement slurry with automated additive selection "
        "based on wellbore conditions.",
    )

    section_label("Wellbore Parameters")
    c1, c2 = st.columns(2)
    with c1:
        ch = st.number_input("Open Hole Diameter (in)", 6.0, 30.0, 12.25, 0.125)
        cc = st.number_input("Casing Outer Diameter (in)", 4.0, 20.0, 9.625, 0.125)
        cl_in = st.number_input(
            f"Cemented Interval Length ({u.depth})",
            u.len_from_si(10.0), u.len_from_si(2000.0), u.len_from_si(200.0), 10.0,
        )
    with c2:
        bht_in = st.number_input(
            f"Bottomhole Circulating Temperature ({u.temperature})",
            u.temp_from_si(20.0), u.temp_from_si(300.0), u.temp_from_si(120.0), 5.0,
        )
        td_in = st.number_input(
            f"Target Slurry Density ({u.density})",
            u.density_from_si(1000.0), u.density_from_si(2200.0), u.density_from_si(1900.0),
            0.1 if u.field else 10.0,
        )
        wr = st.number_input("Water-to-Cement Ratio", 0.30, 0.80, 0.44, 0.01)

    section_label("Job Parameters")
    c1, c2 = st.columns(2)
    with c1:
        excess = st.slider("Open-Hole Excess Factor (%)", 0, 50, 15) / 100.0
    with c2:
        pt = st.number_input("Required Pump Time (min)", 10.0, 180.0, 45.0, 5.0)

    if st.button("Design Cement Slurry", key="dsr", type="primary"):
        req = SlurryDesignRequest(
            hole_diameter_in=ch, casing_od_in=cc, cemented_length_m=u.len_to_si(cl_in),
            bottomhole_temp_c=u.temp_to_si(bht_in), target_density_kg_m3=u.density_to_si(td_in),
            water_ratio=wr, excess_factor=excess, pump_time_min=pt,
        )
        with st.spinner("Designing slurry…"):
            result = CementingEngine.design_slurry(req)

        st.subheader("Volume Summary")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Slurry Volume", f"{u.volume_from_si(result.slurry_volume_m3):.4f} {u.volume}")
        c2.metric("Cement Volume", f"{u.volume_from_si(result.cement_volume_m3):.4f} {u.volume}")
        c3.metric("Mix Water Volume", f"{u.volume_from_si(result.water_volume_m3):.4f} {u.volume}")

        st.subheader("Slurry Properties")
        c1, c2, c3 = st.columns(3)
        c1.metric("Achieved Slurry Density", f"{u.density_from_si(result.total_density_kg_m3):.1f} {u.density}")
        c2.metric("Thickening Time", f"{result.thickening_time_min:.1f} min")
        c3.metric("24h Compressive Strength", f"{u.strength_from_si(result.compressive_strength_mpa):.2f} {u.strength}")

        if result.additive_plan:
            st.subheader("Recommended Additive Schedule")
            st.dataframe(pd.DataFrame(result.additive_plan), use_container_width=True)

        if result.warnings:
            st.subheader("Engineering Warnings")
            for w in result.warnings:
                st.warning(w)

        with st.expander("Additive Database Reference", expanded=False):
            st.dataframe(pd.DataFrame([{
                "Additive Name": a.name,
                "Category": a.category.value,
                f"Dosage Range ({u.concentration})": (
                    f"{u.concentration_from_si(a.dosage_range_kg_m3[0]):.2f} – "
                    f"{u.concentration_from_si(a.dosage_range_kg_m3[1]):.2f}"
                ),
                f"Max Temperature ({u.temperature})": u.temp_from_si(a.max_temperature_c),
                "Specific Gravity": a.specific_gravity,
            } for a in ADDITIVE_DATABASE]), use_container_width=True)
