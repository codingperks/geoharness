import json
import httpx
from bs4 import BeautifulSoup
from ddgs import DDGS
from models.tools import ToolResponse


def web_search(query: str) -> ToolResponse:
    """Perform a web search using DuckDuckGo and return the results."""
    with DDGS() as ddgs:
        results = ddgs.text(query)
        return ToolResponse(output="\n".join([result["body"] for result in results]))


def web_fetch(url: str) -> ToolResponse:
    """Fetch and return the text content of a webpage at a given URL. The URL must start with https:// or http://."""
    if not url.startswith(("https://", "http://")):
        return ToolResponse(output=f"Invalid URL '{url}': must start with https:// or http://")
    response = httpx.get(url, follow_redirects=True)
    soup = BeautifulSoup(response.text, "html.parser")
    return ToolResponse(output=soup.get_text(separator="\n", strip=True))


def get_terrain_data(location: str) -> ToolResponse:
    """Retrieve terrain data for a given location."""
    return ToolResponse(output=f"Terrain data for '{location}'")    

def get_climate_data(lat: float, lon: float) -> ToolResponse:
    """Retrieve climate data for a given location.
        The input should be two floats: latitude, longitude. For example: 51.5074, -0.1278 for London.
        The output will be a JSON string containing monthly climatology data for the following parameters:
        - All Sky Surface Shortwave Downward Irradiance (Solar energy hitting surface accounting for clouds)
        - Clear Sky Surface Shortwave Downward Irradiance (Solar energy hitting surface without clouds)
        - 2 Meter Air Temperature (Air temperature at 2 meters above the surface)
    """
    base_url = "https://power.larc.nasa.gov/api/temporal/climatology/point"
    parameters = ["ALLSKY_SFC_SW_DWN,CLRSKY_SFC_SW_DWN,T2M"]
    params = {
        "parameters": ",".join(parameters),
        "community": "RE",
        "longitude": lon,
        "latitude": lat,
        "format": "JSON"
    }
    response = httpx.get(base_url, params=params)
    if response.status_code != 200:
        return ToolResponse(output=f"Failed to retrieve weather data: {response.status_code} {response.text}")
    data = response.json()
    
    def _label_data(data):
        # Map parameter codes to human-readable labels
        mapping = {
            "ALLSKY_SFC_SW_DWN": "All Sky Surface Shortwave Downward Irradiance",
            "CLRSKY_SFC_SW_DWN": "Clear Sky Surface Shortwave Downward Irradiance",
            "T2M": "2 Meter Air Temperature"
        }
        return {mapping.get(k, k): v for k, v in data.items()}
    
    return ToolResponse(output=json.dumps(_label_data(data)))

# def get_satellite_data(location: str) -> ToolResponse:
#     """Retrieve satellite data for a given location."""
#     return ToolResponse(output=f"Satellite data for '{location}'")


REGISTRY: dict = {
    "web_search": (web_search, web_search.__doc__),
    "web_fetch": (web_fetch, web_fetch.__doc__),
    "get_terrain_data": (get_terrain_data, get_terrain_data.__doc__),
    "get_climate_data": (get_climate_data, get_climate_data.__doc__),
}