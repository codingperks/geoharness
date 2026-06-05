"""
Scans a coarse grid around a coordinate to find one with a target aspect.

Usage:
    uv run eval/solar/utils/find_aspect.py <lat> <lon> <target_aspect>
    e.g. uv run eval/solar/utils/find_aspect.py 36.916198 -2.317827 S
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from tools import get_terrain_data
from models.tools import TerrainData

# 5x5 coarse grid — 25 calls max
STEPS = [-0.04, -0.02, 0.0, 0.02, 0.04]


def scan(lat: float, lon: float, target: str) -> None:
    print(f"Scanning around ({lat}, {lon}) for aspect: {target}\n")
    hits = []
    for dlat in STEPS:
        for dlon in STEPS:
            clat = round(lat + dlat, 6)
            clon = round(lon + dlon, 6)
            try:
                terrain = TerrainData.from_response(get_terrain_data(clat, clon))
                marker = "✓" if terrain.aspect == target else " "
                print(f"  [{marker}] ({clat}, {clon})  aspect={terrain.aspect or 'flat'}  slope={terrain.slope_degrees}°")
                if terrain.aspect == target:
                    hits.append((clat, clon, terrain.slope_degrees, terrain.elevation_m))
            except Exception as e:
                print(f"  [!] ({clat}, {clon})  error: {e}")

    if not hits:
        print("\n  No matches found — try different area.")
    else:
        best = max(hits, key=lambda h: h[2])
        print(f"\n  Best candidate (steepest slope): ({best[0]}, {best[1]})  slope={best[2]}°  elev={best[3]}m")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: uv run eval/solar/utils/find_aspect.py <lat> <lon> <target_aspect>")
        sys.exit(1)
    scan(float(sys.argv[1]), float(sys.argv[2]), sys.argv[3].upper())
