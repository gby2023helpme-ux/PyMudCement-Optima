"""
Cementing Engineering Module for PyMudCement-Optima.

Provides slurry design, additive database, cementing procedure generation,
and P&A plug design capabilities.
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum

GRAVITY = 9.81


class AdditiveCategory(Enum):
    RETARDER = "Retarder"
    ACCELERATOR = "Accelerator"
    WEIGHTING = "Weighting Agent"
    LIGHTWEIGHT = "Lightweight Agent"
    FLUID_LOSS = "Fluid Loss Control"
    GAS_MIGRATION = "Gas Migration Control"
    DISPERSANT = "Dispersant"
    ANTIMICROBIAL = "Antimicrobial"
    DEFOMER = "Defoamer"


@dataclass
class CementAdditive:
    name: str
    category: AdditiveCategory
    dosage_range_kg_m3: Tuple[float, float]
    specific_gravity: float
    max_temperature_c: int
    effect_on_density: float
    cost_per_kg: float = 0.0

    def calculate_density_contribution(self, dosage_kg_m3: float) -> float:
        return dosage_kg_m3 * (self.specific_gravity - 1.0)

    def is_suitable_for_temperature(self, temp_c: float) -> bool:
        return temp_c <= self.max_temperature_c


@dataclass
class SlurryDesignRequest:
    hole_diameter_in: float
    casing_od_in: float
    cemented_length_m: float
    bottomhole_temp_c: float
    target_density_kg_m3: float
    water_ratio: float = 0.44
    excess_factor: float = 0.15
    pump_time_min: float = 30.0
    washout_factor: float = 0.0


@dataclass
class SlurryDesignResult:
    slurry_volume_m3: float
    cement_volume_m3: float
    water_volume_m3: float
    additive_plan: List[Dict]
    total_density_kg_m3: float
    estimated_pump_time_min: float
    warnings: List[str]
    thickening_time_min: float
    compressive_strength_mpa: float


@dataclass
class SpacerDesign:
    name: str
    volume_m3: float
    density_kg_m3: float
    viscosity_cP: float
    pump_time_min: float


@dataclass
class CementingProcedure:
    stage: str
    volume_m3: float
    density_kg_m3: float
    pump_rate_lpm: float
    duration_min: float
    cumulative_volume_m3: float
    notes: str


ADDITIVE_DATABASE = [
    CementAdditive(
        name="CFR-3 (Fluid Loss Reducer)",
        category=AdditiveCategory.FLUID_LOSS,
        dosage_range_kg_m3=(5.0, 15.0),
        specific_gravity=1.2,
        max_temperature_c=175,
        effect_on_density=0.5,
        cost_per_kg=8.50,
    ),
    CementAdditive(
        name="HR-12 (Retarder)",
        category=AdditiveCategory.RETARDER,
        dosage_range_kg_m3=(1.0, 8.0),
        specific_gravity=1.5,
        max_temperature_c=200,
        effect_on_density=0.3,
        cost_per_kg=12.00,
    ),
    CementAdditive(
        name="BA-10 (Acceleration Agent)",
        category=AdditiveCategory.ACCELERATOR,
        dosage_range_kg_m3=(5.0, 25.0),
        specific_gravity=2.1,
        max_temperature_c=120,
        effect_on_density=1.2,
        cost_per_kg=6.00,
    ),
    CementAdditive(
        name="Micromax (Weighting Agent)",
        category=AdditiveCategory.WEIGHTING,
        dosage_range_kg_m3=(50.0, 400.0),
        specific_gravity=4.5,
        max_temperature_c=300,
        effect_on_density=3.5,
        cost_per_kg=3.20,
    ),
    CementAdditive(
        name="Gilsonite (Gas Migration)",
        category=AdditiveCategory.GAS_MIGRATION,
        dosage_range_kg_m3=(5.0, 30.0),
        specific_gravity=1.05,
        max_temperature_c=250,
        effect_on_density=0.1,
        cost_per_kg=2.50,
    ),
    CementAdditive(
        name="CFR-2 (Dispersant)",
        category=AdditiveCategory.DISPERSANT,
        dosage_range_kg_m3=(2.0, 10.0),
        specific_gravity=1.1,
        max_temperature_c=200,
        effect_on_density=0.2,
        cost_per_kg=9.00,
    ),
    CementAdditive(
        name="NF-1 (Antimicrobial)",
        category=AdditiveCategory.ANTIMICROBIAL,
        dosage_range_kg_m3=(0.5, 2.0),
        specific_gravity=1.0,
        max_temperature_c=150,
        effect_on_density=0.0,
        cost_per_kg=15.00,
    ),
    CementAdditive(
        name="Defoamer DF-1",
        category=AdditiveCategory.DEFOMER,
        dosage_range_kg_m3=(0.1, 1.0),
        specific_gravity=0.9,
        max_temperature_c=200,
        effect_on_density=-0.1,
        cost_per_kg=20.00,
    ),
    CementAdditive(
        name="Bentite (Lightweight)",
        category=AdditiveCategory.LIGHTWEIGHT,
        dosage_range_kg_m3=(20.0, 100.0),
        specific_gravity=2.6,
        max_temperature_c=175,
        effect_on_density=1.6,
        cost_per_kg=1.80,
    ),
]


class CementingEngine:
    """Main cementing engineering calculator."""

    @staticmethod
    def calculate_annular_volume(
        hole_diameter_in: float,
        casing_od_in: float,
        length_m: float,
        excess_factor: float = 0.15,
    ) -> float:
        hole_m = hole_diameter_in * 0.0254
        casing_m = casing_od_in * 0.0254
        base_volume = (math.pi / 4) * (hole_m**2 - casing_m**2) * length_m
        return base_volume * (1 + excess_factor)

    @staticmethod
    def calculate_cement_volume(slurry_volume_m3: float, water_ratio: float = 0.44) -> float:
        return slurry_volume_m3 / (1 + water_ratio)

    @staticmethod
    def calculate_water_volume(slurry_volume_m3: float, water_ratio: float = 0.44) -> float:
        cement_vol = CementingEngine.calculate_cement_volume(slurry_volume_m3, water_ratio)
        return cement_vol * water_ratio

    @staticmethod
    def design_slurry(request: SlurryDesignRequest) -> SlurryDesignResult:
        warnings = []

        slurry_vol = CementingEngine.calculate_annular_volume(
            request.hole_diameter_in,
            request.casing_od_in,
            request.cemented_length_m,
            request.excess_factor,
        )

        cement_vol = CementingEngine.calculate_cement_volume(slurry_vol, request.water_ratio)
        water_vol = CementingEngine.calculate_water_volume(slurry_vol, request.water_ratio)

        suitable_additives = [
            a for a in ADDITIVE_DATABASE if a.is_suitable_for_temperature(request.bottomhole_temp_c)
        ]

        additive_plan = []
        total_density_contribution = 0.0

        if request.target_density_kg_m3 > 1500:
            weighting = [a for a in suitable_additives if a.category == AdditiveCategory.WEIGHTING]
            if weighting:
                w = weighting[0]
                dosage = min(
                    (request.target_density_kg_m3 - 1440) / w.specific_gravity,
                    w.dosage_range_kg_m3[1],
                )
                dosage = max(dosage, w.dosage_range_kg_m3[0])
                additive_plan.append({
                    "name": w.name,
                    "dosage_kg_m3": round(dosage, 2),
                    "volume_m3": round(dosage * cement_vol / (w.specific_gravity * 1000), 4),
                    "category": w.category.value,
                })
                total_density_contribution += w.calculate_density_contribution(dosage)
        elif request.target_density_kg_m3 < 1400:
            lightweight = [a for a in suitable_additives if a.category == AdditiveCategory.LIGHTWEIGHT]
            if lightweight:
                lw = lightweight[0]
                dosage = min(
                    (1440 - request.target_density_kg_m3) / lw.specific_gravity,
                    lw.dosage_range_kg_m3[1],
                )
                dosage = max(dosage, lw.dosage_range_kg_m3[0])
                additive_plan.append({
                    "name": lw.name,
                    "dosage_kg_m3": round(dosage, 2),
                    "volume_m3": round(dosage * cement_vol / (lw.specific_gravity * 1000), 4),
                    "category": lw.category.value,
                })
                total_density_contribution += lw.calculate_density_contribution(dosage)

        fluid_loss = [a for a in suitable_additives if a.category == AdditiveCategory.FLUID_LOSS]
        if fluid_loss:
            fl = fluid_loss[0]
            dosage = (fl.dosage_range_kg_m3[0] + fl.dosage_range_kg_m3[1]) / 2
            additive_plan.append({
                "name": fl.name,
                "dosage_kg_m3": round(dosage, 2),
                "volume_m3": round(dosage * cement_vol / (fl.specific_gravity * 1000), 4),
                "category": fl.category.value,
            })
            total_density_contribution += fl.calculate_density_contribution(dosage)

        retarder_candidates = [
            a for a in suitable_additives if a.category == AdditiveCategory.RETARDER
        ]
        if retarder_candidates:
            r = retarder_candidates[0]
            if request.bottomhole_temp_c > 100:
                dosage_range = r.dosage_range_kg_m3
                temp_factor = min((request.bottomhole_temp_c - 100) / 100, 1.0)
                dosage = dosage_range[0] + temp_factor * (dosage_range[1] - dosage_range[0])
                additive_plan.append({
                    "name": r.name,
                    "dosage_kg_m3": round(dosage, 2),
                    "volume_m3": round(dosage * cement_vol / (r.specific_gravity * 1000), 4),
                    "category": r.category.value,
                })
                total_density_contribution += r.calculate_density_contribution(dosage)

        dispersant = [a for a in suitable_additives if a.category == AdditiveCategory.DISPERSANT]
        if dispersant:
            d = dispersant[0]
            dosage = (d.dosage_range_kg_m3[0] + d.dosage_range_kg_m3[1]) / 2
            additive_plan.append({
                "name": d.name,
                "dosage_kg_m3": round(dosage, 2),
                "volume_m3": round(dosage * cement_vol / (d.specific_gravity * 1000), 4),
                "category": d.category.value,
            })

        base_slurry_density = 1440.0
        total_density = base_slurry_density + total_density_contribution

        if abs(total_density - request.target_density_kg_m3) > 50:
            warnings.append(
                f"Target density {request.target_density_kg_m3} kg/m³ differs from "
                f"achieved {total_density:.0f} kg/m³. Adjust weighting/lightweight dosage."
            )

        if request.bottomhole_temp_c > 150:
            warnings.append("High temperature well. Verify retarder concentration with lab tests.")

        if request.pump_time_min < 30:
            warnings.append("Short pump time requested. Ensure adequate retarder for safety margin.")

        thickening_time = request.pump_time_min * 1.5
        compressive_strength = max(3.5, 20.0 - (request.target_density_kg_m3 - 1440) * 0.01)

        return SlurryDesignResult(
            slurry_volume_m3=round(slurry_vol, 4),
            cement_volume_m3=round(cement_vol, 4),
            water_volume_m3=round(water_vol, 4),
            additive_plan=additive_plan,
            total_density_kg_m3=round(total_density, 1),
            estimated_pump_time_min=round(request.pump_time_min * 1.2, 1),
            warnings=warnings,
            thickening_time_min=round(thickening_time, 1),
            compressive_strength_mpa=round(compressive_strength, 2),
        )

    @staticmethod
    def generate_procedure(
        design: SlurryDesignResult,
        pump_rate_lpm: float = 200.0,
        spacer_volume_m3: float = 0.0,
        flush_volume_m3: float = 0.0,
    ) -> List[CementingProcedure]:
        procedure = []
        cumulative = 0.0

        if flush_volume_m3 > 0:
            flush_duration = (flush_volume_m3 * 1000) / pump_rate_lpm
            cumulative += flush_volume_m3
            procedure.append(CementingProcedure(
                stage="1. Flush Fluid",
                volume_m3=round(flush_volume_m3, 4),
                density_kg_m3=1000.0,
                pump_rate_lpm=pump_rate_lpm,
                duration_min=round(flush_duration, 1),
                cumulative_volume_m3=round(cumulative, 4),
                notes="Pump ahead flush to remove mud from annulus",
            ))

        if spacer_volume_m3 > 0:
            spacer_duration = (spacer_volume_m3 * 1000) / pump_rate_lpm
            cumulative += spacer_volume_m3
            procedure.append(CementingProcedure(
                stage="2. Spacer",
                volume_m3=round(spacer_volume_m3, 4),
                density_kg_m3=1300.0,
                pump_rate_lpm=pump_rate_lpm,
                duration_min=round(spacer_duration, 1),
                cumulative_volume_m3=round(cumulative, 4),
                notes="Pump weighted spacer to separate mud and cement",
            ))

        cement_duration = (design.slurry_volume_m3 * 1000) / pump_rate_lpm
        cumulative += design.slurry_volume_m3
        procedure.append(CementingProcedure(
            stage=f"{len(procedure) + 1}. Cement Slurry",
            volume_m3=design.slurry_volume_m3,
            density_kg_m3=design.total_density_kg_m3,
            pump_rate_lpm=pump_rate_lpm,
            duration_min=round(cement_duration, 1),
            cumulative_volume_m3=round(cumulative, 4),
            notes="Pump cement slurry at constant rate. Monitor pump pressure.",
        ))

        displacement_vol = design.slurry_volume_m3 * 1.05
        disp_duration = (displacement_vol * 1000) / pump_rate_lpm
        cumulative += displacement_vol
        procedure.append(CementingProcedure(
            stage=f"{len(procedure) + 1}. Displacement",
            volume_m3=round(displacement_vol, 4),
            density_kg_m3=1000.0,
            pump_rate_lpm=pump_rate_lpm,
            duration_min=round(disp_duration, 1),
            cumulative_volume_m3=round(cumulative, 4),
            notes="Displace with mud. Slow down near bump pressure. Monitor float collar.",
        ))

        return procedure

    @staticmethod
    def calculate_bumping_pressure(
        displacement_pressure_pa: float,
        casing_id_m: float,
        fluid_density_kg_m3: float = 1000.0,
        vertical_depth_m: float = 0.0,
    ) -> Dict[str, float]:
        casing_area = math.pi * (casing_id_m ** 2) / 4
        hydrostatic = fluid_density_kg_m3 * GRAVITY * vertical_depth_m if vertical_depth_m > 0 else 0
        bumping = displacement_pressure_pa + hydrostatic + (casing_area * 100000)
        max_safe = bumping * 0.85

        return {
            "bumping_pressure_pa": round(bumping, 0),
            "bumping_pressure_psi": round(bumping * 0.000145038, 1),
            "max_safe_pressure_pa": round(max_safe, 0),
            "max_safe_pressure_psi": round(max_safe * 0.000145038, 1),
            "casing_area_m2": round(casing_area, 6),
            "safety_margin_pct": 15.0,
        }


class PAPLugDesign:
    """Plug and Abandonment / Suspension plug design."""

    @staticmethod
    def design_suspension_plug(
        hole_diameter_in: float,
        casing_od_in: float,
        plug_length_m: float,
        cement_density_kg_m3: float = 1900.0,
        displacement_volume_m3: float = 0.0,
    ) -> Dict:
        hole_m = hole_diameter_in * 0.0254
        casing_m = casing_od_in * 0.0254
        annular_area = (math.pi / 4) * (hole_m ** 2 - casing_m ** 2)
        cement_volume = annular_area * plug_length_m

        if displacement_volume_m3 == 0:
            displacement_volume_m3 = cement_volume * 1.05

        hydrostatic = cement_density_kg_m3 * GRAVITY * plug_length_m

        return {
            "plug_type": "Suspension Plug",
            "plug_length_m": plug_length_m,
            "cement_volume_m3": round(cement_volume, 4),
            "cement_volume_sacks": round(cement_volume / 0.0326, 1),
            "displacement_volume_m3": round(displacement_volume_m3, 4),
            "cement_density_kg_m3": cement_density_kg_m3,
            "annular_area_m2": round(annular_area, 6),
            "hydrostatic_pressure_pa": round(hydrostatic, 0),
            "hydrostatic_pressure_psi": round(hydrostatic * 0.000145038, 1),
        }

    @staticmethod
    def design_sidetrack_plug(
        hole_diameter_in: float,
        casing_od_in: float,
        plug_length_m: float,
        cement_density_kg_m3: float = 1900.0,
        shoe_depth_m: float = 0.0,
    ) -> Dict:
        hole_m = hole_diameter_in * 0.0254
        casing_m = casing_od_in * 0.0254
        annular_area = (math.pi / 4) * (hole_m ** 2 - casing_m ** 2)
        bore_area = (math.pi / 4) * (hole_m ** 2)
        cement_volume_annular = annular_area * plug_length_m
        cement_volume_bore = bore_area * plug_length_m * 0.3
        total_cement = cement_volume_annular + cement_volume_bore
        displacement = total_cement * 1.05

        return {
            "plug_type": "Sidetrack Plug",
            "plug_length_m": plug_length_m,
            "cement_volume_m3": round(total_cement, 4),
            "cement_volume_sacks": round(total_cement / 0.0326, 1),
            "annular_cement_m3": round(cement_volume_annular, 4),
            "bore_cement_m3": round(cement_volume_bore, 4),
            "displacement_volume_m3": round(displacement, 4),
            "cement_density_kg_m3": cement_density_kg_m3,
            "shoe_depth_m": shoe_depth_m,
        }

    @staticmethod
    def design_abandonment_plug(
        hole_diameter_in: float,
        casing_od_in: float,
        plug_length_m: float,
        top_depth_m: float,
        bottom_depth_m: float,
        cement_density_kg_m3: float = 1900.0,
    ) -> Dict:
        hole_m = hole_diameter_in * 0.0254
        casing_m = casing_od_in * 0.0254
        annular_area = (math.pi / 4) * (hole_m ** 2 - casing_m ** 2)
        bore_area = (math.pi / 4) * (hole_m ** 2)

        annular_cement = annular_area * plug_length_m
        bore_cement = bore_area * plug_length_m
        total_cement = annular_cement + bore_cement

        displacement = total_cement * 1.05

        hydrostatic_top = cement_density_kg_m3 * GRAVITY * top_depth_m
        hydrostatic_bottom = cement_density_kg_m3 * GRAVITY * bottom_depth_m

        return {
            "plug_type": "Abandonment Plug",
            "top_depth_m": top_depth_m,
            "bottom_depth_m": bottom_depth_m,
            "plug_length_m": plug_length_m,
            "cement_volume_m3": round(total_cement, 4),
            "cement_volume_sacks": round(total_cement / 0.0326, 1),
            "annular_cement_m3": round(annular_cement, 4),
            "bore_cement_m3": round(bore_cement, 4),
            "displacement_volume_m3": round(displacement, 4),
            "cement_density_kg_m3": cement_density_kg_m3,
            "hydrostatic_top_psi": round(hydrostatic_top * 0.000145038, 1),
            "hydrostatic_bottom_psi": round(hydrostatic_bottom * 0.000145038, 1),
        }   