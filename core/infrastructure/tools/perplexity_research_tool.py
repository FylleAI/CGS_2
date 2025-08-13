"""
Perplexity Research Tool for premium content research.

This tool provides enhanced research capabilities using Perplexity AI API
specifically designed for premium newsletter content with domain filtering.
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class PerplexityResearchTool:
    """
    Perplexity-powered research tool for premium content generation.
    
    This tool leverages Perplexity AI's online models to provide:
    1. Real-time web research with domain filtering
    2. Premium financial source analysis
    3. Client-specific source research
    4. Automatic citation and source validation
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
        
        # Default model configuration
        self.default_model = "sonar"
        self.max_tokens = 1000
        self.temperature = 0.2
        
        logger.info("🔍 Perplexity Research Tool initialized")
    
    async def research_premium_financial(self,
                                       topic: str,
                                       exclude_topics: str = "crypto,day_trading",
                                       research_timeframe: str = "last 7 days",
                                       premium_sources: Optional[List[str]] = None) -> str:
        """
        Research premium financial content using Perplexity with domain filtering.

        This method is designed to be called by agents using the tool call syntax:
        [research_premium_financial] topic, exclude_topics, timeframe, sources [/research_premium_financial]

        Args:
            topic: Topic focus for the search
            exclude_topics: Topics to exclude (comma-separated)
            research_timeframe: Time period for research (last 7 days, yesterday, last month)
            premium_sources: Optional list of specific premium source URLs

        Returns:
            Formatted research results as JSON string
        """
        start_time = time.time()
        logger.info(f"💰 Starting Perplexity financial research: '{topic}'")
        
        if not self.api_key:
            logger.error("❌ CRITICAL: Perplexity API key not configured")
            raise Exception("Perplexity API key not configured - system cannot proceed without real research data")
        
        try:
            # Parse input if it comes as named parameters (from agent calls)
            if isinstance(topic, str) and ('=' in topic or ',' in topic):
                # Handle named parameters: topic=value, exclude_topics=value, etc.
                if '=' in topic:
                    params = {}
                    # Split by comma first, then by equals
                    param_pairs = [p.strip() for p in topic.split(',')]
                    for pair in param_pairs:
                        if '=' in pair:
                            key, value = pair.split('=', 1)
                            params[key.strip()] = value.strip()

                    # Extract parameters
                    topic = params.get('topic', topic)
                    exclude_topics = params.get('exclude_topics', exclude_topics)
                    research_timeframe = params.get('research_timeframe', research_timeframe)
                    sources_str = params.get('premium_sources', '')

                    logger.info(f"🔧 Parsed parameters: topic='{topic}', exclude_topics='{exclude_topics}', timeframe='{research_timeframe}', sources='{sources_str}'")

                    if sources_str and sources_str != "None":
                        # Clean up sources and remove any parameter prefixes
                        raw_sources = [s.strip() for s in sources_str.split('|') if s.strip()]
                        premium_sources = []
                        for source in raw_sources:
                            # Remove parameter prefix if present (e.g., "premium_sources=domain.com" -> "domain.com")
                            if '=' in source:
                                source = source.split('=', 1)[1].strip()
                            if source:
                                # Extract domain from URL if it's a full URL
                                if source.startswith('http'):
                                    from urllib.parse import urlparse
                                    parsed = urlparse(source)
                                    domain = parsed.netloc
                                    if domain:
                                        premium_sources.append(domain)
                                else:
                                    premium_sources.append(source)
                else:
                    # Fallback to old comma-separated parsing
                    parts = [p.strip() for p in topic.split(',')]
                    if len(parts) >= 1:
                        topic = parts[0]
                    if len(parts) >= 2:
                        exclude_topics = parts[1]
                    if len(parts) >= 3:
                        research_timeframe = parts[2]
                    if len(parts) >= 4:
                        # Parse premium sources from string
                        sources_str = parts[3]
                        if sources_str and sources_str != "None":
                            premium_sources = [s.strip() for s in sources_str.split('|') if s.strip()]
            
            # Use premium sources if provided, otherwise use default financial domains
            if premium_sources:
                # Extract domains from premium source URLs
                financial_domains = []
                for source in premium_sources:
                    if source.startswith('http'):
                        from urllib.parse import urlparse
                        domain = urlparse(source).netloc
                        if domain.startswith('www.'):
                            domain = domain[4:]
                        financial_domains.append(domain)
                    else:
                        financial_domains.append(source)

                logger.info(f"🎯 Using {len(premium_sources)} premium sources: {premium_sources[:3]}...")
            else:
                # Default financial domains for Siebert (prioritized, max 10)
                financial_domains = [
                    "thedailyupside.com",      # Primary Siebert source
                    "moneywithkatie.com",      # Gen Z focused
                    "thehustle.co",            # Gen Z/Millennial focused
                    "morningbrew.com",         # Young professional focused
                    "blog.siebert.com",        # Siebert's own content
                    "axios.com",               # Concise, modern format
                    "wsj.com",                 # Premium financial news
                    "bloomberg.com",           # Market analysis
                    "reuters.com",             # Global financial news
                    "marketwatch.com"          # Accessible financial content
                ]

            # Build research query with timeframe
            query = f"Latest financial news and analysis about {topic} from {research_timeframe}. Focus on market trends, investment insights, and economic developments relevant to Gen Z investors. Exclude {exclude_topics}."
            
            # Execute Perplexity search
            result = await self._execute_perplexity_search(
                query=query,
                domain_filter=financial_domains,
                search_type="financial"
            )
            
            duration = time.time() - start_time
            logger.info(f"✅ Perplexity financial research completed in {duration:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Perplexity financial research error: {e}")
            return json.dumps({
                "error": str(e),
                "topic": topic,
                "results": []
            })
    
    async def research_client_sources(self,
                                    client_name: str,
                                    topic: str = None,
                                    days_back: int = 7,
                                    premium_sources: Optional[List[str]] = None) -> str:
        """
        Research content from client-specific sources using Perplexity.
        
        This method is designed to be called by agents using the tool call syntax:
        [research_client_sources] client_name, topic, days_back [/research_client_sources]
        
        Args:
            client_name: Client identifier for source configuration
            topic: Main topic/theme for research
            days_back: How many days back to search (default: 7)
            
        Returns:
            Formatted research results as JSON string
        """
        start_time = time.time()
        logger.info(f"🎯 Starting client-specific research for {client_name}: '{topic}'")
        
        if not self.api_key:
            logger.error("❌ CRITICAL: Perplexity API key not configured for client research")
            raise Exception("Perplexity API key not configured - system cannot proceed without real research data")
        
        try:
            # Parse input if it comes as named parameters (from agent calls)
            if isinstance(client_name, str) and ('=' in client_name or ',' in client_name):
                # Handle named parameters: client_name=value, topic=value, etc.
                if '=' in client_name:
                    params = {}
                    # Split by comma first, then by equals
                    param_pairs = [p.strip() for p in client_name.split(',')]
                    for pair in param_pairs:
                        if '=' in pair:
                            key, value = pair.split('=', 1)
                            params[key.strip()] = value.strip()

                    # Extract parameters
                    client_name = params.get('client_name', client_name)
                    topic = params.get('topic', topic)
                    days_back_str = params.get('days_back', str(days_back))
                    try:
                        days_back = int(days_back_str)
                    except ValueError:
                        days_back = 7

                    logger.info(f"🔧 Parsed client research parameters: client='{client_name}', topic='{topic}', days_back={days_back}")
                else:
                    # Fallback to old comma-separated parsing
                    parts = [p.strip() for p in client_name.split(',')]
                    if len(parts) >= 2:
                        client_name = parts[0]
                        topic = parts[1]
                    if len(parts) >= 3:
                        try:
                            days_back = int(parts[2])
                        except ValueError:
                            days_back = 7

            # Handle case where topic is still None after parsing
            if topic is None:
                return json.dumps({
                    "error": "Topic parameter is required but was not provided",
                    "client_name": client_name,
                    "results": []
                })
            
            # Get client-specific domains (use premium sources if provided)
            if premium_sources:
                client_domains = []
                for source in premium_sources:
                    if source.startswith('http'):
                        from urllib.parse import urlparse
                        domain = urlparse(source).netloc
                        if domain.startswith('www.'):
                            domain = domain[4:]
                        client_domains.append(domain)
                    else:
                        client_domains.append(source)
                logger.info(f"🎯 Using {len(premium_sources)} premium sources for {client_name}")
            else:
                client_domains = self._get_client_domains(client_name)
            
            # Build research query
            date_filter = f"last {days_back} days"
            query = f"Research content about {topic} from {date_filter}. Focus on recent developments, trends, and insights relevant to {client_name}'s audience."
            
            # Execute Perplexity search
            result = await self._execute_perplexity_search(
                query=query,
                domain_filter=client_domains,
                search_type="client_specific",
                client_name=client_name
            )
            
            duration = time.time() - start_time
            logger.info(f"✅ Client research completed in {duration:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Client research error: {e}")
            return json.dumps({
                "error": str(e),
                "client": client_name,
                "topic": topic,
                "results": []
            })
    
    async def research_general_topic(self, topic: str) -> str:
        """
        General topic research using Perplexity without domain restrictions.
        
        This method is designed to be called by agents using the tool call syntax:
        [research_general_topic] topic [/research_general_topic]
        
        Args:
            topic: Topic to research
            
        Returns:
            Formatted research results as JSON string
        """
        start_time = time.time()
        logger.info(f"🌐 Starting general research: '{topic}'")
        
        if not self.api_key:
            logger.error("❌ CRITICAL: Perplexity API key not configured for general research")
            raise Exception("Perplexity API key not configured - system cannot proceed without real research data")
        
        try:
            # Parse input if it comes as named parameters (from agent calls)
            if isinstance(topic, str) and '=' in topic:
                params = {}
                # Split by comma first, then by equals
                param_pairs = [p.strip() for p in topic.split(',')]
                for pair in param_pairs:
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        params[key.strip()] = value.strip()

                # Extract topic parameter
                topic = params.get('topic', topic)

            # Build research query
            query = f"Comprehensive research about {topic}. Provide recent developments, key insights, statistics, and expert analysis from the last 7 days."
            
            # Execute Perplexity search without domain filtering
            result = await self._execute_perplexity_search(
                query=query,
                domain_filter=None,
                search_type="general"
            )
            
            duration = time.time() - start_time
            logger.info(f"✅ General research completed in {duration:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ General research error: {e}")
            return json.dumps({
                "error": str(e),
                "topic": topic,
                "results": []
            })
    
    async def _execute_perplexity_search(self,
                                       query: str,
                                       domain_filter: Optional[List[str]] = None,
                                       search_type: str = "general",
                                       client_name: Optional[str] = None) -> str:
        """Execute a search using Perplexity API."""
        try:
            import aiohttp
            
            # Enhanced system message for premium financial research
            system_message = """You are a specialized financial research assistant focused on Gen Z and Millennial investors.

RESEARCH OBJECTIVES:
- Extract key financial insights, market trends, and investment opportunities
- Focus on content relevant to young investors (18-35 years old)
- Identify actionable financial advice and educational content
- Highlight cultural connections and trending topics in finance
- Summarize complex financial concepts in accessible language

CONTENT ANALYSIS:
- Prioritize recent market developments and emerging trends
- Look for investment strategies suitable for beginners
- Extract statistics and data points with proper context
- Identify expert opinions and analysis
- Note any mentions of technology, social media, or cultural trends

CITATION REQUIREMENTS:
- Provide specific source URLs and publication dates
- Include author names when available
- Maintain accuracy and factual integrity"""

            # Prepare the payload
            payload = {
                "model": self.default_model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_message
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "top_p": 0.9,
                "return_citations": True,
                "return_images": False,
                "return_related_questions": True
            }
            
            # Add domain filtering if specified (Perplexity limit: 10 domains)
            if domain_filter:
                # Limit to 10 domains due to Perplexity API constraint
                limited_domains = domain_filter[:10]
                payload["search_domain_filter"] = limited_domains
                logger.info(f"🔍 Using domain filter: {limited_domains}")
                if len(domain_filter) > 10:
                    logger.warning(f"⚠️ Domain filter truncated from {len(domain_filter)} to 10 domains (Perplexity limit)")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Create SSL context that handles certificate verification
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            connector = aiohttp.TCPConnector(ssl=ssl_context)

            async with aiohttp.ClientSession(connector=connector) as session:
                logger.debug(f"📡 Making Perplexity API request...")

                async with session.post(
                    self.base_url,
                    json=payload,
                    headers=headers,
                    timeout=30
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"❌ Perplexity API error {response.status}: {error_text}")
                        return json.dumps({
                            "error": f"API error {response.status}: {error_text}",
                            "query": query,
                            "results": []
                        })
                    
                    result = await response.json()

                    # Ensure result is a dictionary
                    if not isinstance(result, dict):
                        logger.error(f"❌ Unexpected result type: {type(result)}")
                        return json.dumps({
                            "error": f"Unexpected API response type: {type(result)}",
                            "query": query,
                            "results": []
                        })

                    # Extract content and citations
                    choices = result.get("choices", [])
                    if choices and isinstance(choices, list) and len(choices) > 0:
                        message = choices[0].get("message", {}) if isinstance(choices[0], dict) else {}
                        content = message.get("content", "") if isinstance(message, dict) else ""
                    else:
                        content = ""

                    citations = result.get("citations", [])
                    related_questions = result.get("related_questions", [])

                    # Enhanced content analysis (only if content exists)
                    content_analysis = {}
                    if content:
                        try:
                            content_analysis = self._analyze_research_content(content, citations, search_type)
                        except Exception as e:
                            logger.warning(f"⚠️ Content analysis failed: {e}")
                            content_analysis = {"error": str(e)}

                    # Format the response with enhanced metadata
                    formatted_result = {
                        "search_type": search_type,
                        "query": query,
                        "content": content,
                        "citations": citations,
                        "related_questions": related_questions,
                        "content_analysis": content_analysis,
                        "domain_filter": domain_filter,
                        "client": client_name,
                        "timestamp": datetime.now().isoformat(),
                        "model_used": self.default_model,
                        "total_citations": len(citations),
                        "premium_sources_used": self._count_premium_sources_used(citations, domain_filter)
                    }
                    
                    logger.info(f"📊 Perplexity search successful: {len(citations)} citations found")
                    return json.dumps(formatted_result, indent=2)
                    
        except ImportError:
            logger.error("❌ aiohttp not available for Perplexity API")
            return json.dumps({
                "error": "aiohttp dependency not available",
                "query": query,
                "results": []
            })
        except Exception as e:
            logger.error(f"❌ Perplexity API execution error: {e}")
            return json.dumps({
                "error": str(e),
                "query": query,
                "results": []
            })
    
    def _get_client_domains(self, client_name: str) -> List[str]:
        """Get domain list for specific client."""
        # Client-specific domain configurations
        client_domains = {
            "siebert": [
                "thedailyupside.com",
                "moneywithkatie.com", 
                "thehustle.co",
                "morningbrew.com",
                "wsj.com",
                "bloomberg.com",
                "reuters.com",
                "marketwatch.com"
            ],
            "default": [
                "wsj.com",
                "bloomberg.com",
                "reuters.com",
                "ft.com",
                "marketwatch.com"
            ]
        }
        
        domains = client_domains.get(client_name.lower(), client_domains["default"])
        logger.info(f"📚 Using {len(domains)} domains for client {client_name}")
        return domains

    def _analyze_research_content(self, content: str, citations: Any, search_type: str) -> Dict[str, Any]:
        """Analyze research content for quality and relevance metrics."""
        # Ensure citations is a list
        if not isinstance(citations, list):
            citations = []

        analysis = {
            "content_length": len(content),
            "word_count": len(content.split()) if content else 0,
            "citation_quality": self._assess_citation_quality(citations),
            "gen_z_relevance": self._assess_gen_z_relevance(content),
            "financial_concepts": self._extract_financial_concepts(content),
            "actionable_insights": self._extract_actionable_insights(content)
        }

        return analysis

    def _assess_citation_quality(self, citations: Any) -> Dict[str, Any]:
        """Assess the quality and diversity of citations."""
        # Ensure citations is a list
        if not isinstance(citations, list):
            citations = []

        if not citations:
            return {"score": 0, "premium_sources": 0, "diversity": 0, "total_citations": 0}

        # Count premium sources
        premium_domains = ["thedailyupside.com", "moneywithkatie.com", "thehustle.co",
                          "morningbrew.com", "blog.siebert.com", "axios.com"]
        premium_count = 0

        unique_domains = set()
        for citation in citations:
            # Handle both dict and string citations
            if isinstance(citation, dict):
                url = citation.get('url', '')
            elif isinstance(citation, str):
                url = citation
            else:
                continue

            if any(domain in url for domain in premium_domains):
                premium_count += 1

            # Extract domain for diversity calculation
            if url:
                try:
                    from urllib.parse import urlparse
                    domain = urlparse(url).netloc
                    unique_domains.add(domain)
                except:
                    pass

        return {
            "score": min(len(citations) / 5.0, 1.0),  # Normalize to 0-1
            "premium_sources": premium_count,
            "diversity": len(unique_domains),
            "total_citations": len(citations)
        }

    def _assess_gen_z_relevance(self, content: str) -> Dict[str, Any]:
        """Assess content relevance to Gen Z audience."""
        if not content:
            return {"score": 0, "indicators": []}

        content_lower = content.lower()

        # Gen Z relevance indicators
        gen_z_indicators = [
            "tiktok", "instagram", "social media", "app", "mobile", "digital",
            "young", "millennial", "gen z", "student", "college", "first job",
            "side hustle", "gig economy", "crypto", "fintech", "robo advisor",
            "micro investing", "fractional shares", "commission free"
        ]

        found_indicators = [indicator for indicator in gen_z_indicators
                           if indicator in content_lower]

        relevance_score = min(len(found_indicators) / 5.0, 1.0)  # Normalize to 0-1

        return {
            "score": relevance_score,
            "indicators": found_indicators,
            "total_indicators": len(found_indicators)
        }

    def _extract_financial_concepts(self, content: str) -> List[str]:
        """Extract key financial concepts from content."""
        if not content:
            return []

        content_lower = content.lower()

        financial_concepts = [
            "investment", "portfolio", "diversification", "risk", "return",
            "stocks", "bonds", "etf", "mutual fund", "index fund",
            "401k", "ira", "roth", "compound interest", "dividend",
            "market volatility", "bull market", "bear market", "recession",
            "inflation", "interest rates", "fed", "gdp", "unemployment"
        ]

        found_concepts = [concept for concept in financial_concepts
                         if concept in content_lower]

        return found_concepts[:10]  # Return top 10 concepts

    def _extract_actionable_insights(self, content: str) -> List[str]:
        """Extract actionable insights from content."""
        if not content:
            return []

        # Look for action-oriented phrases
        action_patterns = [
            "should consider", "can start", "try to", "avoid", "focus on",
            "invest in", "save", "budget", "track", "monitor", "review",
            "diversify", "rebalance", "dollar-cost average", "automate"
        ]

        insights = []
        sentences = content.split('.')

        for sentence in sentences:
            sentence_lower = sentence.lower().strip()
            if any(pattern in sentence_lower for pattern in action_patterns):
                if len(sentence.strip()) > 20:  # Avoid very short sentences
                    insights.append(sentence.strip())

        return insights[:5]  # Return top 5 actionable insights

    def _count_premium_sources_used(self, citations: Any, domain_filter: Optional[List[str]]) -> int:
        """Count how many premium sources were used in citations."""
        if not citations or not domain_filter:
            return 0

        if not isinstance(citations, list):
            return 0

        count = 0
        for citation in citations:
            try:
                if isinstance(citation, dict):
                    url = citation.get('url', '')
                elif isinstance(citation, str):
                    url = citation
                else:
                    continue

                if any(domain in url for domain in domain_filter):
                    count += 1
            except:
                continue

        return count
