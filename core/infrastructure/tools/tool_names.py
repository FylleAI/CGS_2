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
    WEB_SEARCH = "web_search"
    WEB_SEARCH_FINANCIAL = "web_search_financial"

    # RAG
    RAG_GET_CLIENT_CONTENT = "rag_get_client_content"
    RAG_SEARCH_CONTENT = "rag_search_content"

    # Perplexity
    PERPLEXITY_SEARCH = "perplexity_search"

    # Agent delegation
    RESEARCH_AGENT = "research_agent"


# Map legacy or variant names to canonical ToolNames values
ALIASES: Dict[str, str] = {
    # Legacy flip variant seen in code/comments
    # Legacy Perplexity tool names
    "research_premium_financial": ToolNames.PERPLEXITY_SEARCH,
    "research_client_sources": ToolNames.PERPLEXITY_SEARCH,
    "research_general_topic": ToolNames.PERPLEXITY_SEARCH,
    "research_financial_premium": ToolNames.PERPLEXITY_SEARCH,
    # Add more only when encountered in the codebase or YAML
}

