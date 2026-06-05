import json
from dataclasses import dataclass


@dataclass
class ToolResponse:
    output: str


@dataclass
class ClimateData:
    allsky_irradiance: dict[str, float]
    clearsky_irradiance: dict[str, float]
    temperature_2m: dict[str, float]

    @classmethod
    def from_response(cls, response: ToolResponse) -> "ClimateData":
        params = json.loads(response.output)["properties"]["parameter"]
        return cls(
            allsky_irradiance=params["ALLSKY_SFC_SW_DWN"],
            clearsky_irradiance=params["CLRSKY_SFC_SW_DWN"],
            temperature_2m=params["T2M"],
        )


@dataclass
class TerrainData:
    latitude: float
    longitude: float
    elevation_m: float
    slope_degrees: float
    aspect: str | None
    dataset: str

    @classmethod
    def from_response(cls, response: ToolResponse) -> "TerrainData":
        data = json.loads(response.output)
        return cls(
            latitude=data["latitude"],
            longitude=data["longitude"],
            elevation_m=data["elevation_m"],
            slope_degrees=data["slope_degrees"],
            aspect=data.get("aspect"),
            dataset=data["dataset"],
        )