"""Module · System Hydraulics & Dynamic Pressure Drop page."""

import pandas as pd
import plotly.express as px
import streamlit as st

from src.core.hydraulics_engine import SystemHydraulics
from src.core.models import CirculatingGeometry, RheologyModel, RheologyProfile
from src.gui.components import hero, section_label
from src.gui.units import get_units


def render() -> None:
    u = get_units()
    hero(
        "water",
        "System Hydraulics & Dynamic Pressure Drop",
        "Model non-Newtonian fluid mechanics and calculate dynamic pressure "
        "drops throughout the complete circulating system.",
    )

    section_label("Rheological Model")
    model_name = st.selectbox(
        "Fluid Model",
        [m.value for m in RheologyModel],
        index=1,
    )
    profile = RheologyProfile(model=RheologyModel(model_name))
    visc_min = u.viscosity_from_si(0.001)
    visc_max = u.viscosity_from_si(0.1)
    visc_default = u.viscosity_from_si(0.02)
    visc_step = 1.0 if u.field else 0.001
    visc_fmt = None if u.field else "%.4f"
    c1, c2, c3 = st.columns(3)
    if model_name == "Newtonian":
        with c1:
            visc = st.number_input(
                f"Dynamic Viscosity ({u.viscosity})",
                visc_min, visc_max, visc_default, visc_step, format=visc_fmt,
            )
        profile.dynamic_viscosity_pa_s = u.viscosity_to_si(visc)
    elif model_name == "Bingham-Plastic":
        with c1:
            pv = st.number_input(
                f"Plastic Viscosity ({u.viscosity})",
                visc_min, visc_max, visc_default, visc_step, format=visc_fmt,
            )
        with c2:
            yp = st.number_input(
                f"Yield Point ({u.yield_point})",
                0.0, 100.0, u.yield_from_si(10.0), 1.0,
            )
        profile.plastic_viscosity_pa_s = u.viscosity_to_si(pv)
        profile.yield_point_pa = u.yield_to_si(yp)
    elif model_name == "Power Law":
        with c1:
            k = st.number_input("Consistency Index K (Pa·sⁿ)", 0.01, 10.0, 0.5, 0.01, format="%.2f")
        with c2:
            n = st.number_input("Flow Behavior Index n (—)", 0.1, 1.0, 0.7, 0.01)
        profile.consistency_index_pa_sn = k
        profile.flow_behavior_index = n
    else:  # Herschel-Bulkley
        with c1:
            yp = st.number_input(
                f"Yield Point ({u.yield_point})",
                0.0, 100.0, u.yield_from_si(10.0), 1.0,
            )
        with c2:
            k = st.number_input("Consistency Index K (Pa·sⁿ)", 0.01, 10.0, 0.5, 0.01, format="%.2f")
        with c3:
            n = st.number_input("Flow Behavior Index n (—)", 0.1, 1.0, 0.7, 0.01)
        profile.yield_point_pa = u.yield_to_si(yp)
        profile.consistency_index_pa_sn = k
        profile.flow_behavior_index = n

    dens_in = st.number_input(
        f"Mud Density ({u.density})",
        u.density_from_si(800.0), u.density_from_si(2200.0), u.density_from_si(1200.0),
        0.1 if u.field else 10.0,
    )

    section_label("Circulating System Geometry")
    c1, c2 = st.columns(2)
    with c1:
        surf_len = st.number_input(
            f"Surface Line Length ({u.depth})",
            u.len_from_si(1.0), u.len_from_si(5000.0), u.len_from_si(100.0), 100.0,
        )
        surf_id = st.number_input("Surface Line Inner Diameter (in)", 0.5, 8.0, 5.0, 0.125)
        dp_len = st.number_input(
            f"Drill Pipe Length ({u.depth})",
            u.len_from_si(100.0), u.len_from_si(10000.0), u.len_from_si(3000.0), 100.0,
        )
        dp_id = st.number_input("Drill Pipe Inner Diameter (in)", 1.0, 8.0, 4.276, 0.001, format="%.3f")
        dp_od = st.number_input("Drill Pipe Outer Diameter (in)", 2.0, 9.0, 5.0, 0.125)
        dc_len = st.number_input(
            f"Drill Collar Length ({u.depth})",
            u.len_from_si(10.0), u.len_from_si(1000.0), u.len_from_si(200.0), 100.0,
        )
        dc_id = st.number_input("Drill Collar Inner Diameter (in)", 1.0, 6.0, 2.8125, 0.125)
        dc_od = st.number_input("Drill Collar Outer Diameter (in)", 4.0, 12.0, 8.0, 0.125)
    with c2:
        tfa = st.number_input("Bit Total Flow Area (in²)", 0.1, 3.0, 0.82, 0.01)
        hole = st.number_input("Open Hole Diameter (in)", 6.0, 30.0, 12.25, 0.125)
        tvd = st.number_input(
            f"True Vertical Depth ({u.depth})",
            u.len_from_si(100.0), u.len_from_si(10000.0), u.len_from_si(2000.0), 100.0,
        )
        flow_in = st.number_input(
            f"Surface Flow Rate ({u.flow_rate})",
            u.flow_from_si(1.0), u.flow_from_si(100.0), u.flow_from_si(30.0),
            10.0 if u.field else 1.0,
        )

    if st.button("Calculate System Hydraulics", key="csh", type="primary"):
        geom = CirculatingGeometry(
            surface_line_length_m=u.len_to_si(surf_len),
            surface_line_id_m=surf_id * 0.0254,
            drill_pipe_length_m=u.len_to_si(dp_len),
            drill_pipe_id_m=dp_id * 0.0254,
            drill_pipe_od_m=dp_od * 0.0254,
            drill_collar_length_m=u.len_to_si(dc_len),
            drill_collar_id_m=dc_id * 0.0254,
            drill_collar_od_m=dc_od * 0.0254,
            bit_nozzle_area_m2=u.area_to_si(tfa),
            open_hole_diameter_m=hole * 0.0254,
            tvd_m=u.len_to_si(tvd),
        )
        flow_m3_s = u.flow_to_si(flow_in) / 1000.0
        density = u.density_to_si(dens_in)

        with st.spinner("Solving system pressure profile…"):
            result = SystemHydraulics.calculate(geom, profile, density, flow_m3_s)

        total = result["total_pressure_drop_pa"]

        st.subheader("System Summary")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total System ΔP", f"{u.pressure_display_from_si(total):,.1f} {u.pressure_display}")
        c2.metric("Annular ΔP", f"{u.pressure_display_from_si(result['annular_pressure_drop_pa']):,.1f} {u.pressure_display}")
        c3.metric("ECD", f"{u.density_from_si(result['ecd_kg_m3']):.1f} {u.density}")
        c4.metric("Bit ΔP", f"{u.pressure_display_from_si(result['bit_pressure_drop_pa']):,.1f} {u.pressure_display}")

        c1, c2, c3 = st.columns(3)
        c1.metric("Jet Velocity", f"{u.velocity_from_si(result['jet_velocity_m_s']):.1f} {u.velocity}")
        c2.metric("Bit Hydraulic Power", f"{u.power_from_si(result['bit_hydraulic_power_w'] / 1000.0):.1f} {u.power}")
        c3.metric("Hydraulic Impact Force", f"{u.force_from_si(result['hydraulic_impact_force_n']):.0f} {u.force}")

        st.subheader("Section Pressure-Drop Breakdown")
        rows = []
        for s in result["sections"]:
            rows.append({
                "Section": s["name"],
                "Flow Type": s["type"],
                f"Velocity ({u.velocity})": round(u.velocity_from_si(s["velocity_m_s"]), 3),
                "Reynolds": s["reynolds"] if s["reynolds"] else "—",
                "Regime": s["regime"],
                f"ΔP ({u.pressure_display})": round(u.pressure_display_from_si(s["pressure_drop_pa"]), 2),
                "% of Total": round(100.0 * s["pressure_drop_pa"] / total, 1) if total > 0 else 0.0,
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            fig_bar = px.bar(
                df, x="Section", y=f"ΔP ({u.pressure_display})",
                color="Regime", title="Pressure Drop by Section",
                color_discrete_map={
                    "Laminar": "#0ea5e9", "Transition": "#f59e0b", "Turbulent": "#ef4444", "—": "#94a3b8",
                },
            )
            fig_bar.update_layout(showlegend=True)
            st.plotly_chart(fig_bar, use_container_width=True)
        with c2:
            cumulative = []
            running = 0.0
            for s in result["sections"]:
                running += s["pressure_drop_pa"]
                cumulative.append({
                    "Section": s["name"],
                    f"Cumulative ΔP ({u.pressure_display})": u.pressure_display_from_si(running),
                })
            fig_cum = px.line(
                pd.DataFrame(cumulative), x="Section",
                y=f"Cumulative ΔP ({u.pressure_display})",
                title="Cumulative Pressure Profile", markers=True,
            )
            fig_cum.update_traces(line=dict(width=3, color="#1d4ed8"), marker=dict(size=9, color="#f59e0b"))
            st.plotly_chart(fig_cum, use_container_width=True)

        st.caption(
            "Regime from generalized Reynolds number (Re<2100 laminar, 2100≤Re<4000 transition, "
            "Re≥4000 turbulent). Laminar friction uses the exact closed-form effective-viscosity "
            "solution; turbulent uses the Dodge–Metzner correlation."
        )
