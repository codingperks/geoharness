from dataclasses import dataclass, field

@dataclass
class AgentResponse:
    thought: str
    tool_calls: list[dict]
    output: str | None