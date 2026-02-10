"""Enhanced LLM client with batching support"""
import os
import json
import time
from typing import Dict, Any, List, Optional
from pathlib import Path

from src.core.llm.gemini import GeminiClient
from src.core.llm.openai import OpenAIClient
from src.core.llm.mock import MockClient
from config import LLM_PROVIDER, LLM_MAX_RETRIES, OPENAI_API_KEY, GEMINI_API_KEY
from src.utils.logger import get_logger

logger = get_logger(__name__)


class LLMError(Exception):
    """LLM-related errors"""
    pass


class LLMClient:
    """Enhanced LLM client with retry logic and batching support"""

    def __init__(self, provider: str = LLM_PROVIDER, max_retries: int = LLM_MAX_RETRIES):
        self.provider_name = provider
        self.max_retries = max_retries
        self.provider = self._create_provider(provider)
        logger.info(f"Initialized LLM client: {provider}")

    def _create_provider(self, provider: str):
        """Create appropriate LLM provider"""
        if provider == "gemini":
            if not GEMINI_API_KEY:
                raise LLMError("GEMINI_API_KEY not set in environment")
            return GeminiClient(GEMINI_API_KEY)

        elif provider == "openai":
            if not OPENAI_API_KEY:
                raise LLMError("OPENAI_API_KEY not set in environment")
            return OpenAIClient(OPENAI_API_KEY)

        elif provider == "mock":
            logger.warning("Using mock LLM provider (for testing only)")
            return MockClient()

        else:
            raise LLMError(f"Unknown LLM provider: {provider}")

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        json_mode: bool = True
    ) -> Any:
        """
        Generate response from LLM.

        Args:
            prompt: User prompt
            system: System prompt (optional)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            json_mode: Expect JSON response

        Returns:
            Parsed JSON dict if json_mode=True, else string
        """
        for attempt in range(self.max_retries):
            try:
                # Call provider with legacy interface: generate(raw_text, system_prompt)
                # Original providers don't support temperature/max_tokens parameters
                system_prompt = system if system else ""
                response = self.provider.generate(prompt, system_prompt)

                # Providers already return parsed Python objects (dict/list)
                # No need to parse JSON again
                if json_mode:
                    # Response is already parsed by the provider
                    if isinstance(response, (dict, list)):
                        return response
                    # Only parse if it's still a string
                    elif isinstance(response, str):
                        return json.loads(response)
                    else:
                        return response

                return response

            except json.JSONDecodeError as e:
                logger.warning(f"Attempt {attempt + 1}: JSON parsing failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise LLMError(f"Failed to parse JSON after {self.max_retries} attempts")

            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}: Generation failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise LLMError(f"Generation failed after {self.max_retries} attempts: {e}")

    def generate_bulk(
        self,
        prompts: List[str],
        system: Optional[str] = None,
        **kwargs
    ) -> List[Any]:
        """
        Generate responses for multiple prompts.

        Note: For now, processes sequentially. Can be parallelized with async.
        """
        results = []
        for prompt in prompts:
            result = self.generate(prompt=prompt, system=system, **kwargs)
            results.append(result)
        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        if hasattr(self.provider, 'get_stats'):
            return self.provider.get_stats()
        return {}


def get_llm_client(provider: Optional[str] = None) -> LLMClient:
    """
    Get configured LLM client.

    Args:
        provider: LLM provider (openai, gemini, mock). Defaults to config.LLM_PROVIDER
    """
    return LLMClient(provider=provider or LLM_PROVIDER)
