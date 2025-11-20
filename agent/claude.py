#LAYER 2 - AI client implementing the abs base class

from anthropic import Anthropic, APIError
from anthropic.types import TextBlock
from agent.base import AI_Platform


class AnthropicAgent(AI_Platform):

    #parameterized constructor 
    def __init__(self, api_key: str, system_prompt: str | None):

        self.api_key = api_key
        # intial prompt for aglinning the ai behavior should be inputted here 
        # maybe add some startup behaviors such as target a codebase 
        self.system_prompt = system_prompt or "You are a helpful developer assistant."
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-haiku-latest"


    #helper function to extract text according to cluade api bc they be expecting various i/o
    def _extract_text(self, response) -> str:
        texts = [
            block.text
            for block in response.content
            if isinstance(block, TextBlock)
        ]
    
        return "\n".join(texts) if texts else "No text response returned."


    #low lvl wrapper around the raw antropic msgs api
    def chat(self, prompt: str) -> str:

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
        

    #high lvl wrapper - our production concerns 
    #need to add: logging, metrics, security filters, rate limiting, and redis caching
    def process(self, user_input: str) -> str:

        if not user_input or not user_input.strip():
            return "Input is empty."

        try:
            response = self.chat(user_input)
            return response

        except Exception as e:
            return f"Processing error: {str(e)}"



