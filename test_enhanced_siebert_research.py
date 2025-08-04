#!/usr/bin/env python3
"""
Enhanced Siebert Research System Test.

This script tests the optimized research functionality with premium sources,
timeframe controls, and enhanced content analysis.
"""

import asyncio
import os
import sys
import logging
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

from core.infrastructure.tools.perplexity_research_tool import PerplexityResearchTool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_enhanced_premium_research():
    """Test enhanced premium financial research with custom sources."""
    logger.info("🔍 Testing Enhanced Premium Financial Research")
    logger.info("-" * 60)
    
    tool = PerplexityResearchTool(os.getenv("PERPLEXITY_API_KEY"))
    
    # Siebert premium sources
    premium_sources = [
        "https://www.thedailyupside.com/finance/",
        "https://www.thedailyupside.com/investments/",
        "https://moneywithkatie.com/blog/category/investing",
        "https://thehustle.co/news",
        "https://www.morningbrew.com/tag/finance",
        "https://blog.siebert.com/tag/daily-market#BlogListing"
    ]
    
    try:
        # Test with premium sources and timeframe
        result = await tool.research_premium_financial(
            topic="AI investment opportunities for young investors",
            exclude_topics="crypto day trading,get rich quick",
            research_timeframe="last 7 days",
            premium_sources=premium_sources
        )
        
        import json
        data = json.loads(result)
        
        logger.info(f"✅ Research completed successfully!")
        logger.info(f"📊 Content length: {len(data.get('content', ''))}")
        logger.info(f"📚 Total citations: {data.get('total_citations', 0)}")
        logger.info(f"🎯 Premium sources used: {data.get('premium_sources_used', 0)}")
        
        # Analyze content quality
        content_analysis = data.get('content_analysis', {})
        if content_analysis:
            logger.info(f"📈 Content Analysis:")
            logger.info(f"  - Word count: {content_analysis.get('word_count', 0)}")
            logger.info(f"  - Gen Z relevance: {content_analysis.get('gen_z_relevance', {}).get('score', 0):.2f}")
            logger.info(f"  - Citation quality: {content_analysis.get('citation_quality', {}).get('score', 0):.2f}")
            logger.info(f"  - Financial concepts: {len(content_analysis.get('financial_concepts', []))}")
            logger.info(f"  - Actionable insights: {len(content_analysis.get('actionable_insights', []))}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Enhanced premium research failed: {e}")
        return False


async def test_client_sources_with_premium():
    """Test client sources research with premium source override."""
    logger.info("\n🎯 Testing Client Sources with Premium Override")
    logger.info("-" * 60)
    
    tool = PerplexityResearchTool(os.getenv("PERPLEXITY_API_KEY"))
    
    # Custom premium sources for this test
    premium_sources = [
        "https://www.axios.com/newsletters/axios-markets",
        "https://decrypt.co/",
        "https://www.coindesk.com/"
    ]
    
    try:
        result = await tool.research_client_sources(
            client_name="siebert",
            topic="fintech trends for Gen Z",
            days_back=7,
            premium_sources=premium_sources
        )
        
        import json
        data = json.loads(result)
        
        logger.info(f"✅ Client research completed!")
        logger.info(f"👤 Client: {data.get('client', 'unknown')}")
        logger.info(f"📊 Content length: {len(data.get('content', ''))}")
        logger.info(f"📚 Citations: {data.get('total_citations', 0)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Client sources research failed: {e}")
        return False


async def test_timeframe_variations():
    """Test different research timeframes."""
    logger.info("\n⏰ Testing Research Timeframe Variations")
    logger.info("-" * 60)
    
    tool = PerplexityResearchTool(os.getenv("PERPLEXITY_API_KEY"))
    
    timeframes = ["yesterday", "last 7 days", "last month"]
    results = {}
    
    for timeframe in timeframes:
        try:
            logger.info(f"🔍 Testing timeframe: {timeframe}")
            
            result = await tool.research_premium_financial(
                topic="market trends",
                exclude_topics="crypto",
                research_timeframe=timeframe
            )
            
            import json
            data = json.loads(result)
            
            results[timeframe] = {
                "content_length": len(data.get('content', '')),
                "citations": data.get('total_citations', 0),
                "success": True
            }
            
            logger.info(f"  ✅ {timeframe}: {results[timeframe]['content_length']} chars, {results[timeframe]['citations']} citations")
            
        except Exception as e:
            logger.error(f"  ❌ {timeframe}: {e}")
            results[timeframe] = {"success": False, "error": str(e)}
    
    # Summary
    successful = sum(1 for r in results.values() if r.get('success', False))
    logger.info(f"\n📊 Timeframe Test Summary: {successful}/{len(timeframes)} successful")
    
    return successful == len(timeframes)


