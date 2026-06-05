from typing import Literal
from dataclasses import dataclass
from models.tools import ClimateData, TerrainData

@dataclass
class EvalLocation:
    name: str
    lat: float
    lon: float
    terrain_data: TerrainData
    climate_data: ClimateData
    
class EvalTestCase:
    location: EvalLocation
    label: Literal["GOOD", "MARGINAL", "BAD"]