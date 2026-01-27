import os
import time
from core.llm.gemini import GeminiClient
from core.llm.openai import OpenAIClient
from core.llm.mock import MockClient

class LLMError(Exception): pass

def create_client(provider="mock"):
    if provider == "gemini":
        key = os.getenv("GEMINI_API_KEY")
        if not key: raise LLMError("GEMINI_API_KEY missing")
        return GeminiClient(key)
    elif provider == "openai":
        key = os.getenv("OPENAI_API_KEY")
        if not key: raise LLMError("OPENAI_API_KEY missing")
        return OpenAIClient(key)
    return MockClient()

class LLMClient:
    """Facade for LLM interactions with retry logic."""
    def __init__(self, provider="mock", max_retries=3):
        self.provider_name = provider
        self.max_retries = max_retries
        self.provider = create_client(provider)

    def generate_diary(self, raw_text, system_prompt):
        for attempt in range(self.max_retries):
            try:
                return self.provider.generate(raw_text, system_prompt)
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(2**attempt)
                    continue
                raise LLMError(f"Generation failed: {e}")

    def get_usage_stats(self):
        return self.provider.get_stats()
