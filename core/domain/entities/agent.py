"""Agent entity - represents an AI agent in the content generation system."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from enum import Enum

from ..value_objects.provider_config import ProviderConfig


class AgentRole(Enum):
    """Predefined agent roles."""
    RESEARCHER = "researcher"
    WRITER = "writer"
    COPYWRITER = "copywriter"
    EDITOR = "editor"
    ANALYST = "analyst"
    PLANNER = "planner"
    RAG_SPECIALIST = "rag_specialist"
    WEB_SCRAPER = "web_scraper"
    PREMIUM_ANALYZER = "premium_analyzer"
    COMPLIANCE_REVIEWER = "compliance_reviewer"
    ENHANCED_ARTICLE_WRITER = "enhanced_article_writer"
    ENHANCED_ARTICLE_COMPLIANCE_SPECIALIST = "enhanced_article_compliance_specialist"


@dataclass
class Agent:
    """
    Agent entity representing an AI agent with specific capabilities.
    
    An agent is a specialized AI entity that can perform specific tasks
    in the content generation workflow.
    """
    
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    role: AgentRole = AgentRole.RESEARCHER
    goal: str = ""
    backstory: str = ""
    system_message: str = ""
    provider_config: ProviderConfig = field(default_factory=lambda: ProviderConfig())
    tools: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    
    def __post_init__(self) -> None:
        """Validate agent after initialization."""
        if not self.name:
            self.name = f"{self.role.value}_agent"
        
        if not self.goal:
            self.goal = self._default_goal_for_role()
    
    def _default_goal_for_role(self) -> str:
        """Get default goal based on agent role."""
        default_goals = {
            AgentRole.RESEARCHER: "Gather comprehensive and accurate information on given topics",
            AgentRole.COPYWRITER: "Create engaging and well-structured content",
            AgentRole.EDITOR: "Review and improve content for clarity and quality",
            AgentRole.RAG_SPECIALIST: "Retrieve and analyze relevant information from knowledge bases",
            AgentRole.WEB_SCRAPER: "Extract and process information from web sources",
            AgentRole.PREMIUM_ANALYZER: "Analyze premium sources and financial data",
            AgentRole.COMPLIANCE_REVIEWER: "Review content for regulatory compliance and risk management",
            AgentRole.ENHANCED_ARTICLE_WRITER: "Create comprehensive educational articles with Gen Z voice and research integration",
            AgentRole.ENHANCED_ARTICLE_COMPLIANCE_SPECIALIST: "Review Enhanced Articles for FINRA/SEC compliance while preserving Gen Z voice and blog structure"
        }
        return default_goals.get(self.role, "Perform specialized tasks in content generation")
    
    def can_use_tool(self, tool_name: str) -> bool:
        """Check if agent can use a specific tool."""
        return tool_name in self.tools
    
    def add_tool(self, tool_name: str) -> None:
        """Add a tool to the agent's capabilities."""
        if tool_name not in self.tools:
            self.tools.append(tool_name)
    
    def remove_tool(self, tool_name: str) -> None:
        """Remove a tool from the agent's capabilities."""
        if tool_name in self.tools:
            self.tools.remove(tool_name)
    
    def update_provider_config(self, provider_config: ProviderConfig) -> None:
        """Update the agent's provider configuration."""
        self.provider_config = provider_config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary representation."""
        return {
            "id": str(self.id),
            "name": self.name,
            "role": self.role.value,
            "goal": self.goal,
            "backstory": self.backstory,
            "system_message": self.system_message,
            "provider_config": self.provider_config.to_dict(),
            "tools": self.tools,
            "examples": self.examples,
            "metadata": self.metadata,
            "is_active": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Agent":
        """Create agent from dictionary representation."""
        return cls(
            id=UUID(data["id"]) if "id" in data else uuid4(),
            name=data.get("name", ""),
            role=AgentRole(data.get("role", "researcher")),
            goal=data.get("goal", ""),
            backstory=data.get("backstory", ""),
            system_message=data.get("system_message", ""),
            provider_config=ProviderConfig.from_dict(data.get("provider_config", {})),
            tools=data.get("tools", []),
            examples=data.get("examples", []),
            metadata=data.get("metadata", {}),
            is_active=data.get("is_active", True)
        )
