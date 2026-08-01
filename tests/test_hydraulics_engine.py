"""Tests for the non-Newtonian system hydraulics engine."""

import math

import pytest

from src.core.engineering_calculators import BinghamPlasticRheology
from src.core.hydraulics_engine import NonNewtonianFluid, SystemHydraulics
from src.core.models import CirculatingGeometry, MudReport, RheologyModel, RheologyProfile


def newtonian(mu=0.01):
    return RheologyProfile(model=RheologyModel.NEWTONIAN, dynamic_viscosity_pa_s=mu)


def bingham(pv=0.01, yp=5.0):
    return RheologyProfile(model=RheologyModel.BINGHAM, plastic_viscosity_pa_s=pv, yield_point_pa=yp)


def power_law(k=0.5, n=0.7):
    return RheologyProfile(
        model=RheologyModel.POWER_LAW, consistency_index_pa_sn=k, flow_behavior_index=n,
    )


def herschel_bulkley(k=0.5, n=0.7, yp=5.0):
    return RheologyProfile(
        model=RheologyModel.HERSCHEL_BULKLEY,
        consistency_index_pa_sn=k, flow_behavior_index=n, yield_point_pa=yp,
    )


# ── Effective viscosity & Reynolds ──────────────────────────────────

def test_newtonian_effective_viscosity_is_identity():
    f = newtonian(0.02)
    assert NonNewtonianFluid.effective_viscosity(f, 1.0, 0.1, annular=False) == 0.02
    assert NonNewtonianFluid.effective_viscosity(f, 1.0, 0.1, annular=True) == 0.02


def test_bingham_effective_viscosity_adds_yield_term():
    f = bingham(pv=0.01, yp=5.0)
    mu_pipe = NonNewtonianFluid.effective_viscosity(f, 0.5, 0.1, annular=False)
    expected = 0.01 + 5.0 * 0.1 / (6.0 * 0.5)
    assert abs(mu_pipe - expected) < 1e-9
    mu_ann = NonNewtonianFluid.effective_viscosity(f, 0.5, 0.1, annular=True)
    expected_ann = 0.01 + 5.0 * 0.1 / (4.0 * 0.5)
    assert abs(mu_ann - expected_ann) < 1e-9


def test_power_law_effective_viscosity_formula():
    f = power_law(k=0.5, n=0.7)
    mu = NonNewtonianFluid.effective_viscosity(f, 0.5, 0.1, annular=False)
    gamma = 8.0 * 0.5 / 0.1
    factor = (3.0 * 0.7 + 1.0) / (4.0 * 0.7)
    expected = 0.5 * factor ** 0.7 * gamma ** (0.7 - 1.0)
    assert abs(mu - expected) < 1e-9


def test_reynolds_number_newtonian():
    f = newtonian(0.01)
    re = NonNewtonianFluid.reynolds_number(f, 1000.0, 0.1, 0.1, annular=False)
    assert abs(re - (1000.0 * 0.1 * 0.1 / 0.01)) < 1e-6


def test_flow_regime_classification():
    assert NonNewtonianFluid.flow_regime(100) == "Laminar"
    assert NonNewtonianFluid.flow_regime(2100) == "Transition"
    assert NonNewtonianFluid.flow_regime(5000) == "Turbulent"
    assert NonNewtonianFluid.flow_regime(0) == "—"


# ── Pressure drop: exact laminar limits ─────────────────────────────

def test_newtonian_pipe_laminar_dp():
    f = newtonian(0.01)
    v, d, length, rho = 0.1, 0.1, 100.0, 1000.0
    dp = NonNewtonianFluid.pressure_drop(f, rho, v, d, length, annular=False)
    expected = 32.0 * 0.01 * v * length / d ** 2
    assert abs(dp - expected) / expected < 1e-6


def test_newtonian_annulus_laminar_dp():
    f = newtonian(0.01)
    v, d_h, length, rho = 0.1, 0.2, 100.0, 1000.0
    dp = NonNewtonianFluid.pressure_drop(f, rho, v, d_h, length, annular=True)
    expected = 48.0 * 0.01 * v * length / d_h ** 2
    assert abs(dp - expected) / expected < 1e-6


def test_bingham_pipe_laminar_dp_matches_closed_form():
    f = bingham(pv=0.01, yp=5.0)
    v, d, length, rho = 0.5, 0.1, 100.0, 1000.0
    dp = NonNewtonianFluid.pressure_drop(f, rho, v, d, length, annular=False)
    expected = 32.0 * 0.01 * v * length / d ** 2 + 16.0 * 5.0 * length / (3.0 * d)
    assert abs(dp - expected) / expected < 1e-6


def test_power_law_pipe_laminar_dp_matches_closed_form():
    f = power_law(k=0.5, n=0.7)
    v, d, length, rho = 0.5, 0.1, 100.0, 1000.0
    dp = NonNewtonianFluid.pressure_drop(f, rho, v, d, length, annular=False)
    gamma_w = (8.0 * v / d) * (3.0 * 0.7 + 1.0) / (4.0 * 0.7)
    expected = 4.0 * 0.5 * gamma_w ** 0.7 * length / d
    assert abs(dp - expected) / expected < 1e-6


