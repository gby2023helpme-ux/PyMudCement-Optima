"""
Non-Newtonian system hydraulics engine.

Models the fluid mechanics of drilling fluids and cement slurries through
the complete circulating system (surface lines, drill string, bit nozzles
and annuli) using the generalized effective-viscosity method (API RP 13D
style). Supports Newtonian, Bingham-Plastic, Power Law and
Herschel-Bulkley fluids.

Key formulas (Fanning friction factor f):

  Pipe     laminar:  f = 16 / Re ,   ΔP = 2·f·ρ·V²·L / D
  Annulus  laminar:  f = 24 / Re ,   ΔP = 2·f·ρ·V²·L / D_h

with the effective viscosity μ_e chosen so that the laminar ΔP reproduces
the exact closed-form solution for each model:

  Newtonian          μ_e = μ
  Bingham-Plastic    pipe:    μ_e = μ_PV + τ₀·D / (6·V)
                     annulus: μ_e = μ_PV + τ₀·D_h / (4·V)
  Power Law          μ_e = K'·γ̇^(n-1)
                     pipe:    γ̇ = 8·V/D,  K' = K·((3n+1)/(4n))ⁿ
                     annulus: γ̇ = 12·V/D_h, K' = K·((2n+1)/(3n))ⁿ
  Herschel-Bulkley   μ_e = τ₀/γ̇ + K·γ̇^(n-1)  (approximate)

Turbulent / transition flow uses the Dodge-Metzner friction factor:

  1/√f = (4 / n'^0.75)·log₁₀(Re·f^(1-n'/2)) - 0.395 / n'^1.2
"""

import math
from typing import Dict, List, Tuple

from .models import CirculatingGeometry, RheologyModel, RheologyProfile

GRAVITY = 9.81  # m/s²

LAMINAR_RE = 2100
TURBULENT_RE = 4000


