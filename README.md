# PyMudCement-Optima

**Intelligent Mud & Cement Design Suite** — a Python application for automating drilling-fluid design and primary cementing calculations (PENG 258 Capstone Project, UENR).

---

## Setup Instructions

### 1. Prerequisites

- Python **3.10 or newer** (64-bit)
- `pip` (bundled with Python)
- A modern web browser (Chrome, Edge, Firefox, or Safari)

### 2. Get the code

```bash
git clone https://github.com/gby2023helpme-ux/PyMudCement-Optima.git
cd PyMudCement-Optima
```

### 3. Create a virtual environment (recommended)

```bash
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the software

Run the graphical interface:

```bash
streamlit run src/gui/app.py
```

The app opens at `http://localhost:8501`. Log in (or Register a new account) to enter the dashboard.

Run the command-line interface (same engines, no GUI):

```bash
python main/cli.py pressure-balance --depth 2000 --pore-pressure 21000000 --fracture-gradient 15000
```

### 6. Run the test suite

```bash
python -m pytest tests/ -v
```

52 tests validate the core engineering engines (hydrostatics, rheology, annular hydraulics, non-Newtonian system hydraulics, cementing and P&A plug design).

### 7. Deploy to Streamlit Community Cloud (optional)

1. Push the repository to GitHub.
2. On share.streamlit.io, create a new app pointing at the repo, branch `main`, main module `src/gui/app.py`.
3. The cloud installs `requirements.txt` and serves the app at `https://<app>.streamlit.app`.

---

## Dependency Lists

### Runtime dependencies (`requirements.txt`)

| Package | Version | Purpose |
|---------|---------|---------|
| Streamlit | `==1.52.0` | Web application framework (UI, widgets, charts) |
| NumPy | `>=1.24.0` | Numerical arrays |
| SciPy | `>=1.10.0` | Scientific computing |
| Pandas | `>=2.0.0` | Data tables and CSV parsing |
| Plotly | `>=5.0.0` | Interactive charts (bar, line, scatter) |

Notes:

- Streamlit is pinned to `1.52.0` because it is the first release with Python-3.14 wheel support (required by Streamlit Community Cloud).
- Plotly charts render through Streamlit's bundled Plotly.js frontend — no separate frontend install.
- Tests additionally require `pytest` (installed separately: `pip install pytest`).

### Runtime web assets (loaded from Google Fonts, no install needed)

- **Inter** — application typeface.
- **Material Symbols Rounded** — icon font used for UI icons (nav, heroes, logo) and the `oil_barrel` favicon.

---

## User Manual

### 1. Logging in

The app opens on a login screen. Choose **Register** to create an account (username, full name, password), or log in with an existing account. Passwords are stored hashed in `users.json`. After login you land on the **Home** dashboard.

### 2. Choosing a unit system

Use the **SI | Field** selector in the sidebar. SI shows metres, Pa/MPa, kg/m³, m³ and L/s; Field shows ft, psi, ppg, bbl and gpm. Inputs and outputs convert automatically — the engines always calculate in SI internally.

### 3. Module-by-module guide

| Module | What you enter | What you get |
|--------|----------------|--------------|
| **Pressure Balance** | Casing interval depth, pore pressure, fracture gradient | Minimum mud weight, kick / lost-circulation safety warnings |
| **Mud Report Parser** | Upload a CSV mud report | PV/YP values and the Bingham-Plastic shear stress vs shear rate curve |
| **Annular Hydraulics & ECD** | Hole and casing diameters/lengths, flow rate | Annular volume, annular velocity, ECD vs pressure chart |
| **System Hydraulics** | Rheological model + fluid properties, circulating geometry, pump rate | Pressure-drop profile per section, flow regime (laminar/transition/turbulent), bit hydraulics, ECD |
| **Cement Slurry Design** | BHT, target density | Additive plan with dosage, warnings, thickening time |
| **Cementing Procedure Sheet** | Job parameters | Stage-by-stage procedure with a timeline chart |
| **P&A Plug Design** | Plug type and well data | Suspension / sidetrack / abandonment plug calculations |

### 4. Reading the results

- **Safety-critical outputs** are highlighted as warnings — e.g. kick risk when the required mud weight exceeds the fracture gradient, or high ECD approaching the fracture gradient.
- **System Hydraulics** classifies each section as Laminar (`Re < 2100`), Transition, or Turbulent (`Re ≥ 4000`) and shows the share of total pressure drop per section.
- All charts are interactive: hover for values, zoom, and download as PNG from the Plotly toolbar.

### 5. Resetting / logging out

Use **Logout** in the sidebar to end the session. Your account and settings are saved in `users.json` for the next login.

---

## License

MIT License – PENG 258 Capstone Project, UENR.
