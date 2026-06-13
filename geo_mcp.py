from fastmcp import FastMCP
import tools

mcp = FastMCP("Geospatial Tools")

@mcp.tool
def get_climate_data(lat: float, lon: float) -> str:
    """Retrieve climate data for a given location.
        The input should be two floats: latitude, longitude. For example: 51.5074, -0.1278 for London.
        The output will be a JSON string containing monthly climatology data for the following parameters:
        - All Sky Surface Shortwave Downward Irradiance (Solar energy hitting surface accounting for clouds)
        - Clear Sky Surface Shortwave Downward Irradiance (Solar energy hitting surface without clouds)
        - 2 Meter Air Temperature (Air temperature at 2 meters above the surface)
    """
    return tools.get_climate_data(lat=lat, lon=lon).output

@mcp.tool
def get_terrain_data(lat: float, lon: float) -> str:
    """Retrieve terrain elevation data for a given coordinate.
        The input should be two floats: latitude, longitude. For example: 51.5074, -0.1278 for London.
        Returns elevation in metres above sea level. Uses SRTM GL1 (30m) for latitudes within ±60°, COP30 beyond.
    """
    return tools.get_terrain_data(lat=lat, lon=lon).output


if __name__ == "__main__":
    import sys
    transport = "streamable-http" if "--http" in sys.argv else "stdio"
    mcp.run(transport=transport)