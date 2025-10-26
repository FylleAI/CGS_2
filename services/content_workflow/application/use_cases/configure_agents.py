"""Configure agents use case."""

import logging
from typing import List, Optional
from uuid import UUID

from ...domain.entities.agent import Agent, AgentRole
from ...domain.repositories.agent_repository import AgentRepository

logger = logging.getLogger(__name__)


class ConfigureAgentsUseCase:
    """
    Use case for configuring agents.

    This use case handles agent creation, updating, deletion,
    and listing operations.
    """

    def __init__(self, agent_repository: AgentRepository):
        self.agent_repository = agent_repository

    async def create_agent(self, agent_data: dict) -> Agent:
        """Create a new agent."""
        agent = Agent(
            name=agent_data.get("name", ""),
            role=AgentRole(agent_data.get("role", "researcher")),
            goal=agent_data.get("goal", ""),
            backstory=agent_data.get("backstory", ""),
            system_message=agent_data.get("system_message", ""),
            tools=agent_data.get("tools", []),
        )

        return await self.agent_repository.save(agent)

    async def get_agent(self, agent_id: UUID) -> Optional[Agent]:
        """Get an agent by ID."""
        return await self.agent_repository.get_by_id(agent_id)

    async def list_agents(self, client_profile: Optional[str] = None) -> List[Agent]:
        """List agents, optionally filtered by client profile."""
        if client_profile:
            return await self.agent_repository.get_by_client_profile(client_profile)
        return await self.agent_repository.get_all()

    async def update_agent(self, agent: Agent) -> Agent:
        """Update an existing agent."""
        return await self.agent_repository.update(agent)

    async def delete_agent(self, agent_id: UUID) -> bool:
        """Delete an agent."""
        return await self.agent_repository.delete(agent_id)
