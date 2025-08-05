"""Google Gemini service adapter."""

import logging
import time
from typing import Dict, List, Optional, Any, AsyncGenerator
import google.generativeai as genai
from google.generativeai.types import GenerateContentResponse

from ...application.interfaces.llm_provider_interface import (
    LLMProviderInterface,
    LLMResponse,
    LLMStreamChunk
)
from ...domain.value_objects.provider_config import ProviderConfig, LLMProvider

logger = logging.getLogger(__name__)


class GeminiAdapter(LLMProviderInterface):
    """
    Google Gemini service adapter implementing LLMProviderInterface.

    This adapter handles all interactions with Google's Gemini API,
    providing a clean interface for the application layer.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self._model_cache: Dict[str, Any] = {}

    def _get_model(self, config: ProviderConfig):
        """Get or create Gemini model."""
        api_key = config.api_key or self.api_key
        if not api_key:
            raise ValueError("Gemini API key is required")

        # Configure the API key
        genai.configure(api_key=api_key)

        # Cache models to avoid recreation
        cache_key = f"{config.model}_{api_key[:8]}"
        if cache_key not in self._model_cache:
            generation_config = {
                "temperature": config.temperature,
                "top_p": config.top_p,
                "max_output_tokens": config.max_tokens or 8192,
            }
            
            self._model_cache[cache_key] = genai.GenerativeModel(
                model_name=config.model,
                generation_config=generation_config
            )
            logger.debug(f"Created new Gemini model: {config.model}")

        return self._model_cache[cache_key]

    async def generate_content(
        self,
        prompt: str,
        config: ProviderConfig,
        system_message: Optional[str] = None
    ) -> str:
        """Generate content using Gemini."""
        if config.provider != LLMProvider.GEMINI:
            raise ValueError(f"Expected Gemini provider, got {config.provider}")

        try:
            model = self._get_model(config)

            # Prepare the full prompt
            full_prompt = prompt
            if system_message:
                full_prompt = f"{system_message}\n\n{prompt}"

            logger.debug(f"Making Gemini request with model: {config.model}")
            
            # Generate content
            response = model.generate_content(full_prompt)
            
            if not response.text:
                raise ValueError("Gemini returned empty response")

            return response.text

        except Exception as e:
            logger.error(f"Gemini content generation error: {str(e)}")
            raise

    async def generate_content_detailed(
        self,
        prompt: str,
        config: ProviderConfig,
        system_message: Optional[str] = None
    ) -> LLMResponse:
        """Generate content with detailed response."""
        if config.provider != LLMProvider.GEMINI:
            raise ValueError(f"Expected Gemini provider, got {config.provider}")

        try:
            model = self._get_model(config)

            # Prepare the full prompt
            full_prompt = prompt
            if system_message:
                full_prompt = f"{system_message}\n\n{prompt}"

            logger.debug(f"Making detailed Gemini request with model: {config.model}")
            
            start_time = time.time()
            response = model.generate_content(full_prompt)
            end_time = time.time()

            if not response.text:
                raise ValueError("Gemini returned empty response")

            # Extract usage information
            usage = {}
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                usage = {
                    "prompt_tokens": getattr(response.usage_metadata, 'prompt_token_count', 0),
                    "completion_tokens": getattr(response.usage_metadata, 'candidates_token_count', 0),
                    "total_tokens": getattr(response.usage_metadata, 'total_token_count', 0)
                }

            return LLMResponse(
                content=response.text,
                usage=usage,
                model=config.model,
                finish_reason=getattr(response.candidates[0], 'finish_reason', 'stop') if response.candidates else 'stop',
                metadata={
                    "response_time": end_time - start_time,
                    "provider": "gemini",
                    "safety_ratings": getattr(response.candidates[0], 'safety_ratings', []) if response.candidates else []
                }
            )

        except Exception as e:
            logger.error(f"Gemini detailed content generation error: {str(e)}")
            raise

    async def generate_content_stream(
        self,
        prompt: str,
        config: ProviderConfig,
        system_message: Optional[str] = None
    ) -> AsyncGenerator[LLMStreamChunk, None]:
        """Generate content with streaming response."""
        if config.provider != LLMProvider.GEMINI:
            raise ValueError(f"Expected Gemini provider, got {config.provider}")

        try:
            model = self._get_model(config)

            # Prepare the full prompt
            full_prompt = prompt
            if system_message:
                full_prompt = f"{system_message}\n\n{prompt}"

            logger.debug(f"Making streaming Gemini request with model: {config.model}")
            
            # Generate content with streaming
            response = model.generate_content(full_prompt, stream=True)
            
            for chunk in response:
                if chunk.text:
                    yield LLMStreamChunk(
                        content=chunk.text,
                        is_final=False,
                        metadata={"provider": "gemini"}
                    )
            
            # Final chunk
            yield LLMStreamChunk(
                content="",
                is_final=True,
                metadata={"provider": "gemini"}
            )

        except Exception as e:
            logger.error(f"Gemini streaming error: {str(e)}")
            raise

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        config: ProviderConfig
    ) -> LLMResponse:
        """Perform chat completion with message history."""
        if config.provider != LLMProvider.GEMINI:
            raise ValueError(f"Expected Gemini provider, got {config.provider}")

        try:
            model = self._get_model(config)

            # Convert messages to Gemini format
            chat_history = []
            system_message = None
            
            for message in messages:
                role = message.get("role", "user")
                content = message.get("content", "")
                
                if role == "system":
                    system_message = content
                elif role == "user":
                    chat_history.append({"role": "user", "parts": [content]})
                elif role == "assistant":
                    chat_history.append({"role": "model", "parts": [content]})

            # Start chat session
            chat = model.start_chat(history=chat_history[:-1] if chat_history else [])
            
            # Get the last user message
            last_message = chat_history[-1]["parts"][0] if chat_history else ""
            if system_message:
                last_message = f"{system_message}\n\n{last_message}"

            logger.debug(f"Making Gemini chat completion with model: {config.model}")
            
            start_time = time.time()
            response = chat.send_message(last_message)
            end_time = time.time()

            if not response.text:
                raise ValueError("Gemini returned empty response")

            # Extract usage information
            usage = {}
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                usage = {
                    "prompt_tokens": getattr(response.usage_metadata, 'prompt_token_count', 0),
                    "completion_tokens": getattr(response.usage_metadata, 'candidates_token_count', 0),
                    "total_tokens": getattr(response.usage_metadata, 'total_token_count', 0)
                }

            return LLMResponse(
                content=response.text,
                usage=usage,
                model=config.model,
                finish_reason=getattr(response.candidates[0], 'finish_reason', 'stop') if response.candidates else 'stop',
                metadata={
                    "response_time": end_time - start_time,
                    "provider": "gemini",
                    "safety_ratings": getattr(response.candidates[0], 'safety_ratings', []) if response.candidates else []
                }
            )

        except Exception as e:
            logger.error(f"Gemini chat completion error: {str(e)}")
            raise

    async def validate_config(self, config: ProviderConfig) -> bool:
        """Validate Gemini configuration."""
        try:
            if config.provider != LLMProvider.GEMINI:
                return False

            api_key = config.api_key or self.api_key
            if not api_key:
                return False

            # Test API connection
            genai.configure(api_key=api_key)
            models = genai.list_models()
            available_models = [model.name for model in models]
            
            # Check if the specified model is available
            model_name = config.model
            if not model_name.startswith('models/'):
                model_name = f'models/{model_name}'
                
            return model_name in available_models

        except Exception as e:
            logger.warning(f"Gemini config validation failed: {str(e)}")
            return False

    async def get_available_models(self, config: ProviderConfig) -> List[str]:
        """Get available Gemini models."""
        try:
            api_key = config.api_key or self.api_key
            if not api_key:
                raise ValueError("Gemini API key is required")

            genai.configure(api_key=api_key)
            models = genai.list_models()
            
            # Filter for text generation models
            text_models = []
            for model in models:
                if 'generateContent' in model.supported_generation_methods:
                    # Remove 'models/' prefix for cleaner names
                    model_name = model.name.replace('models/', '')
                    text_models.append(model_name)
            
            return text_models

        except Exception as e:
            logger.warning(f"Failed to fetch Gemini models: {str(e)}")
            # Return default models including latest Gemini 2.5 series
            return [
                "gemini-2.5-pro",
                "gemini-2.5-flash",
                "gemini-2.5-flash-lite",
                "gemini-2.5-flash-live",
                "gemini-1.5-pro",
                "gemini-1.5-flash",
                "gemini-pro"
            ]

    async def estimate_tokens(self, text: str, model: str) -> int:
        """Estimate token count for given text."""
        try:
            # Gemini doesn't have a direct token counting API
            # Use a rough estimation: ~4 characters per token
            return len(text) // 4
        except Exception as e:
            logger.warning(f"Token estimation failed: {str(e)}")
            return len(text) // 4

    async def check_health(self, config: ProviderConfig) -> Dict[str, Any]:
        """Check Gemini health and connectivity."""
        try:
            api_key = config.api_key or self.api_key
            if not api_key:
                return {
                    "status": "unhealthy",
                    "error": "API key not configured",
                    "provider": "gemini"
                }

            genai.configure(api_key=api_key)
            
            # Test with a simple request
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content("Hello")
            
            return {
                "status": "healthy",
                "provider": "gemini",
                "model": config.model,
                "response_received": bool(response.text)
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "provider": "gemini"
            }
