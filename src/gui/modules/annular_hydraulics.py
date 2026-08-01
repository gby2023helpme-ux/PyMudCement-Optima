"""Module 3 · Annular Hydraulics & Equivalent Circulating Density page."""

import math

import plotly.express as px
import streamlit as st

from src.core.engineering_calculators import AnnularHydraulics
from src.core.models import AnnularGeometry
from src.gui.components import hero, section_label
from src.gui.units import get_units


def render() -> None:
    u = get_units()
    hero(
        "speed",
        "Annular Hydraulics & Equivalent Circulating Density",
        "Calculate annular volume, fluid velocity, and ECD for a given casing "
        "and hole configuration.",
    )

    section_label("Geometry")
    c1, c2 = st.columns(2)
    with c1:
        casing_in = st.number_input("Casing Outer Diameter (in)", 0.1, 30.0, 9.625, 0.125)
        hole_in = st.number_input("Open Hole Diameter (in)", 0.1, 30.0, 12.25, 0.125)
        length = st.number_input(
            f"Cemented Interval Length ({u.depth})",
            u.len_from_si(1.0), u.len_from_si(5000.0), u.len_from_si(200.0), 10.0,
        )
    with c2:
        washout = st.slider("Hole Washout Factor (%)", 0, 50, 15) / 100.0
        mud_dens_in = st.number_input(
            f"Mud Density ({u.density})",
            u.density_from_si(500.0), u.density_from_si(2500.0), u.density_from_si(1200.0),
            0.1 if u.field else 10.0,
        )
        tvd = st.number_input(
            f"True Vertical Depth ({u.depth})",
            u.len_from_si(100.0), u.len_from_si(10000.0), u.len_from_si(2000.0), 100.0,
        )

    flow_in = st.number_input(
        f"Surface Flow Rate ({u.flow_rate})",
        u.flow_from_si(1.0), u.flow_from_si(100.0), u.flow_from_si(30.0),
        10.0 if u.field else 1.0,
    )

    if st.button("Calculate Annular Hydraulics", key="cah", type="primary"):
        flow_m3_s = u.flow_to_si(flow_in) / 1000.0
        mud_dens = u.density_to_si(mud_dens_in)
        tvd_si = u.len_to_si(tvd)
        geom = AnnularGeometry(
            casing_diameter_in=casing_in, hole_diameter_in=hole_in,
            cemented_interval_length_m=u.len_to_si(length), wash_out_factor=washout,
        )
        vol = AnnularHydraulics.calculate_annular_volume(geom)
        vel = AnnularHydraulics.calculate_fluid_velocity(
            flow_m3_s, geom.hole_diameter_m, geom.casing_diameter_m,
        )
        area = (math.pi / 4) * (geom.hole_diameter_m ** 2 - geom.casing_diameter_m ** 2)

        st.subheader("Results")
        c1, c2, c3 = st.columns(3)
        c1.metric("Annular Volume", f"{u.volume_from_si(vol):.4f} {u.volume}")
        c2.metric("Annular Velocity", f"{u.velocity_from_si(vel):.3f} {u.velocity}")
        c3.metric("Annular Cross-Sectional Area", f"{u.area_from_si(area):.6f} {u.area}")

        st.subheader("Equivalent Circulating Density (ECD)")
        pressure_drops = list(range(0, 2000001, 100000))
        ecd_values = [AnnularHydraulics.calculate_ECD(mud_dens, p, tvd_si) for p in pressure_drops]

        fig = px.line(
            x=[u.pressure_display_from_si(p) for p in pressure_drops],
            y=[u.density_from_si(v) for v in ecd_values],
            title="ECD vs Annular Pressure Drop",
            labels={"x": f"Annular Pressure Drop ({u.pressure_display})",
                    "y": f"ECD ({u.density})"},
        )
        fig.update_traces(line=dict(width=3, color="#1d4ed8"))
        static_display = u.density_from_si(mud_dens)
        fig.add_hline(
            y=static_display, line_dash="dash", line_color="#f59e0b", line_width=2,
            annotation_text=f"Static Mud Weight: {static_display:.1f} {u.density}",
            annotation_font=dict(color="#92400e"),
        )
        st.plotly_chart(fig, use_container_width=True)
