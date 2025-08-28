"""Minimal AgentFactory to centralize Agent creation.

This factory resolves an Agent instance given an agent name (preferred) or a role,
optionally applying client-specific YAML overrides via AgentRepository.
"""
from __future__ import annotations

from typing import Optional, Dict, Any

from ...domain.entities.agent import Agent, AgentRole
from ...domain.repositories.agent_repository import AgentRepository


from ..tools.tool_names import ToolNames, ALIASES

DEFAULT_AGENTS: Dict[str, Dict[str, Any]] = {
    "rag_specialist": {
        "role": AgentRole.RESEARCHER,
        "tools": [ToolNames.RAG_GET_CLIENT_CONTENT, ToolNames.RAG_SEARCH_CONTENT],
        "system_message": "You specialize in retrieving relevant information from knowledge bases and creating structured briefs."
    },
    "web_searcher": {
        "role": AgentRole.RESEARCHER,
        "tools": [ToolNames.WEB_SEARCH, ToolNames.WEB_SEARCH_FINANCIAL],
        "system_message": "You specialize in web research and finding current trends and information."
    },
    "perplexity_researcher": {
        "role": AgentRole.RESEARCHER,
        "tools": [
            ToolNames.RESEARCH_PREMIUM_FINANCIAL,
            ToolNames.RESEARCH_CLIENT_SOURCES,
            ToolNames.RESEARCH_GENERAL_TOPIC
        ],
        "system_message": (
            "You are a premium financial researcher for Gen Z/Millennial investors. "
            "Always use Perplexity tools to gather multi-source evidence: first from client-specific sources (blog.siebert.com and related), "
            "then from premium financial sources (DailyUpside, MorningBrew, Axios, MoneyWithKatie, The Hustle), and finally general topic checks. "
            "Respect workflow variables research_timeframe, exclude_topics, premium_sources, siebert_target_urls. "
            "Return a compact JSON object with keys: client_sources, premium_financial, general. "
            "Each key must include: highlights (bullet points), citations (URL array), and quality (scores or short notes)."
        )
    },
    "copywriter": {
        "role": AgentRole.WRITER,
        "tools": [],
        "system_message": "You create high-quality, engaging content that meets specific requirements and brand guidelines."
    },
    "enhanced_article_writer": {
        "role": AgentRole.ENHANCED_ARTICLE_WRITER,
        "tools": [],
        "system_message": "You write enhanced articles aligned with brand voice and target audience."
    },
    "enhanced_article_compliance_specialist": {
        "role": AgentRole.ENHANCED_ARTICLE_COMPLIANCE_SPECIALIST,
        "tools": [],
        "system_message": "You review content for compliance (e.g., FINRA/SEC) ensuring adherence to regulatory standards."
    },
    "analyst": {
        "role": AgentRole.ANALYST,
        "tools": [],
        "system_message": (
            "You are an analytical writer who synthesizes research into structured newsletter content. "
            "Use ONLY provided research data. Do NOT invent facts. "
            "Prioritize: feature story, 3-4 key trends, 3-5 stats, 3 actionable steps. "
            "Cite source URLs inline where relevant. Maintain Gen Z tone and mobile-first brevity."
        )
    },
}


class AgentFactory:
    def __init__(self, agent_repository: AgentRepository | None = None) -> None:
        self.agent_repository = agent_repository

    async def get(self, *, name: Optional[str], role: Optional[AgentRole], ctx: Dict[str, Any]) -> Agent:
        """Resolve an Agent by name (preferred) or role, with client-specific overrides if present."""
        # Prefer explicit client_profile; fallback to client_name used elsewhere in context
        client_profile = (ctx or {}).get("client_profile") or (ctx or {}).get("client_name")

        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"🧩 AgentFactory.get called with name={name}, role={getattr(role, 'value', None)}, client_profile={client_profile}")

        # Log context keys for debugging
        context_keys = list((ctx or {}).keys())
        logger.debug(f"📋 Available context keys: {context_keys}")

        # 1) Prefer client-specific YAML override by name
        if name and self.agent_repository:
            try:
                if client_profile:
                    # Try to get agents for this client and select by name
                    logger.debug(f"🔍 Searching for client-specific agent '{name}' in profile '{client_profile}'")
                    client_agents = await getattr(self.agent_repository, "get_by_client_profile")(client_profile)  # type: ignore[attr-defined]
                    logger.debug(f"📋 Found {len(client_agents)} agents for profile '{client_profile}': {[a.name for a in client_agents]}")

                    for a in client_agents:
                        if a.name == name:
                            logger.info(f"✅ Resolved client-specific agent '{name}' for profile '{client_profile}'")
                            return a

                    # If client-specific agent not found, log warning but continue to fallback
                    logger.warning(f"⚠️ Client-specific agent '{name}' not found for profile '{client_profile}', trying global search")

                # Fallback: global search by name (may return default profile)
                logger.debug(f"🔍 Searching for global agent '{name}'")
                agent = await getattr(self.agent_repository, "get_by_name")(name)  # type: ignore[attr-defined]
                if agent:
                    if client_profile:
                        logger.warning(f"⚠️ Using global agent '{name}' instead of client-specific for profile '{client_profile}'")
                    else:
                        logger.info(f"✅ Resolved global agent by name '{name}' (no client profile specified)")
                    return agent
            except Exception as e:
                logger.warning(f"⚠️ Agent resolution via repository failed: {e}")

        # 2) Default catalog by name (with warning if client-specific was expected)
        if name and name in DEFAULT_AGENTS:
            spec = DEFAULT_AGENTS[name]
            agent = Agent(name=name, role=spec["role"], tools=spec.get("tools", []), system_message=spec.get("system_message", ""))
            if client_profile:
                logger.warning(f"⚠️ Using DEFAULT agent spec for '{name}' instead of client-specific for profile '{client_profile}'")
            else:
                logger.info(f"ℹ️ Using DEFAULT agent spec for name '{name}'")
        else:
            agent = None

        # 3) Fallback by role (basic agent) - with warning for client-specific contexts
        if agent is None and role:
            # Simple role-based fallback; name derived from role
            fallback_name = f"{role.value}_agent"
            agent = Agent(name=fallback_name, role=role, tools=[])
            if client_profile and client_profile != 'default':
                logger.warning(f"⚠️ Using ROLE-based fallback agent '{fallback_name}' for client '{client_profile}' - client-specific agent not found")
            else:
                logger.info(f"ℹ️ Using ROLE-based fallback agent '{fallback_name}'")

        # 4) Last resort: generic researcher - with strong warning for client-specific contexts
        if agent is None:
            agent = Agent(name="researcher_agent", role=AgentRole.RESEARCHER, tools=[])
            if client_profile and client_profile != 'default':
                logger.error(f"🚨 Using LAST-RESORT generic researcher agent for client '{client_profile}' - this may cause brand compliance issues")
            else:
                logger.info("ℹ️ Using LAST-RESORT generic researcher agent")

        # Validate tools are available in context
        agent_executor = (ctx or {}).get('agent_executor')
        if agent_executor and getattr(agent, 'tools', None):
            try:
                available_tools = set(getattr(agent_executor, 'tools_registry', {}).keys())
                missing_tools = set(agent.tools) - available_tools
                if missing_tools:
                    logger.warning(f"⚠️ Agent {agent.name} has unregistered tools: {missing_tools}")
            except Exception:
                pass

        logger.info(f"🤝 Final agent resolved: name={agent.name}, role={getattr(agent.role, 'value', None)}")
        return agent

