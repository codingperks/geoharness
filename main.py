import sys
from agent import Agent
from concurrent.futures import ThreadPoolExecutor, as_completed
from langfuse import get_client


_TOOL_ERROR_STRINGS = ("failed to retrieve", "no elevation data available")


def run(task: str, tool_registry: dict | None = None, output_config: dict | None = None, mcp_uri: str | None = None) -> tuple[dict, int, bool, str | None]:
    agent = Agent("GeoHarness Agent", tool_registry=tool_registry, output_config=output_config, mcp_uri=mcp_uri)
    langfuse = get_client()

    max_iterations = 10
    iterations = 0
    tool_error = False
    trace_id = None
    with langfuse.start_as_current_observation(name="Geoharness react", as_type="span") as span:
        trace_id = span.trace_id
        for iterations in range(1, max_iterations + 1):
            response = agent.act(task)

            if response.tool_calls:
                with ThreadPoolExecutor() as executor:
                    futures = {executor.submit(agent.call_tool, tc["name"], tc["args"]): tc["name"] for tc in response.tool_calls}
                    tool_results = []
                    for future in as_completed(futures):
                        result = future.result()
                        tool_results.append(result)
                        if any(e in result.lower() for e in _TOOL_ERROR_STRINGS):
                            tool_error = True

                combined = "\n\n".join(tool_results)
                print(f"Tool Response: {combined}")
                agent.observe(combined)

            else:
                agent.observe(response.thought or "")

            reflection = agent.reflect()

            if "task_complete: yes" in reflection.lower():
                final_output = agent.output()
                break
        
        else:
            final_output = agent.output()

    langfuse.flush()
    return final_output, iterations, tool_error, trace_id


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py \"<task>\"")
        sys.exit(1)

    output, iterations, tool_error, trace_id = run(sys.argv[1])
    print(output.get("output", output))
    print(f"[{iterations} iteration(s)]{'  ⚠ tool error' if tool_error else ''}")
    if trace_id:
        print(f"Trace: {trace_id}")
