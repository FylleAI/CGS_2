"""Minimal AgentFactory to centralize Agent creation.

This factory resolves an Agent instance given an agent name (preferred) or a role,
optionally applying client-specific YAML overrides via AgentRepository.
"""
from __future__ import annotations

from typing import Optional, Dict, Any

from ...domain.entities.agent import Agent, AgentRole
from ...domain.repositories.agent_repository import AgentRepository


class AgentFactory:
    def __init__(self, agent_repository: AgentRepository | None = None) -> None:
        self.agent_repository = agent_repository

    async def get(self, *, name: Optional[str], role: Optional[AgentRole], ctx: Dict[str, Any]) -> Agent:
        """Resolve an Agent by name (preferred) or role, with client-specific overrides if present."""
        # Prefer explicit client_profile; fallback to client_name used elsewhere in context
        client_profile = (ctx or {}).get("client_profile") or (ctx or {}).get("client_name")

        import logging
        logger = logging.getLogger(__name__)
        logger.info(
            f"🧩 AgentFactory.get called with name={name}, role={getattr(role, 'value', None)}, client_profile={client_profile}"
        )

        # Log context keys for debugging
        context_keys = list((ctx or {}).keys())
        logger.debug(f"📋 Available context keys: {context_keys}")

        # Normalise legacy names
        if name == "research_specialist":
            name = "research_agent"

        # 1) Prefer client-specific YAML override by name
        if name and self.agent_repository:
            try:
                if client_profile:
                    # Try to get agents for this client and select by name
                    logger.debug(
                        f"🔍 Searching for client-specific agent '{name}' in profile '{client_profile}'"
                    )
                    client_agents = await getattr(self.agent_repository, "get_by_client_profile")(client_profile)  # type: ignore[attr-defined]
                    logger.debug(
                        f"📋 Found {len(client_agents)} agents for profile '{client_profile}': {[a.name for a in client_agents]}"
                    )

                    for a in client_agents:
                        if a.name == name:
                            logger.info(
                                f"✅ Resolved client-specific agent '{name}' for profile '{client_profile}'"
                            )
                            return a

                    # If client-specific agent not found, log warning but continue to fallback
                    logger.warning(
                        f"⚠️ Client-specific agent '{name}' not found for profile '{client_profile}', trying global search"
                    )

                # Fallback: global search by name (may return default profile)
                logger.debug(f"🔍 Searching for global agent '{name}'")
                agent = await getattr(self.agent_repository, "get_by_name")(name)  # type: ignore[attr-defined]
                if agent:
                    if client_profile:
                        logger.warning(
                            f"⚠️ Using global agent '{name}' instead of client-specific for profile '{client_profile}'"
                        )
                    else:
                        logger.info(
                            f"✅ Resolved global agent by name '{name}' (no client profile specified)"
                        )
                    return agent
            except Exception as e:
                logger.warning(f"⚠️ Agent resolution via repository failed: {e}")

        agent = None

        # 2) Fallback by role (basic agent) - with warning for client-specific contexts
        if agent is None and role:
            fallback_name = f"{role.value}_agent"
            agent = Agent(name=fallback_name, role=role, tools=[])
            if client_profile and client_profile != 'default':
                logger.warning(
                    f"⚠️ Using ROLE-based fallback agent '{fallback_name}' for client '{client_profile}' - client-specific agent not found"
                )
            else:
                logger.info(f"ℹ️ Using ROLE-based fallback agent '{fallback_name}'")

        # 3) Last resort: generic researcher - with strong warning for client-specific contexts
        if agent is None:
            agent = Agent(name="researcher_agent", role=AgentRole.RESEARCHER, tools=[])
            if client_profile and client_profile != 'default':
                logger.error(
                    f"🚨 Using LAST-RESORT generic researcher agent for client '{client_profile}' - this may cause brand compliance issues"
                )
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

        logger.info(
            f"🤝 Final agent resolved: name={agent.name}, role={getattr(agent.role, 'value', None)}"
        )
        return agent
