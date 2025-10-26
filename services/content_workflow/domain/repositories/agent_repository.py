"""Agent repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities.agent import Agent, AgentRole


class AgentRepository(ABC):
    """
    Abstract repository for agent persistence.

    This interface defines the contract for agent data access,
    allowing different implementations (file-based, database, etc.)
    """

    @abstractmethod
    async def save(self, agent: Agent) -> Agent:
        """
        Save an agent.

        Args:
            agent: The agent to save

        Returns:
            The saved agent with any generated fields populated
        """
        pass

    @abstractmethod
    async def get_by_id(self, agent_id: UUID) -> Optional[Agent]:
        """
        Get an agent by ID.

        Args:
            agent_id: The agent ID

        Returns:
            The agent if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Agent]:
        """
        Get an agent by name.

        Args:
            name: The agent name

        Returns:
            The agent if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_role(self, role: AgentRole) -> List[Agent]:
        """
        Get all agents with a specific role.

        Args:
            role: The agent role

        Returns:
            List of agents with the specified role
        """
        pass

    @abstractmethod
    async def get_all(self) -> List[Agent]:
        """
        Get all agents.

        Returns:
            List of all agents
        """
        pass

    @abstractmethod
    async def get_active(self) -> List[Agent]:
        """
        Get all active agents.

        Returns:
            List of active agents
        """
        pass

    @abstractmethod
    async def update(self, agent: Agent) -> Agent:
        """
        Update an existing agent.

        Args:
            agent: The agent to update

        Returns:
            The updated agent

        Raises:
            ValueError: If agent doesn't exist
        """
        pass

    @abstractmethod
    async def delete(self, agent_id: UUID) -> bool:
        """
        Delete an agent.

        Args:
            agent_id: The agent ID to delete

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def exists(self, agent_id: UUID) -> bool:
        """
        Check if an agent exists.

        Args:
            agent_id: The agent ID to check

        Returns:
            True if exists, False otherwise
        """
        pass

    @abstractmethod
    async def get_by_client_profile(self, profile_name: str) -> List[Agent]:
        """
        Get agents configured for a specific client profile.

        Args:
            profile_name: The client profile name

        Returns:
            List of agents for the profile
        """
        pass

    @abstractmethod
    async def get_agents_with_tool(self, tool_name: str) -> List[Agent]:
        """
        Get agents that can use a specific tool.

        Args:
            tool_name: The tool name

        Returns:
            List of agents that can use the tool
        """
        pass

    @abstractmethod
    async def search(self, query: str) -> List[Agent]:
        """
        Search agents by name, role, or description.

        Args:
            query: The search query

        Returns:
            List of matching agents
        """
        pass
