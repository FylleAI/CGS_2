"""Google Gemini service adapter."""

import logging
import os

import time
from typing import Dict, List, Optional, Any, AsyncGenerator
import httpx
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

    def __init__(
        self,
        api_key: Optional[str] = None,
        project_id: Optional[str] = None,
        location: str = "global",
        use_vertex: bool = True,
        endpoint: str = "aiplatform.googleapis.com",
        api_version: str = "v1",
        sa_credentials_path: Optional[str] = None,
    ):
        self.api_key = api_key
        self.project_id = project_id
        self.location = location or "global"
        self.use_vertex = use_vertex
        self.endpoint = endpoint or "aiplatform.googleapis.com"
        self.api_version = api_version or "v1"
        # Optional path to Service Account JSON provided via settings
        self.sa_credentials_path = sa_credentials_path
        self._model_cache: Dict[str, Any] = {}

    def _get_model(self, config: ProviderConfig):
        """Get or create Gemini model (AI Studio SDK fallback)."""
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
                generation_config=generation_config,
            )
            logger.debug(f"Created new Gemini model (AI Studio): {config.model}")
        return self._model_cache[cache_key]

    def _vertex_endpoint_url(self, model: str, stream: bool = False) -> str:
        api = "streamGenerateContent" if stream else "generateContent"
        # Prefer project/locations path when project_id is available
        if self.project_id:
            return (
                f"https://{self.endpoint}/{self.api_version}/projects/{self.project_id}/"
                f"locations/{self.location}/publishers/google/models/{model}:{api}"
            )
        # Fallback to publisher-only path supported by API key quickstart
        return f"https://{self.endpoint}/{self.api_version}/publishers/google/models/{model}:{api}"

    def _get_sa_bearer_token(self) -> Optional[str]:
        """Return OAuth2 Bearer token from Service Account.
        Checks GOOGLE_APPLICATION_CREDENTIALS env var first, then adapter-provided path.
        Lazily imports google-auth to avoid hard dependency when not using SA.
        """
        try:
            path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or self.sa_credentials_path
            if not path:
                return None
            # Lazy import to avoid ImportError at startup if dependency not installed
            from google.oauth2 import service_account  # type: ignore
            from google.auth.transport.requests import Request  # type: ignore

            creds = service_account.Credentials.from_service_account_file(
                path, scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            creds.refresh(Request())
            return creds.token
        except Exception as e:
            logger.warning(f"Service Account auth not available: {e}")
            return None

    async def _vertex_call(self, model: str, body: Dict[str, Any], stream: bool = False) -> Any:
        url = self._vertex_endpoint_url(model, stream=stream)
        timeout = httpx.Timeout(60.0)

        headers: Optional[Dict[str, str]] = None
        params: Optional[Dict[str, str]] = None

        # Prefer Service Account bearer token when available
        token = self._get_sa_bearer_token()
        if token:
            headers = {"Authorization": f"Bearer {token}"}
        else:
            # Fallback to API key authentication
            if not self.api_key:
                raise ValueError(
                    "Gemini (Vertex) requires Service Account (GOOGLE_APPLICATION_CREDENTIALS) or an API key"
                )
            params = {"key": self.api_key}

        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, json=body, headers=headers, params=params)
        resp.raise_for_status()
        return resp.json()

    def _build_contents_from_text(self, text: str) -> List[Dict[str, Any]]:
        return [{"role": "user", "parts": [{"text": text}]}]

    def _build_system_instruction(self, system_message: Optional[str]) -> Optional[Dict[str, Any]]:
        if not system_message:
            return None
        return {"role": "system", "parts": [{"text": system_message}]}

    def _extract_text_from_vertex_response(self, data: Dict[str, Any]) -> str:
        # Vertex response: candidates[0].content.parts[].text
        try:
            candidates = data.get("candidates", [])
            if not candidates:
                return ""
            parts = candidates[0].get("content", {}).get("parts", [])
            texts = [p.get("text", "") for p in parts if p.get("text")]
            return "".join(texts)
        except Exception:
            return ""

    def _extract_usage_from_vertex_response(self, data: Dict[str, Any]) -> Dict[str, int]:
        usage = {}
        meta = data.get("usageMetadata") or data.get("usage_metadata") or {}
        if isinstance(meta, dict):
            usage = {
                "prompt_tokens": int(meta.get("promptTokenCount", meta.get("prompt_token_count", 0) or 0)),
                "completion_tokens": int(meta.get("candidatesTokenCount", meta.get("candidates_token_count", 0) or 0)),
                "total_tokens": int(meta.get("totalTokenCount", meta.get("total_token_count", 0) or 0)),
            }
        return usage

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
            if self.use_vertex:
                contents = self._build_contents_from_text(prompt)
                sys_inst = self._build_system_instruction(system_message)
                body: Dict[str, Any] = {
                    "contents": contents,
                    "generation_config": {
                        "temperature": config.temperature,
                        "top_p": config.top_p,
                        "max_output_tokens": config.max_tokens or 8192,
                    },
                }
                if sys_inst:
                    body["system_instruction"] = sys_inst
                data = await self._vertex_call(config.model, body)
                text = self._extract_text_from_vertex_response(data)
                if not text:
                    raise ValueError("Vertex Gemini returned empty response")
                return text

            # Fallback to Google AI Studio SDK
            model = self._get_model(config)
            full_prompt = f"{system_message}\n\n{prompt}" if system_message else prompt
            logger.debug(f"Making Gemini request with model: {config.model}")
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
            start_time = time.time()
            if self.use_vertex:
                contents = self._build_contents_from_text(prompt)
                sys_inst = self._build_system_instruction(system_message)
                body: Dict[str, Any] = {
                    "contents": contents,
                    "generation_config": {
                        "temperature": config.temperature,
                        "top_p": config.top_p,
                        "max_output_tokens": config.max_tokens or 8192,
                    },
                }
                if sys_inst:
                    body["system_instruction"] = sys_inst
                data = await self._vertex_call(config.model, body)
                end_time = time.time()
                text = self._extract_text_from_vertex_response(data)
                if not text:
                    raise ValueError("Vertex Gemini returned empty response")
                usage = self._extract_usage_from_vertex_response(data)
                candidates = data.get("candidates", [])
                finish_reason = (candidates[0].get("finishReason") if candidates else "stop") or "stop"
                safety = (candidates[0].get("safetyRatings") if candidates else []) or []
                return LLMResponse(
                    content=text,
                    usage=usage,
                    model=config.model,
                    finish_reason=finish_reason,
                    metadata={
                        "response_time": end_time - start_time,
                        "provider": "gemini",
                        "safety_ratings": safety,
                    },
                )

            # Fallback to Google AI Studio SDK
            model = self._get_model(config)
            full_prompt = f"{system_message}\n\n{prompt}" if system_message else prompt
            logger.debug(f"Making detailed Gemini request with model: {config.model}")
            response = model.generate_content(full_prompt)
            end_time = time.time()
            if not response.text:
                raise ValueError("Gemini returned empty response")
            usage = {}
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                usage = {
                    "prompt_tokens": getattr(response.usage_metadata, 'prompt_token_count', 0),
                    "completion_tokens": getattr(response.usage_metadata, 'candidates_token_count', 0),
                    "total_tokens": getattr(response.usage_metadata, 'total_token_count', 0),
                }
            return LLMResponse(
                content=response.text,
                usage=usage,
                model=config.model,
                finish_reason=(getattr(response.candidates[0], 'finish_reason', 'stop') if response.candidates else 'stop'),
                metadata={
                    "response_time": end_time - start_time,
                    "provider": "gemini",
                    "safety_ratings": getattr(response.candidates[0], 'safety_ratings', []) if response.candidates else [],
                },
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
            if self.use_vertex:
                # Non-stream fallback for Vertex for now
                contents = self._build_contents_from_text(prompt)
                sys_inst = self._build_system_instruction(system_message)
                body: Dict[str, Any] = {
                    "contents": contents,
                    "generation_config": {
                        "temperature": config.temperature,
                        "top_p": config.top_p,
                        "max_output_tokens": config.max_tokens or 8192,
                    },
                }
                if sys_inst:
                    body["system_instruction"] = sys_inst
                data = await self._vertex_call(config.model, body)
                text = self._extract_text_from_vertex_response(data)
                if text:
                    yield LLMStreamChunk(content=text, is_final=False, metadata={"provider": "gemini"})
                yield LLMStreamChunk(content="", is_final=True, metadata={"provider": "gemini"})
                return

            # Fallback to Google AI Studio streaming
            model = self._get_model(config)
            full_prompt = f"{system_message}\n\n{prompt}" if system_message else prompt
            logger.debug(f"Making streaming Gemini request with model: {config.model}")
            response = model.generate_content(full_prompt, stream=True)
            for chunk in response:
                if chunk.text:
                    yield LLMStreamChunk(content=chunk.text, is_final=False, metadata={"provider": "gemini"})
            yield LLMStreamChunk(content="", is_final=True, metadata={"provider": "gemini"})

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
            # Convert messages
            contents: List[Dict[str, Any]] = []
            system_message: Optional[str] = None
            for m in messages:
                role = m.get("role", "user")
                text = m.get("content", "")
                if role == "system":
                    system_message = text
                elif role == "user":
                    contents.append({"role": "user", "parts": [{"text": text}]})
                elif role == "assistant":
                    contents.append({"role": "model", "parts": [{"text": text}]})

            start_time = time.time()
            if self.use_vertex:
                body: Dict[str, Any] = {
                    "contents": contents or self._build_contents_from_text(""),
                    "generation_config": {
                        "temperature": config.temperature,
                        "top_p": config.top_p,
                        "max_output_tokens": config.max_tokens or 8192,
                    },
                }
                sys_inst = self._build_system_instruction(system_message)
                if sys_inst:
                    body["system_instruction"] = sys_inst
                data = await self._vertex_call(config.model, body)
                end_time = time.time()
                text = self._extract_text_from_vertex_response(data)
                if not text:
                    raise ValueError("Vertex Gemini returned empty response")
                usage = self._extract_usage_from_vertex_response(data)
                candidates = data.get("candidates", [])
                finish_reason = (candidates[0].get("finishReason") if candidates else "stop") or "stop"
                safety = (candidates[0].get("safetyRatings") if candidates else []) or []
                return LLMResponse(
                    content=text,
                    usage=usage,
                    model=config.model,
                    finish_reason=finish_reason,
                    metadata={
                        "response_time": end_time - start_time,
                        "provider": "gemini",
                        "safety_ratings": safety,
                    },
                )

            # Fallback to Google AI Studio chat
            model = self._get_model(config)
            chat_history = [c for c in contents]
            chat = model.start_chat(history=chat_history[:-1] if chat_history else [])
            last_message = chat_history[-1]["parts"][0]["text"] if chat_history else ""
            if system_message:
                last_message = f"{system_message}\n\n{last_message}"
            response = chat.send_message(last_message)
            end_time = time.time()
            if not response.text:
                raise ValueError("Gemini returned empty response")
            usage = {}
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                usage = {
                    "prompt_tokens": getattr(response.usage_metadata, 'prompt_token_count', 0),
                    "completion_tokens": getattr(response.usage_metadata, 'candidates_token_count', 0),
                    "total_tokens": getattr(response.usage_metadata, 'total_token_count', 0),
                }
            return LLMResponse(
                content=response.text,
                usage=usage,
                model=config.model,
                finish_reason=(getattr(response.candidates[0], 'finish_reason', 'stop') if response.candidates else 'stop'),
                metadata={
                    "response_time": end_time - start_time,
                    "provider": "gemini",
                    "safety_ratings": getattr(response.candidates[0], 'safety_ratings', []) if response.candidates else [],
                },
            )

        except Exception as e:
            logger.error(f"Gemini chat completion error: {str(e)}")
            raise

    async def validate_config(self, config: ProviderConfig) -> bool:
        """Validate Gemini configuration."""
        try:
            if config.provider != LLMProvider.GEMINI:
                return False

            if self.use_vertex:
                # Prefer Service Account; fallback to API key
                sa_token = self._get_sa_bearer_token()
                if not sa_token and not (config.api_key or self.api_key):
                    return False
                # Minimal ping using generateContent
                body = {
                    "contents": self._build_contents_from_text("ping"),
                    "generation_config": {"temperature": 0, "max_output_tokens": 8},
                }
                try:
                    _ = await self._vertex_call(config.model, body)
                    return True
                except Exception as ve:
                    logger.warning(f"Vertex Gemini validation failed: {ve}")
                    return False

            # For AI Studio fallback, require API key
            api_key = config.api_key or self.api_key
            if not api_key:
                return False

            # Fallback: AI Studio SDK validation
            genai.configure(api_key=api_key)
            models = genai.list_models()
            available_models = [model.name for model in models]
            model_name = config.model
            if not model_name.startswith('models/'):
                model_name = f'models/{model_name}'
            return model_name in available_models

        except Exception as e:
            logger.warning(f"Gemini config validation failed: {str(e)}")
            return False

    async def get_available_models(self, config: ProviderConfig) -> List[Dict[str, Any]]:
        """Get available Gemini models with token limits."""
        try:
            api_key = config.api_key or self.api_key
            if not api_key:
                raise ValueError("Gemini API key is required")

            genai.configure(api_key=api_key)
            models = genai.list_models()

            text_models: List[Dict[str, Any]] = []
            config_models = {m["name"]: m for m in config.get_available_models()}
            for model in models:
                if 'generateContent' in model.supported_generation_methods:
                    model_name = model.name.replace('models/', '')
                    info = config_models.get(model_name)
                    if info:
                        text_models.append(info)

            return text_models or config.get_available_models()

        except Exception as e:
            logger.warning(f"Failed to fetch Gemini models: {str(e)}")
            # Return default models including latest Gemini 2.5 series
            return config.get_available_models()

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
            if self.use_vertex:
                # Prefer Service Account; fallback to API key if SA is not available
                sa_token = self._get_sa_bearer_token()
                if not sa_token:
                    api_key = config.api_key or self.api_key
                    if not api_key:
                        return {"status": "unhealthy", "error": "No SA or API key configured", "provider": "gemini"}

                body = {"contents": self._build_contents_from_text("Hello"), "generation_config": {"temperature": 0, "max_output_tokens": 8}}
                data = await self._vertex_call(config.model, body)
                text = self._extract_text_from_vertex_response(data)
                return {"status": "healthy", "provider": "gemini", "model": config.model, "response_received": bool(text)}

            # Fallback to AI Studio requires an API key
            api_key = config.api_key or self.api_key
            if not api_key:
                return {"status": "unhealthy", "error": "API key not configured", "provider": "gemini"}

            # Fallback to AI Studio
            genai.configure(api_key=api_key)
            response = genai.GenerativeModel(config.model if config.model else 'gemini-pro').generate_content("Hello")
            return {"status": "healthy", "provider": "gemini", "model": config.model, "response_received": bool(response.text)}

        except Exception as e:
            return {"status": "unhealthy", "error": str(e), "provider": "gemini"}
