"""
Workflow registry for dynamic workflow management.
"""

import logging
import os
from typing import Dict, Type, Any
from .base.workflow_base import WorkflowHandler

logger = logging.getLogger(__name__)


class WorkflowRegistry:
    """
    Registry for managing workflow handlers dynamically.

    This allows adding new workflow types without modifying core code.
    """

    def __init__(self):
        self._handlers: Dict[str, Type[WorkflowHandler]] = {}
        self._instances: Dict[str, WorkflowHandler] = {}
        logger.info("🏗️ Workflow registry initialized")

    def register(
        self, workflow_type: str, handler_class: Type[WorkflowHandler]
    ) -> None:
        """
        Register a workflow handler class.

        Args:
            workflow_type: Unique identifier for the workflow type
            handler_class: Handler class that inherits from WorkflowHandler
        """
        if not issubclass(handler_class, WorkflowHandler):
            raise ValueError(
                f"Handler must inherit from WorkflowHandler: {handler_class}"
            )

        self._handlers[workflow_type] = handler_class
        logger.info(
            f"📝 Registered workflow handler: {workflow_type} -> {handler_class.__name__}"
        )

    def get_handler(self, workflow_type: str) -> WorkflowHandler:
        """
        Get a workflow handler instance.

        Args:
            workflow_type: Type of workflow to get handler for

        Returns:
            WorkflowHandler instance

        Raises:
            ValueError: If workflow type is not registered
        """
        if workflow_type not in self._handlers:
            available_types = list(self._handlers.keys())
            raise ValueError(
                f"Unknown workflow type: {workflow_type}. Available: {available_types}"
            )

        # Use cached instance if available
        if workflow_type not in self._instances:
            handler_class = self._handlers[workflow_type]
            self._instances[workflow_type] = handler_class(workflow_type)
            logger.debug(f"🔧 Created new handler instance: {workflow_type}")

        return self._instances[workflow_type]

    def invalidate_cache(self, workflow_type: str = None) -> None:
        """
        Invalidate cached handler instances to force reload.

        Args:
            workflow_type: Specific workflow type to invalidate, or None for all
        """
        if workflow_type:
            if workflow_type in self._instances:
                del self._instances[workflow_type]
                logger.info(f"🔄 Invalidated cache for workflow: {workflow_type}")
        else:
            self._instances.clear()
            logger.info("🔄 Invalidated all workflow handler caches")

    def list_workflows(self) -> Dict[str, str]:
        """
        List all registered workflow types.

        Returns:
            Dictionary mapping workflow_type to handler class name
        """
        return {
            workflow_type: handler_class.__name__
            for workflow_type, handler_class in self._handlers.items()
        }

    def is_registered(self, workflow_type: str) -> bool:
        """Check if a workflow type is registered."""
        return workflow_type in self._handlers

    async def execute_workflow(
        self, workflow_type: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a workflow with dynamic context.

        Args:
            workflow_type: Type of workflow to execute
            context: Dynamic context from frontend

        Returns:
            Execution results
        """
        logger.info(f"🚀 Executing workflow: {workflow_type}")
        logger.debug(f"📊 Context keys: {list(context.keys())}")

        handler = self.get_handler(workflow_type)
        result = await handler.execute(context)

        logger.info(f"✅ Workflow execution completed: {workflow_type}")
        return result


# Global registry instance
workflow_registry = WorkflowRegistry()


def invalidate_workflow_cache(workflow_type: str = None) -> None:
    """Global function to invalidate workflow cache."""
    workflow_registry.invalidate_cache(workflow_type)


def register_workflow(workflow_type: str):
    """
    Decorator for registering workflow handlers.

    Usage:
        @register_workflow('enhanced_article')
        class EnhancedArticleHandler(WorkflowHandler):
            pass
    """

    def decorator(handler_class: Type[WorkflowHandler]):
        workflow_registry.register(workflow_type, handler_class)
        return handler_class

    return decorator


def get_workflow_handler(workflow_type: str) -> WorkflowHandler:
    """Get a workflow handler instance."""
    return workflow_registry.get_handler(workflow_type)


async def execute_dynamic_workflow(
    workflow_type: str, context: Dict[str, Any]
) -> Dict[str, Any]:
    """Execute a workflow with dynamic context."""
    # Add agent repository to context if not present
    if "agent_repository" not in context:
        from ..repositories.yaml_agent_repository import YamlAgentRepository

        context["agent_repository"] = YamlAgentRepository()

    # Add agent executor to context if not present
    if "agent_executor" not in context:
        from ..orchestration.agent_executor import AgentExecutor
        from ..external_services.openai_adapter import OpenAIAdapter
        from ...domain.value_objects.provider_config import ProviderConfig, LLMProvider
        from ..config.settings import Settings
        from ..tools.web_search_tool import WebSearchTool
        from ..tools.rag_tool import RAGTool
        from ..tools.perplexity_research_tool import PerplexityResearchTool
        from ..tools.image_generation_tool import image_generation_tool
        from ..tools.brand_style_guide_tool import BrandStyleGuideTool

        # Initialize with default settings
        settings = Settings()

        # Seed tool-cost env vars from Settings so tools that read os.getenv pick them up
        def _set_env_if(val, key):
            if val is not None:
                os.environ[key] = str(val)
        _set_env_if(settings.serper_cost_per_call_usd, "SERPER_COST_PER_CALL_USD")
        _set_env_if(settings.perplexity_cost_per_call_usd, "PERPLEXITY_COST_PER_CALL_USD")
        _set_env_if(settings.perplexity_cost_per_1k_tokens, "PERPLEXITY_COST_PER_1K_TOKENS")
        _set_env_if(
            settings.perplexity_sonar_cost_per_1k_tokens_input,
            "PERPLEXITY_SONAR_COST_PER_1K_TOKENS_INPUT",
        )
        _set_env_if(
            settings.perplexity_sonar_cost_per_1k_tokens_output,
            "PERPLEXITY_SONAR_COST_PER_1K_TOKENS_OUTPUT",
        )
        _set_env_if(
            settings.perplexity_sonar_pro_cost_per_1k_tokens_input,
            "PERPLEXITY_SONAR_PRO_COST_PER_1K_TOKENS_INPUT",
        )
        _set_env_if(
            settings.perplexity_sonar_pro_cost_per_1k_tokens_output,
            "PERPLEXITY_SONAR_PRO_COST_PER_1K_TOKENS_OUTPUT",
        )
        _set_env_if(settings.openai_image_cost_usd, "OPENAI_IMAGE_COST_USD")
        _set_env_if(settings.openai_image_cost_low_usd, "OPENAI_IMAGE_COST_LOW_USD")
        _set_env_if(settings.openai_image_cost_medium_usd, "OPENAI_IMAGE_COST_MEDIUM_USD")
        _set_env_if(settings.openai_image_cost_high_usd, "OPENAI_IMAGE_COST_HIGH_USD")
        _set_env_if(settings.gemini_image_cost_usd, "GEMINI_IMAGE_COST_USD")

        provider_config = ProviderConfig(
            provider=LLMProvider.OPENAI, model="gpt-4o", temperature=0.7
        )
        llm_provider = OpenAIAdapter(settings.openai_api_key)

        agent_executor = AgentExecutor(
            agent_repository=context["agent_repository"],
            llm_provider=llm_provider,
            provider_config=provider_config,
        )

        # Initialize and register tools (use canonical names)
        from ..tools.tool_names import ToolNames

        web_search_tool = WebSearchTool(settings.serper_api_key)
        rag_tool = RAGTool()
        perplexity_tool = PerplexityResearchTool(settings.perplexity_api_key)
        brand_style_tool = BrandStyleGuideTool()

        agent_executor.register_tools(
            {
                ToolNames.WEB_SEARCH_SERPER: {
                    "function": web_search_tool.search,
                    "description": "Search the web for current information and trends",
                    "metadata": {
                        "provider": "serper",
                        "category": "web_search",
                        # Prefer Settings-based pricing (loaded from .env), fallback to tool defaults
                        "cost_per_call_usd": settings.serper_cost_per_call_usd or web_search_tool.cost_per_call_usd,
                        "cost_source": ("env" if settings.serper_cost_per_call_usd is not None else web_search_tool.cost_source),
                    },
                },
                ToolNames.RAG_GET_CLIENT_CONTENT: {
                    "function": rag_tool.get_client_content,
                    "description": "Retrieve content from client knowledge base",
                    "metadata": {
                        "provider": "rag",
                        "category": "knowledge_base",
                        "cost_per_call_usd": 0.0,
                    },
                },
                ToolNames.RAG_SEARCH_CONTENT: {
                    "function": rag_tool.search_content,
                    "description": "Search within client knowledge base",
                    "metadata": {
                        "provider": "rag",
                        "category": "knowledge_base",
                        "cost_per_call_usd": 0.0,
                    },
                },
                ToolNames.WEB_SEARCH_PERPLEXITY: {
                    "function": perplexity_tool.search,
                    "description": "Search using Perplexity AI",
                    "metadata": {
                        "provider": "perplexity",
                        "category": "web_research",
                        "cost_per_call_usd": perplexity_tool.cost_per_call_usd,
                        "cost_per_1k_tokens_usd": perplexity_tool.cost_per_token_usd
                        * 1000,
                        "cost_source": perplexity_tool.cost_source,
                        "token_cost_source": perplexity_tool.token_cost_source,
                    },
                },
                ToolNames.IMAGE_GENERATION: {
                    "function": image_generation_tool,
                    "description": "Generate contextual images for the final article",
                    "metadata": {
                        "provider": "image_generation",
                        "category": "creative",
                        "cost_override_key": "image_generation_tool",
                    },
                },
                ToolNames.BRAND_STYLE_GUIDE: {
                    "function": brand_style_tool.get_style,
                    "description": "Retrieve brand palette and visual guardrails",
                    "metadata": {
                        "provider": "brand_style",
                        "category": "knowledge_base",
                        "cost_per_call_usd": 0.0,
                    },
                },
            }
        )

        context["agent_executor"] = agent_executor

    # Remove agent_repository from context before returning to avoid serialization issues
    result = await workflow_registry.execute_workflow(workflow_type, context)

    # Clean up non-serializable objects from result
    if "agent_repository" in result:
        del result["agent_repository"]
    if "agent_executor" in result:
        del result["agent_executor"]

    return result


def list_available_workflows() -> Dict[str, str]:
    """List all available workflow types."""
    return workflow_registry.list_workflows()
