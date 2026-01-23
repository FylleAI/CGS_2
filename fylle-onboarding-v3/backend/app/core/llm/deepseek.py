"""
DeepSeek Provider Implementation for Fylle Onboarding v3
DeepSeek uses OpenAI-compatible API.
"""

import json
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI

from .base import (
    BaseLLMProvider,
    LLMConfig,
    LLMMessage,
    LLMProvider,
    LLMResponse,
    LLMUsage,
    calculate_cost,
)


class DeepSeekProvider(BaseLLMProvider):
    """DeepSeek LLM provider implementation (OpenAI-compatible)."""
    
    provider = LLMProvider.DEEPSEEK
    DEFAULT_BASE_URL = "https://api.deepseek.com/v1"
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url or self.DEFAULT_BASE_URL,
        )
    
    async def generate(
        self,
        messages: List[LLMMessage],
        config: LLMConfig,
    ) -> LLMResponse:
        """Generate a response using DeepSeek."""
        
        openai_messages = [
            {"role": m.role, "content": m.content}
            for m in messages
        ]
        
        kwargs = {
            "model": config.model,
            "messages": openai_messages,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "top_p": config.top_p,
        }
        
        if config.stop:
            kwargs["stop"] = config.stop
        
        response = await self.client.chat.completions.create(**kwargs)
        
        usage = LLMUsage(
            prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
            completion_tokens=response.usage.completion_tokens if response.usage else 0,
            total_tokens=response.usage.total_tokens if response.usage else 0,
        )
        
        return LLMResponse(
            content=response.choices[0].message.content or "",
            usage=usage,
            model=config.model,
            provider=self.provider.value,
            finish_reason=response.choices[0].finish_reason,
            raw_response=response.model_dump(),
        )
    
    async def generate_json(
        self,
        messages: List[LLMMessage],
        config: LLMConfig,
        schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate a JSON response using DeepSeek."""
        
        json_messages = list(messages)
        if json_messages and json_messages[0].role == "system":
            json_messages[0] = LLMMessage(
                role="system",
                content=json_messages[0].content + "\n\nRespond with valid JSON only. No additional text or markdown.",
            )
        else:
            json_messages.insert(0, LLMMessage(
                role="system",
                content="Respond with valid JSON only. No additional text or markdown.",
            ))
        
        response = await self.generate(json_messages, config)
        
        # Clean response
        content = response.content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1])
        
        return json.loads(content)
    
    def _get_default_model(self) -> str:
        return "deepseek-chat"
    
    def _estimate_cost(self, usage: LLMUsage, model: str) -> float:
        return calculate_cost(self.provider, model, usage)
