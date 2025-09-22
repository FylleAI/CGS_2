"""Canonical tool names and alias mappings.

Centralize tool name constants to ensure consistent references across:
- Agent YAML definitions
- Tool registration (AgentExecutor)
- Prompts and runtime parsing

Add aliases only for backward compatibility or minor naming variants.
Avoid aliases that change semantics or parameter signatures.
"""
from __future__ import annotations

from typing import Dict


class ToolNames:
    # Web search
    WEB_SEARCH_SERPER = "web_search"
    WEB_SEARCH_PERPLEXITY = "perplexity_search"

    # RAG
    RAG_GET_CLIENT_CONTENT = "rag_get_client_content"
    RAG_SEARCH_CONTENT = "rag_search_content"

    # Image generation
    IMAGE_GENERATION = "image_generation_tool"


# Map legacy or variant names to canonical ToolNames values
ALIASES: Dict[str, str] = {
    # Legacy Perplexity research variants
    "research_premium_financial": ToolNames.WEB_SEARCH_PERPLEXITY,
    "research_client_sources": ToolNames.WEB_SEARCH_PERPLEXITY,
    "research_general_topic": ToolNames.WEB_SEARCH_PERPLEXITY,
    "research_financial_premium": ToolNames.WEB_SEARCH_PERPLEXITY,
    # Legacy web search variant
    "web_search_financial": ToolNames.WEB_SEARCH_SERPER,
    # Image generation variants
    "image_generation": ToolNames.IMAGE_GENERATION,
    "generate_image": ToolNames.IMAGE_GENERATION,
    # Add more only when encountered in the codebase or YAML
}

