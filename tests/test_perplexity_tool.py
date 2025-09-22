import os
import pytest

from core.infrastructure.tools.perplexity_research_tool import PerplexityResearchTool


@pytest.mark.asyncio
async def test_api_key_format():
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        pytest.skip("PERPLEXITY_API_KEY not set")
    assert api_key.startswith("pplx-")


@pytest.mark.asyncio
async def test_basic_search():
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        pytest.skip("PERPLEXITY_API_KEY not set")

    tool = PerplexityResearchTool(api_key)
    result = await tool.search("test query")
    assert isinstance(result, dict)
    assert "data" in result
    assert "choices" in result["data"] or "error" in result["data"]
