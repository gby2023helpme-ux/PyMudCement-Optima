"""Unit-system abstraction for the GUI.

The core engines always work in SI (metres, Pa, kg/m³). This module lets
each page collect inputs and display results in either SI or Oilfield
(Field) units through a single ``Units`` helper bound to the
``unit_system`` entry of ``st.session_state``.
"""

from enum import Enum

import streamlit as st

from src.core.constants import (
    CP_PER_PA_S,
    KG_M3_PER_PPG,
    M_PER_FT,
    PA_PER_LBF_100FT2,
    PA_PER_PSI,
)

PA_M_PER_PSI_FT = PA_PER_PSI / M_PER_FT
M3_PER_BBL = 0.158987294928
LPM_PER_BBL_MIN = 158.987294928
LPS_PER_GPM = 0.0630901964
M_S_PER_FT_MIN = 0.00508
M2_PER_IN2 = 0.00064516
MPA_PER_PSI = 0.006894757293
KG_M3_PER_LB_BBL = 2.853010174
KW_PER_HP = 0.745699872
N_PER_LBF = 4.4482216152605


class UnitSystem(str, Enum):
    """The two supported unit systems."""

    SI = "SI"
    FIELD = "Field"

    @classmethod
    def _missing_(cls, value):
        # Defensive fallback: any unset/stale widget value defaults to SI.
        return cls.SI


