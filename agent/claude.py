from anthropic import Anthropic, APIError
from anthropic.types import TextBlock
from agent.base import AI_Platform


class AnthropicAgent(AI_Platform):

    def __init__(self, api_key: str, system_prompt: str | None):

        self.api_key = api_key
        self.system_prompt = system_prompt or "You are a helpful developer assistant."
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-haiku-latest"



    def _extract_text(self, response) -> str:
        texts = [
            block.text
            for block in response.content
            if isinstance(block, TextBlock)
        ]
    
        return "\n".join(texts) if texts else "No text response returned."



    def chat(self, prompt: str) -> str:
        """
        Low-level wrapper around the Anthropic Messages API.
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=self.system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )

            return self._extract_text(response)

        except APIError as e:
            return f"Anthropic API error: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
        

    def process(self, user_input: str) -> str:
        """
        High-level method used by your CLI / API layer.
        This is where you add:
        - logging
        - metrics
        - security filters
        - rate limiting
        - caching (later with Redis)
        """
        if not user_input or not user_input.strip():
            return "Input is empty."

        try:
            response = self.chat(user_input)
            return response

        except Exception as e:
            return f"Processing error: {str(e)}"