async def test_content_analysis_quality():
    """Test the enhanced content analysis features."""
    logger.info("\n🧠 Testing Enhanced Content Analysis")
    logger.info("-" * 60)
    
    tool = PerplexityResearchTool(os.getenv("PERPLEXITY_API_KEY"))
    
    try:
        result = await tool.research_premium_financial(
            topic="investment apps for college students",
            exclude_topics="gambling,day trading"
        )
        
        import json
        data = json.loads(result)
        
        content_analysis = data.get('content_analysis', {})
        
        if not content_analysis:
            logger.error("❌ No content analysis found")
            return False
        
        logger.info("✅ Content Analysis Results:")
        
        # Gen Z relevance
        gen_z = content_analysis.get('gen_z_relevance', {})
        logger.info(f"📱 Gen Z Relevance Score: {gen_z.get('score', 0):.2f}")
        logger.info(f"📱 Gen Z Indicators: {gen_z.get('indicators', [])[:5]}")
        
        # Citation quality
        citations = content_analysis.get('citation_quality', {})
        logger.info(f"📚 Citation Quality Score: {citations.get('score', 0):.2f}")
        logger.info(f"📚 Premium Sources: {citations.get('premium_sources', 0)}")
        logger.info(f"📚 Source Diversity: {citations.get('diversity', 0)}")
        
        # Financial concepts
        concepts = content_analysis.get('financial_concepts', [])
        logger.info(f"💰 Financial Concepts: {concepts[:5]}")
        
        # Actionable insights
        insights = content_analysis.get('actionable_insights', [])
        logger.info(f"🎯 Actionable Insights: {len(insights)}")
        for i, insight in enumerate(insights[:3], 1):
            logger.info(f"  {i}. {insight[:100]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Content analysis test failed: {e}")
        return False


async def test_agent_call_syntax():
    """Test the agent call syntax with all new parameters."""
    logger.info("\n🤖 Testing Agent Call Syntax")
    logger.info("-" * 60)
    
    tool = PerplexityResearchTool(os.getenv("PERPLEXITY_API_KEY"))
    
    try:
        # Simulate agent call with all parameters
        agent_input = "sustainable investing, crypto day trading, last 7 days, https://www.thedailyupside.com/finance/|https://moneywithkatie.com/blog/category/investing"
        
        result = await tool.research_premium_financial(agent_input)
        
        import json
        data = json.loads(result)
        
        logger.info(f"✅ Agent syntax test successful!")
        logger.info(f"📊 Content: {len(data.get('content', ''))} chars")
        logger.info(f"📚 Citations: {data.get('total_citations', 0)}")
        logger.info(f"🎯 Premium sources used: {data.get('premium_sources_used', 0)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Agent syntax test failed: {e}")
        return False


async def main():
    """Run all enhanced research tests."""
    logger.info("🚀 Starting Enhanced Siebert Research System Tests")
    logger.info("=" * 80)
    
    # Check API key
    if not os.getenv("PERPLEXITY_API_KEY"):
        logger.error("❌ PERPLEXITY_API_KEY not set")
        return
    
    tests = [
        ("Enhanced Premium Research", test_enhanced_premium_research),
        ("Client Sources with Premium", test_client_sources_with_premium),
        ("Timeframe Variations", test_timeframe_variations),
        ("Content Analysis Quality", test_content_analysis_quality),
        ("Agent Call Syntax", test_agent_call_syntax)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            logger.error(f"💥 {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Final summary
    logger.info("\n" + "=" * 80)
    logger.info("📊 ENHANCED RESEARCH SYSTEM TEST SUMMARY")
    logger.info("=" * 80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
    
    percentage = (passed / total) * 100
    logger.info(f"\n🎯 Overall Score: {passed}/{total} ({percentage:.1f}%)")
    
    if percentage >= 80:
        logger.info("🎉 EXCELLENT! Enhanced research system is ready for production")
    elif percentage >= 60:
        logger.info("👍 GOOD! System working well with minor issues")
    else:
        logger.info("⚠️ NEEDS WORK! Significant improvements required")


if __name__ == "__main__":
    # Set environment variable
    os.environ["PERPLEXITY_API_KEY"] = "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"
    
    # Run tests
    asyncio.run(main())
