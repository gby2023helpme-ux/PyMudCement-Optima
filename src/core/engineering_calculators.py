"""
Core mathematical engines for PyMudCement-Optima.

This module contains the fundamental engineering calculations for both drilling fluids
and cementing operations as specified in the PENG 258 capstone project requirements.
"""

import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

from .models import (
    Formation,
    MudReport,
    AnnularGeometry,
    SlurryDesign,
)

GRAVITY = 9.81  # m/s²

class HydrostaticPressureCalculator:
    """Calculates hydrostatic pressure balance for drilling operations."""

    @staticmethod
    def calculate_mud_weight_for_pore_balance(
        formation: Formation
    ) -> Tuple[float, float]:
        """
        Calculate minimum mud weight required to balance formation pore pressure.

        Args:
            formation: Formation object with pore pressure and depth

        Returns:
            Tuple of (mud_weight_kg_m3, equivalent_mud_weight_ppg)

        Formula:
            P_hydrostatic = mud_density × gravity × depth
            Set P_hydrostatic = P_pore to balance
        """
        # Calculate required mud density to balance pore pressure
        required_mud_density = formation.pore_pressure_pa / (
            GRAVITY * formation.depth_m
        )

        # Convert from kg/m³ to PPG (1 ppg = 119.826 kg/m³, so 1 kg/m³ = 0.0083454 ppg)
        required_mud_weight_ppg = required_mud_density / 119.826

        return required_mud_density, required_mud_weight_ppg

    @staticmethod
    def evaluate_safety_window(
        mud_density: float,
        pore_pressure: float,
        fracture_gradient: float,
        depth_m: float
    ) -> Dict[str, float]:
        """
        Evaluate if mud weight is within safe operational window.

        Args:
            mud_density: Current mud density (kg/m³)
            pore_pressure: Formation pore pressure (Pa)
            fracture_gradient: Fracture gradient of formation
            depth_m: Depth of formation (m)

        Returns:
            Dictionary with safety status and limits

        Criteria:
            Mud weight must be > pore pressure to avoid kicks
            Mud weight must be < fracture pressure to avoid lost circulation
        """
        fracture_pressure = fracture_gradient * GRAVITY * depth_m
        hydrostatic_pressure = mud_density * GRAVITY * depth_m

        if hydrostatic_pressure < pore_pressure:
            safety_status = "INSUFFICIENT - Risk of kick"
        elif hydrostatic_pressure > fracture_pressure:
            safety_status = "EXCESSIVE - Risk of lost circulation"
        else:
            safety_status = "SAFE - Within operational window"

        return {
            "safety_status": safety_status,
            "pore_pressure_limit": pore_pressure / (GRAVITY * depth_m),
            "fracture_pressure_limit": fracture_pressure / (GRAVITY * depth_m),
            "mud_density": mud_density,
        }


class BinghamPlasticRheology:
    """Implements Bingham-Plastic fluid model for drilling hydraulics."""

    @staticmethod
    def calculate_shear_stress(
        yield_point_pa: float,
        plastic_viscosity_pa_s: float,
        shear_rate_s1: float
    ) -> float:
        """
        Calculate shear stress using Bingham-Plastic model.

        Formula:
            τ = YP + μ × γ_rate

        Args:
            yield_point_pa: Yield Point (Pa)
            plastic_viscosity_pa_s: Plastic Viscosity (Pa·s)
            shear_rate_s1: Shear rate (s⁻¹)

        Returns:
            Shear stress (Pa)
        """
        return yield_point_pa + (plastic_viscosity_pa_s * shear_rate_s1)

    @staticmethod
    def convert_units(mud_report: MudReport) -> Tuple[MudReport, Dict[str, float]]:
        """
        Convert standard mud report units to SI units for calculations.

        Args:
            mud_report: Mud report with field units

        Returns:
            Tuple of (SI_unit_mud_report, conversion_factors)
        """
        # Create new mud report with converted units
        si_mud_report = MudReport(
            api_number=mud_report.api_number,
            date=mud_report.date,
            temperature_c=mud_report.temperature_c,
            density_kg_m3=mud_report.density_kg_m3,
            plastic_viscosity_cP=mud_report.plastic_viscosity_cP,
            yield_point_lbf_100ft2=mud_report.yield_point_lbf_100ft2,
            mud_weight_ppg=mud_report.mud_weight_ppg,
            notes=mud_report.notes,
        )

        # Conversion factors
        conversion_factors = {
            "C_to_K": mud_report.temperature_c + 273.15,
            "PPG_to_kgm3": mud_report.mud_weight_ppg * 119.826,
            "cP_to_Pa_s": mud_report.plastic_viscosity_cP / 1000.0,
            "lbf_100ft2_to_Pa": mud_report.yield_point_lbf_100ft2 * 47.8803,
        }

        return si_mud_report, conversion_factors


