import io
import json
import os
import zipfile
import httpx
from bs4 import BeautifulSoup
from ddgs import DDGS
from dotenv import load_dotenv
from models.tools import ToolResponse

load_dotenv()


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


def get_terrain_data(lat: float, lon: float) -> ToolResponse:
    """Retrieve terrain elevation data for a given coordinate.
    The input should be two floats: latitude, longitude. For example: 51.5074, -0.1278 for London.
    Returns elevation in metres above sea level from the SRTM GL1 30m dataset.
    """
    offset = 0.01
    params = {
        "demtype": "SRTMGL1",
        "south": lat - offset,
        "north": lat + offset,
        "west": lon - offset,
        "east": lon + offset,
        "outputFormat": "AAIGrid",
        "API_Key": os.getenv("OPENTOPOGRAPHY_KEY"),
    }
    response = httpx.get("https://portal.opentopography.org/API/globaldem", params=params, timeout=30.0)
    if response.status_code != 200:
        return ToolResponse(output=f"Failed to retrieve terrain data: {response.status_code} {response.text}")

    # Response may be a zip archive containing the .asc file
    if response.content[:2] == b"PK":
        with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
            asc_name = next(n for n in zf.namelist() if n.endswith(".asc"))
            text = zf.read(asc_name).decode()
    else:
        text = response.text

    lines = text.strip().splitlines()
    header = {}
    data_start = 0
    for i, line in enumerate(lines):
        parts = line.split()
        if parts[0].lower() in ("ncols", "nrows", "xllcorner", "yllcorner", "xllcenter", "yllcenter", "cellsize", "nodata_value"):
            header[parts[0].lower()] = parts[1]
            data_start = i + 1
        else:
            break

    ncols = int(header["ncols"])
    nrows = int(header["nrows"])
    nodata = float(header.get("nodata_value", -9999))
    rows = [[float(v) for v in line.split()] for line in lines[data_start:] if line.strip()]
    
    cx, cy = ncols // 2, nrows // 2
    elevation = rows[cy][cx]

    def _slope_and_aspect(rows, header, lat):
        import numpy as np
        grid = np.array(rows)
        cellsize_deg = float(header["cellsize"])
        cellsize_ns = cellsize_deg * 111320
        cellsize_ew = cellsize_deg * 111320 * np.cos(np.radians(lat))
        dy, dx = np.gradient(grid, cellsize_ns, cellsize_ew)
        slope = round(float(np.degrees(np.arctan(np.sqrt(dx[cy, cx]**2 + dy[cy, cx]**2)))), 1)
        if slope < 1.0:
            return slope, None
        aspect_deg = float(np.degrees(np.arctan2(dx[cy, cx], -dy[cy, cx]))) % 360
        aspect = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"][round(aspect_deg / 45) % 8]
        return slope, aspect

    slope, aspect = _slope_and_aspect(rows, header, lat)

    if elevation == nodata:
        return ToolResponse(output=f"No elevation data available for coordinates ({lat}, {lon})")

    result = {
        "latitude": lat,
        "longitude": lon,
        "elevation_m": elevation,
        "slope_degrees": slope,
        "dataset": "SRTM GL1 (30m resolution)",
    }
    if aspect is not None:
        result["aspect"] = aspect
    else:
        result["aspect_note"] = "terrain too flat for meaningful aspect calculation"
    return ToolResponse(output=json.dumps(result))    
    

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
    
    return ToolResponse(output=json.dumps(data))

# def get_satellite_data(location: str) -> ToolResponse:
#     """Retrieve satellite data for a given location."""
#     return ToolResponse(output=f"Satellite data for '{location}'")


REGISTRY: dict = {
    "web_search": (web_search, web_search.__doc__),
    "web_fetch": (web_fetch, web_fetch.__doc__),
    "get_terrain_data": (get_terrain_data, get_terrain_data.__doc__),
    "get_climate_data": (get_climate_data, get_climate_data.__doc__),
}