class NonNewtonianFluid:
    """Effective-viscosity rheology, Reynolds number and friction factor."""

    @staticmethod
    def characteristic_shear_rate(v: float, diameter_m: float, annular: bool) -> float:
        """Equivalent Newtonian shear rate for a given flow geometry."""
        return (12.0 if annular else 8.0) * v / diameter_m

    @staticmethod
    def effective_viscosity(
        fluid: RheologyProfile, v: float, diameter_m: float, annular: bool
    ) -> float:
        """Effective viscosity (Pa·s) matching the exact laminar solution."""
        if v <= 0.0 or diameter_m <= 0.0:
            return 0.0

        if fluid.model == RheologyModel.NEWTONIAN:
            return fluid.dynamic_viscosity_pa_s

        if fluid.model == RheologyModel.BINGHAM:
            c = 6.0 if not annular else 4.0
            return fluid.plastic_viscosity_pa_s + (
                fluid.yield_point_pa * diameter_m / (c * v)
            )

        gamma = NonNewtonianFluid.characteristic_shear_rate(v, diameter_m, annular)
        n = max(fluid.flow_behavior_index, 1e-6)

        if fluid.model == RheologyModel.POWER_LAW:
            factor = (
                (2.0 * n + 1.0) / (3.0 * n) if annular else (3.0 * n + 1.0) / (4.0 * n)
            )
            return fluid.consistency_index_pa_sn * (factor ** n) * gamma ** (n - 1.0)

        # Herschel-Bulkley (approximate)
        return fluid.yield_point_pa / gamma + fluid.consistency_index_pa_sn * gamma ** (n - 1.0)

    @staticmethod
    def flow_behavior_index_at_wall(
        fluid: RheologyProfile, v: float, diameter_m: float, annular: bool
    ) -> float:
        """Generalized flow behaviour index n' at the wall (for Dodge-Metzner)."""
        if fluid.model in (RheologyModel.NEWTONIAN, RheologyModel.BINGHAM):
            return 1.0
        n = max(fluid.flow_behavior_index, 1e-6)
        if fluid.model == RheologyModel.POWER_LAW:
            return n
        gamma = NonNewtonianFluid.characteristic_shear_rate(v, diameter_m, annular)
        tau_yield = max(fluid.yield_point_pa, 0.0)
        tau_total = tau_yield + fluid.consistency_index_pa_sn * gamma ** n
        if tau_total <= 0.0:
            return n
        return n * fluid.consistency_index_pa_sn * gamma ** n / tau_total

    @staticmethod
    def reynolds_number(
        fluid: RheologyProfile, density_kg_m3: float, v: float, diameter_m: float,
        annular: bool,
    ) -> float:
        """Generalized Reynolds number for the flow geometry."""
        mu_e = NonNewtonianFluid.effective_viscosity(fluid, v, diameter_m, annular)
        if mu_e <= 0.0 or v <= 0.0:
            return 0.0
        return density_kg_m3 * v * diameter_m / mu_e

    @staticmethod
    def flow_regime(reynolds: float) -> str:
        """Classify flow regime from the generalized Reynolds number."""
        if reynolds <= 0.0:
            return "—"
        if reynolds < LAMINAR_RE:
            return "Laminar"
        if reynolds < TURBULENT_RE:
            return "Transition"
        return "Turbulent"

    @staticmethod
    def dodge_metzner_friction(reynolds: float, n_prime: float) -> float:
        """Turbulent Fanning friction factor (Dodge & Metzner, 1959)."""
        if reynolds <= 0.0:
            return 0.0
        np_ = max(n_prime, 0.05)
        f = 0.001
        for _ in range(60):
            try:
                rhs = (
                    (4.0 / np_ ** 0.75) * math.log10(reynolds * f ** (1.0 - np_ / 2.0))
                    - 0.395 / np_ ** 1.2
                )
            except (ValueError, OverflowError):
                break
            if rhs <= 0.0:
                break
            f_new = 1.0 / (rhs ** 2)
            if abs(f_new - f) / max(f, 1e-12) < 1e-6:
                f = f_new
                break
            f = f_new
        return max(f, 1e-5)

    @staticmethod
    def friction_factor(
        fluid: RheologyProfile, density_kg_m3: float, v: float, diameter_m: float,
        annular: bool,
    ) -> Tuple[float, float, str]:
        """Return (Fanning friction factor, Reynolds number, flow regime)."""
        re = NonNewtonianFluid.reynolds_number(fluid, density_kg_m3, v, diameter_m, annular)
        if re <= 0.0:
            return 0.0, 0.0, "—"
        if re < LAMINAR_RE:
            f = 24.0 / re if annular else 16.0 / re
            return f, re, "Laminar"
        np_ = NonNewtonianFluid.flow_behavior_index_at_wall(fluid, v, diameter_m, annular)
        f = NonNewtonianFluid.dodge_metzner_friction(re, np_)
        regime = "Transition" if re < TURBULENT_RE else "Turbulent"
        return f, re, regime

    @staticmethod
    def pressure_drop(
        fluid: RheologyProfile, density_kg_m3: float, v: float, diameter_m: float,
        length_m: float, annular: bool,
    ) -> float:
        """Pressure drop (Pa) across a straight flow section."""
        if v <= 0.0 or diameter_m <= 0.0 or length_m <= 0.0:
            return 0.0
        f, _, _ = NonNewtonianFluid.friction_factor(
            fluid, density_kg_m3, v, diameter_m, annular,
        )
        return 2.0 * f * density_kg_m3 * v ** 2 * length_m / diameter_m


