"""Module 1 · Hydrostatic Pressure Balance page."""

import pandas as pd
import plotly.express as px
import streamlit as st

from src.core.engineering_calculators import HydrostaticPressureCalculator
from src.core.models import Formation
from src.gui.components import hero, section_label, status_pill
from src.gui.units import get_units


def render() -> None:
    u = get_units()
    hero(
        "balance",
        "Hydrostatic Pressure Balance",
        "Calculate the minimum mud weight required to balance formation pore pressure "
        "across each casing interval.",
    )

    section_label("Wellbore Configuration")
    num_intervals = st.slider("Number of Casing Intervals", 1, 10, 3, key="nci")
    formations = []

    depth_max = u.len_from_si(10000.0)
    pp_max = u.pressure_from_si(1e8)
    fg_max = u.gradient_from_si(50000.0)
    depth_step = 100.0
    pp_step = 100.0 if u.field else 1e6
    fg_step = 0.05 if u.field else 1000.0

    for i in range(num_intervals):
        with st.expander(f"Casing Interval {i + 1}", expanded=(i == 0)):
            c1, c2, c3 = st.columns(3)
            with c1:
                depth = st.number_input(
                    f"True Vertical Depth ({u.depth})", 0.0, depth_max,
                    u.len_from_si(1000.0 + i * 500.0), depth_step, key=f"d{i}",
                )
            with c2:
                pp = st.number_input(
                    f"Pore Pressure ({u.pressure})", 0.0, pp_max,
                    u.pressure_from_si(1e7), pp_step, key=f"pp{i}",
                    format="%.1f" if u.field else "%.0f",
                )
            with c3:
                fg = st.number_input(
                    f"Fracture Gradient ({u.gradient})", 0.0, fg_max,
                    u.gradient_from_si(12000.0), fg_step, key=f"fg{i}",
                    format="%.2f" if u.field else None,
                )
            formations.append(Formation(
                name=f"Interval {i + 1}", depth_m=u.len_to_si(depth),
                pore_pressure_pa=u.pressure_to_si(pp), fracture_gradient=u.gradient_to_si(fg),
            ))

    if st.button("Calculate Mud Weight Requirements", key="cpb", type="primary"):
        with st.spinner("Evaluating pore pressure balance…"):
            rows = []
            for f in formations:
                rd, rp = HydrostaticPressureCalculator.calculate_mud_weight_for_pore_balance(f)
                sc = HydrostaticPressureCalculator.evaluate_safety_window(
                    rd, f.pore_pressure_pa, f.fracture_gradient, f.depth_m,
                )
                status = sc["safety_status"]
                if "INSUFFICIENT" in status or "EXCESSIVE" in status:
                    pill = status_pill(status, "danger")
                else:
                    pill = status_pill(status, "ok")
                rows.append({
                    "Interval": f.name,
                    f"Depth ({u.depth})": round(u.len_from_si(f.depth_m), 1),
                    f"Pore Pressure ({u.pressure_display})": round(
                        u.pressure_display_from_si(f.pore_pressure_pa), 2,
                    ),
                    **(
                        {"Required Mud Density (kg/m³)": round(rd, 2)}
                        if not u.field
                        else {"Required Mud Weight (ppg)": round(rp, 2)}
                    ),
                    "Safety Status": sc["safety_status"],
                    "Status": pill,
                })

        df = pd.DataFrame(rows)
        st.subheader("Results")
        st.dataframe(
            df[[
                "Interval",
                f"Depth ({u.depth})",
                f"Pore Pressure ({u.pressure_display})",
                "Required Mud Density (kg/m³)" if not u.field else "Required Mud Weight (ppg)",
                "Status",
            ]],
            use_container_width=True,
            column_config={"Status": st.column_config.Column(width="medium")},
        )

        density_key = "Required Mud Density (kg/m³)" if not u.field else "Required Mud Weight (ppg)"
        fig = px.line(
            df, x=f"Depth ({u.depth})", y=density_key,
            title="Required Mud Weight vs Depth", markers=True,
        )
        fig.update_traces(line=dict(width=3, color="#1d4ed8"), marker=dict(size=9, color="#f59e0b"))
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Safety Assessment")
        for r in rows:
            if "INSUFFICIENT" in r["Safety Status"] or "EXCESSIVE" in r["Safety Status"]:
                st.error(f"{r['Interval']}: {r['Safety Status']}")
            else:
                st.success(f"{r['Interval']}: {r['Safety Status']}")
