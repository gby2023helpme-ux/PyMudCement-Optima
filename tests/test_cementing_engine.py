import unittest
import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.cementing_engine import (
    CementingEngine,
    PAPLugDesign,
    ADDITIVE_DATABASE,
    SlurryDesignRequest,
    CementAdditive,
    AdditiveCategory,
)


class TestCementingEngine(unittest.TestCase):
    """Tests for the core cementing calculations."""

    def test_annular_volume_basic(self):
        vol = CementingEngine.calculate_annular_volume(
            hole_diameter_in=12.25,
            casing_od_in=9.625,
            length_m=200,
            excess_factor=0.15,
        )
        self.assertGreater(vol, 0)
        self.assertIsInstance(vol, float)

    def test_annular_volume_no_excess(self):
        vol = CementingEngine.calculate_annular_volume(
            hole_diameter_in=12.25,
            casing_od_in=9.625,
            length_m=100,
            excess_factor=0.0,
        )
        hole_m = 12.25 * 0.0254
        casing_m = 9.625 * 0.0254
        expected = (math.pi / 4) * (hole_m ** 2 - casing_m ** 2) * 100
        self.assertAlmostEqual(vol, expected, places=6)

    def test_annular_volume_with_excess(self):
        vol_no_excess = CementingEngine.calculate_annular_volume(
            12.25, 9.625, 100, excess_factor=0.0
        )
        vol_15pct = CementingEngine.calculate_annular_volume(
            12.25, 9.625, 100, excess_factor=0.15
        )
        self.assertAlmostEqual(vol_15pct, vol_no_excess * 1.15, places=6)

    def test_cement_volume(self):
        cement = CementingEngine.calculate_cement_volume(10.0, water_ratio=0.44)
        expected = 10.0 / 1.44
        self.assertAlmostEqual(cement, expected, places=4)

    def test_water_volume(self):
        water = CementingEngine.calculate_water_volume(10.0, water_ratio=0.44)
        cement = CementingEngine.calculate_cement_volume(10.0, 0.44)
        self.assertAlmostEqual(water, cement * 0.44, places=4)

    def test_design_slurry_returns_valid_result(self):
        req = SlurryDesignRequest(
            hole_diameter_in=12.25,
            casing_od_in=9.625,
            cemented_length_m=200,
            bottomhole_temp_c=120,
            target_density_kg_m3=1900,
        )
        result = CementingEngine.design_slurry(req)
        self.assertGreater(result.slurry_volume_m3, 0)
        self.assertGreater(result.cement_volume_m3, 0)
        self.assertGreater(result.water_volume_m3, 0)
        self.assertAlmostEqual(result.water_volume_m3, result.cement_volume_m3 * 0.44, places=4)

    def test_design_slurry_density_check(self):
        req = SlurryDesignRequest(
            hole_diameter_in=12.25,
            casing_od_in=9.625,
            cemented_length_m=200,
            bottomhole_temp_c=80,
            target_density_kg_m3=1440,
        )
        result = CementingEngine.design_slurry(req)
        self.assertAlmostEqual(result.total_density_kg_m3, 1440.0, delta=100)

    def test_design_slurry_high_temp_warning(self):
        req = SlurryDesignRequest(
            hole_diameter_in=12.25,
            casing_od_in=9.625,
            cemented_length_m=200,
            bottomhole_temp_c=200,
            target_density_kg_m3=1900,
        )
        result = CementingEngine.design_slurry(req)
        temp_warnings = [w for w in result.warnings if "temperature" in w.lower()]
        self.assertTrue(len(temp_warnings) > 0)

    def test_generate_procedure_stages(self):
        req = SlurryDesignRequest(
            hole_diameter_in=12.25,
            casing_od_in=9.625,
            cemented_length_m=200,
            bottomhole_temp_c=120,
            target_density_kg_m3=1900,
        )
        design = CementingEngine.design_slurry(req)
        proc = CementingEngine.generate_procedure(design, pump_rate_lpm=200, spacer_volume_m3=2.0, flush_volume_m3=1.5)
        self.assertEqual(len(proc), 4)
        self.assertIn("Flush", proc[0].stage)
        self.assertIn("Spacer", proc[1].stage)
        self.assertIn("Cement", proc[2].stage)
        self.assertIn("Displacement", proc[3].stage)

    def test_generate_procedure_no_spacer(self):
        req = SlurryDesignRequest(
            hole_diameter_in=12.25,
            casing_od_in=9.625,
            cemented_length_m=200,
            bottomhole_temp_c=120,
            target_density_kg_m3=1900,
        )
        design = CementingEngine.design_slurry(req)
        proc = CementingEngine.generate_procedure(design, pump_rate_lpm=200, spacer_volume_m3=0, flush_volume_m3=0)
        self.assertEqual(len(proc), 2)

    def test_generate_procedure_cumulative_volume(self):
        req = SlurryDesignRequest(
            hole_diameter_in=12.25,
            casing_od_in=9.625,
            cemented_length_m=200,
            bottomhole_temp_c=120,
            target_density_kg_m3=1900,
        )
        design = CementingEngine.design_slurry(req)
        proc = CementingEngine.generate_procedure(design, pump_rate_lpm=200, spacer_volume_m3=2.0, flush_volume_m3=1.5)
        cumulative_sum = sum(p.volume_m3 for p in proc)
        self.assertAlmostEqual(cumulative_sum, proc[-1].cumulative_volume_m3, places=4)

    def test_bumping_pressure(self):
        result = CementingEngine.calculate_bumping_pressure(
            displacement_pressure_pa=2000000,
            casing_id_m=0.22,
            fluid_density_kg_m3=1000,
            vertical_depth_m=1500,
        )
        self.assertIn("bumping_pressure_pa", result)
        self.assertIn("bumping_pressure_psi", result)
        self.assertIn("max_safe_pressure_pa", result)
        self.assertIn("safety_margin_pct", result)
        self.assertEqual(result["safety_margin_pct"], 15.0)
        self.assertGreater(result["bumping_pressure_pa"], 2000000)

    def test_bumping_pressure_conversion(self):
        result = CementingEngine.calculate_bumping_pressure(
            displacement_pressure_pa=1000000,
            casing_id_m=0.22,
        )
        psi = result["bumping_pressure_pa"] * 0.000145038
        self.assertAlmostEqual(result["bumping_pressure_psi"], psi, places=1)


