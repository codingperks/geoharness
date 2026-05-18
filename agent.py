from llm import send_message

class Agent:
    """
    An agent that can perform tasks by calling tools and observing results.
    ReAct agent: observe -> reflect -> act -> observe -> reflect -> act etc. 
    """
    
    def __init__(self, name: str):
        self.name: str = name
        self.act_prompt: str = """
            You are a helpful assistant who can perform any task.
            You will be responsible for calling tools, observing results, deciding if you have completed the task, and then outputting a final status message.

            You are solving the following task:
            {task}

            Current conversation history:
            {history}

            Your response should be in the following format:
            Thought: <your reasoning about what to do next>
            Tool Call: <tool name and arguments if you want to call a tool, otherwise leave blank>
            Output: <final answer if you have completed the task, otherwise leave blank>
        """
        self.observe_prompt: str = """
            You are processing the result of a tool call or external input.

            You are solving the following task:
            {task}

            Current conversation history:
            {history}

            New observation:
            {observation}

            Summarise what you observed and what it means for completing the task.
            Observation Summary: <your summary>
        """
        self.reflect_prompt: str = """
            You are reflecting on your progress so far.

            You are solving the following task:
            {task}

            Current conversation history:
            {history}

            Evaluate whether the task is complete and whether your approach is working.
            Is the task complete? <yes/no>
            What is working: <what is going well>
            What to improve: <what to change on the next attempt, or leave blank if complete>
        """
        self.output_prompt: str = """
            You are deciding on the final output of the task.

            You are solving the following task:
            {task}

            Current conversation history:
            {history}

            Decide on the final output of the task and whether you have completed it.
            Final Output: <your final output>
            Is the task complete? <yes/no>
        """
        self.history: list[str] = []
        
    def observe(self, observation: str) -> str:
        print(f"\n[observe] input: {observation}")
        response = send_message(self.observe_prompt.format(task="", history="\n".join(self.history), observation=observation))
        print(f"[observe] response: {response}")
        self.history.append(f"Observation: {observation}")
        self.history.append(f"Observation Summary: {response}")
        return response

    def act(self, message: str) -> str:
        print(f"\n[act] task: {message}")
        observation = send_message(self.act_prompt.format(task=message, history="\n".join(self.history)))
        print(f"[act] response: {observation}")
        self.history.append(f"User: {message}")
        self.history.append(f"Agent: {observation}")
        return observation

    def reflect(self) -> str:
        print(f"\n[reflect]")
        response = send_message(self.reflect_prompt.format(task="", history="\n".join(self.history)))
        print(f"[reflect] response: {response}")
        self.history.append(f"Reflection: {response}")
        return response

    def call_tool(self, tool_name: str, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement this method.")

    def output(self, message: str) -> tuple[str, bool]:
        print(f"\n[output] task: {message}")
        response = send_message(self.output_prompt.format(task=message, history="\n".join(self.history)))
        print(f"[output] response: {response}")
        self.history.append(f"Final Output: {response}")
        return response, "yes" in response.lower()
    

    
    