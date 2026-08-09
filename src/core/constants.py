"""Shared physical and engineering constants.

Single source of truth for the unit-conversion factors, physical constants
and slurry-design basis values used by the core engines and the GUI layer.
SI is the canonical system (metres, Pa, kg/m³, °C); no calculation module
hard-codes a conversion factor or design basis inline.
"""

# ── physical constants ────────────────────────────────────────────────
GRAVITY = 9.81  # m/s²
WATER_DENSITY_KC_M3 = 1000.0  # kg/m³

# ── unit-conversion factors (SI = canonical) ──────────────────────────
M_PER_IN = 0.0254  # m per inch
M_PER_FT = 0.3048  # m per foot
L_PER_M3 = 1000.0  # litres per m³
W_PER_KW = 1000.0  # watts per kilowatt
CP_PER_PA_S = 1000.0  # centipoise per Pa·s
KG_M3_PER_PPG = 119.8264273207  # kg/m³ per ppg
PA_PER_PSI = 6894.757293168  # Pa per psi
PSI_PER_PA = 1.0 / PA_PER_PSI  # psi per Pa
PA_PER_LBF_100FT2 = 0.47880259  # Pa per lbf/100ft²
SACK_VOLUME_M3 = 0.0326  # cement volume per 94-lb sack (~m³/sack)

# ── operational safety factors ────────────────────────────────────────
MAX_SAFE_PRESSURE_FACTOR = 0.85  # max safe = 85% of bumping pressure
PLUG_BUMP_GEL_FACTOR = 0.05  # empirical gel build-up factor for plug bumping
BUMPING_AREA_TERM_PA = 100000.0  # empirical bumping term per m² of casing area

# ── cement slurry design basis ────────────────────────────────────────
BASE_SLURRY_DENSITY_KC_M3 = 1440.0  # neat Class-G cement slurry (kg/m³)
WEIGHTING_THRESHOLD_DENSITY_KC_M3 = 1500.0  # above this, add a weighting agent
LIGHTWEIGHT_THRESHOLD_DENSITY_KC_M3 = 1400.0  # below this, add a lightweight agent
DENSITY_MATCH_TOLERANCE_KC_M3 = 50.0  # acceptable achieved-vs-target gap (kg/m³)
RETARDER_ONSET_TEMPERATURE_C = 100.0  # retarder ramps up above this temperature
RETARDER_TEMP_RAMP_C = 100.0  # retarder reaches max dosage 100 °C above onset
HIGH_TEMPERATURE_WARNING_C = 150.0  # lab verification advised above this
MIN_PUMP_TIME_WARNING_MIN = 30.0  # shorter pump times need retarder margin
THICKENING_TIME_FACTOR = 1.5  # thickening time safety multiplier on pump time
ESTIMATED_PUMP_TIME_FACTOR = 1.2  # job-duration safety multiplier on pump time
MIN_COMPRESSIVE_STRENGTH_MPA = 3.5  # floor on estimated 24 h strength (MPa)
COMPRESSIVE_STRENGTH_OFFSET_MPA = 20.0  # strength intercept at base density (MPa)
COMPRESSIVE_STRENGTH_SLOPE = 0.01  # strength reduction per kg/m³ above base
DISPLACEMENT_VOLUME_FACTOR = 1.05  # extra volume to displace plugs/slurry
SIDETRACK_BORE_FILL_FRACTION = 0.3  # fraction of borehole volume filled for sidetrack plugs
FLUSH_DENSITY_KC_M3 = 1000.0  # water flush density (kg/m³)
SPACER_DENSITY_KC_M3 = 1300.0  # typical weighted spacer density (kg/m³)

# ── cement base densities by cement type (kg/m³) ──────────────────────
CEMENT_BASE_DENSITIES = {
    "WATER_BASED": 1440.0,
    "OIL_BASED": 1380.0,
    "FOAM": 1250.0,
    "GEL": 1500.0,
    "LIGHTEN": 1300.0,
    "HEAVY_DENSITY": 1800.0,
}
