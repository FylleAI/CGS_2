"""
Abstract LLM Interface for Fylle Onboarding v3
Provides a unified interface for all LLM providers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"
    PERPLEXITY = "perplexity"


class LLMConfig(BaseModel):
    """Configuration for an LLM request."""
    provider: LLMProvider
    model: str
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=1)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    stop: Optional[List[str]] = None
    response_format: Optional[Dict[str, Any]] = None  # For JSON mode
    
    class Config:
        use_enum_values = True


class LLMMessage(BaseModel):
    """A message in a conversation."""
    role: str = Field(..., pattern="^(system|user|assistant)$")
    content: str


class LLMUsage(BaseModel):
    """Token usage statistics."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    

class LLMResponse(BaseModel):
    """Response from an LLM provider."""
    content: str
    usage: LLMUsage
    model: str
    provider: str
    finish_reason: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    provider: LLMProvider
    
    @abstractmethod
    async def generate(
        self,
        messages: List[LLMMessage],
        config: LLMConfig,
    ) -> LLMResponse:
        """
        Generate a response from the LLM.
        
        Args:
            messages: List of messages in the conversation
            config: Configuration for the request
            
        Returns:
            LLMResponse with generated content and usage stats
        """
        pass
    
    @abstractmethod
    async def generate_json(
        self,
        messages: List[LLMMessage],
        config: LLMConfig,
        schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a JSON response from the LLM.
        
        Args:
            messages: List of messages in the conversation
            config: Configuration for the request
            schema: Optional JSON schema for validation
            
        Returns:
            Parsed JSON response
        """
        pass
    
    def _estimate_cost(self, usage: LLMUsage, model: str) -> float:
        """
        Estimate the cost of the request in USD.
        Override in subclasses with actual pricing.
        """
        return 0.0
    
    async def health_check(self) -> bool:
        """Check if the provider is healthy and accessible."""
        try:
            response = await self.generate(
                messages=[LLMMessage(role="user", content="Hi")],
                config=LLMConfig(
                    provider=self.provider,
                    model=self._get_default_model(),
                    max_tokens=10,
                ),
            )
            return bool(response.content)
        except Exception:
            return False
    
    @abstractmethod
    def _get_default_model(self) -> str:
        """Get the default model for this provider."""
        pass


# Provider-specific pricing (per 1M tokens)
PROVIDER_PRICING = {
    LLMProvider.OPENAI: {
        "gpt-4-turbo-preview": {"input": 10.0, "output": 30.0},
        "gpt-4": {"input": 30.0, "output": 60.0},
        "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
    },
    LLMProvider.ANTHROPIC: {
        "claude-3-opus-20240229": {"input": 15.0, "output": 75.0},
        "claude-3-sonnet-20240229": {"input": 3.0, "output": 15.0},
        "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
    },
    LLMProvider.GEMINI: {
        "gemini-1.5-pro": {"input": 7.0, "output": 21.0},
        "gemini-1.5-flash": {"input": 0.075, "output": 0.3},
    },
    LLMProvider.DEEPSEEK: {
        "deepseek-chat": {"input": 0.14, "output": 0.28},
        "deepseek-coder": {"input": 0.14, "output": 0.28},
    },
    LLMProvider.PERPLEXITY: {
        "sonar-pro": {"input": 3.0, "output": 15.0},
        "sonar": {"input": 1.0, "output": 1.0},
    },
}


def calculate_cost(provider: LLMProvider, model: str, usage: LLMUsage) -> float:
    """Calculate cost in USD for a request."""
    pricing = PROVIDER_PRICING.get(provider, {}).get(model)
    if not pricing:
        return 0.0
    
    input_cost = (usage.prompt_tokens / 1_000_000) * pricing["input"]
    output_cost = (usage.completion_tokens / 1_000_000) * pricing["output"]
    return input_cost + output_cost
