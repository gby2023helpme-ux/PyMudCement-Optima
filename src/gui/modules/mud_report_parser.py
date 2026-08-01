"""Module 2 · Mud Report Parser & Rheological Profiling page."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.core.engineering_calculators import BinghamPlasticRheology
from src.core.models import MudReport
from src.gui.components import hero, section_label


def render() -> None:
    hero(
        "upload_file",
        "Mud Report Parser & Rheological Profiling",
        "Upload a digital mud report to parse drilling fluid properties "
        "and generate rheological profiles.",
    )

    section_label("Data Input")
    uploaded = st.file_uploader("Upload Mud Report (CSV format)", type=["csv"])

    if uploaded:
        with st.spinner("Parsing mud report…"):
            df = pd.read_csv(uploaded)
        st.subheader("Uploaded Data")
        st.dataframe(df, use_container_width=True)

        reports = []
        for _, row in df.iterrows():
            reports.append(MudReport(
                api_number=str(row.get("API Number", "")),
                temperature_c=float(row.get("Temperature (C)", row.get("Temperature (°C)", 0))),
                density_kg_m3=float(row.get("Density (kg/m3)", row.get("Density (kg/m³)", 0))),
                plastic_viscosity_cP=float(row.get("PV (cP)", 0)),
                yield_point_lbf_100ft2=float(row.get("YP (lbf/100ft2)", row.get("YP (lbf/100ft²)", 0))),
                mud_weight_ppg=float(row.get("Mud Weight (ppg)", 0)),
            ))

        st.success(f"Successfully parsed **{len(reports)}** mud report entries.")

        if reports:
            c1, c2 = st.columns(2)
            with c1:
                fig_pv = px.bar(
                    x=[r.api_number or str(i + 1) for i, r in enumerate(reports)],
                    y=[r.plastic_viscosity_cP for r in reports],
                    title="Plastic Viscosity (PV)",
                    labels={"x": "Sample", "y": "PV (cP)"},
                    color_discrete_sequence=["#1d4ed8"],
                )
                st.plotly_chart(fig_pv, use_container_width=True)
            with c2:
                fig_yp = px.bar(
                    x=[r.api_number or str(i + 1) for i, r in enumerate(reports)],
                    y=[r.yield_point_lbf_100ft2 for r in reports],
                    title="Yield Point (YP)",
                    labels={"x": "Sample", "y": "YP (lbf/100ft²)"},
                    color_discrete_sequence=["#0ea5e9"],
                )
                st.plotly_chart(fig_yp, use_container_width=True)

            st.subheader("Bingham-Plastic Rheology Curve")
            st.caption("Shear stress computed using the Bingham-Plastic model:  τ = YP + μ_PV × γ̇")
            shear_rates = [5.1, 10.2, 170, 341, 511, 1022]
            fig = go.Figure()
            for r in reports:
                pv_pa = r.plastic_viscosity_cP / 1000.0
                yp_pa = r.yield_point_lbf_100ft2 * 47.8803
                ss = [BinghamPlasticRheology.calculate_shear_stress(yp_pa, pv_pa, sr) for sr in shear_rates]
                fig.add_trace(go.Scatter(
                    x=shear_rates, y=ss, mode="lines+markers",
                    name=r.api_number or "Sample",
                    line=dict(width=2.5),
                ))
            fig.update_layout(
                title="Shear Stress vs Shear Rate",
                xaxis_title="Shear Rate (s⁻¹)",
                yaxis_title="Shear Stress (Pa)",
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(
            "**Expected CSV columns:** API Number, Temperature (C), Density (kg/m3), "
            "PV (cP), YP (lbf/100ft2), Mud Weight (ppg)"
        )
