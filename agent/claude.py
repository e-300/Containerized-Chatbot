# LAYER 2 - AI client implementing the abs base class

from anthropic import Anthropic, APIError
from anthropic.types import TextBlock
from agent.base import AI_Platform
import redis
import hashlib


class AnthropicAgent(AI_Platform):
    # parameterized constructor
    def __init__(
        self,
        api_key: str,
        system_prompt: str | None,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        socket_connect_timeout: float = 5,
    ):
        self.api_key = api_key
        self.system_prompt = system_prompt or "You are a helpful developer assistant."
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-haiku-latest"

        # Redis client with connection pooling
        try:
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=0,
                decode_responses=True,
                socket_connect_timeout=socket_connect_timeout,
            )

            # Test connection
            self.redis_client.ping()
            # control var
            self.redis_enabled = True

        except (redis.ConnectionError, redis.TimeoutError) as e:
            print(f"Redis connection failed: {e}. Caching disabled.")
            self.redis_enabled = False

    # Generate redis caching key
    def _generate_cache_key(self, user_input: str) -> str:
        cache_string = f"{self.system_prompt}:{user_input}"
        hash_result = hashlib.sha256(cache_string.encode()).hexdigest()
        result = f"agent_cache:{hash_result}"
        return result

    # helper function to extract text according to cluade api bc they be expecting various i/o
    def _extract_text(self, response) -> str:
        texts = [
            block.text for block in response.content if isinstance(block, TextBlock)
        ]

        return "\n".join(texts) if texts else "No text response returned."

    # low lvl wrapper around the raw antropic msgs api
    def chat(self, prompt: str) -> str:
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=self.system_prompt,
                messages=[{"role": "user", "content": prompt}],
            )

            return self._extract_text(response)

        except APIError as e:
            return f"Anthropic API error: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
        




    # high lvl wrapper - our production concerns
    # need to add: logging, metrics, security filters, rate limiting, and redis caching
    def process(self, user_input: str) -> str:
        if not user_input or not user_input.strip():
            return "Input is empty."
        

        try:
            # Check Redis cache if enabled
            if self.redis_enabled:
                cache_key = self._generate_cache_key(user_input)

                try:
                    cached_response = self.redis_client.get(cache_key)
                    # Explicitly check type and return if found
                    if cached_response is not None and isinstance(cached_response, str):
                        return str(cached_response)


                except (redis.RedisError, AttributeError, NameError) as e:
                    print(f"Redis GET error: {e}. Proceeding without cache.")

                    # Disable Redis for this instance if connection is broken
                    self.redis_enabled = False



            # cache miss or Redis disabled - call llm
            response = self.chat(user_input)

            # store in Redis cache if enabled and response is valid
            if (
                self.redis_enabled
                and response
                and not response.startswith("Anthropic API error")
            ):
                try:
                    self.redis_client.setex(cache_key, 3600, response)
                except redis.RedisError as e:
                    print(f"Redis SET error: {e}. Response returned without caching.")

            return response

        except Exception as e:
            return f"Processing error: {str(e)}"
