"""
Probes coordinates against the climate and terrain APIs, scores each location,
and writes the eval dataset JSON.

Usage:
    uv run eval/solar/utils/build_eval_dataset.py                        # all locations in eval_locations.txt
    uv run eval/solar/utils/build_eval_dataset.py <lat> <lon>            # single coordinate (prints scores, no file output)
"""

import json
import sys
import os
from dataclasses import asdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from tools import get_climate_data, get_terrain_data
from models.tools import ClimateData, TerrainData
from models.eval import EvalLocation, EvalTestCase

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "../data/output/eval_dataset.json")


def probe(lat: float, lon: float, name: str = "") -> EvalTestCase | None:
    label = f"{name} ({lat}, {lon})" if name else f"({lat}, {lon})"
    print(f"\n{'─' * 60}")
    print(f"  {label}")
    print(f"{'─' * 60}")

    try:
        climate = ClimateData.from_response(get_climate_data(lat, lon))
        terrain = TerrainData.from_response(get_terrain_data(lat, lon))
    except Exception as e:
        print(f"  ERROR: {e}")
        return None

    allsky = climate.allsky_irradiance["ANN"]
    clearsky = climate.clearsky_irradiance["ANN"]
    cloud_loss_pct = round((1 - allsky / clearsky) * 100, 1)
    temp = climate.temperature_2m["ANN"]

    def label_irradiance(v):
        return "GOOD" if v >= 4.5 else "MARGINAL" if v >= 3.0 else "BAD"

    def label_cloud_loss(v):
        return "GOOD" if v < 20 else "MARGINAL" if v <= 40 else "BAD"

    def label_aspect(v):
        if v is None or terrain.slope_degrees <= 10:
            return "N/A (slope too gentle for aspect to matter)"
        good = "S" if lat >= 0 else "N"
        bad = ("N", "NE", "NW") if lat >= 0 else ("S", "SE", "SW")
        if v == good:
            return "GOOD"
        if v in bad:
            return "BAD"
        return "MARGINAL"

    def label_slope(v):
        return "GOOD" if v <= 10 else "MARGINAL" if v <= 20 else "BAD"

    def label_temperature(v):
        return "GOOD" if 0 <= v <= 25 else "MARGINAL" if v <= 65 else "BAD"

    scores = [
        label_irradiance(allsky),
        label_cloud_loss(cloud_loss_pct),
        label_slope(terrain.slope_degrees),
        label_temperature(temp),
    ]
    if terrain.aspect is not None:
        scores.append(label_aspect(terrain.aspect))

    verdict = "BAD" if "BAD" in scores else "MARGINAL" if "MARGINAL" in scores else "GOOD"

    print(f"  Solar (all-sky annual):   {allsky} kWh/m²/day  →  {label_irradiance(allsky)}")
    print(f"  Cloud cover loss:         {cloud_loss_pct}%  →  {label_cloud_loss(cloud_loss_pct)}")
    print(f"  Avg temperature:          {temp}°C  →  {label_temperature(temp)}")
    print(f"  Slope:                    {terrain.slope_degrees}°  →  {label_slope(terrain.slope_degrees)}")
    print(f"  Aspect:                   {terrain.aspect or 'flat'}  →  {label_aspect(terrain.aspect)}")
    print(f"  Elevation:                {terrain.elevation_m}m  (not scored)")
    print(f"\n  OVERALL: {verdict}")

    location = EvalLocation(name=name, lat=lat, lon=lon, climate_data=climate, terrain_data=terrain)
    return EvalTestCase(location=location, expected_verdict=verdict)


def parse_locations_file(path: str) -> list[tuple[str, float, float]]:
    locations = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.endswith(":") or "locations" in line.lower() or "marginal" in line.lower() or "bad" in line.lower() or "good" in line.lower():
                continue
            try:
                name, coords = line.rsplit(":", 1)
                lat, lon = [float(x.strip()) for x in coords.split(",")]
                locations.append((name.strip(), lat, lon))
            except ValueError:
                continue
    return locations


if __name__ == "__main__":
    if len(sys.argv) == 3:
        probe(float(sys.argv[1]), float(sys.argv[2]))
    else:
        locations_file = os.path.join(os.path.dirname(__file__), "../data/input/eval_locations.txt")
        test_cases = [
            tc for tc in (
                probe(lat, lon, name)
                for name, lat, lon in parse_locations_file(locations_file)
            )
            if tc is not None
        ]
        with open(OUTPUT_PATH, "w") as f:
            json.dump([asdict(tc) for tc in test_cases], f, indent=2)
        print(f"\nDataset saved to {OUTPUT_PATH} ({len(test_cases)} locations)")
