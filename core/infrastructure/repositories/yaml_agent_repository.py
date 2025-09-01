"""YAML-based agent repository implementation."""

import yaml
import logging
import asyncio
from typing import List, Optional
from uuid import UUID
from pathlib import Path

from ...domain.entities.agent import Agent, AgentRole
from ...domain.repositories.agent_repository import AgentRepository

logger = logging.getLogger(__name__)


class YamlAgentRepository(AgentRepository):
    """
    YAML-based implementation of AgentRepository.
    
    This implementation stores agent configurations as YAML files,
    organized by client profiles.
    """
    
    def __init__(self, base_path: str = "data/profiles"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _get_agent_file_path(self, client_profile: str, agent_name: str) -> Path:
        """Get file path for agent configuration."""
        return self.base_path / client_profile / "agents" / f"{agent_name}.yaml"
    
    async def _load_agent_from_file(self, file_path: Path) -> Optional[Agent]:
        """Load agent from YAML file without blocking the event loop."""
        try:
            if not file_path.exists():
                return None

            def read_file() -> dict:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)

            data = await asyncio.to_thread(read_file)

            return Agent(
                name=data.get('name', file_path.stem),
                role=AgentRole(data.get('role', 'researcher')),
                goal=data.get('goal', ''),
                backstory=data.get('backstory', ''),
                system_message=data.get('system_message', ''),
                tools=data.get('tools', []),
                examples=data.get('examples', []),
                metadata=data.get('metadata', {})
            )

        except Exception as e:
            logger.error(f"Failed to load agent from {file_path}: {str(e)}")
            return None

    async def _save_agent_to_file(self, agent: Agent, file_path: Path) -> bool:
        """Save agent to YAML file without blocking the event loop."""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)

            data = {
                'name': agent.name,
                'role': agent.role.value,
                'goal': agent.goal,
                'backstory': agent.backstory,
                'system_message': agent.system_message,
                'tools': agent.tools,
                'examples': agent.examples,
                'metadata': agent.metadata,
                'is_active': agent.is_active
            }

            def write_file() -> None:
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

            await asyncio.to_thread(write_file)
            return True

        except Exception as e:
            logger.error(f"Failed to save agent to {file_path}: {str(e)}")
            return False
    
    async def save(self, agent: Agent) -> Agent:
        """Save an agent."""
        # For YAML implementation, we need a client profile context
        # This is a simplified implementation
        client_profile = agent.metadata.get('client_profile', 'default')
        file_path = self._get_agent_file_path(client_profile, agent.name)
        
        if await self._save_agent_to_file(agent, file_path):
            return agent
        else:
            raise Exception(f"Failed to save agent {agent.name}")
    
    async def get_by_id(self, agent_id: UUID) -> Optional[Agent]:
        """Get an agent by ID."""
        # For YAML implementation, we search through all files
        all_agents = await self.get_all()
        for agent in all_agents:
            if agent.id == agent_id:
                return agent
        return None
    
    async def get_by_name(self, name: str) -> Optional[Agent]:
        """Get an agent by name."""
        # Search through all client profiles
        for profile_dir in self.base_path.iterdir():
            if profile_dir.is_dir():
                agents_dir = profile_dir / "agents"
                if agents_dir.exists():
                    agent_file = agents_dir / f"{name}.yaml"
                    agent = await self._load_agent_from_file(agent_file)
                    if agent:
                        return agent
        return None
    
    async def get_by_role(self, role: AgentRole) -> List[Agent]:
        """Get all agents with a specific role."""
        all_agents = await self.get_all()
        return [agent for agent in all_agents if agent.role == role]
    
    async def get_all(self) -> List[Agent]:
        """Get all agents."""
        agents = []
        
        for profile_dir in self.base_path.iterdir():
            if profile_dir.is_dir():
                agents_dir = profile_dir / "agents"
                if agents_dir.exists():
                    for agent_file in agents_dir.glob("*.yaml"):
                        agent = await self._load_agent_from_file(agent_file)
                        if agent:
                            agent.metadata['client_profile'] = profile_dir.name
                            agents.append(agent)
        
        return agents
    
    async def get_active(self) -> List[Agent]:
        """Get all active agents."""
        all_agents = await self.get_all()
        return [agent for agent in all_agents if agent.is_active]
    
    async def update(self, agent: Agent) -> Agent:
        """Update an existing agent."""
        # Same as save for YAML implementation
        return await self.save(agent)
    
    async def delete(self, agent_id: UUID) -> bool:
        """Delete an agent."""
        agent = await self.get_by_id(agent_id)
        if not agent:
            return False
        
        client_profile = agent.metadata.get('client_profile', 'default')
        file_path = self._get_agent_file_path(client_profile, agent.name)
        
        try:
            if file_path.exists():
                file_path.unlink()
                return True
        except Exception as e:
            logger.error(f"Failed to delete agent file {file_path}: {str(e)}")
        
        return False
    
    async def exists(self, agent_id: UUID) -> bool:
        """Check if an agent exists."""
        agent = await self.get_by_id(agent_id)
        return agent is not None
    
    async def get_by_client_profile(self, profile_name: str) -> List[Agent]:
        """Get agents configured for a specific client profile."""
        agents = []
        profile_dir = self.base_path / profile_name
        
        if profile_dir.exists():
            agents_dir = profile_dir / "agents"
            if agents_dir.exists():
                for agent_file in agents_dir.glob("*.yaml"):
                    agent = await self._load_agent_from_file(agent_file)
                    if agent:
                        agent.metadata['client_profile'] = profile_name
                        agents.append(agent)
        
        return agents
    
    async def get_agents_with_tool(self, tool_name: str) -> List[Agent]:
        """Get agents that can use a specific tool."""
        all_agents = await self.get_all()
        return [agent for agent in all_agents if agent.can_use_tool(tool_name)]
    
    async def search(self, query: str) -> List[Agent]:
        """Search agents by name, role, or description."""
        all_agents = await self.get_all()
        query_lower = query.lower()
        
        results = []
        for agent in all_agents:
            if (query_lower in agent.name.lower() or
                query_lower in agent.role.value.lower() or
                query_lower in agent.goal.lower() or
                query_lower in agent.backstory.lower()):
                results.append(agent)
        
        return results
