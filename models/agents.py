from dataclasses import dataclass

@dataclass
class AgentResponse:
    thought: str
    tool_call: str | None
    tool_args: str | None
    output: str | None