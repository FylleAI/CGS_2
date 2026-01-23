"""
Anthropic (Claude) Provider Implementation for Fylle Onboarding v3
"""

import json
from typing import Any, Dict, List, Optional

from anthropic import AsyncAnthropic

from .base import (
    BaseLLMProvider,
    LLMConfig,
    LLMMessage,
    LLMProvider,
    LLMResponse,
    LLMUsage,
    calculate_cost,
)


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude LLM provider implementation."""
    
    provider = LLMProvider.ANTHROPIC
    
    def __init__(self, api_key: str):
        self.client = AsyncAnthropic(api_key=api_key)
    
    async def generate(
        self,
        messages: List[LLMMessage],
        config: LLMConfig,
    ) -> LLMResponse:
        """Generate a response using Anthropic Claude."""
        
        # Extract system message if present
        system_content = None
        chat_messages = []
        
        for m in messages:
            if m.role == "system":
                system_content = m.content
            else:
                chat_messages.append({"role": m.role, "content": m.content})
        
        kwargs = {
            "model": config.model,
            "messages": chat_messages,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "top_p": config.top_p,
        }
        
        if system_content:
            kwargs["system"] = system_content
            
        if config.stop:
            kwargs["stop_sequences"] = config.stop
        
        response = await self.client.messages.create(**kwargs)
        
        # Extract content from response
        content = ""
        if response.content:
            content = response.content[0].text if response.content[0].type == "text" else ""
        
        usage = LLMUsage(
            prompt_tokens=response.usage.input_tokens if response.usage else 0,
            completion_tokens=response.usage.output_tokens if response.usage else 0,
            total_tokens=(response.usage.input_tokens + response.usage.output_tokens) if response.usage else 0,
        )
        
        return LLMResponse(
            content=content,
            usage=usage,
            model=config.model,
            provider=self.provider.value,
            finish_reason=response.stop_reason,
            raw_response=response.model_dump(),
        )
    
    async def generate_json(
        self,
        messages: List[LLMMessage],
        config: LLMConfig,
        schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate a JSON response using Anthropic Claude."""
        
        # Add JSON instruction to system message
        json_messages = list(messages)
        system_exists = False
        
        for i, m in enumerate(json_messages):
            if m.role == "system":
                json_messages[i] = LLMMessage(
                    role="system",
                    content=m.content + "\n\nRespond with valid JSON only. No additional text.",
                )
                system_exists = True
                break
        
        if not system_exists:
            json_messages.insert(0, LLMMessage(
                role="system",
                content="Respond with valid JSON only. No additional text.",
            ))
        
        response = await self.generate(json_messages, config)
        
        # Clean response content (remove markdown code blocks if present)
        content = response.content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1])
        
        return json.loads(content)
    
    def _get_default_model(self) -> str:
        return "claude-3-sonnet-20240229"
    
    def _estimate_cost(self, usage: LLMUsage, model: str) -> float:
        return calculate_cost(self.provider, model, usage)
