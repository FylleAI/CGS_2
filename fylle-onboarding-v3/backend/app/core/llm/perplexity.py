"""
Perplexity Provider Implementation for Fylle Onboarding v3
Perplexity uses OpenAI-compatible API and is specialized for research.
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


class PerplexityProvider(BaseLLMProvider):
    """Perplexity LLM provider implementation (OpenAI-compatible)."""
    
    provider = LLMProvider.PERPLEXITY
    DEFAULT_BASE_URL = "https://api.perplexity.ai"
    
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=self.DEFAULT_BASE_URL,
        )
    
    async def generate(
        self,
        messages: List[LLMMessage],
        config: LLMConfig,
    ) -> LLMResponse:
        """Generate a response using Perplexity."""
        
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
        """Generate a JSON response using Perplexity."""
        
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
        return "sonar-pro"
    
    def _estimate_cost(self, usage: LLMUsage, model: str) -> float:
        return calculate_cost(self.provider, model, usage)
    
    async def research(
        self,
        query: str,
        config: Optional[LLMConfig] = None,
    ) -> LLMResponse:
        """
        Perform a research query using Perplexity's search capabilities.
        This is a convenience method that wraps generate with research-optimized settings.
        """
        if config is None:
            config = LLMConfig(
                provider=self.provider,
                model=self._get_default_model(),
                temperature=0.2,  # Lower temp for factual research
                max_tokens=4096,
            )
        
        messages = [
            LLMMessage(
                role="system",
                content="You are a research assistant. Provide accurate, well-sourced information. Include relevant sources and citations when available.",
            ),
            LLMMessage(role="user", content=query),
        ]
        
        return await self.generate(messages, config)
