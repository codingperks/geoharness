import inspect
import json

from models.agents import AgentResponse
from llm import send_message
import tools

_DEFAULT_OUTPUT_CONFIG = {
    "format": {
        "type": "json_schema",
        "schema": {
            "type": "object",
            "properties": {
                "output": {"type": "string"},
            },
            "required": ["output"],
            "additionalProperties": False,
        }
    }
}


class Agent:
    """
    An agent that can perform tasks by calling tools and observing results.
    ReAct agent: observe -> reflect -> act -> observe -> reflect -> act etc. 
    """
    
    def __init__(self, name: str, tool_registry: dict | None = None, output_config: dict | None = None):
        self.name: str = name
        self.task: str = ""
        self.act_prompt: str = """
            You are a helpful assistant who can perform any task.
            You will be responsible for calling tools, observing results, deciding if you have completed the task, and then outputting a final status message.

            You are solving the following task:
            {task}

            Current conversation history:
            {history}
            
            You have access to the following tools:
            {tools}
            
            Your response should be in the following format:
            Thought: <your reasoning about what to do next>
            Tool Calls: <JSON array of tools to call, e.g. [{{"name": "tool_name", "args": {{"lat": 51.5074, "lon": -0.1278}}}}]. Leave blank if not calling any tools. You may call multiple tools in one step if they are independent.>
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

            Rules:
            - Only report what is explicitly present in the observation above. Do not infer, assume, or generate content that is not there.
            - If the observation does not contain the information needed, say so clearly. Do not invent plausible-sounding content.
            - Quote the exact text from the observation when stating a fact.

            Exact quotes from the observation relevant to the task: <copy the relevant raw text verbatim, or write "nothing relevant found">
            Observation Summary: <your summary based only on the quoted text above>
        """
        self.reflect_prompt: str = """
            You are reflecting on your progress so far.

            You are solving the following task:
            {task}

            Current conversation history:
            {history}

            Evaluate whether the task is complete and whether your approach is working.
            Before answering, check: did you make any assumptions about the contents of a source without actually reading it? If so, mark the task as incomplete and verify those assumptions first.
            TASK_COMPLETE: yes or no
            What is working: <what is going well>
            Unverified assumptions: <list any conclusions drawn from inference rather than direct evidence, or leave blank if none>
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
        self.tool_registry: dict = tool_registry if tool_registry is not None else tools.REGISTRY
        self.output_config: dict = output_config if output_config is not None else _DEFAULT_OUTPUT_CONFIG
        
    def observe(self, observation: str) -> str:
        print(f"\n[observe] input: {observation}")
        response = send_message(self.observe_prompt.format(task=self.task, history="\n".join(self.history), observation=observation), name="observe")
        print(f"[observe] response: {response}")
        self.history.append(f"Observation: {observation}")
        self.history.append(f"Observation Summary: {response}")
        return response

    def _clean_line(self, line: str) -> str:
        return line.replace("**", "").replace("`", "").strip()

    def _parse_act_response(self, raw: str) -> AgentResponse:
        thought = output = None
        tool_calls = []
        for line in raw.splitlines():
            line = self._clean_line(line)
            if line.startswith("Thought:"):
                thought = line.removeprefix("Thought:").strip()
            elif line.startswith("Tool Calls:"):
                value = line.removeprefix("Tool Calls:").strip()
                if value:
                    try:
                        tool_calls = json.loads(value)
                    except json.JSONDecodeError:
                        pass
            elif line.startswith("Output:"):
                value = line.removeprefix("Output:").strip()
                if value:
                    output = value
        return AgentResponse(thought=thought, tool_calls=tool_calls, output=output)

    def act(self, message: str) -> AgentResponse:
        print(f"\n[act] task: {message}")
        if self.task == "":
            self.task = message
        tool_descriptions = "\n".join(
            f"- {name}: {desc} | params: {list(inspect.signature(fn).parameters.keys())}"
            for name, (fn, desc) in self.tool_registry.items()
        )
        raw = send_message(self.act_prompt.format(task=self.task, history="\n".join(self.history), tools=tool_descriptions), name="act")
        print(f"[act] response: {raw}")
        self.history.append(f"User: {message}")
        self.history.append(f"Agent: {raw}")
        return self._parse_act_response(raw)

    def reflect(self) -> str:
        print(f"\n[reflect]")
        response = send_message(self.reflect_prompt.format(task=self.task, history="\n".join(self.history)), name="reflect")
        print(f"[reflect] response: {response}")
        self.history.append(f"Reflection: {response}")
        return response

    def call_tool(self, tool_name: str, tool_args: dict | str | None = None):
        if tool_name not in self.tool_registry:
            raise ValueError(f"Tool '{tool_name}' not found.")
        fn, _ = self.tool_registry[tool_name]
        if isinstance(tool_args, str):
            first_param = next(iter(inspect.signature(fn).parameters))
            tool_args = {first_param: tool_args}
        tool_call = fn(**(tool_args or {}))
        self.history.append(f"Executed tool '{tool_name}' with args {tool_args}")
        self.history.append(f"Tool Response: {tool_call.output}")
        return tool_call.output

    def output(self) -> dict:
        print(f"\n[output] task: {self.task}")
        response = send_message(self.output_prompt.format(task=self.task, history="\n".join(self.history)), name="output", output_config=self.output_config)
        print(f"[output] response: {response}")
        self.history.append(f"Final Output: {response}")
        return response
    

    
    