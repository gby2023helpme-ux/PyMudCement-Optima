"""
Test suite for PyMudCement-Optima.

This module contains comprehensive unit and integration tests for both drilling fluids
and cementing engineering calculations, ensuring accuracy and reliability of the
mathematical computations.
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.engineering_calculators import (
    HydrostaticPressureCalculator,
    BinghamPlasticRheology,
    AnnularHydraulics,
    SlurryDesigner,
)
from src.core.models import (
    Formation,
    MudReport,
    AnnularGeometry,
)

class TestHydrostaticPressureCalculator(unittest.TestCase):
    """Test hydrostatic pressure balance calculations."""

    def test_calculate_mud_weight_for_pore_balance(self):
        """Test minimum mud weight calculation for pore pressure balance."""
        formation = Formation(
            name="Test Interval",
            depth_m=1000.0,
            pore_pressure_pa=10000000.0,
            fracture_gradient=12000.0,
        )

        required_density, required_ppg = (
            HydrostaticPressureCalculator.calculate_mud_weight_for_pore_balance(
                formation
            )
        )

        # Actual calculation: 10,000,000 / (9.81 * 1000) = 1019.368 kg/m³
        # Convert: 1019.368 / 119.826 = 8.507 ppg
        self.assertAlmostEqual(required_density, 1019.368, places=3)
        self.assertGreaterEqual(required_density, 1000.0)
        self.assertAlmostEqual(required_ppg, 8.507, places=3)

    def test_evaluate_safety_window_safe(self):
        """Test evaluation of safe operational window."""
        result = HydrostaticPressureCalculator.evaluate_safety_window(
            mud_density=1080.0,
            pore_pressure=10500000.0,
            fracture_gradient=12000.0,
            depth_m=1000.0
        )

        self.assertEqual(result["safety_status"], "SAFE - Within operational window")
        self.assertAlmostEqual(
            result["pore_pressure_limit"], 1070.336, places=3
        )
        self.assertAlmostEqual(
            result["fracture_pressure_limit"], 12000.0, places=3
        )

    def test_evaluate_safety_window_kick_risk(self):
        """Test evaluation when mud weight is below pore pressure."""
        result = HydrostaticPressureCalculator.evaluate_safety_window(
            mud_density=950.0,
            pore_pressure=10500000.0,
            fracture_gradient=12000.0,
            depth_m=1000.0
        )

        self.assertIn("INSUFFICIENT", result["safety_status"])


class TestBinghamPlasticRheology(unittest.TestCase):
    """Test Bingham-Plastic fluid model calculations."""

    def test_calculate_shear_stress(self):
        """Test shear stress calculation using Bingham-Plastic model."""
        shear_stress = BinghamPlasticRheology.calculate_shear_stress(
            yield_point_pa=5000.0,
            plastic_viscosity_pa_s=0.5,
            shear_rate_s1=100.0
        )

        expected = 5000.0 + (0.5 * 100.0)
        self.assertAlmostEqual(shear_stress, expected, places=3)

    def test_unit_conversion(self):
        """Test mud report unit conversion to SI units."""
        mud_report = MudReport(
            api_number="12345",
            temperature_c=75.0,
            density_kg_m3=1250.0,
            plastic_viscosity_cP=45.0,
            yield_point_lbf_100ft2=25.0,
            mud_weight_ppg=11.5,
        )

        si_mud_report, conversion_factors = (
            BinghamPlasticRheology.convert_units(mud_report)
        )

        self.assertEqual(mud_report.temperature_c, si_mud_report.temperature_c)
        self.assertEqual(mud_report.density_kg_m3, si_mud_report.density_kg_m3)
        self.assertEqual(mud_report.plastic_viscosity_cP, si_mud_report.plastic_viscosity_cP)


class TestAnnularHydraulics(unittest.TestCase):
    """Test annular hydraulics calculations."""

    def test_calculate_annular_volume(self):
        """Test annular volume calculation."""
        geometry = AnnularGeometry(
            casing_diameter_in=9.625,
            hole_diameter_in=10.0,
            cemented_interval_length_m=100.0,
            wash_out_factor=0.15,
        )

        volume = AnnularHydraulics.calculate_annular_volume(geometry)

        expected = 0.428841  # Pre-calculated value
        self.assertAlmostEqual(volume, expected, places=3)

    def test_calculate_ECD(self):
        """Test Equivalent Circulating Density calculation."""
        ecd = AnnularHydraulics.calculate_ECD(
            mud_density_kg_m3=1200.0,
            annular_pressure_drop_pa=500000.0,
            depth_m=1500.0
        )

        expected = 1233.979
        self.assertAlmostEqual(ecd, expected, places=3)

    def test_calculate_fluid_velocity(self):
        """Test fluid velocity calculation in annulus."""
        velocity = AnnularHydraulics.calculate_fluid_velocity(
            flow_rate_m3_s=0.1,
            hole_diameter_m=0.3048,
            casing_diameter_m=0.245
        )

        self.assertGreater(velocity, 0.0)
        self.assertLess(velocity, 10.0)


class TestSlurryDesigner(unittest.TestCase):
    """Test cement slurry design calculations."""

    def test_calculate_slurry_volumes(self):
        """Test total slurry volume calculation."""
        geometry = AnnularGeometry(
            casing_diameter_in=9.625,
            hole_diameter_in=10.0,
            cemented_interval_length_m=100.0,
        )

        volumes = SlurryDesigner.calculate_slurry_volumes(
            geometry=geometry,
            mud_volume_m3=0.2,  # Use realistic value (annular volume is ~0.429 m³)
            spacer_volume_m3=0.1,
            displacement_volume_m3=0.05,
        )

        self.assertIn("annular_volume_m3", volumes)
        self.assertIn("cement_volume_m3", volumes)
        self.assertIn("spacer_volume_m3", volumes)
        self.assertIn("displacement_volume_m3", volumes)
        self.assertIn("total_volume_m3", volumes)
        
        # Verify calculations (approximate)
        self.assertAlmostEqual(volumes["annular_volume_m3"], 0.428841, places=3)
        # Annular volume - spacer - displacement = 0.428841 - 0.1 - 0.05 = 0.278841
        self.assertAlmostEqual(volumes["cement_volume_m3"], 0.278841, places=3)

    def test_calculate_plug_bumping_pressure(self):
        """Test plug bumping pressure calculation."""
        result = SlurryDesigner.calculate_plug_bumping_pressure(
            casing_diameter_m=0.245,
            displacement_pressure_pa=2000000.0,
            cement_set_time_min=30.0,
        )

        self.assertIn("bumping_pressure_pa", result)
        self.assertIn("max_safe_pressure_pa", result)
        self.assertIn("safety_margin_percentage", result)
        self.assertIn("casing_area_m2", result)

    def test_volume_validation_error(self):
        """Test error handling for invalid volume inputs."""
        geometry = AnnularGeometry(
            casing_diameter_in=9.625,
            hole_diameter_in=10.0,
            cemented_interval_length_m=100.0,
        )

        with self.assertRaises(ValueError):
            SlurryDesigner.calculate_slurry_volumes(
                geometry=geometry,
                mud_volume_m3=1.0,  # Exceeds annular volume (~0.429 m³)
                spacer_volume_m3=0.1,
                displacement_volume_m3=0.05,
            )