class AnnularHydraulics:
    """Calculates annular pressure drops and Equivalent Circulating Density (ECD)."""

    @staticmethod
    def calculate_annular_volume(geometry: AnnularGeometry) -> float:
        """
        Calculate annular volume for cementing or drilling operations.

        Formula:
            V_annular = (π/4) × (D_hole² - d_casing²) × L × (1 + We)

        Args:
            geometry: AnnularGeometry object with casing and hole dimensions

        Returns:
            Annular volume (m³)
        """
        hole_area = math.pi * (geometry.hole_diameter_m ** 2) / 4
        casing_area = math.pi * (geometry.casing_diameter_m ** 2) / 4

        base_volume = (hole_area - casing_area) * geometry.cemented_interval_length_m
        excess_volume = base_volume * geometry.wash_out_factor

        total_volume = base_volume + excess_volume

        return total_volume

    @staticmethod
    def calculate_ECD(
        mud_density_kg_m3: float,
        annular_pressure_drop_pa: float,
        depth_m: float
    ) -> float:
        """
        Calculate Equivalent Circulating Density (ECD).

        Formula:
            ECD = (P_hydrostatic + P_annular) / (gravity × depth)

        Args:
            mud_density_kg_m3: Mud density (kg/m³)
            annular_pressure_drop_pa: Annular pressure drop (Pa)
            depth_m: True vertical depth (m)

        Returns:
            Equivalent Circulating Density (kg/m³)
        """
        hydrostatic_pressure = mud_density_kg_m3 * GRAVITY * depth_m
        total_pressure = hydrostatic_pressure + annular_pressure_drop_pa

        ecd = total_pressure / (GRAVITY * depth_m)

        return ecd

    @staticmethod
    def calculate_fluid_velocity(
        flow_rate_m3_s: float,
        hole_diameter_m: float,
        casing_diameter_m: float
    ) -> float:
        """
        Calculate fluid velocity in the annulus.

        Args:
            flow_rate_m3_s: Flow rate (m³/s)
            hole_diameter_m: Hole diameter (m)
            casing_diameter_m: Casing diameter (m)

        Returns:
            Fluid velocity (m/s)
        """
        annular_area = (
            math.pi * hole_diameter_m ** 2 / 4
            - math.pi * casing_diameter_m ** 2 / 4
        )

        if annular_area <= 0:
            return 0.0

        velocity = flow_rate_m3_s / annular_area
        return velocity


class SlurryDesigner:
    """Designs cement slurries and calculates volumes for cementing operations."""

    @staticmethod
    def calculate_slurry_volumes(
        geometry: AnnularGeometry,
        mud_volume_m3: float,
        spacer_volume_m3: float,
        displacement_volume_m3: float
    ) -> Dict[str, float]:
        """
        Calculate total volumes required for a cementing job.

        Args:
            geometry: AnnularGeometry object
            mud_volume_m3: Volume of drilling mud (m³)
            spacer_volume_m3: Volume of spacer fluid (m³)
            displacement_volume_m3: Volume of displacement fluid (m³)

        Returns:
            Dictionary with total volumes and breakdown
        """
        annular_volume = AnnularHydraulics.calculate_annular_volume(geometry)

        # Validate that mud replacement is possible
        if mud_volume_m3 > annular_volume:
            raise ValueError("Mud volume exceeds annular volume")

        cement_volume = annular_volume - spacer_volume_m3 - displacement_volume_m3

        if cement_volume < 0:
            raise ValueError("Spacer and displacement volumes exceed annular volume")

        return {
            "annular_volume_m3": annular_volume,
            "cement_volume_m3": cement_volume,
            "spacer_volume_m3": spacer_volume_m3,
            "displacement_volume_m3": displacement_volume_m3,
            "total_volume_m3": annular_volume + mud_volume_m3 +
                               spacer_volume_m3 + displacement_volume_m3,
        }

    @staticmethod
    def calculate_plug_bumping_pressure(
        casing_diameter_m: float,
        displacement_pressure_pa: float,
        cement_set_time_min: float,
        emergency_stoping_time_min: float = 15.0
    ) -> Dict[str, float]:
        """
        Calculate plug bumping pressure for operational safety limits.

        Args:
            casing_diameter_m: Casing inner diameter (m)
            displacement_pressure_pa: Pressure from displacement fluid (Pa)
            cement_set_time_min: Cement gelation/set time (min)
            emergency_stoping_time_min: Emergency stopping time (min)

        Returns:
            Dictionary with pressure calculations and safety limits
        """
        casing_area = math.pi * (casing_diameter_m ** 2) / 4

        # Calculate required bumping pressure
        bumping_pressure = displacement_pressure_pa + (
            casing_area * 9.81 * 0.05 * emergency_stoping_time_min
        )

        # Calculate safe operational window
        max_safe_pressure = bumping_pressure * 0.85  # 85% of bumping pressure

        return {
            "bumping_pressure_pa": bumping_pressure,
            "max_safe_pressure_pa": max_safe_pressure,
            "safety_margin_percentage": 15.0,
            "casing_area_m2": casing_area,
        }