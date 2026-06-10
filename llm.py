import json
import os
import time
import anthropic
from dotenv import load_dotenv
from langfuse import get_client

load_dotenv()

_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_KEY"))
model = os.getenv("LLM_MODEL", "claude-sonnet-4-5")
_langfuse = get_client()


def send_message(prompt: str, name: str = "llm_call", output_config: dict | None = None) -> dict | str:
    for attempt in range(3):
        try:
            with _langfuse.start_as_current_observation(as_type="generation", name=name, model=model, input=prompt) as generation:
                message = _client.messages.create(
                    model=model,
                    max_tokens=1024,
                    messages=[{"role": "user", "content": prompt}],
                    **({"output_config": output_config} if output_config else {}),
                )
                result = message.content[0].text
                generation.update(output=result)
            return json.loads(result) if output_config else result
        except anthropic.RateLimitError:
            if attempt == 2:
                raise
            time.sleep(30 * (attempt + 1))
