"""
LLM Router for Fylle Onboarding v3
Routes requests to the appropriate LLM provider based on configuration.
"""

from typing import Any, Dict, List, Optional

from .base import (
    BaseLLMProvider,
    LLMConfig,
    LLMMessage,
    LLMProvider,
    LLMResponse,
)
from .openai import OpenAIProvider
from .anthropic import AnthropicProvider
from .gemini import GeminiProvider
from .deepseek import DeepSeekProvider
from .perplexity import PerplexityProvider


class LLMRouter:
    """
    Routes LLM requests to the appropriate provider.
    Manages provider instances and provides a unified interface.
    """
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        deepseek_api_key: Optional[str] = None,
        perplexity_api_key: Optional[str] = None,
        # Vertex AI options
        use_vertex_gemini: bool = False,
        gcp_project_id: Optional[str] = None,
        gcp_location: str = "us-central1",
        # Default provider
        default_provider: LLMProvider = LLMProvider.GEMINI,
        default_research_provider: LLMProvider = LLMProvider.PERPLEXITY,
    ):
        self.providers: Dict[LLMProvider, BaseLLMProvider] = {}
        self.default_provider = default_provider
        self.default_research_provider = default_research_provider
        
        # Initialize available providers
        if openai_api_key:
            self.providers[LLMProvider.OPENAI] = OpenAIProvider(api_key=openai_api_key)
        
        if anthropic_api_key:
            self.providers[LLMProvider.ANTHROPIC] = AnthropicProvider(api_key=anthropic_api_key)
        
        if gemini_api_key or use_vertex_gemini:
            self.providers[LLMProvider.GEMINI] = GeminiProvider(
                api_key=gemini_api_key,
                use_vertex=use_vertex_gemini,
                project_id=gcp_project_id,
                location=gcp_location,
            )
        
        if deepseek_api_key:
            self.providers[LLMProvider.DEEPSEEK] = DeepSeekProvider(api_key=deepseek_api_key)
        
        if perplexity_api_key:
            self.providers[LLMProvider.PERPLEXITY] = PerplexityProvider(api_key=perplexity_api_key)
    
    def get_provider(self, provider: Optional[LLMProvider] = None) -> BaseLLMProvider:
        """Get a provider instance by name, or the default provider."""
        target = provider or self.default_provider
        
        if target not in self.providers:
            available = list(self.providers.keys())
            if not available:
                raise RuntimeError("No LLM providers configured. Check API keys in settings.")
            
            # Fallback to first available
            target = available[0]
        
        return self.providers[target]
    
    async def generate(
        self,
        messages: List[LLMMessage],
        config: Optional[LLMConfig] = None,
        provider: Optional[LLMProvider] = None,
    ) -> LLMResponse:
        """
        Generate a response using the specified or default provider.
        
        Args:
            messages: List of messages in the conversation
            config: Optional configuration (provider's default used if not specified)
            provider: Optional provider to use (default used if not specified)
            
        Returns:
            LLMResponse with generated content
        """
        llm = self.get_provider(provider)
        
        if config is None:
            config = LLMConfig(
                provider=llm.provider,
                model=llm._get_default_model(),
            )
        
        return await llm.generate(messages, config)
    
    async def generate_json(
        self,
        messages: List[LLMMessage],
        config: Optional[LLMConfig] = None,
        provider: Optional[LLMProvider] = None,
        schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a JSON response using the specified or default provider.
        
        Args:
            messages: List of messages in the conversation
            config: Optional configuration
            provider: Optional provider to use
            schema: Optional JSON schema for validation
            
        Returns:
            Parsed JSON response
        """
        llm = self.get_provider(provider)
        
        if config is None:
            config = LLMConfig(
                provider=llm.provider,
                model=llm._get_default_model(),
            )
        
        return await llm.generate_json(messages, config, schema)
    
    async def research(
        self,
        query: str,
        provider: Optional[LLMProvider] = None,
    ) -> LLMResponse:
        """
        Perform a research query using the research provider.
        
        Args:
            query: The research query
            provider: Optional provider (defaults to research provider)
            
        Returns:
            LLMResponse with research results
        """
        target = provider or self.default_research_provider
        llm = self.get_provider(target)
        
        # Check if provider supports research method
        if hasattr(llm, 'research'):
            return await llm.research(query)
        
        # Fallback to standard generate
        messages = [
            LLMMessage(
                role="system",
                content="You are a research assistant. Provide accurate, comprehensive information on the topic.",
            ),
            LLMMessage(role="user", content=query),
        ]
        
        config = LLMConfig(
            provider=target,
            model=llm._get_default_model(),
            temperature=0.2,
        )
        
        return await llm.generate(messages, config)
    
    def available_providers(self) -> List[LLMProvider]:
        """Return list of configured providers."""
        return list(self.providers.keys())
    
    async def health_check(self) -> Dict[LLMProvider, bool]:
        """Check health of all configured providers."""
        results = {}
        for provider, llm in self.providers.items():
            results[provider] = await llm.health_check()
        return results
