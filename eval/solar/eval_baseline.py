import json
import os
import sys
from dataclasses import asdict
from datetime import datetime, timezone

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from eval import load_test_cases, EVAL_OUTPUT, RESULTS_DIR
from models.eval import EvalTestCase
import llm

PROMPT_TEMPLATE = """\
Is {name} ({lat}, {lon}) a good location for ground-mounted solar panels? \
Base your verdict solely on the data provided below — do not factor in general \
knowledge about the location, land use, or regulations. \
When the data presents multiple factors (e.g. solar irradiance, cloud cover, slope, \
aspect, temperature), the overall verdict should be driven by the weakest factor, not \
an average — a site with strong irradiance but a problematic slope or aspect should \
not be rated GOOD overall. \
Assess and give a verdict of GOOD, MARGINAL, or BAD based on the data below.

Climate data:
{climate_data}

Terrain data:
{terrain_data}\
"""


def build_prompt(tc: EvalTestCase) -> str:
    return PROMPT_TEMPLATE.format(
        name=tc.location.name,
        lat=tc.location.lat,
        lon=tc.location.lon,
        climate_data=json.dumps(asdict(tc.location.climate_data)),
        terrain_data=json.dumps(asdict(tc.location.terrain_data)),
    )


def evaluate_case(tc: EvalTestCase) -> dict:
    prompt = build_prompt(tc)
    output = llm.send_message(prompt, name="baseline", output_config=EVAL_OUTPUT)
    verdict = output.get("verdict", "Failed to output verdict")
    return {
        "name": tc.location.name,
        "expected": tc.expected_verdict,
        "actual": verdict,
        "passed": verdict == tc.expected_verdict,
        "prompt": prompt,
        "model": llm.model,
        "output": output,
        "mode": "baseline",
    }


def evaluate():
    test_cases = load_test_cases()
    results = [evaluate_case(tc) for tc in test_cases]

    passed = sum(r["passed"] for r in results)
    print(f"\n{'═' * 60}")
    print(f"  Baseline results: {passed}/{len(results)} passed")
    print(f"{'═' * 60}")
    for r in sorted(results, key=lambda r: r["name"]):
        status = "PASS" if r["passed"] else "FAIL"
        print(f"  [{status}] {r['name']}: expected={r['expected']}, got={r['actual']}")

    os.makedirs(RESULTS_DIR, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    results_path = os.path.join(RESULTS_DIR, f"baseline_{timestamp}.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nFull results saved to {results_path}")
    return results


if __name__ == "__main__":
    evaluate()
