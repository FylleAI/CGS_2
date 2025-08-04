#!/usr/bin/env python3
"""
Test script for the Perplexity Research Tool.

This script tests the new Perplexity tool to ensure it works correctly
before integrating into workflows.
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


async def test_perplexity_api_key():
    """Test if Perplexity API key is configured."""
    logger.info("🧪 Testing Perplexity API key configuration...")
    
    api_key = os.getenv("PERPLEXITY_API_KEY")
    
    if not api_key:
        logger.error("❌ PERPLEXITY_API_KEY not found in environment")
        return False
    
    if not api_key.startswith("pplx-"):
        logger.error("❌ Invalid Perplexity API key format")
        return False
    
    logger.info(f"✅ Perplexity API key configured: {api_key[:10]}...")
    return True


async def test_tool_initialization():
    """Test tool initialization."""
    logger.info("🧪 Testing PerplexityResearchTool initialization...")
    
    api_key = os.getenv("PERPLEXITY_API_KEY")
    tool = PerplexityResearchTool(api_key)
    
    if not tool.api_key:
        logger.error("❌ Tool API key not set")
        return False
    
    logger.info("✅ Tool initialized successfully")
    return True


async def test_premium_financial_research():
    """Test premium financial research functionality."""
    logger.info("🧪 Testing premium financial research...")
    
    api_key = os.getenv("PERPLEXITY_API_KEY")
    tool = PerplexityResearchTool(api_key)
    
    try:
        # Test with a simple financial topic
        topic = "artificial intelligence market trends"
        exclude_topics = "crypto,day_trading"
        
        logger.info(f"🔍 Researching: {topic}")
        result = await tool.research_premium_financial(topic, exclude_topics)
        
        # Parse the result
        import json
        result_data = json.loads(result)
        
        if "error" in result_data:
            logger.error(f"❌ Research failed: {result_data['error']}")
            return False
        
        logger.info(f"✅ Research successful!")
        logger.info(f"📊 Content length: {len(result_data.get('content', ''))}")
        logger.info(f"📚 Citations found: {result_data.get('total_citations', 0)}")
        
        # Show first 200 characters of content
        content = result_data.get('content', '')
        if content:
            logger.info(f"📄 Content preview: {content[:200]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Premium financial research test failed: {e}")
        return False


async def test_client_sources_research():
    """Test client-specific sources research."""
    logger.info("🧪 Testing client sources research...")
    
    api_key = os.getenv("PERPLEXITY_API_KEY")
    tool = PerplexityResearchTool(api_key)
    
    try:
        # Test with Siebert client
        client_name = "siebert"
        topic = "financial market outlook 2025"
        days_back = 7
        
        logger.info(f"🎯 Researching for client {client_name}: {topic}")
        result = await tool.research_client_sources(client_name, topic, days_back)
        
        # Parse the result
        import json
        result_data = json.loads(result)
        
        if "error" in result_data:
            logger.error(f"❌ Client research failed: {result_data['error']}")
            return False
        
        logger.info(f"✅ Client research successful!")
        logger.info(f"👤 Client: {result_data.get('client', 'unknown')}")
        logger.info(f"📊 Content length: {len(result_data.get('content', ''))}")
        logger.info(f"📚 Citations found: {result_data.get('total_citations', 0)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Client sources research test failed: {e}")
        return False


async def test_general_topic_research():
    """Test general topic research."""
    logger.info("🧪 Testing general topic research...")
    
    api_key = os.getenv("PERPLEXITY_API_KEY")
    tool = PerplexityResearchTool(api_key)
    
    try:
        # Test with a general topic
        topic = "renewable energy trends 2025"
        
        logger.info(f"🌐 Researching general topic: {topic}")
        result = await tool.research_general_topic(topic)
        
        # Parse the result
        import json
        result_data = json.loads(result)
        
        if "error" in result_data:
            logger.error(f"❌ General research failed: {result_data['error']}")
            return False
        
        logger.info(f"✅ General research successful!")
        logger.info(f"📊 Content length: {len(result_data.get('content', ''))}")
        logger.info(f"📚 Citations found: {result_data.get('total_citations', 0)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ General topic research test failed: {e}")
        return False


async def test_tool_call_syntax():
    """Test tool call syntax (simulating agent usage)."""
    logger.info("🧪 Testing tool call syntax...")
    
    api_key = os.getenv("PERPLEXITY_API_KEY")
    tool = PerplexityResearchTool(api_key)
    
    try:
        # Test comma-separated input (as agents would call it)
        input_string = "artificial intelligence, crypto,day_trading"
        
        logger.info(f"🤖 Testing agent-style call: {input_string}")
        result = await tool.research_premium_financial(input_string)
        
        # Parse the result
        import json
        result_data = json.loads(result)
        
        if "error" in result_data:
            logger.error(f"❌ Tool call syntax test failed: {result_data['error']}")
            return False
        
        logger.info(f"✅ Tool call syntax test successful!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Tool call syntax test failed: {e}")
        return False


async def main():
    """Run all tests."""
    logger.info("🚀 Starting Perplexity Research Tool Tests")
    logger.info("=" * 60)
    
    tests = [
        ("API Key Configuration", test_perplexity_api_key),
        ("Tool Initialization", test_tool_initialization),
        ("Premium Financial Research", test_premium_financial_research),
        ("Client Sources Research", test_client_sources_research),
        ("General Topic Research", test_general_topic_research),
        ("Tool Call Syntax", test_tool_call_syntax)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running: {test_name}")
        logger.info("-" * 40)
        
        try:
            success = await test_func()
            results.append((test_name, success))
            
            if success:
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            logger.error(f"💥 {test_name}: CRASHED - {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
    
    logger.info(f"\n🏁 Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Perplexity tool is ready for integration.")
    else:
        logger.warning(f"⚠️ {total - passed} tests failed. Please review and fix issues.")


if __name__ == "__main__":
    # Check dependencies
    try:
        import aiohttp
    except ImportError:
        logger.error("❌ Missing dependency: aiohttp")
        logger.info("💡 Install with: pip install aiohttp")
        sys.exit(1)
    
    # Run tests
    asyncio.run(main())
