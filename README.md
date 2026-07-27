# PyMudCement-Optima

**Intelligent Mud & Cement Design Suite**

A Python-based software application for automating drilling fluid design and primary cementing calculations, developed as the PENG 258 Capstone Project at UENR.

---

## Quick Start

```bash
cd PyMudCement-Optima
pip install -r requirements.txt

# Run tests (33 tests)
python -m pytest tests/ -v

# Run Streamlit GUI
streamlit run src/gui/drilling_interface.py

# Run CLI
python main/cli.py pressure-balance --depth 2000 --pore-pressure 21000000 --fracture-gradient 15000
```

---

## Features

### Drilling Fluids Engine
- **Hydrostatic Pressure Balance** – Calculate minimum mud weight to balance formation pore pressure
- **Safety Window Alerts** – Instant warnings for kick risk or lost circulation
- **Mud Report Parser** – Upload CSV mud reports, parse PV/YP data
- **Bingham-Plastic Rheology** – Shear stress vs shear rate curves from mud report data
- **Annular Hydraulics** – Volume, velocity, and ECD calculations
- **ECD Tracking** – Plot ECD vs annular pressure drop

### Cementing Engineering Module
- **Slurry Design** – Automated additive selection based on BHT and target density
- **Additive Database** – 9 additives with dosage ranges, temperature limits, and costs
- **Procedure Sheet Generator** – Stage-by-stage cementing job procedure with timelines
- **Bumping Pressure** – Calculate safe operational limits for rig crew
- **P&A Plug Design** – Suspension, sidetrack, and abandonment plug calculations

### GUI (6 Tabs)
| Tab | Description |
|-----|-------------|
| Pressure Balance | Formation data input → mud weight calculation → safety alerts |
| Mud Report Parser | CSV upload → PV/YP charts → Bingham-Plastic rheology curve |
| Annular Hydraulics & ECD | Casing/hole input → volume, velocity, ECD vs pressure chart |
| Cement Slurry Design | BHT, target density → additive plan, warnings, thickening time |
| Cementing Procedure Sheet | Full procedure generator with stage timeline chart |
| P&A Plug Design | Suspension / Sidetrack / Abandonment plug calculations |

---

## Project Structure

```
PyMudCement-Optima/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── models.py                  # Data classes and enums
│   │   ├── engineering_calculators.py # Drilling fluids math engines
│   │   └── cementing_engine.py        # Cementing math engines
│   └── gui/
│       ├── __init__.py
│       └── drilling_interface.py       # Streamlit GUI (6 tabs)
├── tests/
│   ├── test_engineering_calculators.py # 11 tests
│   └── test_cementing_engine.py        # 22 tests
├── main/
│   ├── __init__.py
│   └── cli.py                         # CLI entry point
├── docs/
│   └── TECHNICAL_REPORT.md            # Mathematical validation report
├── requirements.txt
└── README.md
```

---

## Engineering Equations Implemented

### Hydrostatic Pressure Balance
```
P_hydrostatic = ρ_mud × g × z
Required mud density = P_pore / (g × z)
```

### Bingham-Plastic Rheology
```
τ = YP + μ_PV × γ̇
```

### Annular Volume
```
V_annular = (π/4) × (D_hole² - D_casing²) × L × (1 + W_e)
```

### Equivalent Circulating Density
```
ECD = (P_hydrostatic + P_annular) / (g × z)
```

### Cement Volume
```
V_cement = V_slurry / (1 + w)
V_water = V_cement × w
```

---

## Testing

```bash
python -m pytest tests/ -v
```

**33 tests** covering:
- Hydrostatic pressure calculations
- Bingham-Plastic rheology
- Annular volume and ECD
- Cement slurry design
- Procedure sheet generation
- Bumping pressure
- P&A plug design (suspension, sidetrack, abandonment)
- Additive database validation

---

## Technical Report

See `docs/TECHNICAL_REPORT.md` for:
- Hand-calculated verification of all core equations
- Comparative analysis against industry cementing company recommendations
- Limitations and recommendations

---

## Requirements

- Python 3.10+
- NumPy, SciPy
- Streamlit
- Pandas, Plotly

---

## License

MIT License – PENG 258 Capstone Project, UENR
