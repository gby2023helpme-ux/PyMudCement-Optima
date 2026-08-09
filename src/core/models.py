"""
Enhanced models and utilities for PyMudCement-Optima.

This module extends the basic data models with additional cement-specific
configurations and utility functions for the drilling engineering suite.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union
from enum import Enum, auto
import math

from .constants import BASE_SLURRY_DENSITY_KC_M3, CEMENT_BASE_DENSITIES, M_PER_FT, M_PER_IN


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
        return self.casing_diameter_in * M_PER_IN

    @property
    def hole_diameter_m(self) -> float:
        return self.hole_diameter_in * M_PER_IN


class RheologyModel(Enum):
    """Supported rheological (non-Newtonian) fluid models."""

    NEWTONIAN = "Newtonian"
    BINGHAM = "Bingham-Plastic"
    POWER_LAW = "Power Law"
    HERSCHEL_BULKLEY = "Herschel-Bulkley"


@dataclass
class RheologyProfile:
    """Rheological properties of the circulating fluid.

    Only the fields relevant to the chosen ``model`` are used:
    Newtonian -> ``dynamic_viscosity_pa_s``; Bingham -> plastic viscosity +
    yield point; Power Law -> consistency index + flow behaviour index;
    Herschel-Bulkley -> yield point + consistency index + behaviour index.
    """

    model: RheologyModel = RheologyModel.BINGHAM
    plastic_viscosity_pa_s: float = 0.0
    yield_point_pa: float = 0.0
    consistency_index_pa_sn: float = 0.0
    flow_behavior_index: float = 1.0
    dynamic_viscosity_pa_s: float = 0.0


@dataclass
class CirculatingGeometry:
    """Pipe/annular geometry of a complete circulating system.

    Diameters and lengths are SI (m). ``drill_pipe_annulus`` uses the
    open-hole diameter as its outer boundary; the drill-collar annulus
    spans the drill-collar length only.
    """

    surface_line_length_m: float
    surface_line_id_m: float
    drill_pipe_length_m: float
    drill_pipe_id_m: float
    drill_pipe_od_m: float
    drill_collar_length_m: float
    drill_collar_id_m: float
    drill_collar_od_m: float
    bit_nozzle_area_m2: float
    open_hole_diameter_m: float
    tvd_m: float

    @property
    def drill_pipe_annulus_length_m(self) -> float:
        return self.drill_pipe_length_m

    @property
    def drill_collar_annulus_length_m(self) -> float:
        return self.drill_collar_length_m


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
        return self.inner_diameter_in * M_PER_IN

    @property
    def outer_diameter_m(self) -> float:
        return self.outer_diameter_in * M_PER_IN

    @property
    def length_m(self) -> float:
        return self.length_ft * M_PER_FT


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
        base_density = CEMENT_BASE_DENSITIES.get(
            self.base_cement.name, BASE_SLURRY_DENSITY_KC_M3
        )
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
        return math.pi * self.diameter_m ** 2 / 4.0

    @property
    def displacement_ratio(self) -> float:
        if self.cement_volume_m3 == 0:
            return 0.0
        return self.displacement_volume_m3 / self.cement_volume_m3