def test_laminar_friction_factor():
    f = newtonian(0.01)
    ff, re, regime = NonNewtonianFluid.friction_factor(f, 1000.0, 0.1, 0.1, annular=False)
    assert regime == "Laminar"
    assert abs(ff - 16.0 / re) < 1e-12


# ── Turbulent regime ────────────────────────────────────────────────

def test_turbulent_regime_and_friction_less_than_laminar():
    f = newtonian(0.001)
    ff, re, regime = NonNewtonianFluid.friction_factor(f, 1000.0, 5.0, 0.1, annular=False)
    assert regime == "Turbulent"
    assert re > 4000
    assert ff < 16.0 / 2100.0


def test_dodge_metzner_newtonian_limit():
    f = NonNewtonianFluid.dodge_metzner_friction(1e5, 1.0)
    assert 0.003 < f < 0.006


def test_hb_effective_viscosity_has_yield_term():
    f = herschel_bulkley(k=0.5, n=0.7, yp=5.0)
    mu = NonNewtonianFluid.effective_viscosity(f, 0.5, 0.1, annular=False)
    gamma = 8.0 * 0.5 / 0.1
    expected = 5.0 / gamma + 0.5 * gamma ** -0.3
    assert abs(mu - expected) < 1e-9


# ── Whole system ────────────────────────────────────────────────────

def make_geometry():
    return CirculatingGeometry(
        surface_line_length_m=100.0,
        surface_line_id_m=0.1,
        drill_pipe_length_m=2000.0,
        drill_pipe_id_m=0.1,
        drill_pipe_od_m=0.13,
        drill_collar_length_m=200.0,
        drill_collar_id_m=0.08,
        drill_collar_od_m=0.2,
        bit_nozzle_area_m2=0.001,
        open_hole_diameter_m=0.3,
        tvd_m=2000.0,
    )


def test_system_calculate_sums_sections_and_ecd():
    geom = make_geometry()
    result = SystemHydraulics.calculate(geom, newtonian(), 1000.0, 0.03)
    assert len(result["sections"]) == 6  # 5 flow sections + bit
    assert any(s["name"] == "Bit (nozzles)" for s in result["sections"])
    section_sum = sum(s["pressure_drop_pa"] for s in result["sections"])
    assert abs(section_sum - result["total_pressure_drop_pa"]) < 1e-6
    annular = sum(
        s["pressure_drop_pa"] for s in result["sections"] if s["type"] == "Annular Flow"
    )
    assert abs(annular - result["annular_pressure_drop_pa"]) < 1e-6
    expected_ecd = 1000.0 + annular / (9.81 * 2000.0)
    assert abs(result["ecd_kg_m3"] - expected_ecd) < 1e-6


def test_system_zero_flow_gives_zero_drops():
    geom = make_geometry()
    result = SystemHydraulics.calculate(geom, bingham(), 1000.0, 0.0)
    assert result["total_pressure_drop_pa"] == 0.0
    assert result["annular_pressure_drop_pa"] == 0.0
    assert result["bit_pressure_drop_pa"] == 0.0
    assert result["ecd_kg_m3"] == 1000.0


def test_bit_pressure_drop_scales_with_flow_squared():
    geom = make_geometry()
    r1 = SystemHydraulics.calculate(geom, newtonian(), 1000.0, 0.02)
    r2 = SystemHydraulics.calculate(geom, newtonian(), 1000.0, 0.04)
    ratio = r2["bit_pressure_drop_pa"] / r1["bit_pressure_drop_pa"]
    assert abs(ratio - 4.0) < 1e-6


def test_ecd_increases_with_flow():
    geom = make_geometry()
    low = SystemHydraulics.calculate(geom, bingham(), 1100.0, 0.015)
    high = SystemHydraulics.calculate(geom, bingham(), 1100.0, 0.045)
    assert high["ecd_kg_m3"] > low["ecd_kg_m3"] > 1100.0


def test_pressure_drop_increases_with_length():
    geom = make_geometry()
    base = SystemHydraulics.calculate(geom, power_law(), 1000.0, 0.03)
    geom.drill_pipe_length_m *= 2.0
    longer = SystemHydraulics.calculate(geom, power_law(), 1000.0, 0.03)
    assert longer["total_pressure_drop_pa"] > base["total_pressure_drop_pa"]


# ── Unit conversion fix ─────────────────────────────────────────────

def test_mud_report_ppg_conversion_factor_is_correct():
    mr = MudReport(mud_weight_ppg=10.0, density_kg_m3=1198.26, plastic_viscosity_cP=20.0)
    _, factors = BinghamPlasticRheology.convert_units(mr)
    assert abs(factors["PPG_to_kgm3"] - 10.0 * 119.826) < 1e-6
    assert abs(factors["cP_to_Pa_s"] - 0.02) < 1e-12