class SystemHydraulics:
    """Pressure-drop profile through the complete circulating system."""

    DISCHARGE_COEFFICIENT = 0.95

    @staticmethod
    def _pipe_area(diameter_m: float) -> float:
        return math.pi * diameter_m ** 2 / 4.0

    @staticmethod
    def _annular_area(outer_diameter_m: float, inner_diameter_m: float) -> float:
        return math.pi * (outer_diameter_m ** 2 - inner_diameter_m ** 2) / 4.0

    @classmethod
    def build_sections(cls, geometry: CirculatingGeometry) -> List[Dict]:
        """Ordered list of flow sections from surface line to annulus."""
        return [
            {
                "name": "Surface Lines",
                "kind": "pipe",
                "length_m": geometry.surface_line_length_m,
                "diameter_m": geometry.surface_line_id_m,
            },
            {
                "name": "Drill Pipe (interior)",
                "kind": "pipe",
                "length_m": geometry.drill_pipe_length_m,
                "diameter_m": geometry.drill_pipe_id_m,
            },
            {
                "name": "Drill Collars (interior)",
                "kind": "pipe",
                "length_m": geometry.drill_collar_length_m,
                "diameter_m": geometry.drill_collar_id_m,
            },
            {
                "name": "Drill Collar Annulus",
                "kind": "annulus",
                "length_m": geometry.drill_collar_annulus_length_m,
                "outer_diameter_m": geometry.open_hole_diameter_m,
                "inner_diameter_m": geometry.drill_collar_od_m,
            },
            {
                "name": "Drill Pipe Annulus",
                "kind": "annulus",
                "length_m": geometry.drill_pipe_annulus_length_m,
                "outer_diameter_m": geometry.open_hole_diameter_m,
                "inner_diameter_m": geometry.drill_pipe_od_m,
            },
        ]

    @classmethod
    def calculate(
        cls,
        geometry: CirculatingGeometry,
        fluid: RheologyProfile,
        density_kg_m3: float,
        flow_rate_m3_s: float,
        discharge_coefficient: float = DISCHARGE_COEFFICIENT,
    ) -> Dict:
        """Compute pressure drop, velocities, regime and ECD for the system."""
        q = max(flow_rate_m3_s, 0.0)
        sections: List[Dict] = []
        annular_dp = 0.0

        for spec in cls.build_sections(geometry):
            annular = spec["kind"] == "annulus"
            if annular:
                outer = spec["outer_diameter_m"]
                inner = spec["inner_diameter_m"]
                d = outer - inner
                area = cls._annular_area(outer, inner)
            else:
                d = spec["diameter_m"]
                area = cls._pipe_area(d)

            v = q / area if area > 0.0 else 0.0
            dp = NonNewtonianFluid.pressure_drop(
                fluid, density_kg_m3, v, d, spec["length_m"], annular,
            )
            re = NonNewtonianFluid.reynolds_number(fluid, density_kg_m3, v, d, annular)
            regime = NonNewtonianFluid.flow_regime(re)
            if annular:
                annular_dp += dp
            sections.append({
                "name": spec["name"],
                "type": "Annular Flow" if annular else "Pipe Flow",
                "length_m": spec["length_m"],
                "diameter_m": d,
                "velocity_m_s": v,
                "reynolds": int(round(re)),
                "regime": regime,
                "pressure_drop_pa": dp,
            })

        # Bit nozzles (Newtonian nozzle equation)
        nozzle_area = max(geometry.bit_nozzle_area_m2, 0.0)
        if nozzle_area > 0.0:
            jet_velocity = q / nozzle_area
            bit_dp = (
                density_kg_m3 * q ** 2
                / (2.0 * discharge_coefficient ** 2 * nozzle_area ** 2)
                if q > 0.0 else 0.0
            )
        else:
            jet_velocity = 0.0
            bit_dp = 0.0

        sections.append({
            "name": "Bit (nozzles)",
            "type": "Nozzle Flow",
            "length_m": 0.0,
            "diameter_m": math.sqrt(4.0 * nozzle_area / math.pi) if nozzle_area > 0.0 else 0.0,
            "velocity_m_s": jet_velocity,
            "reynolds": 0,
            "regime": "—",
            "pressure_drop_pa": bit_dp,
        })

        total_dp = sum(s["pressure_drop_pa"] for s in sections)
        ecd = (
            density_kg_m3 + annular_dp / (GRAVITY * geometry.tvd_m)
            if geometry.tvd_m > 0.0 else density_kg_m3
        )

        return {
            "sections": sections,
            "total_pressure_drop_pa": total_dp,
            "annular_pressure_drop_pa": annular_dp,
            "bit_pressure_drop_pa": bit_dp,
            "ecd_kg_m3": ecd,
            "jet_velocity_m_s": jet_velocity,
            "bit_hydraulic_power_w": bit_dp * q,
            "hydraulic_impact_force_n": (
                density_kg_m3 * q ** 2 / nozzle_area if nozzle_area > 0.0 else 0.0
            ),
        }
