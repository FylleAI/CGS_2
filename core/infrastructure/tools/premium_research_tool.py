"""
Perplexity Research Tool for premium content research.

This tool provides enhanced research capabilities using Perplexity AI API
specifically designed for premium newsletter content with domain filtering.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class PerplexityResearchTool:
    """
    Premium research tool for multi-source content aggregation.
    
    This tool provides reliable content research through multiple methods:
    1. Client-specific source scraping
    2. API-based research (Perplexity, SerpAPI)
    3. Fallback mechanisms and validation
    
    Designed to integrate seamlessly with existing workflow system.
    """
    
    def __init__(self, 
                 perplexity_api_key: Optional[str] = None,
                 serpapi_key: Optional[str] = None,
                 config_dir: str = "data/profiles"):
        self.perplexity_api_key = perplexity_api_key
        self.serpapi_key = serpapi_key
        self.config_dir = Path(config_dir)
        self._client_configs = {}
        
        logger.info("🔍 Premium Research Tool initialized")
    
    async def research_premium_sources(self, 
                                     client_name: str,
                                     topic: str,
                                     days_back: int = 7) -> str:
        """
        Research content from client-specific premium sources.
        
        This method is designed to be called by agents using the tool call syntax:
        [research_premium_sources] client_name, topic, days_back [/research_premium_sources]
        
        Args:
            client_name: Client identifier for source configuration
            topic: Main topic/theme for research
            days_back: How many days back to search (default: 7)
            
        Returns:
            Formatted research results as JSON string
        """
        start_time = time.time()
        logger.info(f"🚀 Starting premium research for {client_name}: '{topic}'")
        
        try:
            # Parse input if it comes as comma-separated string (from agent calls)
            if isinstance(client_name, str) and ',' in client_name:
                parts = [p.strip() for p in client_name.split(',')]
                if len(parts) >= 2:
                    client_name = parts[0]
                    topic = parts[1]
                if len(parts) >= 3:
                    try:
                        days_back = int(parts[2])
                    except ValueError:
                        days_back = 7
            
            # Load client-specific sources
            sources = self._load_client_sources(client_name)
            if not sources:
                logger.warning(f"No sources found for client {client_name}, using fallback research")
                return await self._fallback_research(topic, days_back)
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Research from multiple sources
            research_results = []
            
            # Layer 1: Client-specific source scraping
            source_results = await self._research_client_sources(sources, topic, start_date, end_date)
            research_results.extend(source_results)
            
            # Layer 2: API-based research (if available)
            if self.perplexity_api_key:
                api_results = await self._research_via_perplexity(topic, start_date, end_date)
                research_results.extend(api_results)
            
            # Process and rank results
            processed_results = self._process_and_rank_results(research_results, topic)
            
            # Format output for agent consumption
            output = self._format_research_output(processed_results, client_name, topic, days_back)
            
            duration = time.time() - start_time
            logger.info(f"✅ Premium research completed: {len(processed_results)} items in {duration:.2f}s")
            
            return output
            
        except Exception as e:
            logger.error(f"❌ Premium research error: {e}")
            return json.dumps({
                "error": str(e),
                "client": client_name,
                "topic": topic,
                "results": []
            })
    
    async def research_financial_premium(self,
                                       topic: str,
                                       exclude_topics: str = "crypto,day_trading") -> str:
        """
        Research premium financial content with enhanced filtering.
        
        This method provides enhanced financial research capabilities
        specifically for premium newsletter content.
        
        Args:
            topic: Topic focus for the search
            exclude_topics: Topics to exclude (comma-separated)
            
        Returns:
            Formatted financial research results
        """
        start_time = time.time()
        logger.info(f"💰 Starting premium financial research: '{topic}'")
        
        try:
            # Enhanced financial source list
            financial_sources = [
                "wsj.com", "bloomberg.com", "reuters.com", "ft.com",
                "marketwatch.com", "cnbc.com", "barrons.com"
            ]
            
            # Build enhanced search queries
            search_queries = [
                f"site:wsj.com OR site:bloomberg.com {topic} last 7 days",
                f"financial analysis {topic} market trends 2025",
                f"investment outlook {topic} expert analysis",
                f"economic impact {topic} market implications"
            ]
            
            research_results = []
            
            # Use Perplexity API if available for enhanced financial research
            if self.perplexity_api_key:
                for query in search_queries:
                    try:
                        result = await self._perplexity_financial_search(query, financial_sources)
                        if result:
                            research_results.append(result)
                    except Exception as e:
                        logger.warning(f"Perplexity query failed: {e}")
                        continue
            
            # Fallback to basic research if no API results
            if not research_results:
                logger.info("Using fallback financial research")
                return await self._fallback_financial_research(topic, exclude_topics)
            
            # Process and format results
            processed_results = self._process_financial_results(research_results, topic, exclude_topics)
            output = self._format_financial_output(processed_results, topic)
            
            duration = time.time() - start_time
            logger.info(f"✅ Premium financial research completed in {duration:.2f}s")
            
            return output
            
        except Exception as e:
            logger.error(f"❌ Premium financial research error: {e}")
            return json.dumps({
                "error": str(e),
                "topic": topic,
                "results": []
            })
    
    def _load_client_sources(self, client_name: str) -> List[Dict[str, Any]]:
        """Load source configuration for a specific client."""
        if client_name in self._client_configs:
            return self._client_configs[client_name]
        
        config_file = self.config_dir / client_name / "sources.json"
        
        if not config_file.exists():
            logger.warning(f"No source config found for client {client_name}")
            return []
        
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            sources = config_data.get('sources', [])
            self._client_configs[client_name] = sources
            logger.info(f"Loaded {len(sources)} sources for client {client_name}")
            return sources
            
        except Exception as e:
            logger.error(f"Error loading sources for {client_name}: {e}")
            return []
    
    async def _research_client_sources(self, sources: List[Dict[str, Any]], 
                                     topic: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Research content from client-specific sources."""
        results = []
        
        # For now, return mock data structure
        # This will be implemented with actual scraping logic
        for source in sources[:3]:  # Limit to first 3 sources for now
            mock_result = {
                "title": f"Premium content from {source.get('name', 'Unknown Source')}",
                "content": f"Research content about {topic} from {source.get('url', '')}",
                "url": source.get('url', ''),
                "source": source.get('name', 'Unknown'),
                "category": source.get('category', 'general'),
                "published_date": datetime.now().isoformat(),
                "relevance_score": 0.8
            }
            results.append(mock_result)
        
        logger.info(f"🕷️ Client sources research: {len(results)} items found")
        return results
    
    async def _research_via_perplexity(self, topic: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Research using Perplexity API."""
        # Placeholder for Perplexity API integration
        logger.info("📡 Perplexity research (placeholder)")
        return []
    
    async def _perplexity_financial_search(self, query: str, sources: List[str]) -> Optional[Dict[str, Any]]:
        """Enhanced financial search using Perplexity API."""
        # Placeholder for enhanced Perplexity financial search
        logger.debug(f"📡 Perplexity financial search: {query}")
        return None
    
    async def _fallback_research(self, topic: str, days_back: int) -> str:
        """Fallback research when no client sources are available."""
        logger.info(f"🔄 Using fallback research for topic: {topic}")
        
        fallback_result = {
            "research_type": "fallback",
            "topic": topic,
            "days_back": days_back,
            "results": [
                {
                    "title": f"General research about {topic}",
                    "content": f"Fallback research content for {topic}. This would normally contain web search results.",
                    "source": "fallback_research",
                    "relevance_score": 0.5
                }
            ],
            "total_results": 1,
            "duration_ms": 100
        }
        
        return json.dumps(fallback_result, indent=2)
    
    async def _fallback_financial_research(self, topic: str, exclude_topics: str) -> str:
        """Fallback financial research."""
        logger.info(f"🔄 Using fallback financial research for: {topic}")
        
        fallback_result = {
            "research_type": "fallback_financial",
            "topic": topic,
            "exclude_topics": exclude_topics,
            "results": [
                {
                    "title": f"Financial analysis: {topic}",
                    "content": f"Fallback financial research for {topic}. Excluding: {exclude_topics}",
                    "source": "fallback_financial",
                    "relevance_score": 0.6
                }
            ],
            "total_results": 1
        }
        
        return json.dumps(fallback_result, indent=2)
    
    def _process_and_rank_results(self, results: List[Dict[str, Any]], topic: str) -> List[Dict[str, Any]]:
        """Process and rank research results by relevance."""
        # Simple ranking by relevance score
        return sorted(results, key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    def _process_financial_results(self, results: List[Dict[str, Any]], topic: str, exclude_topics: str) -> List[Dict[str, Any]]:
        """Process financial research results with filtering."""
        exclude_list = [t.strip().lower() for t in exclude_topics.split(',')]
        
        filtered_results = []
        for result in results:
            content_text = f"{result.get('title', '')} {result.get('content', '')}".lower()
            
            # Check if we should exclude this content
            should_exclude = any(exclude_topic in content_text for exclude_topic in exclude_list)
            
            if not should_exclude:
                filtered_results.append(result)
        
        return filtered_results
    
    def _format_research_output(self, results: List[Dict[str, Any]], 
                              client_name: str, topic: str, days_back: int) -> str:
        """Format research results for agent consumption."""
        output = {
            "research_type": "premium_sources",
            "client": client_name,
            "topic": topic,
            "days_back": days_back,
            "total_results": len(results),
            "results": results[:10],  # Limit to top 10 results
            "timestamp": datetime.now().isoformat()
        }
        
        return json.dumps(output, indent=2)
    
    def _format_financial_output(self, results: List[Dict[str, Any]], topic: str) -> str:
        """Format financial research results."""
        output = {
            "research_type": "premium_financial",
            "topic": topic,
            "total_results": len(results),
            "results": results[:10],  # Limit to top 10 results
            "timestamp": datetime.now().isoformat()
        }
        
        return json.dumps(output, indent=2)