class TestPAPLugDesign(unittest.TestCase):
    """Tests for P&A plug design sub-module."""

    def test_suspension_plug_volume(self):
        result = PAPLugDesign.design_suspension_plug(
            hole_diameter_in=12.25,
            casing_od_in=9.625,
            plug_length_m=50,
        )
        self.assertGreater(result["cement_volume_m3"], 0)
        self.assertGreater(result["displacement_volume_m3"], result["cement_volume_m3"])
        self.assertEqual(result["plug_type"], "Suspension Plug")

    def test_suspension_plug_sacks(self):
        result = PAPLugDesign.design_suspension_plug(
            hole_diameter_in=12.25,
            casing_od_in=9.625,
            plug_length_m=50,
        )
        expected_sacks = result["cement_volume_m3"] / 0.0326
        self.assertAlmostEqual(result["cement_volume_sacks"], round(expected_sacks, 1), places=1)

    def test_sidetrack_plug(self):
        result = PAPLugDesign.design_sidetrack_plug(
            hole_diameter_in=12.25,
            casing_od_in=9.625,
            plug_length_m=30,
            shoe_depth_m=1500,
        )
        self.assertEqual(result["plug_type"], "Sidetrack Plug")
        self.assertGreater(result["cement_volume_m3"], 0)
        self.assertGreater(result["annular_cement_m3"], 0)
        self.assertGreater(result["bore_cement_m3"], 0)
        self.assertEqual(result["shoe_depth_m"], 1500)

    def test_abandonment_plug(self):
        result = PAPLugDesign.design_abandonment_plug(
            hole_diameter_in=12.25,
            casing_od_in=9.625,
            plug_length_m=100,
            top_depth_m=1000,
            bottom_depth_m=1100,
        )
        self.assertEqual(result["plug_type"], "Abandonment Plug")
        self.assertGreater(result["cement_volume_m3"], 0)
        self.assertGreater(result["annular_cement_m3"], 0)
        self.assertGreater(result["bore_cement_m3"], 0)
        self.assertGreater(result["hydrostatic_bottom_psi"], result["hydrostatic_top_psi"])

    def test_plug_types_all_valid(self):
        for hole, casing, length in [(8.5, 5.5, 30), (12.25, 9.625, 50), (17.5, 13.375, 100)]:
            s = PAPLugDesign.design_suspension_plug(hole, casing, length)
            self.assertGreater(s["cement_volume_m3"], 0)
            sid = PAPLugDesign.design_sidetrack_plug(hole, casing, length)
            self.assertGreater(sid["cement_volume_m3"], 0)
            ab = PAPLugDesign.design_abandonment_plug(hole, casing, length, 1000, 1100)
            self.assertGreater(ab["cement_volume_m3"], 0)


class TestAdditiveDatabase(unittest.TestCase):
    """Tests for the cement additive database."""

    def test_database_not_empty(self):
        self.assertGreater(len(ADDITIVE_DATABASE), 0)

    def test_additive_has_required_fields(self):
        for add in ADDITIVE_DATABASE:
            self.assertIsInstance(add, CementAdditive)
            self.assertGreater(len(add.name), 0)
            self.assertIsInstance(add.category, AdditiveCategory)
            self.assertEqual(len(add.dosage_range_kg_m3), 2)
            self.assertGreater(add.specific_gravity, 0)
            self.assertGreater(add.max_temperature_c, 0)

    def test_temperature_suitability(self):
        high_temp_additives = [a for a in ADDITIVE_DATABASE if a.is_suitable_for_temperature(200)]
        low_temp_only = [a for a in ADDITIVE_DATABASE if not a.is_suitable_for_temperature(200)]
        self.assertGreater(len(high_temp_additives), 0)
        self.assertGreater(len(low_temp_only), 0)

    def test_density_contribution(self):
        for add in ADDITIVE_DATABASE:
            contrib = add.calculate_density_contribution(10.0)
            self.assertIsInstance(contrib, float)


if __name__ == "__main__":
    unittest.main()