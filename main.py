from agent import Agent

if __name__ == "__main__":
    agent = Agent("GeoHarness Agent")

    while True:
        response = agent.act("What is the capital of France ")
        agent.observe(response)
        reflection = agent.reflect()
        
        if "yes" in reflection.lower():
            final_output, _ = agent.output("What is the capital of France")
            print(f"Final Output: {final_output}")
            print(f"history: {agent.history}")
            break