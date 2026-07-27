import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.core.engineering_calculators import (
    HydrostaticPressureCalculator,
    BinghamPlasticRheology,
    AnnularHydraulics,
    SlurryDesigner,
)
from src.core.cementing_engine import (
    CementingEngine,
    PAPLugDesign,
    ADDITIVE_DATABASE,
    SlurryDesignRequest,
)
from src.core.models import (
    Formation,
    MudReport,
    AnnularGeometry,
)

GRAVITY = 9.81

st.set_page_config(page_title="PyMudCement-Optima", layout="wide", page_icon="⛽")

# ── Plotly Global Theme ──
import plotly.io as pio
pio.templates["uenr"] = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor="#b34141",
        plot_bgcolor="#ffffff",
        font=dict(family="sans-serif", size=13, color="#111827"),
        title=dict(font=dict(color="#111827", size=18, family="sans-serif")),
        xaxis=dict(gridcolor="#e5e7eb", zerolinecolor="#d1d5db", title_font=dict(color="#111827"), tickfont=dict(color="#374151")),
        yaxis=dict(gridcolor="#e5e7eb", zerolinecolor="#d1d5db", title_font=dict(color="#111827"), tickfont=dict(color="#374151")),
        legend=dict(font=dict(color="#374151")),
        colorway=["#1d4ed8", "#2563eb", "#3b82f6", "#60a5fa", "#93c5fd", "#1e3a5f", "#047857", "#c2410c"],
    )
)
pio.templates.default = "uenr"

