import json
from tools import get_climate_data


def test_get_weather_data():
    # live api call
    # London
    lat = 51.5074
    lon = -0.1278

    result = get_climate_data(lat, lon)
    data = json.loads(result.output)

    properties = data.get("properties", {})
    parameters = properties.get("parameter", {})

    for param, monthly in parameters.items():
        values = list(monthly.values())
        print(f"{param}: {values}")