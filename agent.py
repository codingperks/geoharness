

class Agent:
    def __init__(self, name: str):
        self.name: str = name
        self.prompt: str = ""
        self.history: list[str] = []

    def act(self, observation: str) -> str:
        raise NotImplementedError("Subclasses must implement this method.")
    
    def observe(self, observation: str):
        raise NotImplementedError("Subclasses must implement this method.")
        
    def call_tool(self, tool_name: str, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement this method.")
    
    def output(self, message: str) -> str:
        raise NotImplementedError("Subclasses must implement this method.")
    
    