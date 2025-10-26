"""Anthropic service adapter."""

import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
import anthropic
from anthropic import AsyncAnthropic

from ...application.interfaces.llm_provider_interface import (
    LLMProviderInterface,
    LLMResponse,
    LLMStreamChunk,
)
from ...domain.value_objects.provider_config import ProviderConfig, LLMProvider

logger = logging.getLogger(__name__)


class AnthropicAdapter(LLMProviderInterface):
    """
    Anthropic service adapter implementing LLMProviderInterface.

    This adapter handles all interactions with Anthropic's API,
    providing a clean interface for the application layer.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self._client: Optional[AsyncAnthropic] = None

    def _get_client(self, config: ProviderConfig) -> AsyncAnthropic:
        """Get or create Anthropic client."""
        api_key = config.api_key or self.api_key
        if not api_key:
            raise ValueError("Anthropic API key is required")

        if not self._client or self._client.api_key != api_key:
            client_kwargs = {"api_key": api_key}
            if config.base_url:
                client_kwargs["base_url"] = config.base_url

            self._client = AsyncAnthropic(**client_kwargs)
            logger.debug("Created new Anthropic client")

        return self._client

    async def generate_content(
        self, prompt: str, config: ProviderConfig, system_message: Optional[str] = None
    ) -> str:
        """Generate content using Anthropic."""
        if config.provider != LLMProvider.ANTHROPIC:
            raise ValueError(f"Expected Anthropic provider, got {config.provider}")

        client = self._get_client(config)

        # Prepare messages
        messages = [{"role": "user", "content": prompt}]

        # Prepare request parameters
        request_params = {
            "model": config.model,
            "messages": messages,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens or 4000,
        }

        # Add system message if provided
        if system_message:
            request_params["system"] = system_message

        # Add additional parameters
        if config.additional_params:
            request_params.update(config.additional_params)

        try:
            logger.debug(f"Making Anthropic request with model: {config.model}")
            response = await client.messages.create(**request_params)

            # Extract content from response
            content = ""
            for content_block in response.content:
                if content_block.type == "text":
                    content += content_block.text

            return content

        except Exception as e:
            # If Anthropic requires streaming for long requests, transparently retry with streaming
            if "Streaming is required" in str(e):
                logger.info(
                    "Anthropic response requires streaming, retrying with stream"
                )
                try:
                    accumulated = []
                    async with client.messages.stream(**request_params) as stream:
                        async for event in stream:
                            if event.type == "content_block_delta":
                                delta = getattr(event, "delta", None)
                                if (
                                    delta
                                    and getattr(delta, "type", None) == "text_delta"
                                ):
                                    accumulated.append(delta.text)
                    return "".join(accumulated)
                except Exception as se:
                    logger.error(f"Anthropic streaming fallback failed: {str(se)}")
                    raise
            logger.error(f"Anthropic content generation error: {str(e)}")
            raise

    async def generate_content_detailed(
        self, prompt: str, config: ProviderConfig, system_message: Optional[str] = None
    ) -> LLMResponse:
        """Generate content with detailed response."""
        if config.provider != LLMProvider.ANTHROPIC:
            raise ValueError(f"Expected Anthropic provider, got {config.provider}")

        client = self._get_client(config)

        # Prepare messages
        messages = [{"role": "user", "content": prompt}]

        # Prepare request parameters
        request_params = {
            "model": config.model,
            "messages": messages,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens or 4000,
        }

        # Add system message if provided
        if system_message:
            request_params["system"] = system_message

        # Add additional parameters
        if config.additional_params:
            request_params.update(config.additional_params)

        try:
            response = await client.messages.create(**request_params)

            # Extract content from response
            content = ""
            for content_block in response.content:
                if content_block.type == "text":
                    content += content_block.text

            return LLMResponse(
                content=content,
                usage={
                    "prompt_tokens": (
                        response.usage.input_tokens if response.usage else 0
                    ),
                    "completion_tokens": (
                        response.usage.output_tokens if response.usage else 0
                    ),
                    "total_tokens": (
                        (response.usage.input_tokens + response.usage.output_tokens)
                        if response.usage
                        else 0
                    ),
                },
                model=response.model,
                finish_reason=response.stop_reason or "",
                metadata={
                    "response_id": response.id,
                    "stop_sequence": response.stop_sequence,
                },
            )

        except Exception as e:
            # Retry with streaming if required by Anthropic
            if "Streaming is required" in str(e):
                logger.info(
                    "Anthropic response requires streaming, retrying with stream"
                )
                try:
                    accumulated = []
                    async with client.messages.stream(**request_params) as stream:
                        async for event in stream:
                            if event.type == "content_block_delta":
                                delta = getattr(event, "delta", None)
                                if (
                                    delta
                                    and getattr(delta, "type", None) == "text_delta"
                                ):
                                    accumulated.append(delta.text)
                        # Try to fetch final message for usage metrics
                        try:
                            final_msg = await stream.get_final_message()
                            usage = {
                                "prompt_tokens": (
                                    final_msg.usage.input_tokens
                                    if getattr(final_msg, "usage", None)
                                    else 0
                                ),
                                "completion_tokens": (
                                    final_msg.usage.output_tokens
                                    if getattr(final_msg, "usage", None)
                                    else 0
                                ),
                                "total_tokens": (
                                    (
                                        final_msg.usage.input_tokens
                                        + final_msg.usage.output_tokens
                                    )
                                    if getattr(final_msg, "usage", None)
                                    else 0
                                ),
                            }
                            model = getattr(final_msg, "model", config.model)
                            finish_reason = getattr(final_msg, "stop_reason", "") or ""
                            return LLMResponse(
                                content="".join(accumulated),
                                usage=usage,
                                model=model,
                                finish_reason=finish_reason,
                            )
                        except Exception:
                            return LLMResponse(
                                content="".join(accumulated),
                                usage={
                                    "prompt_tokens": 0,
                                    "completion_tokens": 0,
                                    "total_tokens": 0,
                                },
                                model=config.model,
                                finish_reason="stream",
                            )
                except Exception as se:
                    logger.error(
                        f"Anthropic streaming fallback (detailed) failed: {str(se)}"
                    )
                    raise
            logger.error(f"Anthropic detailed generation error: {str(e)}")
            raise

    async def generate_content_stream(
        self, prompt: str, config: ProviderConfig, system_message: Optional[str] = None
    ) -> AsyncGenerator[LLMStreamChunk, None]:
        """Generate content with streaming response."""
        if config.provider != LLMProvider.ANTHROPIC:
            raise ValueError(f"Expected Anthropic provider, got {config.provider}")

        client = self._get_client(config)

        # Prepare messages
        messages = [{"role": "user", "content": prompt}]

        # Prepare request parameters
        request_params = {
            "model": config.model,
            "messages": messages,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens or 4000,
            "stream": True,
        }

        # Add system message if provided
        if system_message:
            request_params["system"] = system_message

        # Add additional parameters
        if config.additional_params:
            request_params.update(config.additional_params)

        try:
            async with client.messages.stream(**request_params) as stream:
                async for chunk in stream:
                    if chunk.type == "content_block_delta":
                        if chunk.delta.type == "text_delta":
                            yield LLMStreamChunk(
                                content=chunk.delta.text, is_final=False
                            )
                    elif chunk.type == "message_stop":
                        yield LLMStreamChunk(content="", is_final=True)

        except Exception as e:
            logger.error(f"Anthropic streaming error: {str(e)}")
            raise

    async def chat_completion(
        self, messages: List[Dict[str, str]], config: ProviderConfig
    ) -> LLMResponse:
        """Perform chat completion."""
        if config.provider != LLMProvider.ANTHROPIC:
            raise ValueError(f"Expected Anthropic provider, got {config.provider}")

        client = self._get_client(config)

        # Convert messages to Anthropic format
        anthropic_messages = []
        system_message = None

        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")

            if role == "system":
                system_message = content
            elif role in ["user", "assistant"]:
                anthropic_messages.append({"role": role, "content": content})

        # Prepare request parameters
        request_params = {
            "model": config.model,
            "messages": anthropic_messages,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens or 4000,
        }

        # Add system message if found
        if system_message:
            request_params["system"] = system_message

        # Add additional parameters
        if config.additional_params:
            request_params.update(config.additional_params)

        try:
            response = await client.messages.create(**request_params)

            # Extract content from response
            content = ""
            for content_block in response.content:
                if content_block.type == "text":
                    content += content_block.text

            return LLMResponse(
                content=content,
                usage={
                    "prompt_tokens": (
                        response.usage.input_tokens if response.usage else 0
                    ),
                    "completion_tokens": (
                        response.usage.output_tokens if response.usage else 0
                    ),
                    "total_tokens": (
                        (response.usage.input_tokens + response.usage.output_tokens)
                        if response.usage
                        else 0
                    ),
                },
                model=response.model,
                finish_reason=response.stop_reason or "",
            )

        except Exception as e:
            if "Streaming is required" in str(e):
                logger.info(
                    "Anthropic response requires streaming, retrying with stream"
                )
                try:
                    accumulated = []
                    async with client.messages.stream(**request_params) as stream:
                        async for event in stream:
                            if event.type == "content_block_delta":
                                delta = getattr(event, "delta", None)
                                if (
                                    delta
                                    and getattr(delta, "type", None) == "text_delta"
                                ):
                                    accumulated.append(delta.text)
                        try:
                            final_msg = await stream.get_final_message()
                            usage = {
                                "prompt_tokens": (
                                    final_msg.usage.input_tokens
                                    if getattr(final_msg, "usage", None)
                                    else 0
                                ),
                                "completion_tokens": (
                                    final_msg.usage.output_tokens
                                    if getattr(final_msg, "usage", None)
                                    else 0
                                ),
                                "total_tokens": (
                                    (
                                        final_msg.usage.input_tokens
                                        + final_msg.usage.output_tokens
                                    )
                                    if getattr(final_msg, "usage", None)
                                    else 0
                                ),
                            }
                            model = getattr(final_msg, "model", config.model)
                            finish_reason = getattr(final_msg, "stop_reason", "") or ""
                            return LLMResponse(
                                content="".join(accumulated),
                                usage=usage,
                                model=model,
                                finish_reason=finish_reason,
                            )
                        except Exception:
                            return LLMResponse(
                                content="".join(accumulated),
                                usage={
                                    "prompt_tokens": 0,
                                    "completion_tokens": 0,
                                    "total_tokens": 0,
                                },
                                model=config.model,
                                finish_reason="stream",
                            )
                except Exception as se:
                    logger.error(f"Anthropic chat streaming fallback failed: {str(se)}")
                    raise
            logger.error(f"Anthropic chat completion error: {str(e)}")
            raise

    async def validate_config(self, config: ProviderConfig) -> bool:
        """Validate Anthropic configuration."""
        try:
            if config.provider != LLMProvider.ANTHROPIC:
                return False

            api_key = config.api_key or self.api_key
            if not api_key:
                return False

            # Test with a simple request
            test_response = await self.generate_content("Test", config)
            return bool(test_response)

        except Exception as e:
            logger.debug(f"Anthropic config validation failed: {str(e)}")
            return False

    async def get_available_models(
        self, config: ProviderConfig
    ) -> List[Dict[str, Any]]:
        """Get available Anthropic models with token limits."""
        try:
            # For now, return the predefined list from config
            return config.get_available_models()
        except Exception:
            # Fallback to ProviderConfig source of truth
            return config.get_available_models()

    async def estimate_tokens(self, text: str, model: str) -> int:
        """
        Estimate token count for Anthropic models.

        Anthropic uses a different tokenization than OpenAI,
        but this provides a reasonable approximation.
        """
        # Anthropic models generally have similar token ratios to OpenAI
        # This is an approximation - for exact counts, you'd need the Anthropic tokenizer
        words = text.split()
        # Anthropic models tend to have slightly higher token counts
        return int(len(words) * 1.4)

    async def check_health(self, config: ProviderConfig) -> Dict[str, Any]:
        """Check provider health and connectivity."""
        try:
            # Test with a minimal request
            import time

            start_time = time.time()
            test_response = await self.generate_content(
                "Hello", config, system_message="Respond with just 'Hi'"
            )
            response_time = time.time() - start_time

            return {
                "status": "healthy",
                "provider": "anthropic",
                "model": config.model,
                "response_time_ms": response_time * 1000,
                "test_response_length": len(test_response),
                "message": "Provider is responding normally",
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": "anthropic",
                "model": config.model,
                "error": str(e),
                "message": "Provider health check failed",
            }
