"""Tests for the SimpleSystemPromptBuilder."""

from core.domain.entities.agent import Agent, AgentRole
from core.infrastructure.orchestration.simple_system_prompt_builder import SimpleSystemPromptBuilder
from core.infrastructure.tools.tool_names import ToolNames


def legacy_system_prompt(agent: Agent, context, tool_descriptions: str) -> str:
    """Replicate the legacy system message construction for parity tests."""
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
            agent.role,
            "You are an AI assistant helping with content generation."
        )

    if agent.backstory:
        system_message += f"\n\n{agent.backstory}"

    if agent.goal:
        system_message += f"\n\nYour goal is: {agent.goal}"

    if context.get('client_profile'):
        system_message += f"\n\nYou are working for client: {context.get('client_profile')}"

    if context.get('target_audience'):
        system_message += f"\n\nThe target audience is: {context.get('target_audience')}"

    if tool_descriptions:
        system_message += f"\n\nYou have access to the following tools:\n{tool_descriptions}"
        system_message += "\n\nIMPORTANT: When you need to use a tool, format your response EXACTLY like this:"
        system_message += f"\n[{ToolNames.RAG_GET_CLIENT_CONTENT}] client_name [/{ToolNames.RAG_GET_CLIENT_CONTENT}]"
        system_message += f"\n[{ToolNames.RAG_GET_CLIENT_CONTENT}] client_name, document_name [/{ToolNames.RAG_GET_CLIENT_CONTENT}]"
        system_message += f"\n[{ToolNames.RAG_SEARCH_CONTENT}] client_name, search_query [/{ToolNames.RAG_SEARCH_CONTENT}]"
        system_message += f"\n[{ToolNames.RAG_SEARCH_CONTENT}] search_query [/{ToolNames.RAG_SEARCH_CONTENT}] (defaults to 'siebert' client)"
        system_message += f"\n[{ToolNames.WEB_SEARCH_SERPER}] your search query [/{ToolNames.WEB_SEARCH_SERPER}]"
        system_message += f"\n[{ToolNames.WEB_SEARCH_PERPLEXITY}] your search query [/{ToolNames.WEB_SEARCH_PERPLEXITY}]"
        system_message += "\n\nCRITICAL RULES:"
        system_message += "\n- Use EXACT tool names from the list above"
        system_message += "\n- For rag_search_content: ALWAYS provide a specific search query"
        system_message += "\n- For multi-parameter tools: separate parameters with commas"
        system_message += "\n- Do NOT use generic placeholders like 'TOOL_NAME'"

    return system_message


def test_builder_matches_legacy_parity():
    """Ensure the builder matches the legacy implementation for multiple scenarios."""
    builder = SimpleSystemPromptBuilder()

    tool_descriptions_full = (
        f"- {ToolNames.RAG_GET_CLIENT_CONTENT}: Access client knowledge base"
        f"\n- {ToolNames.WEB_SEARCH_SERPER}: Search the web for current information"
    )
    tool_descriptions_research = (
        f"- {ToolNames.RAG_SEARCH_CONTENT}: Retrieve specific client documents"
    )

    agent_full = Agent(
        name="FullAgent",
        role=AgentRole.WRITER,
        system_message="You are a meticulous writer.",
        backstory="You craft narratives backed by thorough research.",
        goal="Deliver engaging and informative articles.",
        tools=[ToolNames.RAG_GET_CLIENT_CONTENT, ToolNames.WEB_SEARCH_SERPER],
    )
    context_full = {
        "client_profile": "Acme Financial",
        "target_audience": "Institutional investors",
    }

    agent_research = Agent(
        name="ResearchAgent",
        role=AgentRole.RESEARCHER,
        system_message="",
        backstory="",
        goal="Identify the most relevant market insights.",
        tools=[ToolNames.RAG_SEARCH_CONTENT],
    )
    context_research = {
        "client_profile": "Zenith Capital",
    }

    scenarios = [
        (agent_full, context_full, tool_descriptions_full),
        (agent_research, context_research, tool_descriptions_research),
    ]

    for agent, context, tool_desc in scenarios:
        legacy_message = legacy_system_prompt(agent, context, tool_desc)
        assert builder.build(agent, context, tool_desc) == legacy_message


def test_builder_runtime_fields_order():
    """Runtime context fields must keep legacy order and separators."""
    builder = SimpleSystemPromptBuilder()

    agent = Agent(
        name="ContextAgent",
        role=AgentRole.WRITER,
        system_message="You are a strategic communicator.",
        backstory="You excel at tailoring messages to diverse audiences.",
        goal="Create persuasive copy that drives action.",
        tools=[ToolNames.WEB_SEARCH_PERPLEXITY],
    )
    context = {
        "client_profile": "Atlas Advisors",
        "target_audience": "High-net-worth individuals",
    }
    tool_description = (
        f"- {ToolNames.WEB_SEARCH_PERPLEXITY}: Provide cited research summaries"
    )

    result = builder.build(agent, context, tool_description)

    expected_order = [
        agent.system_message,
        agent.backstory,
        f"Your goal is: {agent.goal}",
        "You are working for client: Atlas Advisors",
        "The target audience is: High-net-worth individuals",
        "You have access to the following tools:",
        tool_description.split('\n')[0],
    ]

    for text in expected_order:
        assert text in result

    for earlier, later in zip(expected_order, expected_order[1:]):
        assert result.index(earlier) < result.index(later)

    assert "\n\nYour goal is: " in result
    assert "\n\nYou are working for client: " in result
    assert "\n\nThe target audience is: " in result


def test_builder_no_tools_block():
    """Ensure the tools block is omitted when no tools are provided."""
    builder = SimpleSystemPromptBuilder()

    agent = Agent(
        name="SimpleAgent",
        role=AgentRole.WRITER,
        system_message="You are a concise assistant.",
        backstory="",
        goal="Respond clearly to user requests.",
        tools=[],
    )

    context = {}
    tool_descriptions = ""

    result = builder.build(agent, context, tool_descriptions)
    legacy_message = legacy_system_prompt(agent, context, tool_descriptions)

    assert result == legacy_message
    assert "You have access to the following tools:" not in result
    assert "IMPORTANT: When you need to use a tool" not in result
    assert "CRITICAL RULES:" not in result
