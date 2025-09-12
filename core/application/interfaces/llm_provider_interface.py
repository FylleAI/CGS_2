"""LLM Provider interface."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass

from ...domain.value_objects.provider_config import ProviderConfig


@dataclass
class LLMResponse:
    """Response from LLM provider."""
    content: str
    usage: Dict[str, int] = None
    model: str = ""
    finish_reason: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self) -> None:
        if self.usage is None:
            self.usage = {}
        if self.metadata is None:
            self.metadata = {}


@dataclass
class LLMStreamChunk:
    """Streaming chunk from LLM provider."""
    content: str
    is_final: bool = False
    metadata: Dict[str, Any] = None
    
    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


class LLMProviderInterface(ABC):
    """
    Abstract interface for LLM providers.
    
    This interface defines the contract for interacting with different
    LLM providers (OpenAI, Anthropic, DeepSeek, etc.)
    """
    
    @abstractmethod
    async def generate_content(
        self, 
        prompt: str, 
        config: ProviderConfig,
        system_message: Optional[str] = None
    ) -> str:
        """
        Generate content using the LLM.
        
        Args:
            prompt: The user prompt
            config: Provider configuration
            system_message: Optional system message
            
        Returns:
            Generated content as string
        """
        pass
    
    @abstractmethod
    async def generate_content_detailed(
        self, 
        prompt: str, 
        config: ProviderConfig,
        system_message: Optional[str] = None
    ) -> LLMResponse:
        """
        Generate content with detailed response information.
        
        Args:
            prompt: The user prompt
            config: Provider configuration
            system_message: Optional system message
            
        Returns:
            Detailed LLM response
        """
        pass
    
    @abstractmethod
    async def generate_content_stream(
        self, 
        prompt: str, 
        config: ProviderConfig,
        system_message: Optional[str] = None
    ) -> AsyncGenerator[LLMStreamChunk, None]:
        """
        Generate content with streaming response.
        
        Args:
            prompt: The user prompt
            config: Provider configuration
            system_message: Optional system message
            
        Yields:
            Streaming chunks of generated content
        """
        pass
    
    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        config: ProviderConfig
    ) -> LLMResponse:
        """
        Perform chat completion with message history.
        
        Args:
            messages: List of messages in chat format
            config: Provider configuration
            
        Returns:
            LLM response
        """
        pass
    
    @abstractmethod
    async def validate_config(self, config: ProviderConfig) -> bool:
        """
        Validate provider configuration.
        
        Args:
            config: Provider configuration to validate
            
        Returns:
            True if configuration is valid
        """
        pass
    
    @abstractmethod
    async def get_available_models(self, config: ProviderConfig) -> List[Dict[str, Any]]:
        """
        Get list of available models for the provider with metadata.

        Args:
            config: Provider configuration

        Returns:
            List of model information dictionaries
        """
        pass
    
    @abstractmethod
    async def estimate_tokens(self, text: str, model: str) -> int:
        """
        Estimate token count for given text.
        
        Args:
            text: Text to estimate tokens for
            model: Model name for tokenization
            
        Returns:
            Estimated token count
        """
        pass
    
    @abstractmethod
    async def check_health(self, config: ProviderConfig) -> Dict[str, Any]:
        """
        Check provider health and connectivity.
        
        Args:
            config: Provider configuration
            
        Returns:
            Health status information
        """
        pass
