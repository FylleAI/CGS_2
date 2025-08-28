"""Canonical tool names and alias mappings.

Centralize tool name constants to ensure consistent references across:
- Agent definitions (DEFAULT_AGENTS and YAML)
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

    # Perplexity research
    RESEARCH_PREMIUM_FINANCIAL = "research_premium_financial"
    RESEARCH_CLIENT_SOURCES = "research_client_sources"
    RESEARCH_GENERAL_TOPIC = "research_general_topic"


# Map legacy or variant names to canonical ToolNames values
ALIASES: Dict[str, str] = {
    # Legacy flip variant seen in code/comments
    "research_financial_premium": ToolNames.RESEARCH_PREMIUM_FINANCIAL,
    # Add more only when encountered in the codebase or YAML
}

