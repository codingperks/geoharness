from typing import Literal
from dataclasses import dataclass
from models.tools import ClimateData, TerrainData


@dataclass
class EvalLocation:
    name: str
    lat: float
    lon: float
    climate_data: ClimateData
    terrain_data: TerrainData


@dataclass
class EvalTestCase:
    location: EvalLocation
    expected_verdict: Literal["GOOD", "MARGINAL", "BAD"]
    
@dataclass
class EvalResult:
    test_case: EvalTestCase
    actual_verdict: str | None
    passed: bool
    output: dict
    prompt: str
    model: str
    iterations: int
    tool_error: bool
    trace_id: str | None
    steps: list[dict]
