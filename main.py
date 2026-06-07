import sys
from agent import Agent
from langfuse import get_client


def run(task: str, tool_registry: dict | None = None) -> str:
    agent = Agent("GeoHarness Agent", tool_registry=tool_registry)
    langfuse = get_client()

    max_iterations = 10
    iterations = 0
    with langfuse.start_as_current_observation(name="Geoharness react", as_type="span"):
        for iterations in range(1, max_iterations + 1):
            response = agent.act(task)

            if response.tool_call:
                tool_result = agent.call_tool(response.tool_call, response.tool_args)
                print(f"Tool Response: {tool_result}")
                agent.observe(tool_result)
            else:
                agent.observe(response.thought or "")

            reflection = agent.reflect()

            if "task_complete: yes" in reflection.lower():
                final_output, _ = agent.output()
                break
        else:
            final_output, _ = agent.output()

    langfuse.flush()
    return final_output, iterations


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py \"<task>\"")
        sys.exit(1)

    output, iterations = run(sys.argv[1])
    print(output)
    print(f"[{iterations} iteration(s)]")
