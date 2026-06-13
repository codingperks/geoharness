import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from main import run
from models.eval import EvalTestCase, EvalLocation, EvalResult
from models.tools import ClimateData, TerrainData
import llm
import tools

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "../..")
EVAL_TOOLS = {k: v for k, v in tools.REGISTRY.items() if k in ("get_climate_data", "get_terrain_data")}
MCP_SERVER_PATH = os.path.join(PROJECT_ROOT, "geo_mcp.py")
MCP_URI = "http://localhost:8000/mcp"

DATASET_PATH = os.path.join(os.path.dirname(__file__), "data/eval_dataset.json")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")

EVAL_OUTPUT = {
    "format" : {
        "type": "json_schema",
        "schema" : {
            "type" : "object",
            "properties": {
                "verdict": {"type": "string"},
                "output": {"type": "string"}
            },
            "required": ["verdict", "output"],
            "additionalProperties": False,
        }
    }
}


def load_test_cases() -> list[EvalTestCase]:
    with open(DATASET_PATH) as f:
        data = json.load(f)
    return [
        EvalTestCase(
            location=EvalLocation(
                **{**tc["location"],
                   "climate_data": ClimateData(**tc["location"]["climate_data"]),
                   "terrain_data": TerrainData(**tc["location"]["terrain_data"])},
            ),
            expected_verdict=tc["expected_verdict"],
        )
        for tc in data
    ]


def evaluate_case(tc: EvalTestCase, mcp_uri: str | None = None) -> EvalResult:
    prompt = (
    f"Is {tc.location.name} ({tc.location.lat}, {tc.location.lon}) a good location "
    f"for ground-mounted solar panels? Use the available tools to assess the location. "
    f"Base your verdict solely on the data the tools return — do not factor in general "
    f"knowledge about the location, land use, or regulations."
    f"Assess and give a verdict of GOOD, MARGINAL, or BAD based on the data the tools return."
)

    output, iterations, tool_error, trace_id = run(
        prompt,
        tool_registry=None if mcp_uri else EVAL_TOOLS,
        output_config=EVAL_OUTPUT,
        mcp_uri=mcp_uri,
    )
    verdict = output.get("verdict", "Failed to output verdict")

    return EvalResult(
        test_case=tc,
        actual_verdict=verdict,
        passed=verdict == tc.expected_verdict,
        output=output,
        prompt=prompt,
        model=llm.model,
        iterations=iterations,
        tool_error=tool_error,
        trace_id=trace_id,
    )
    
    
def evaluate(use_mcp: bool = False):
    test_cases: list[EvalTestCase] = load_test_cases()
    results: list[EvalResult] = []

    mcp_proc = None
    mcp_uri = None
    if use_mcp:
        mcp_proc = subprocess.Popen(
            ["uv", "run", MCP_SERVER_PATH],
            cwd=PROJECT_ROOT,
        )
        time.sleep(2)
        mcp_uri = MCP_URI

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {executor.submit(evaluate_case, tc, mcp_uri): tc for tc in test_cases}
            for future in as_completed(futures):
                results.append(future.result())
    finally:
        if mcp_proc:
            mcp_proc.terminate()
    
    passed = sum(r.passed for r in results)
    print(f"\n{'═' * 60}")
    print(f"  Results: {passed}/{len(results)} passed")
    print(f"{'═' * 60}")
    for r in sorted(results, key=lambda r: r.test_case.location.name):
        status = "PASS" if r.passed else "FAIL"
        flag = "  ⚠ tool error" if r.tool_error else ""
        print(f"  [{status}] {r.test_case.location.name}: expected={r.test_case.expected_verdict}, got={r.actual_verdict} ({r.iterations} iter){flag}")

    os.makedirs(RESULTS_DIR, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    results_path = os.path.join(RESULTS_DIR, f"eval_{timestamp}.json")
    with open(results_path, "w") as f:
        json.dump(
            [
                {
                    "name": r.test_case.location.name,
                    "expected": r.test_case.expected_verdict,
                    "actual": r.actual_verdict,
                    "passed": r.passed,
                    "prompt": r.prompt,
                    "model": r.model,
                    "iterations": r.iterations,
                    "tool_error": r.tool_error,
                    "output": r.output,
                    "mcp": use_mcp,
                    "trace_id": r.trace_id,
                }
                for r in results
            ],
            f,
            indent=2,
        )
    print(f"\nFull results saved to {results_path}")
    return results


if __name__ == "__main__":
    evaluate(use_mcp="--mcp" in sys.argv)
