"""Simple system prompt builder for agents."""

from typing import Any, Dict

from ...domain.entities.agent import Agent, AgentRole


class SimpleSystemPromptBuilder:
    """Build system prompts for agents using existing inline logic."""

    def build(
        self, agent: Agent, context: Dict[str, Any], tool_descriptions: str
    ) -> str:
        """Compose the system message exactly as the legacy implementation."""
        context = context or {}

        if agent.system_message:
            system_message = agent.system_message
        else:
            role_messages = {
                AgentRole.RESEARCHER: "You are an expert researcher who finds accurate, relevant information and presents it clearly.",
                AgentRole.WRITER: "You are an expert writer who creates engaging, well-structured content tailored to specific audiences.",
                AgentRole.EDITOR: "You are an expert editor who refines content for clarity, coherence, and alignment with style guidelines.",
                AgentRole.ANALYST: "You are an expert analyst who examines data and information to extract meaningful insights.",
                AgentRole.PLANNER: "You are an expert planner who organizes complex tasks into clear, actionable steps.",
                AgentRole.COMPLIANCE_REVIEWER: "You are an expert compliance reviewer who ensures content meets regulatory standards and risk management requirements.",
            }
            system_message = role_messages.get(
                agent.role, "You are an AI assistant helping with content generation."
            )

        if agent.backstory:
            system_message += f"\n\n{agent.backstory}"

        if agent.goal:
            system_message += f"\n\nYour goal is: {agent.goal}"

        if context.get("client_profile"):
            system_message += (
                f"\n\nYou are working for client: {context.get('client_profile')}"
            )

        if context.get("target_audience"):
            system_message += (
                f"\n\nThe target audience is: {context.get('target_audience')}"
            )

        if tool_descriptions:
            system_message += (
                f"\n\nYou have access to the following tools:\n{tool_descriptions}"
            )
            from ..tools.tool_names import ToolNames

            system_message += "\n\nIMPORTANT: When you need to use a tool, format your response EXACTLY like this:"
            system_message += f"\n[{ToolNames.RAG_GET_CLIENT_CONTENT}] client_name [/{ToolNames.RAG_GET_CLIENT_CONTENT}]"
            system_message += f"\n[{ToolNames.RAG_GET_CLIENT_CONTENT}] client_name, document_name [/{ToolNames.RAG_GET_CLIENT_CONTENT}]"
            system_message += f"\n[{ToolNames.RAG_SEARCH_CONTENT}] client_name, search_query [/{ToolNames.RAG_SEARCH_CONTENT}]"
            system_message += f"\n[{ToolNames.RAG_SEARCH_CONTENT}] search_query [/{ToolNames.RAG_SEARCH_CONTENT}] (defaults to 'siebert' client)"
            system_message += f"\n[{ToolNames.WEB_SEARCH_SERPER}] your search query [/{ToolNames.WEB_SEARCH_SERPER}]"
            system_message += f"\n[{ToolNames.WEB_SEARCH_PERPLEXITY}] your search query [/{ToolNames.WEB_SEARCH_PERPLEXITY}]"
            system_message += (
                f"\n[{ToolNames.IMAGE_GENERATION}] article_content: <approved article text>\\n"
                f"image_style: professional\\n"
                f"image_provider: openai [/{ToolNames.IMAGE_GENERATION}]"
            )
            system_message += "\n\nCRITICAL RULES:"
            system_message += "\n- Use EXACT tool names from the list above"
            system_message += (
                "\n- For rag_search_content: ALWAYS provide a specific search query"
            )
            system_message += (
                "\n- For multi-parameter tools: separate parameters with commas"
            )
            system_message += "\n- Do NOT use generic placeholders like 'TOOL_NAME'"

        return system_message