st.markdown("""
<style>
    /* ── Reset & Page ── */
    .stApp { background-color: #ffffff; }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] { background-color: #1e3a5f; }
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
    section[data-testid="stSidebar"] .stMarkdown li {
        color: #ffffff !important;
    }

    /* ── Headings: dark on white ── */
    h1 { color: #111827 !important; font-weight: 700; }
    h2 { color: #111827 !important; font-weight: 600; }
    h3 { color: #111827 !important; font-weight: 600; }

    /* ── Body / captions ── */
    p, span, .stMarkdown { color: #111827 !important; }
    caption, .stCaption, .stCaption p,
    [data-testid="stCaptionContainer"] p { color: #6b7280 !important; }

    /* ── Tabs ── */
    button[data-baseweb="tab"] {
        color: #6b7280 !important; font-weight: 600;
        border-bottom: 3px solid transparent;
    }
    button[data-baseweb="tab"]:hover { color: #111827 !important; }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #111827 !important;
        border-bottom: 3px solid #1d4ed8;
    }

    /* ── Metric Cards ── */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-left: 5px solid #1d4ed8;
        border-radius: 8px;
        padding: 12px 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    div[data-testid="stMetric"] label {
        color: #6b7280 !important; font-weight: 500; font-size: 0.85rem;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #111827 !important; font-weight: 700; font-size: 1.5rem;
    }

    /* ── Primary Button ── */
    button[kind="primary"],
    .stButton > button[kind="primary"] {
        background-color: #1d4ed8 !important;
        color: #ffffff !important;
        border: none;
        border-radius: 6px;
        padding: 8px 28px;
        font-weight: 600;
    }
    button[kind="primary"]:hover {
        background-color: #1e40af !important;
        color: #ffffff !important;
    }

    /* ── Secondary Button ── */
    .stButton > button:not([kind="primary"]) {
        background-color: #eff6ff !important;
        color: #1d4ed8 !important;
        border: 1px solid #bfdbfe;
        border-radius: 6px;
        font-weight: 600;
    }
    .stButton > button:not([kind="primary"]):hover {
        background-color: #dbeafe !important;
        color: #1e40af !important;
    }

    /* ── Alerts: dark text on tinted bg ── */
    div[data-testid="stAlert"][kind="error"] {
        background-color: #fef2f2; border-left: 5px solid #dc2626;
        color: #991b1b !important; border-radius: 6px;
    }
    div[data-testid="stAlert"][kind="success"] {
        background-color: #f0fdf4; border-left: 5px solid #16a34a;
        color: #166534 !important; border-radius: 6px;
    }
    div[data-testid="stAlert"][kind="warning"] {
        background-color: #fffbeb; border-left: 5px solid #d97706;
        color: #92400e !important; border-radius: 6px;
    }
    div[data-testid="stAlert"][kind="info"] {
        background-color: #eff6ff; border-left: 5px solid #1d4ed8;
        color: #1e40af !important; border-radius: 6px;
    }

    /* ── Expanders ── */
    details { border: 1px solid #1e3a5f; border-radius: 8px; }
    details summary,
    details summary span,
    details summary p,
    details summary div,
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary span,
    [data-testid="stExpander"] summary p {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-weight: 600 !important;
        background-color: #1e3a5f !important;
    }
    details summary:hover,
    [data-testid="stExpander"] summary:hover {
        background-color: #1e40af !important;
    }
    details[open] summary,
    details[open] summary span,
    details[open] summary p,
    [data-testid="stExpander"][aria-expanded="true"] summary,
    [data-testid="stExpander"][aria-expanded="true"] summary span {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        background-color: #1e3a5f !important;
    }
    details[open] { border-color: #1e3a5f; }

    /* ── Horizontal Rule ── */
    hr { border: none; border-top: 1px solid #e5e7eb; margin: 1rem 0; }

    /* ── Radio buttons ── */
    .stRadio > div { gap: 8px; }
    .stRadio > div > div > label { color: #111827 !important; font-weight: 500; }

    /* ── Form labels ── */
    .stNumberInput label, .stSlider label, .stSelectbox label,
    .stMultiSelect label, .stTextArea label, .stFileUploader label {
        color: #111827 !important; font-weight: 500;
    }

    /* ── Input values ── */
    .stNumberInput input, .stTextInput input,
    [data-baseweb="input"] input, [data-baseweb="numberinput"] input,
    .stNumberInput div[data-baseweb="input"] input {
        color: #111827 !important; font-weight: 600 !important;
        background-color: #ffffff !important;
        -webkit-text-fill-color: #111827 !important;
    }

    /* ── Slider value ── */
    .stSlider [data-baseweb="thumb"] + div,
    .stSlider [data-baseweb="thumb"] + div span,
    .stSlider [role="slider"] + div span {
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
    }

    /* ── All form input containers ── */
    [data-baseweb="input"],
    [data-baseweb="numberinput"],
    [data-baseweb="select"],
    [data-baseweb="textarea"] {
        color: #111827 !important;
    }

    /* ── File uploader ── */
    .stFileUploader [data-testid="stFileUploadDropzone"] {
        border-color: #93c5fd !important; background-color: #eff6ff !important;
    }
    .stFileUploader [data-testid="stFileUploadDropzone"] p,
    .stFileUploader [data-testid="stFileUploadDropzone"] span,
    .stFileUploader [data-testid="stFileUploadDropzone"] small,
    .stFileUploader [data-testid="stFileUploadDropzone"] div,
    .stFileUploader [data-testid="stFileUploadDropzone"] svg,
    .stFileUploader [data-baseweb="file-uploader"] span,
    .stFileUploader [data-baseweb="file-uploader"] div,
    .stFileUploader [data-baseweb="file-uploader"] p,
    section[data-testid="stFileUploadDropzone"] span,
    section[data-testid="stFileUploadDropzone"] p,
    section[data-testid="stFileUploadDropzone"] div,
    section[data-testid="stFileUploadDropzone"] small {
        color: #1e40af !important;
        -webkit-text-fill-color: #1e40af !important;
    }
    .stFileUploader [data-testid="stFileUploadDropzone"] strong {
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
    }

    /* ── Plotly chart containers ── */
    .stPlotlyChart { background-color: #ffffff; border-radius: 8px; padding: 4px; }

    /* ── DataFrame ── */
    .stDataFrame { border: 1px solid #e5e7eb; border-radius: 8px; }
    .stDataFrame [role="columnheader"] {
        color: #111827 !important; font-weight: 700;
        background-color: #eff6ff;
    }

    /* ── Selectbox values ── */
    .stSelectbox [data-baseweb="select"] { color: #111827 !important; }

    /* ── Tooltip ── */
    .stTooltipLabel { color: #6b7280 !important; }

    /* ── Sidebar radio active dot ── */
    section[data-testid="stSidebar"] .stRadio > div > div > label::before {
        background-color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("PyMudCement-Optima")
st.caption("Intelligent Mud & Cement Design Suite  |  PENG 258 Capstone Project  |  UENR")

nav = st.sidebar
nav.header("Modules")
page = nav.radio("Select Module", [
    "Pressure Balance",
    "Mud Report Parser",
    "Annular Hydraulics & ECD",
    "Cement Slurry Design",
    "Cementing Procedure Sheet",
    "P&A Plug Design",
])

if page == "Pressure Balance":
    st.header("Hydrostatic Pressure Balance")
    st.write("Calculate the minimum mud weight required to balance formation pore pressure across each casing interval.")

    num_intervals = st.slider("Number of Casing Intervals", 1, 10, 3)
    formations = []

    for i in range(num_intervals):
        with st.expander(f"Casing Interval {i + 1}", expanded=(i == 0)):
            c1, c2, c3 = st.columns(3)
            with c1:
                depth = st.number_input(
                    "True Vertical Depth (m)",
                    0.0, 10000.0, 1000.0 + i * 500.0, 100.0, key=f"d{i}",
                )
            with c2:
                pp = st.number_input(
                    "Formation Pore Pressure (Pa)",
                    0.0, 100000000.0, 10000000.0, 1000000.0,
                    key=f"pp{i}", format="%.0f",
                )
            with c3:
                fg = st.number_input(
                    "Fracture Gradient (Pa/m)",
                    0.0, 50000.0, 12000.0, 1000.0, key=f"fg{i}",
                )
            formations.append(Formation(
                name=f"Interval {i + 1}", depth_m=depth,
                pore_pressure_pa=pp, fracture_gradient=fg,
            ))

    if st.button("Calculate Mud Weight Requirements", key="cpb"):
        rows = []
        for f in formations:
            rd, rp = HydrostaticPressureCalculator.calculate_mud_weight_for_pore_balance(f)
            sc = HydrostaticPressureCalculator.evaluate_safety_window(
                rd, f.pore_pressure_pa, f.fracture_gradient, f.depth_m,
            )
            rows.append({
                "Interval": f.name,
                "Depth (m)": f.depth_m,
                "Pore Pressure (MPa)": round(f.pore_pressure_pa / 1e6, 2),
                "Required Mud Density (kg/m³)": round(rd, 2),
                "Required Mud Weight (ppg)": round(rp, 2),
                "Safety Status": sc["safety_status"],
            })

        df = pd.DataFrame(rows)
        st.subheader("Results")
        st.dataframe(df, use_container_width=True)

        fig = px.line(
            df, x="Depth (m)", y="Required Mud Density (kg/m³)",
            title="Required Mud Weight vs Depth", markers=True,
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Safety Assessment")
        for r in rows:
            if "INSUFFICIENT" in r["Safety Status"] or "EXCESSIVE" in r["Safety Status"]:
                st.error(f"{r['Interval']}: {r['Safety Status']}")
            else:
                st.success(f"{r['Interval']}: {r['Safety Status']}")

elif page == "Mud Report Parser":
    st.header("Mud Report Parser & Rheological Profiling")
    st.write("Upload a digital mud report to parse drilling fluid properties and generate rheological profiles.")

    uploaded = st.file_uploader("Upload Mud Report (CSV format)", type=["csv"])

    if uploaded:
        df = pd.read_csv(uploaded)
        st.subheader("Uploaded Data")
        st.dataframe(df, use_container_width=True)

        reports = []
        for _, row in df.iterrows():
            reports.append(MudReport(
                api_number=str(row.get("API Number", "")),
                temperature_c=float(row.get("Temperature (C)", row.get("Temperature (\u00b0C)", 0))),
                density_kg_m3=float(row.get("Density (kg/m3)", row.get("Density (kg/m\u00b3)", 0))),
                plastic_viscosity_cP=float(row.get("PV (cP)", 0)),
                yield_point_lbf_100ft2=float(row.get("YP (lbf/100ft2)", row.get("YP (lbf/100ft\u00b2)", 0))),
                mud_weight_ppg=float(row.get("Mud Weight (ppg)", 0)),
            ))

        st.success(f"Successfully parsed {len(reports)} mud report entries.")

        if reports:
            c1, c2 = st.columns(2)
            with c1:
                fig_pv = px.bar(
                    x=[r.api_number or str(i + 1) for i, r in enumerate(reports)],
                    y=[r.plastic_viscosity_cP for r in reports],
                    title="Plastic Viscosity (PV)",
                    labels={"x": "Sample", "y": "PV (cP)"},
                )
                st.plotly_chart(fig_pv, use_container_width=True)
            with c2:
                fig_yp = px.bar(
                    x=[r.api_number or str(i + 1) for i, r in enumerate(reports)],
                    y=[r.yield_point_lbf_100ft2 for r in reports],
                    title="Yield Point (YP)",
                    labels={"x": "Sample", "y": "YP (lbf/100ft²)"},
                )
                st.plotly_chart(fig_yp, use_container_width=True)

            st.subheader("Bingham-Plastic Rheology Curve")
            st.write("Shear stress computed using the Bingham-Plastic model:  τ = YP + μ_PV × γ̇")
            shear_rates = [5.1, 10.2, 170, 341, 511, 1022]
            fig = go.Figure()
            for r in reports:
                pv_pa = r.plastic_viscosity_cP / 1000.0
                yp_pa = r.yield_point_lbf_100ft2 * 47.8803
                ss = [BinghamPlasticRheology.calculate_shear_stress(yp_pa, pv_pa, sr) for sr in shear_rates]
                fig.add_trace(go.Scatter(
                    x=shear_rates, y=ss, mode="lines+markers",
                    name=r.api_number or "Sample",
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

elif page == "Annular Hydraulics & ECD":
    st.header("Annular Hydraulics & Equivalent Circulating Density")
    st.write("Calculate annular volume, fluid velocity, and ECD for a given casing and hole configuration.")

    c1, c2 = st.columns(2)
    with c1:
        casing_in = st.number_input("Casing Outer Diameter (in)", 0.1, 30.0, 9.625, 0.125)
        hole_in = st.number_input("Open Hole Diameter (in)", 0.1, 30.0, 12.25, 0.125)
        length_m = st.number_input("Cemented Interval Length (m)", 1.0, 5000.0, 200.0, 10.0)
    with c2:
        washout = st.slider("Hole Washout Factor (%)", 0, 50, 15) / 100.0
        mud_dens = st.number_input("Mud Density (kg/m³)", 500.0, 2500.0, 1200.0, 10.0)
        tvd = st.number_input("True Vertical Depth (m)", 100.0, 10000.0, 2000.0, 100.0)

    flow = st.number_input("Surface Flow Rate (L/s)", 1.0, 100.0, 30.0, 1.0) / 1000.0

    if st.button("Calculate Annular Hydraulics", key="cah"):
        geom = AnnularGeometry(
            casing_diameter_in=casing_in, hole_diameter_in=hole_in,
            cemented_interval_length_m=length_m, wash_out_factor=washout,
        )
        vol = AnnularHydraulics.calculate_annular_volume(geom)
        vel = AnnularHydraulics.calculate_fluid_velocity(flow, geom.hole_diameter_m, geom.casing_diameter_m)
        area = (math.pi / 4) * (geom.hole_diameter_m ** 2 - geom.casing_diameter_m ** 2)

        st.subheader("Results")
        c1, c2, c3 = st.columns(3)
        c1.metric("Annular Volume", f"{vol:.4f} m³")
        c2.metric("Annular Velocity", f"{vel:.3f} m/s")
        c3.metric("Annular Cross-Sectional Area", f"{area:.6f} m²")

        st.subheader("Equivalent Circulating Density (ECD)")
        pressure_drops = list(range(0, 2000001, 100000))
        ecd_values = [AnnularHydraulics.calculate_ECD(mud_dens, p, tvd) for p in pressure_drops]

        fig = px.line(
            x=[p / 1e6 for p in pressure_drops], y=ecd_values,
            title="ECD vs Annular Pressure Drop",
            labels={"x": "Annular Pressure Drop (MPa)", "y": "ECD (kg/m³)"},
        )
        fig.add_hline(
            y=mud_dens, line_dash="dash", line_color="green",
            annotation_text=f"Static Mud Weight: {mud_dens} kg/m³",
        )
        st.plotly_chart(fig, use_container_width=True)

elif page == "Cement Slurry Design":
    st.header("Cement Slurry Design")
    st.write("Design a primary cement slurry with automated additive selection based on wellbore conditions.")

    c1, c2 = st.columns(2)
    with c1:
        ch = st.number_input("Open Hole Diameter (in)", 6.0, 30.0, 12.25, 0.125)
        cc = st.number_input("Casing Outer Diameter (in)", 4.0, 20.0, 9.625, 0.125)
        cl = st.number_input("Cemented Interval Length (m)", 10.0, 2000.0, 200.0, 10.0)
    with c2:
        bht = st.number_input("Bottomhole Circulating Temperature (°C)", 20.0, 300.0, 120.0, 5.0)
        td = st.number_input("Target Slurry Density (kg/m³)", 1000.0, 2200.0, 1900.0, 10.0)
        wr = st.number_input("Water-to-Cement Ratio", 0.30, 0.80, 0.44, 0.01)

    excess = st.slider("Open-Hole Excess Factor (%)", 0, 50, 15) / 100.0
    pt = st.number_input("Required Pump Time (min)", 10.0, 180.0, 45.0, 5.0)

    if st.button("Design Cement Slurry", key="dsr"):
        req = SlurryDesignRequest(
            hole_diameter_in=ch, casing_od_in=cc, cemented_length_m=cl,
            bottomhole_temp_c=bht, target_density_kg_m3=td,
            water_ratio=wr, excess_factor=excess, pump_time_min=pt,
        )
        result = CementingEngine.design_slurry(req)

        st.subheader("Volume Summary")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Slurry Volume", f"{result.slurry_volume_m3:.4f} m³")
        c2.metric("Cement Volume", f"{result.cement_volume_m3:.4f} m³")
        c3.metric("Mix Water Volume", f"{result.water_volume_m3:.4f} m³")

        st.subheader("Slurry Properties")
        c1, c2, c3 = st.columns(3)
        c1.metric("Achieved Slurry Density", f"{result.total_density_kg_m3:.1f} kg/m³")
        c2.metric("Thickening Time", f"{result.thickening_time_min:.1f} min")
        c3.metric("24h Compressive Strength", f"{result.compressive_strength_mpa:.2f} MPa")

        if result.additive_plan:
            st.subheader("Recommended Additive Schedule")
            st.dataframe(pd.DataFrame(result.additive_plan), use_container_width=True)

        if result.warnings:
            st.subheader("Engineering Warnings")
            for w in result.warnings:
                st.warning(w)

        st.subheader("Additive Database Reference")
        st.dataframe(pd.DataFrame([{
            "Additive Name": a.name,
            "Category": a.category.value,
            "Dosage Range (kg/m³)": f"{a.dosage_range_kg_m3[0]} – {a.dosage_range_kg_m3[1]}",
            "Max Temperature (°C)": a.max_temperature_c,
            "Specific Gravity": a.specific_gravity,
        } for a in ADDITIVE_DATABASE]), use_container_width=True)

elif page == "Cementing Procedure Sheet":
    st.header("Cementing Job Procedure Sheet")
    st.write("Generate a stage-by-stage cementing procedure with volumes, pump rates, and durations.")

    c1, c2 = st.columns(2)
    with c1:
        ch = st.number_input("Open Hole Diameter (in)", 6.0, 30.0, 12.25, 0.125, key="ph")
        cc = st.number_input("Casing Outer Diameter (in)", 4.0, 20.0, 9.625, 0.125, key="pc")
        cl = st.number_input("Cemented Interval Length (m)", 10.0, 2000.0, 200.0, 10.0, key="pl")
    with c2:
        bht = st.number_input("Bottomhole Circulating Temperature (°C)", 20.0, 300.0, 120.0, 5.0, key="pt")
        td = st.number_input("Target Slurry Density (kg/m³)", 1000.0, 2200.0, 1900.0, 10.0, key="pd")
        pr = st.number_input("Surface Pump Rate (L/min)", 50.0, 1000.0, 200.0, 10.0, key="ppr")

    sv = st.number_input("Spacer Volume (m³)", 0.0, 10.0, 2.0, 0.1, key="psv")
    fv = st.number_input("Flush Volume (m³)", 0.0, 10.0, 1.5, 0.1, key="pfv")

    if st.button("Generate Procedure Sheet", key="gps"):
        req = SlurryDesignRequest(
            hole_diameter_in=ch, casing_od_in=cc, cemented_length_m=cl,
            bottomhole_temp_c=bht, target_density_kg_m3=td,
        )
        design = CementingEngine.design_slurry(req)
        proc = CementingEngine.generate_procedure(
            design, pump_rate_lpm=pr, spacer_volume_m3=sv, flush_volume_m3=fv,
        )

        st.subheader("Procedure Sheet")
        df_proc = pd.DataFrame([{
            "Stage": p.stage,
            "Volume (m³)": p.volume_m3,
            "Density (kg/m³)": p.density_kg_m3,
            "Pump Rate (L/min)": p.pump_rate_lpm,
            "Duration (min)": p.duration_min,
            "Cumulative Volume (m³)": p.cumulative_volume_m3,
            "Operational Notes": p.notes,
        } for p in proc])
        st.dataframe(df_proc, use_container_width=True)

        total_time = sum(p.duration_min for p in proc)
        total_vol = sum(p.volume_m3 for p in proc)

        c1, c2 = st.columns(2)
        c1.metric("Total Pump Time", f"{total_time:.1f} min")
        c2.metric("Total Fluid Volume", f"{total_vol:.4f} m³")

        st.subheader("Stage Duration Timeline")
        fig = px.bar(
            df_proc, x="Stage", y="Duration (min)",
            color="Stage", title="Pump Time by Stage",
        )
        st.plotly_chart(fig, use_container_width=True)

        if design.warnings:
            st.subheader("Engineering Warnings")
            for w in design.warnings:
                st.warning(w)

elif page == "P&A Plug Design":
    st.header("Plug & Abandonment / Suspension / Sidetrack Design")
    st.write("Design cement plugs for well suspension, open-hole sidetracking, or plug and abandonment (P&A) operations.")

    plug_type = st.radio("Select Plug Type", ["Suspension Plug", "Sidetrack Plug", "Abandonment Plug"])

    c1, c2 = st.columns(2)
    with c1:
        ch = st.number_input("Open Hole Diameter (in)", 6.0, 30.0, 12.25, 0.125, key="pph")
        cc = st.number_input("Casing Outer Diameter (in)", 4.0, 20.0, 9.625, 0.125, key="ppc")
        pl = st.number_input("Plug Length (m)", 5.0, 500.0, 50.0, 5.0, key="ppl")
    with c2:
        cd = st.number_input("Cement Slurry Density (kg/m³)", 1500.0, 2200.0, 1900.0, 10.0, key="pcd")
        sidetrack_depth = 0.0
        abandon_top = 0.0
        abandon_bottom = 0.0
        if plug_type == "Abandonment Plug":
            abandon_top = st.number_input("Plug Top Depth (m)", 0.0, 10000.0, 1000.0, 100.0, key="ptd")
            abandon_bottom = st.number_input("Plug Bottom Depth (m)", 0.0, 10000.0, 1050.0, 100.0, key="pbd")
        if plug_type == "Sidetrack Plug":
            sidetrack_depth = st.number_input("Casing Shoe Depth (m)", 0.0, 10000.0, 1000.0, 100.0, key="psd")

    if st.button("Design Cement Plug", key="dp"):
        if plug_type == "Suspension Plug":
            result = PAPLugDesign.design_suspension_plug(ch, cc, pl, cd)
        elif plug_type == "Sidetrack Plug":
            result = PAPLugDesign.design_sidetrack_plug(ch, cc, pl, cd, sidetrack_depth)
        else:
            result = PAPLugDesign.design_abandonment_plug(ch, cc, pl, abandon_top, abandon_bottom, cd)

        st.subheader(f"{plug_type} — Design Results")

        for k, v in result.items():
            label = k.replace("_", " ").title()
            if isinstance(v, float):
                if v < 1:
                    st.metric(label, f"{v:.6f}")
                elif v > 10000:
                    st.metric(label, f"{v:,.1f}")
                else:
                    st.metric(label, f"{v:.2f}")
            elif isinstance(v, int):
                st.metric(label, f"{v:,}")