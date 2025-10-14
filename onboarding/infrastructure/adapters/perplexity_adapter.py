"""Perplexity adapter for company research.

Wraps the CGS PerplexityResearchTool for onboarding-specific research.
"""

import logging
from typing import Any, Dict, Optional

from core.infrastructure.tools.perplexity_research_tool import PerplexityResearchTool
from onboarding.config.settings import OnboardingSettings

logger = logging.getLogger(__name__)


class PerplexityAdapter:
    """
    Adapter for Perplexity research in onboarding flow.
    
    Reuses CGS PerplexityResearchTool with onboarding-specific configuration.
    """
    
    def __init__(self, settings: OnboardingSettings):
        """
        Initialize Perplexity adapter.
        
        Args:
            settings: Onboarding settings with Perplexity configuration
        """
        self.settings = settings
        
        if not settings.is_perplexity_configured():
            raise ValueError("Perplexity API key not configured")
        
        # Initialize CGS tool with onboarding settings
        self.tool = PerplexityResearchTool(
            api_key=settings.perplexity_api_key,
            model=settings.perplexity_model,
            timeout=settings.perplexity_timeout,
        )
        
        logger.info(
            f"Perplexity adapter initialized with model: {settings.perplexity_model}"
        )
    
    async def research_company(
        self,
        brand_name: str,
        website: Optional[str] = None,
        additional_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Research a company using Perplexity.
        
        Args:
            brand_name: Company/brand name to research
            website: Optional company website
            additional_context: Optional additional context
        
        Returns:
            Research results with metadata
        """
        # Build research query
        query_parts = [f"Research the company '{brand_name}'"]
        
        if website:
            query_parts.append(f"(website: {website})")
        
        query_parts.extend([
            "Provide:",
            "1. Company description and key offerings",
            "2. Industry and market positioning",
            "3. Target audience and customer segments",
            "4. Brand voice and communication style (if evident)",
            "5. Recent news or developments",
            "6. Key differentiators and competitive advantages",
        ])
        
        if additional_context:
            query_parts.append(f"Additional context: {additional_context}")
        
        query = " ".join(query_parts)
        
        logger.info(f"Researching company: {brand_name}")
        logger.debug(f"Research query: {query[:200]}...")
        
        try:
            # Execute search via CGS tool
            result = await self.tool.search(query)
            
            # Extract response
            data = result.get("data", {})
            choices = data.get("choices", [])
            
            if not choices:
                raise ValueError("No research results returned from Perplexity")
            
            # Get first choice content
            content = choices[0].get("message", {}).get("content", "")
            
            # Build structured response
            research_result = {
                "brand_name": brand_name,
                "website": website,
                "raw_content": content,
                "provider": result.get("provider"),
                "model_used": result.get("model_used"),
                "duration_ms": result.get("duration_ms"),
                "usage_tokens": result.get("usage_tokens"),
                "cost_usd": result.get("cost_usd"),
                "cost_source": result.get("cost_source"),
            }
            
            logger.info(
                f"Research completed: {result.get('usage_tokens', 0)} tokens, "
                f"${result.get('cost_usd', 0):.4f}"
            )
            
            return research_result
            
        except Exception as e:
            logger.error(f"Perplexity research failed: {str(e)}")
            raise
    
    async def research_with_retry(
        self,
        brand_name: str,
        website: Optional[str] = None,
        additional_context: Optional[str] = None,
        max_retries: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Research with exponential backoff retry.
        
        Args:
            brand_name: Company name
            website: Optional website
            additional_context: Optional context
            max_retries: Max retry attempts (defaults to settings)
        
        Returns:
            Research results
        """
        import asyncio
        
        max_retries = max_retries or self.settings.perplexity_max_retries
        backoff = self.settings.retry_backoff_seconds
        
        for attempt in range(max_retries):
            try:
                return await self.research_company(
                    brand_name, website, additional_context
                )
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(
                        f"Perplexity research failed after {max_retries} attempts"
                    )
                    raise
                
                wait_time = backoff * (2 ** attempt)
                logger.warning(
                    f"Perplexity attempt {attempt + 1} failed: {str(e)}. "
                    f"Retrying in {wait_time}s..."
                )
                await asyncio.sleep(wait_time)
        
        raise RuntimeError("Unexpected retry loop exit")