class Units:
    """Unit converters + display labels for one unit system.

    ``*_to_si`` converts a user-entered value into SI; ``*_from_si``
    converts an engine result back into the display system. In SI mode
    every conversion is the identity, so existing behaviour is preserved.
    """

    def __init__(self, system: UnitSystem | str = "SI"):
        self.system = system if isinstance(system, UnitSystem) else UnitSystem(system)
        self.field = self.system == UnitSystem.FIELD

    # ── display labels ──────────────────────────────────────────────
    @property
    def depth(self) -> str:
        return "ft" if self.field else "m"

    @property
    def pressure(self) -> str:
        return "psi" if self.field else "Pa"

    @property
    def pressure_display(self) -> str:
        return "psi" if self.field else "MPa"

    @property
    def gradient(self) -> str:
        return "psi/ft" if self.field else "Pa/m"

    @property
    def density(self) -> str:
        return "ppg" if self.field else "kg/m³"

    @property
    def volume(self) -> str:
        return "bbl" if self.field else "m³"

    @property
    def pump_rate(self) -> str:
        return "bbl/min" if self.field else "L/min"

    @property
    def flow_rate(self) -> str:
        return "gpm" if self.field else "L/s"

    @property
    def velocity(self) -> str:
        return "ft/min" if self.field else "m/s"

    @property
    def area(self) -> str:
        return "in²" if self.field else "m²"

    @property
    def temperature(self) -> str:
        return "°F" if self.field else "°C"

    @property
    def strength(self) -> str:
        return "psi" if self.field else "MPa"

    @property
    def concentration(self) -> str:
        return "lb/bbl" if self.field else "kg/m³"

    @property
    def viscosity(self) -> str:
        return "cP" if self.field else "Pa·s"

    @property
    def yield_point(self) -> str:
        return "lbf/100ft²" if self.field else "Pa"

    @property
    def power(self) -> str:
        return "hp" if self.field else "kW"

    @property
    def force(self) -> str:
        return "lbf" if self.field else "N"

    # ── length: m ↔ ft ──────────────────────────────────────────────
    def len_to_si(self, v: float) -> float:
        return v * M_PER_FT if self.field else v

    def len_from_si(self, v: float) -> float:
        return v / M_PER_FT if self.field else v

    # ── pressure: Pa ↔ psi ──────────────────────────────────────────
    def pressure_to_si(self, v: float) -> float:
        return v * PA_PER_PSI if self.field else v

    def pressure_from_si(self, v: float) -> float:
        return v / PA_PER_PSI if self.field else v

    def pressure_display_from_si(self, v: float) -> float:
        return v / PA_PER_PSI if self.field else v / 1e6

    # ── pressure gradient: Pa/m ↔ psi/ft ────────────────────────────
    def gradient_to_si(self, v: float) -> float:
        return v * PA_M_PER_PSI_FT if self.field else v

    def gradient_from_si(self, v: float) -> float:
        return v / PA_M_PER_PSI_FT if self.field else v

    # ── density: kg/m³ ↔ ppg ────────────────────────────────────────
    def density_to_si(self, v: float) -> float:
        return v * KG_M3_PER_PPG if self.field else v

    def density_from_si(self, v: float) -> float:
        return v / KG_M3_PER_PPG if self.field else v

    # ── volume: m³ ↔ bbl ────────────────────────────────────────────
    def volume_to_si(self, v: float) -> float:
        return v * M3_PER_BBL if self.field else v

    def volume_from_si(self, v: float) -> float:
        return v / M3_PER_BBL if self.field else v

    # ── pump rate: L/min ↔ bbl/min ──────────────────────────────────
    def pump_to_si(self, v: float) -> float:
        return v * LPM_PER_BBL_MIN if self.field else v

    def pump_from_si(self, v: float) -> float:
        return v / LPM_PER_BBL_MIN if self.field else v

    # ── flow rate: L/s ↔ gpm ────────────────────────────────────────
    def flow_to_si(self, v: float) -> float:
        return v * LPS_PER_GPM if self.field else v

    def flow_from_si(self, v: float) -> float:
        return v / LPS_PER_GPM if self.field else v

    # ── velocity: m/s ↔ ft/min ──────────────────────────────────────
    def velocity_to_si(self, v: float) -> float:
        return v * M_S_PER_FT_MIN if self.field else v

    def velocity_from_si(self, v: float) -> float:
        return v / M_S_PER_FT_MIN if self.field else v

    # ── area: m² ↔ in² ──────────────────────────────────────────────
    def area_to_si(self, v: float) -> float:
        return v * M2_PER_IN2 if self.field else v

    def area_from_si(self, v: float) -> float:
        return v / M2_PER_IN2 if self.field else v

    # ── temperature: °C ↔ °F ────────────────────────────────────────
    def temp_to_si(self, v: float) -> float:
        return (v - 32.0) * 5.0 / 9.0 if self.field else v

    def temp_from_si(self, v: float) -> float:
        return v * 9.0 / 5.0 + 32.0 if self.field else v

    # ── compressive strength: MPa ↔ psi ─────────────────────────────
    def strength_to_si(self, v: float) -> float:
        return v * MPA_PER_PSI if self.field else v

    def strength_from_si(self, v: float) -> float:
        return v / MPA_PER_PSI if self.field else v

    # ── concentration: kg/m³ ↔ lb/bbl ───────────────────────────────
    def concentration_from_si(self, v: float) -> float:
        return v / KG_M3_PER_LB_BBL if self.field else v

    # ── viscosity: Pa·s ↔ cP ────────────────────────────────────────
    def viscosity_to_si(self, v: float) -> float:
        return v / CP_PER_PA_S if self.field else v

    def viscosity_from_si(self, v: float) -> float:
        return v * CP_PER_PA_S if self.field else v

    # ── yield point: Pa ↔ lbf/100ft² ────────────────────────────────
    def yield_to_si(self, v: float) -> float:
        return v * PA_PER_LBF_100FT2 if self.field else v

    def yield_from_si(self, v: float) -> float:
        return v / PA_PER_LBF_100FT2 if self.field else v

    # ── power: kW ↔ hp ──────────────────────────────────────────────
    def power_to_si(self, v: float) -> float:
        return v * KW_PER_HP if self.field else v

    def power_from_si(self, v: float) -> float:
        return v / KW_PER_HP if self.field else v

    # ── force: N ↔ lbf ──────────────────────────────────────────────
    def force_to_si(self, v: float) -> float:
        return v * N_PER_LBF if self.field else v

    def force_from_si(self, v: float) -> float:
        return v / N_PER_LBF if self.field else v


def get_units() -> Units:
    """Build a ``Units`` helper from the current session unit system."""
    return Units(st.session_state.get("unit_system", "SI"))
