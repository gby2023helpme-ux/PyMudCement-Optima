"""Module 5 · Cementing Job Procedure Sheet page."""

import pandas as pd
import plotly.express as px
import streamlit as st

from src.core.cementing_engine import CementingEngine, SlurryDesignRequest
from src.gui.components import hero, section_label
from src.gui.units import get_units


def render() -> None:
    u = get_units()
    hero(
        "description",
        "Cementing Job Procedure Sheet",
        "Generate a stage-by-stage cementing procedure with volumes, pump rates, "
        "and durations.",
    )

    section_label("Wellbore Parameters")
    c1, c2 = st.columns(2)
    with c1:
        ch = st.number_input("Open Hole Diameter (in)", 6.0, 30.0, 12.25, 0.125, key="ph")
        cc = st.number_input("Casing Outer Diameter (in)", 4.0, 20.0, 9.625, 0.125, key="pc")
        cl_in = st.number_input(
            f"Cemented Interval Length ({u.depth})",
            u.len_from_si(10.0), u.len_from_si(2000.0), u.len_from_si(200.0), 10.0, key="pl",
        )
    with c2:
        bht_in = st.number_input(
            f"Bottomhole Circulating Temperature ({u.temperature})",
            u.temp_from_si(20.0), u.temp_from_si(300.0), u.temp_from_si(120.0), 5.0, key="pt",
        )
        td_in = st.number_input(
            f"Target Slurry Density ({u.density})",
            u.density_from_si(1000.0), u.density_from_si(2200.0), u.density_from_si(1900.0),
            0.1 if u.field else 10.0, key="pd",
        )
        pr_in = st.number_input(
            f"Surface Pump Rate ({u.pump_rate})",
            u.pump_from_si(50.0), u.pump_from_si(1000.0), u.pump_from_si(200.0),
            0.1 if u.field else 10.0, key="ppr",
        )

    section_label("Pre-Flush Volumes")
    c1, c2 = st.columns(2)
    with c1:
        sv_in = st.number_input(
            f"Spacer Volume ({u.volume})", 0.0, u.volume_from_si(10.0),
            u.volume_from_si(2.0), 0.5 if u.field else 0.1, key="psv",
        )
    with c2:
        fv_in = st.number_input(
            f"Flush Volume ({u.volume})", 0.0, u.volume_from_si(10.0),
            u.volume_from_si(1.5), 0.5 if u.field else 0.1, key="pfv",
        )

    if st.button("Generate Procedure Sheet", key="gps", type="primary"):
        req = SlurryDesignRequest(
            hole_diameter_in=ch, casing_od_in=cc, cemented_length_m=u.len_to_si(cl_in),
            bottomhole_temp_c=u.temp_to_si(bht_in), target_density_kg_m3=u.density_to_si(td_in),
        )
        with st.spinner("Generating procedure…"):
            design = CementingEngine.design_slurry(req)
            proc = CementingEngine.generate_procedure(
                design, pump_rate_lpm=u.pump_to_si(pr_in),
                spacer_volume_m3=u.volume_to_si(sv_in), flush_volume_m3=u.volume_to_si(fv_in),
            )

        st.subheader("Procedure Sheet")
        df_proc = pd.DataFrame([{
            "Stage": p.stage,
            f"Volume ({u.volume})": u.volume_from_si(p.volume_m3),
            f"Density ({u.density})": u.density_from_si(p.density_kg_m3),
            f"Pump Rate ({u.pump_rate})": u.pump_from_si(p.pump_rate_lpm),
            "Duration (min)": p.duration_min,
            f"Cumulative Volume ({u.volume})": u.volume_from_si(p.cumulative_volume_m3),
            "Operational Notes": p.notes,
        } for p in proc])
        st.dataframe(df_proc, use_container_width=True)

        total_time = sum(p.duration_min for p in proc)
        total_vol = sum(p.volume_m3 for p in proc)

        c1, c2 = st.columns(2)
        c1.metric("Total Pump Time", f"{total_time:.1f} min")
        c2.metric("Total Fluid Volume", f"{u.volume_from_si(total_vol):.4f} {u.volume}")

        st.subheader("Stage Duration Timeline")
        fig = px.bar(
            df_proc, x="Stage", y="Duration (min)",
            color="Stage", title="Pump Time by Stage",
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        if design.warnings:
            st.subheader("Engineering Warnings")
            for w in design.warnings:
                st.warning(w)
