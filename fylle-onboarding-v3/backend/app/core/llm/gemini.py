"""
Google Gemini Provider Implementation for Fylle Onboarding v3
Supports both API Key and Vertex AI authentication.
"""

import json
from typing import Any, Dict, List, Optional

from .base import (
    BaseLLMProvider,
    LLMConfig,
    LLMMessage,
    LLMProvider,
    LLMResponse,
    LLMUsage,
    calculate_cost,
)


class GeminiProvider(BaseLLMProvider):
    """Google Gemini LLM provider implementation."""
    
    provider = LLMProvider.GEMINI
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        use_vertex: bool = False,
        project_id: Optional[str] = None,
        location: str = "us-central1",
    ):
        self.use_vertex = use_vertex
        self.project_id = project_id
        self.location = location
        
        if use_vertex:
            # Use Vertex AI
            import vertexai
            from vertexai.generative_models import GenerativeModel
            
            vertexai.init(project=project_id, location=location)
            self._vertex_model_class = GenerativeModel
        else:
            # Use API Key
            import google.generativeai as genai
            
            genai.configure(api_key=api_key)
            self._genai = genai
    
    async def generate(
        self,
        messages: List[LLMMessage],
        config: LLMConfig,
    ) -> LLMResponse:
        """Generate a response using Google Gemini."""
        
        if self.use_vertex:
            return await self._generate_vertex(messages, config)
        else:
            return await self._generate_api_key(messages, config)
    
    async def _generate_api_key(
        self,
        messages: List[LLMMessage],
        config: LLMConfig,
    ) -> LLMResponse:
        """Generate using API Key method."""
        
        model = self._genai.GenerativeModel(config.model)
        
        # Convert messages to Gemini format
        # Gemini expects alternating user/model messages
        gemini_contents = []
        system_content = None
        
        for m in messages:
            if m.role == "system":
                system_content = m.content
            elif m.role == "user":
                gemini_contents.append({"role": "user", "parts": [m.content]})
            elif m.role == "assistant":
                gemini_contents.append({"role": "model", "parts": [m.content]})
        
        # Prepend system content to first user message if exists
        if system_content and gemini_contents:
            first_user = gemini_contents[0]
            first_user["parts"][0] = f"{system_content}\n\n{first_user['parts'][0]}"
        
        generation_config = {
            "temperature": config.temperature,
            "max_output_tokens": config.max_tokens,
            "top_p": config.top_p,
        }
        
        if config.stop:
            generation_config["stop_sequences"] = config.stop
        
        response = model.generate_content(
            gemini_contents,
            generation_config=generation_config,
        )
        
        # Extract usage metadata
        usage = LLMUsage(
            prompt_tokens=response.usage_metadata.prompt_token_count if response.usage_metadata else 0,
            completion_tokens=response.usage_metadata.candidates_token_count if response.usage_metadata else 0,
            total_tokens=response.usage_metadata.total_token_count if response.usage_metadata else 0,
        )
        
        return LLMResponse(
            content=response.text,
            usage=usage,
            model=config.model,
            provider=self.provider.value,
            finish_reason="stop",
        )
    
    async def _generate_vertex(
        self,
        messages: List[LLMMessage],
        config: LLMConfig,
    ) -> LLMResponse:
        """Generate using Vertex AI."""
        
        model = self._vertex_model_class(config.model)
        
        # Convert messages
        contents = []
        system_instruction = None
        
        for m in messages:
            if m.role == "system":
                system_instruction = m.content
            elif m.role == "user":
                contents.append({"role": "user", "parts": [{"text": m.content}]})
            elif m.role == "assistant":
                contents.append({"role": "model", "parts": [{"text": m.content}]})
        
        generation_config = {
            "temperature": config.temperature,
            "max_output_tokens": config.max_tokens,
            "top_p": config.top_p,
        }
        
        if system_instruction:
            model = self._vertex_model_class(
                config.model,
                system_instruction=system_instruction,
            )
        
        response = await model.generate_content_async(
            contents,
            generation_config=generation_config,
        )
        
        usage = LLMUsage(
            prompt_tokens=response.usage_metadata.prompt_token_count if response.usage_metadata else 0,
            completion_tokens=response.usage_metadata.candidates_token_count if response.usage_metadata else 0,
            total_tokens=response.usage_metadata.total_token_count if response.usage_metadata else 0,
        )
        
        return LLMResponse(
            content=response.text,
            usage=usage,
            model=config.model,
            provider=self.provider.value,
            finish_reason="stop",
        )
    
    async def generate_json(
        self,
        messages: List[LLMMessage],
        config: LLMConfig,
        schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate a JSON response using Gemini."""
        
        # Add JSON instruction
        json_messages = list(messages)
        for i, m in enumerate(json_messages):
            if m.role == "system":
                json_messages[i] = LLMMessage(
                    role="system",
                    content=m.content + "\n\nRespond with valid JSON only. No markdown formatting.",
                )
                break
        else:
            json_messages.insert(0, LLMMessage(
                role="system",
                content="Respond with valid JSON only. No markdown formatting.",
            ))
        
        response = await self.generate(json_messages, config)
        
        # Clean response
        content = response.content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1])
        
        return json.loads(content)
    
    def _get_default_model(self) -> str:
        return "gemini-1.5-pro"
    
    def _estimate_cost(self, usage: LLMUsage, model: str) -> float:
        return calculate_cost(self.provider, model, usage)
