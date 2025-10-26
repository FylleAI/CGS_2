"""DeepSeek service adapter."""

import logging
import time
from typing import Dict, List, Optional, Any, AsyncGenerator

import httpx
from openai import AsyncOpenAI

from ...application.interfaces.llm_provider_interface import (
    LLMProviderInterface,
    LLMResponse,
    LLMStreamChunk,
)
from ...domain.value_objects.provider_config import ProviderConfig, LLMProvider

logger = logging.getLogger(__name__)


class DeepSeekAdapter(LLMProviderInterface):
    """
    DeepSeek service adapter implementing LLMProviderInterface.

    This adapter handles all interactions with DeepSeek's API using OpenAI-compatible format.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com"
        self.client = None

    def _get_client(self) -> AsyncOpenAI:
        """Get or create DeepSeek client."""
        if self.client is None:
            if not self.api_key:
                raise ValueError("DeepSeek API key is required")

            self.client = AsyncOpenAI(
                api_key=self.api_key, base_url=self.base_url, timeout=600.0
            )
            logger.debug("Created new DeepSeek client")
        return self.client

    async def generate_content(
        self, prompt: str, config: ProviderConfig, system_message: Optional[str] = None
    ) -> str:
        """Generate content using DeepSeek."""
        try:
            logger.debug(f"Making DeepSeek request with model: {config.model}")

            client = self._get_client()

            # Prepare messages
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})

            # Make API call
            response = await client.chat.completions.create(
                model=config.model,
                messages=messages,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                frequency_penalty=config.frequency_penalty,
                presence_penalty=config.presence_penalty,
            )

            content = response.choices[0].message.content
            logger.debug(f"DeepSeek response received: {len(content)} characters")

            return content

        except Exception as e:
            logger.error(f"DeepSeek API error: {str(e)}")
            raise RuntimeError(f"DeepSeek generation failed: {str(e)}")

    async def generate_content_detailed(
        self, prompt: str, config: ProviderConfig, system_message: Optional[str] = None
    ) -> LLMResponse:
        """Generate content with detailed response."""
        try:
            logger.debug(f"Making detailed DeepSeek request with model: {config.model}")

            client = self._get_client()

            # Prepare messages
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})

            # Make API call
            start_time = time.time()
            response = await client.chat.completions.create(
                model=config.model,
                messages=messages,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                frequency_penalty=config.frequency_penalty,
                presence_penalty=config.presence_penalty,
            )
            duration = time.time() - start_time

            content = response.choices[0].message.content

            return LLMResponse(
                content=content,
                model=config.model,
                finish_reason=response.choices[0].finish_reason or "completed",
                usage={
                    "prompt_tokens": (
                        response.usage.prompt_tokens if response.usage else 0
                    ),
                    "completion_tokens": (
                        response.usage.completion_tokens if response.usage else 0
                    ),
                    "total_tokens": (
                        response.usage.total_tokens if response.usage else 0
                    ),
                },
                response_time=duration,
            )

        except Exception as e:
            logger.error(f"DeepSeek detailed API error: {str(e)}")
            raise RuntimeError(f"DeepSeek detailed generation failed: {str(e)}")

    async def generate_content_stream(
        self, prompt: str, config: ProviderConfig, system_message: Optional[str] = None
    ) -> AsyncGenerator[LLMStreamChunk, None]:
        """Generate content with streaming response."""
        try:
            logger.debug(
                f"Making streaming DeepSeek request with model: {config.model}"
            )

            client = self._get_client()

            # Prepare messages
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})

            # Make streaming API call
            stream = await client.chat.completions.create(
                model=config.model,
                messages=messages,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                frequency_penalty=config.frequency_penalty,
                presence_penalty=config.presence_penalty,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield LLMStreamChunk(
                        content=chunk.choices[0].delta.content, is_final=False
                    )

            # Final chunk
            yield LLMStreamChunk(content="", is_final=True)

        except Exception as e:
            logger.error(f"DeepSeek streaming API error: {str(e)}")
            yield LLMStreamChunk(content=f"Error: {str(e)}", is_final=True)

    async def chat_completion(
        self, messages: List[Dict[str, str]], config: ProviderConfig
    ) -> LLMResponse:
        """Perform chat completion."""
        try:
            logger.debug(f"Making DeepSeek chat completion with model: {config.model}")

            client = self._get_client()

            # Make API call
            start_time = time.time()
            response = await client.chat.completions.create(
                model=config.model,
                messages=messages,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                frequency_penalty=config.frequency_penalty,
                presence_penalty=config.presence_penalty,
            )
            duration = time.time() - start_time

            content = response.choices[0].message.content

            return LLMResponse(
                content=content,
                model=config.model,
                finish_reason=response.choices[0].finish_reason or "completed",
                usage={
                    "prompt_tokens": (
                        response.usage.prompt_tokens if response.usage else 0
                    ),
                    "completion_tokens": (
                        response.usage.completion_tokens if response.usage else 0
                    ),
                    "total_tokens": (
                        response.usage.total_tokens if response.usage else 0
                    ),
                },
                response_time=duration,
            )

        except Exception as e:
            logger.error(f"DeepSeek chat completion error: {str(e)}")
            raise RuntimeError(f"DeepSeek chat completion failed: {str(e)}")

    async def validate_config(self, config: ProviderConfig) -> bool:
        """Validate DeepSeek configuration."""
        if config.provider != LLMProvider.DEEPSEEK:
            return False

        if not self.api_key:
            logger.warning("DeepSeek API key not provided")
            return False

        try:
            # Test API connection
            client = self._get_client()
            # Simple validation call
            await client.models.list()
            return True
        except Exception as e:
            logger.error(f"DeepSeek config validation failed: {str(e)}")
            return False

    async def get_available_models(
        self, config: ProviderConfig
    ) -> List[Dict[str, Any]]:
        """Get available DeepSeek models with token limits."""
        try:
            client = self._get_client()
            models = await client.models.list()
            config_models = {m["name"]: m for m in config.get_available_models()}
            available = []
            for model in models.data:
                info = config_models.get(model.id)
                if info:
                    available.append(info)
            return available or config.get_available_models()
        except Exception as e:
            logger.warning(f"Failed to fetch DeepSeek models: {str(e)}")
            # Return default models
            return config.get_available_models()

    async def estimate_tokens(self, text: str, model: str) -> int:
        """Estimate token count for DeepSeek models."""
        # DeepSeek uses similar tokenization to GPT models
        # Rough estimation: 1 token ≈ 0.75 words
        words = len(text.split())
        return int(words * 1.33)

    async def check_health(self, config: ProviderConfig) -> Dict[str, Any]:
        """Check DeepSeek service health."""
        try:
            if not self.api_key:
                return {
                    "status": "unhealthy",
                    "provider": "deepseek",
                    "error": "API key not provided",
                }

            client = self._get_client()
            # Test API connection
            start_time = time.time()
            await client.models.list()
            response_time = time.time() - start_time

            return {
                "status": "healthy",
                "provider": "deepseek",
                "api_key_valid": True,
                "response_time_ms": round(response_time * 1000, 2),
                "base_url": self.base_url,
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": "deepseek",
                "error": str(e),
                "api_key_valid": bool(self.api_key),
            }
