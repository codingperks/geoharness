from tools import get_climate_data, get_terrain_data
from models.tools import ClimateData, TerrainData

LAT = 51.5074
LON = -0.1278


def test_get_climate_data():
    result = get_climate_data(LAT, LON)
    data = ClimateData.from_response(result)

    print(f"Annual all-sky irradiance: {data.allsky_irradiance['ANN']} kWh/m²/day")
    print(f"Annual clear-sky irradiance: {data.clearsky_irradiance['ANN']} kWh/m²/day")
    print(f"Annual temperature: {data.temperature_2m['ANN']}°C")

    assert data.allsky_irradiance["ANN"] > 0
    assert data.clearsky_irradiance["ANN"] > data.allsky_irradiance["ANN"]
    assert -50 < data.temperature_2m["ANN"] < 50


def test_get_terrain_data():
    result = get_terrain_data(LAT, LON)
    data = TerrainData.from_response(result)

    print(f"Elevation: {data.elevation_m}m")
    print(f"Slope: {data.slope_degrees}°")
    print(f"Aspect: {data.aspect}")

    assert data.elevation_m > -500
    assert 0 <= data.slope_degrees < 90
    