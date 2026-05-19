import sys
from agent import Agent

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py \"<task>\"")
        sys.exit(1)

    task = sys.argv[1]
    agent = Agent("GeoHarness Agent")

    while True:
        response = agent.act(task)

        if response.tool_call:
            tool_result = agent.call_tool(response.tool_call, response.tool_args)
            print(f"Tool Response: {tool_result}")
            agent.observe(tool_result)
        else:
            agent.observe(response.thought or "")

        reflection = agent.reflect()

        if "yes" in reflection.lower():
            final_output, _ = agent.output(task)
            print(f"Final Output: {final_output}")
            break