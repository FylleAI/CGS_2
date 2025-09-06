#!/usr/bin/env python3
"""Simple smoke tests for the PerplexityResearchTool."""

import asyncio
import os
import logging
from dotenv import load_dotenv

load_dotenv()

from core.infrastructure.tools.perplexity_research_tool import PerplexityResearchTool

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_api_key() -> bool:
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        logger.warning("PERPLEXITY_API_KEY missing; skipping live search test")
        return True
    if not api_key.startswith("pplx-"):
        logger.error("Invalid API key format")
        return False
    return True

async def test_basic_search() -> bool:
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        # Skip when key not available
        return True
    tool = PerplexityResearchTool(api_key)
    try:
        result = await tool.search("test query")
        return bool(result)
    except Exception as exc:
        logger.error(f"Search failed: {exc}")
        return False

async def main() -> None:
    tests = [
        ("API key", test_api_key),
        ("Basic search", test_basic_search),
    ]
    for name, fn in tests:
        ok = await fn()
        status = "PASSED" if ok else "FAILED"
        logger.info(f"{name}: {status}")

if __name__ == "__main__":
    asyncio.run(main())
