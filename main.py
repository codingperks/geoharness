import sys
from agent import Agent
from langfuse import get_client


def run(task: str) -> str:
    agent = Agent("GeoHarness Agent")
    langfuse = get_client()

    with langfuse.start_as_current_observation(name="Geoharness react", as_type="span"):
        while True:
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

    langfuse.flush()
    return final_output


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py \"<task>\"")
        sys.exit(1)

    print(run(sys.argv[1]))
