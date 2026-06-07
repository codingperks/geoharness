# Eval Scoring Rules

Rules used to assign GOOD / MARGINAL / BAD labels to eval locations based on raw geospatial data.
These labels form the ground truth for the eval set.

---

## Location selection

10 coordinates across three categories: good, marginal, and bad. Selection criteria:

- **Spread across latitudes and hemispheres** — avoid clustering in one region
- **Variety of failure modes** — bad locations should be bad for different reasons (climate, terrain, land cover)
- **At least one conflicting-signal location** — good irradiance but poor terrain, or ideal terrain but poor climate, to test whether the agent synthesises correctly rather than pattern-matching on a single signal
- **Avoid previously tested coordinates** — London, Belgium, and Cornwall were used during development and have already influenced prompt tuning

Specific coordinates were identified by rough geographic knowledge (e.g. known solar farm regions, mountain ranges), then verified against NASA POWER annual irradiance values using `probe_location.py` before being added. Coordinates were adjusted slightly from initial GMaps picks to land on terrain with appropriate aspect and slope where possible.

**Note on Amazon Rainforest:** currently scores MARGINAL on climate + terrain data alone (irradiance is reasonable but cloud cover is high). Expected to become BAD once a satellite/land cover tool is added, as dense forest cover makes the location unsuitable regardless of irradiance. Label will be updated at that point.

---

## Solar Irradiance (all-sky annual, kWh/m²/day)

| Label    | Range         |
|----------|---------------|
| GOOD     | ≥ 4.5         |
| MARGINAL | 3.0 – 4.5     |
| BAD      | < 3.0         |

**Source:** World Bank / ESMAP Global Solar Atlas uses ~4.5 kWh/m²/day as the threshold above which utility-scale solar is considered economically attractive in most markets. Below 3.0 kWh/m²/day, generation is insufficient for cost-effective deployment without heavy subsidies.

---

## Cloud Cover Loss (% reduction from clear-sky to all-sky irradiance)

| Label    | Range     |
|----------|-----------|
| GOOD     | < 20%     |
| MARGINAL | 20 – 40%  |
| BAD      | > 40%     |

**Source:** Derived from NASA POWER ALLSKY vs CLRSKY values. A >40% persistent cloud cover reduction indicates a climate where solar is systematically constrained regardless of irradiance potential. Complements the irradiance label — a location can have high clear-sky potential but poor real-world output due to cloud cover.

---

## Aspect (terrain facing direction)

**Northern hemisphere (lat ≥ 0):**

| Label    | Aspects           |
|----------|-------------------|
| GOOD     | S                 |
| MARGINAL | SE, SW, E, W      |
| BAD      | N, NE, NW         |
| N/A      | Slope < 1° (flat) |

**Southern hemisphere (lat < 0):**

| Label    | Aspects           |
|----------|-------------------|
| GOOD     | N                 |
| MARGINAL | NE, NW, E, W      |
| BAD      | S, SE, SW         |
| N/A      | Slope ≤ 10° |

**Note:** Aspect is only scored when slope > 10°. On gentle terrain, panels can be independently oriented regardless of slope direction, so terrain aspect is not a meaningful constraint.

**Source:** Basic solar geometry — south-facing surfaces in the northern hemisphere receive maximum annual solar exposure. East/west-facing surfaces typically lose 15–25% of annual yield compared to south-facing (exact loss depends on latitude, tilt, and module configuration; consistent with simulation results across the PV literature). North-facing surfaces receive minimal direct irradiance and are generally unsuitable for fixed-tilt installations. (Hay & McKay, 1985.)

---

## Slope

| Label    | Range       |
|----------|-------------|
| GOOD     | 0° – 10°    |
| MARGINAL | 10° – 20°   |
| BAD      | > 20°       |

**Source:** Ground-mounted solar installations require accessible, stable terrain. Slopes above 20° significantly increase civil engineering costs (grading, anchoring, access roads) and introduce erosion risk. 10–20° is installable but adds material cost. These thresholds reflect general solar farm site assessment practice; specific limits vary by developer and jurisdiction.

---

## Temperature (annual average, °C)

| Label    | Range        |
|----------|--------------|
| GOOD     | 0 – 25°C     |
| MARGINAL | 25 – 65°C    |
| BAD      | < 0°C or > 65°C |

**Note:** This uses annual average air temperature as a proxy for thermal stress on panels. Panel surface temperature runs ~20–30°C above ambient. Above 25°C ambient (i.e. ~45–55°C panel temp), efficiency losses from the temperature coefficient (~0.35–0.45%/°C above STC of 25°C) become significant. Below 0°C annual average, freeze-thaw cycling and prolonged snow cover reduce output and increase maintenance burden.  
**Source:** IEC 61215 standard test conditions (STC = 25°C); manufacturer temperature coefficient data; Skoplaki & Palyvos (2009), "On the temperature dependence of photovoltaic module electrical performance," Solar Energy, vol. 83. Note: the paper reports ~0.40–0.50%/°C for standard crystalline silicon; the lower end of the range here (~0.35%/°C) applies to premium HIT/heterojunction modules.

---

## Elevation

Not scored. Elevation has a minor positive effect on irradiance (less atmospheric attenuation at higher altitude) but this is already captured in the NASA POWER irradiance values, which are surface measurements. Slope and aspect derived from the DEM are more relevant than raw elevation.

---

## Overall location label

A location's overall label is determined by its worst individual score across irradiance, cloud cover, aspect, and slope:
- All GOOD → GOOD
- Any MARGINAL, none BAD → MARGINAL  
- Any BAD → BAD

This is conservative by design — a location with excellent irradiance but a north-facing slope should not be labelled GOOD.
