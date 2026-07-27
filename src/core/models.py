"""
Enhanced models and utilities for PyMudCement-Optima.

This module extends the basic data models with additional cement-specific
configurations and utility functions for the drilling engineering suite.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union
from enum import Enum, auto
import math


class FluidType(Enum):
    WATER = "Water"
    MIXED = "Mixed"
    BARITE = "Barite"
    POLYMER = "Polymer"
    CUSTOM = "Custom"


@dataclass
class Formation:
    name: str
    depth_m: float
    pore_pressure_pa: float
    fracture_gradient: float
    formation_type: str = ""


@dataclass
class MudReport:
    api_number: str = ""
    date: str = ""
    temperature_c: float = 0.0
    density_kg_m3: float = 0.0
    plastic_viscosity_cP: float = 0.0
    yield_point_lbf_100ft2: float = 0.0
    mud_weight_ppg: float = 0.0
    notes: str = ""


@dataclass
class AnnularGeometry:
    casing_diameter_in: float
    hole_diameter_in: float
    cemented_interval_length_m: float
    wash_out_factor: float = 0.15

    @property
    def casing_diameter_m(self) -> float:
        return self.casing_diameter_in * 0.0254

    @property
    def hole_diameter_m(self) -> float:
        return self.hole_diameter_in * 0.0254


@dataclass
class SlurryDesign:
    base_cement: Optional[str] = None
    additive_percentage: float = 0.0
    temperature_c: float = 20.0
    pump_time_min: float = 0.0

    @property
    def total_density_kg_m3(self) -> float:
        return None


class CementType(Enum):
    OIL_BASED = auto()
    WATER_BASED = auto()
    FOAM = auto()
    GEL = auto()
    LIGHTEN = auto()
    HEAVY_DENSITY = auto()


class AdditiveType(Enum):
    RETARDER = auto()
    ACCELERATOR = auto()
    WATER_REDUCER = auto()
    AIR_ENTRAINER = auto()
    SET_ACCELERATOR = auto()
    WEIGHTING_AGENT = auto()
    FILLER = auto()
    POZZOLAN = auto()


@dataclass
class CasingSpec:
    size_in: float
    weight_ppf: float
    material: str
    inner_diameter_in: float
    outer_diameter_in: float
    length_ft: float

    @property
    def inner_diameter_m(self) -> float:
        return self.inner_diameter_in * 0.0254

    @property
    def outer_diameter_m(self) -> float:
        return self.outer_diameter_in * 0.0254

    @property
    def length_m(self) -> float:
        return self.length_ft * 0.3048


@dataclass
class CementAdditive:
    name: str
    additive_type: AdditiveType
    dosage_ppm: float
    specific_gravity: float
    temperature_stability_c: int

    @property
    def weight_per_m3(self) -> float:
        return self.dosage_ppm * self.specific_gravity

    @property
    def volume_percentage(self) -> float:
        return (self.dosage_ppm / 1000000) * 100


@dataclass
class CementSlurry:
    base_cement: CementType
    additives: List[CementAdditive] = field(default_factory=list)
    water_content_ratio: float = 0.45
    temperature_c: float = 20.0
    pump_time_min: float = 0.0

    @property
    def total_additive_percentage(self) -> float:
        return sum(add.weight_per_m3 for add in self.additives) / 1000.0

    @property
    def estimated_density_kg_m3(self) -> float:
        base_densities = {
            CementType.WATER_BASED: 1440.0,
            CementType.OIL_BASED: 1380.0,
            CementType.FOAM: 1250.0,
            CementType.GEL: 1500.0,
            CementType.LIGHTEN: 1300.0,
            CementType.HEAVY_DENSITY: 1800.0,
        }
        base_density = base_densities.get(self.base_cement, 1440.0)
        additive_density = sum(add.weight_per_m3 for add in self.additives)
        return base_density + additive_density


@dataclass
class PlugDesign:
    length_m: float
    diameter_m: float
    cement_volume_m3: float
    displacement_volume_m3: float
    set_depth_m: float
    plug_type: str = "Disc"

    @property
    def annular_area_m2(self) -> float:
        return math.pi * self.diameter_m ** 2

    @property
    def displacement_ratio(self) -> float:
        if self.cement_volume_m3 == 0:
            return 0.0
        return self.displacement_volume_m3 / self.cement_volume_m3