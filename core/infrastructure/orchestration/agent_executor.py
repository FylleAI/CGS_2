"""Agent executor for task execution."""

import json
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ...application.interfaces.llm_provider_interface import LLMProviderInterface
from ...domain.entities.agent import Agent
from ...domain.repositories.agent_repository import AgentRepository
from ...domain.value_objects.provider_config import ProviderConfig
from ..logging.agent_logger import InteractionType, LogLevel, agent_logger
from ..logging.cost_calculator import CostBreakdown, TokenUsage, cost_calculator
from ..logging.tool_cost_calculator import tool_cost_calculator
from .simple_system_prompt_builder import SimpleSystemPromptBuilder

logger = logging.getLogger(__name__)


@dataclass
class ToolExecutionResult:
    """Normalized representation of tool execution outcomes."""

    output_text: str
    raw_output: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentExecutor:
    """
    Executor for AI agents.

    This class handles the execution of AI agents with appropriate tools
    and LLM backends.
    """

    def __init__(
        self,
        agent_repository: AgentRepository,
        llm_provider: LLMProviderInterface,
        provider_config: ProviderConfig,
    ):
        self.agent_repository = agent_repository
        self.llm_provider = llm_provider
        self.provider_config = provider_config
        self.tools_registry = {}
        self.system_prompt_builder = SimpleSystemPromptBuilder()

    def register_tool(
        self,
        tool_name: str,
        tool_function: callable,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Register a tool for agent use."""
        self.tools_registry[tool_name] = {
            "function": tool_function,
            "description": description,
            "metadata": metadata or {},
        }

    def register_tools(self, tools: Dict[str, Dict[str, Any]]):
        """Register multiple tools at once."""
        for tool_name, tool_info in tools.items():
            self.register_tool(
                tool_name,
                tool_info["function"],
                tool_info.get("description", f"Tool: {tool_name}"),
                tool_info.get("metadata"),
            )

    async def execute_agent(
        self, agent: Agent, task_description: str, context: Dict[str, Any] = None
    ) -> str:
        """
        Execute an agent with a specific task.

        Args:
            agent: The agent to execute
            task_description: Description of the task to perform
            context: Additional context for the agent

        Returns:
            Agent's output as a string
        """
        context = context or {}

        # Start agent session with detailed logging
        session_id = agent_logger.start_agent_session(
            agent_id=str(agent.id),
            agent_name=agent.name,
            task_id=context.get("task_id", "unknown"),
            workflow_id=context.get("workflow_id", "unknown"),
            task_description=task_description,
        )

        try:
            # Log agent thinking process
            agent_logger.log_agent_thinking(
                session_id=session_id,
                thought=f"Starting task execution for: {task_description[:100]}...",
                reasoning=f"Agent role: {agent.role.value}, Available tools: {len(agent.tools)}",
                next_action="Preparing system message and prompt",
            )

            # Prepare system message
            system_message = self._prepare_system_message(agent, context)

            # Prepare tools for this agent
            agent_tools = self._get_agent_tools(agent)

            # Log available tools
            if agent_tools:
                agent_logger.log_agent_thinking(
                    session_id=session_id,
                    thought=f"Tools available: {', '.join(agent_tools)}",
                    reasoning="These tools can be used to enhance the response",
                    next_action="Preparing prompt with tool instructions",
                )

            # Prepare prompt
            prompt = self._prepare_prompt(task_description, context, agent_tools)

            # Get dynamic provider config from context or use default
            dynamic_config = self._get_dynamic_provider_config(context)

            # Log LLM request
            request_id = agent_logger.log_llm_request(
                session_id=session_id,
                provider=dynamic_config.provider.value,
                model=dynamic_config.model,
                prompt=prompt,
                system_message=system_message,
            )

            # Execute LLM call with timing
            start_time = time.time()
            logger.debug(
                f"system_prompt_source=builder_v1, length={len(system_message)}"
            )
            llm_response = await self.llm_provider.generate_content(
                prompt=prompt, config=dynamic_config, system_message=system_message
            )
            duration_ms = (time.time() - start_time) * 1000

            # Extract actual response content
            response = (
                llm_response.content
                if hasattr(llm_response, "content")
                else str(llm_response)
            )

            # Get real token usage from API response
            token_usage = self._extract_token_usage(llm_response)

            # Calculate accurate cost
            cost_breakdown = cost_calculator.calculate_cost(
                provider=dynamic_config.provider.value,
                model=dynamic_config.model,
                token_usage=token_usage,
            )

            # Log LLM response with real usage data
            agent_logger.log_llm_response(
                session_id=session_id,
                request_id=request_id,
                provider=dynamic_config.provider.value,
                model=dynamic_config.model,
                response=response,
                tokens_used=token_usage.total_tokens,
                cost_usd=cost_breakdown.total_cost,
                duration_ms=duration_ms,
            )

            # Process tool calls if any
            final_response = await self.process_tool_calls(
                response, session_id, agent.name
            )

            # End agent session successfully
            agent_logger.end_agent_session(
                session_id=session_id, success=True, final_output=final_response
            )

            tracker = context.get("tracker")
            run_id = context.get("run_id")
            step_number = context.get("step_number")
            if tracker and run_id:
                try:
                    tracker.log_agent_execution(
                        run_id=run_id,
                        agent_name=agent.name,
                        step=step_number or 0,
                        input_data={"task_description": task_description},
                        output_data={"response": final_response},
                        tokens=token_usage.total_tokens,
                        cost=cost_breakdown.total_cost,
                        provider_name=dynamic_config.provider.value,
                        model_name=dynamic_config.model,
                        duration_seconds=duration_ms / 1000,
                    )
                except Exception as e:  # pragma: no cover
                    logger.warning(f"Tracker log_agent_execution failed: {e}")

            return final_response

        except Exception as e:
            # End agent session with error
            agent_logger.end_agent_session(
                session_id=session_id, success=False, error_message=str(e)
            )
            raise

    def _prepare_system_message(
        self, agent: Agent, context: Dict[str, Any] = None
    ) -> str:
        """Prepare system message for the agent using the simple builder."""
        context = context or {}
        tools_info = self._get_agent_tools_descriptions(agent)
        return self.system_prompt_builder.build(agent, context, tools_info)

    def _prepare_prompt(
        self,
        task_description: str,
        context: Dict[str, Any] = None,
        tools: List[str] = None,
    ) -> str:
        """Prepare the prompt for the agent."""
        context = context or {}
        prompt_parts = [task_description]

        # Add context information
        if context:
            context_str = "\n\n## Context Information\n"
            for key, value in context.items():
                if key not in ["client_profile", "target_audience"] and value:
                    context_str += f"\n- {key}: {value}"
            prompt_parts.append(context_str)

        # Add tools reminder if tools are available
        if tools:
            tools_reminder = "\n\n## Available Tools\n"
            tools_reminder += "You can use these tools to enhance your response:\n"
            from ..tools.tool_names import ToolNames

            for tool in tools:
                if tool == ToolNames.RAG_GET_CLIENT_CONTENT:
                    tools_reminder += f"- {tool}: Use [{ToolNames.RAG_GET_CLIENT_CONTENT}] client_name [/{ToolNames.RAG_GET_CLIENT_CONTENT}] to retrieve all content for a client\n"
                    tools_reminder += f"  Example: [{ToolNames.RAG_GET_CLIENT_CONTENT}] siebert [/{ToolNames.RAG_GET_CLIENT_CONTENT}]\n"
                elif tool == ToolNames.RAG_SEARCH_CONTENT:
                    tools_reminder += f"- {tool}: Use [{ToolNames.RAG_SEARCH_CONTENT}] client_name, search_query [/{ToolNames.RAG_SEARCH_CONTENT}] to search within client content\n"
                    tools_reminder += f"  Example: [{ToolNames.RAG_SEARCH_CONTENT}] siebert, Mark Malek insights [/{ToolNames.RAG_SEARCH_CONTENT}]\n"
                    tools_reminder += f"  Shorthand: [{ToolNames.RAG_SEARCH_CONTENT}] Mark Malek insights [/{ToolNames.RAG_SEARCH_CONTENT}] (defaults to siebert)\n"
                elif tool == ToolNames.WEB_SEARCH_SERPER:
                    tools_reminder += f"- {tool}: Use [{ToolNames.WEB_SEARCH_SERPER}] your search query [/{ToolNames.WEB_SEARCH_SERPER}] to search the web for current information\n"
                elif tool == ToolNames.WEB_SEARCH_PERPLEXITY:
                    tools_reminder += f"- {tool}: Use [{ToolNames.WEB_SEARCH_PERPLEXITY}] your search query [/{ToolNames.WEB_SEARCH_PERPLEXITY}] for Perplexity research with citations\n"
                elif tool == ToolNames.IMAGE_GENERATION:
                    tools_reminder += f"- {tool}: Provide article_content, image_style, and image_provider lines inside the tool block to generate contextual visuals\n"
                else:
                    tools_reminder += f"- {tool}: Use [{tool}] your input [/{tool}]\n"

            tools_reminder += "\n⚠️ CRITICAL: Use the EXACT tool names shown above. Do NOT use placeholders like 'TOOL_NAME'."
            prompt_parts.append(tools_reminder)

        # Add final instructions
        prompt_parts.append("\n\nPlease provide a comprehensive response to the task.")

        return "\n".join(prompt_parts)

    def _get_agent_tools(self, agent: Agent) -> List[str]:
        """Get the list of tools available to this agent."""
        available_tools = []

        from ..tools.tool_names import ALIASES

        for tool_name in agent.tools:
            canonical = ALIASES.get(tool_name, tool_name)
            if canonical in self.tools_registry:
                available_tools.append(canonical)

        return available_tools

    def _get_agent_tools_descriptions(self, agent: Agent) -> str:
        """Get descriptions of tools available to this agent."""
        tool_descriptions = []

        from ..tools.tool_names import ALIASES

        for tool_name in agent.tools:
            canonical = ALIASES.get(tool_name, tool_name)
            if canonical in self.tools_registry:
                description = self.tools_registry[canonical]["description"]
                tool_descriptions.append(f"- {canonical}: {description}")

        return "\n".join(tool_descriptions)

    async def process_tool_calls(
        self,
        agent_response: str,
        session_id: str = None,
        agent_name: Optional[str] = None,
    ) -> str:
        """
        Process tool calls in the agent's response.

        This function looks for tool calls in the format [TOOL_NAME] input [/TOOL_NAME]
        and executes the corresponding tools.

        Args:
            agent_response: The agent's response text
            session_id: Agent session ID for logging

        Returns:
            Updated response with tool results
        """
        # Find all tool calls
        tool_pattern = r"\[(\w+)\](.*?)\[/\1\]"
        tool_calls = re.findall(tool_pattern, agent_response, re.DOTALL)

        if not tool_calls:
            if session_id:
                agent_logger.log_agent_thinking(
                    session_id=session_id,
                    thought="No tool calls detected in response",
                    reasoning="Agent provided direct response without using tools",
                    next_action="Returning response as-is",
                )
            return agent_response

        if session_id:
            agent_logger.log_agent_thinking(
                session_id=session_id,
                thought=f"Detected {len(tool_calls)} tool calls",
                reasoning=f"Tools to execute: {[call[0] for call in tool_calls]}",
                next_action="Processing tool calls sequentially",
            )

        # Process each tool call
        for tool_name, tool_input in tool_calls:
            from ..tools.tool_names import ALIASES

            original_tool_name = tool_name
            canonical_tool_name = ALIASES.get(original_tool_name, original_tool_name)

            if canonical_tool_name in self.tools_registry:
                tool_info = self.tools_registry[canonical_tool_name]
                tool_metadata = tool_info.get("metadata", {})

                # Log tool call start
                call_id = None
                if session_id:
                    call_id = agent_logger.log_tool_call(
                        session_id=session_id,
                        tool_name=original_tool_name,
                        tool_input=tool_input.strip(),
                        tool_description=tool_info["description"],
                        metadata=tool_metadata,
                    )

                try:
                    # Execute the tool with timing
                    start_time = time.time()
                    tool_function = tool_info["function"]

                    # Parse tool input based on tool type
                    execution_result = await self._execute_tool_with_params(
                        canonical_tool_name,
                        tool_function,
                        tool_input.strip(),
                        agent_name,
                        tool_metadata,
                    )
                    duration_ms = (time.time() - start_time) * 1000

                    execution_metadata = dict(execution_result.metadata or {})
                    if tool_metadata:
                        execution_metadata = {
                            **tool_metadata,
                            **execution_metadata,
                        }

                    cost_details = tool_cost_calculator.calculate_cost(
                        canonical_tool_name, tool_metadata, execution_metadata
                    )
                    if cost_details.cost_usd:
                        execution_metadata["cost_usd"] = cost_details.cost_usd
                    execution_metadata.setdefault(
                        "cost_source", cost_details.source
                    )
                    execution_metadata.setdefault("units", cost_details.units)

                    # Log successful tool response
                    if session_id and call_id:
                        agent_logger.log_tool_response(
                            session_id=session_id,
                            call_id=call_id,
                            tool_name=original_tool_name,
                            tool_output=execution_result.output_text,
                            duration_ms=duration_ms,
                            success=True,
                            cost_usd=cost_details.cost_usd,
                            metadata=execution_metadata,
                        )

                    # Replace the tool call with the result
                    tool_call = (
                        f"[{original_tool_name}]{tool_input}[/{original_tool_name}]"
                    )
                    tool_result_text = (
                        f"[{original_tool_name} RESULT]\n"
                        f"{execution_result.output_text}\n"
                        f"[/{original_tool_name} RESULT]"
                    )
                    agent_response = agent_response.replace(
                        tool_call, tool_result_text
                    )

                except Exception as e:
                    duration_ms = (
                        (time.time() - start_time) * 1000
                        if "start_time" in locals()
                        else 0
                    )

                    # Log tool error
                    if session_id and call_id:
                        agent_logger.log_tool_error(
                            session_id=session_id,
                            call_id=call_id,
                            tool_name=tool_name,
                            error=e,
                            duration_ms=duration_ms,
                            metadata=tool_metadata,
                        )

                    # Replace with error message
                    tool_call = f"[{tool_name}]{tool_input}[/{tool_name}]"
                    error_text = (
                        f"[{tool_name} ERROR] {str(e)} [/{tool_name} ERROR]"
                    )
                    agent_response = agent_response.replace(tool_call, error_text)
            else:
                # Tool not found - log error
                if session_id:
                    call_id = agent_logger.log_tool_call(
                        session_id=session_id,
                        tool_name=tool_name,
                        tool_input=tool_input.strip(),
                        tool_description="Tool not found",
                        metadata={"provider": "unknown"},
                    )

                    agent_logger.log_tool_error(
                        session_id=session_id,
                        call_id=call_id,
                        tool_name=tool_name,
                        error=Exception(
                            f"Tool '{tool_name}' not found in registry"
                        ),
                        duration_ms=0,
                        metadata={"provider": "unknown"},
                    )

                tool_call = f"[{tool_name}]{tool_input}[/{tool_name}]"
                error_text = f"[{tool_name} ERROR] Tool not found [/{tool_name} ERROR]"
                agent_response = agent_response.replace(tool_call, error_text)

        return agent_response

    async def _execute_tool_with_params(
        self,
        tool_name: str,
        tool_function: callable,
        tool_input: str,
        agent_name: Optional[str] = None,
        tool_metadata: Optional[Dict[str, Any]] = None,
    ) -> ToolExecutionResult:
        """
        Execute tool with proper parameter parsing and validation.

        Args:
            tool_name: Name of the tool to execute
            tool_function: The tool function to call
            tool_input: Raw input string from agent

        Returns:
            Tool execution result
        """
        try:
            # Validate parameters first
            is_valid, error_msg = self._validate_tool_parameters(tool_name, tool_input)
            if not is_valid:
                raise ValueError(f"Parameter validation failed: {error_msg}")

            # Handle different tool signatures
            if tool_name == "rag_search_content":
                # Parse: "client_name, search_query" or just "search_query"
                parts = [part.strip() for part in tool_input.split(",", 1)]

                if len(parts) == 2:
                    client_name, query = parts
                elif len(parts) == 1:
                    # Default to 'siebert' if only query provided
                    client_name = "siebert"
                    query = parts[0]
                else:
                    raise ValueError(
                        "rag_search_content requires format: 'client_name, search_query' or just 'search_query'"
                    )

                if not query.strip():
                    raise ValueError("Search query cannot be empty")

                result = await tool_function(
                    client_name, query, agent_name=agent_name
                )
                return self._normalize_tool_result(
                    tool_name, result, tool_metadata
                )

            elif tool_name == "rag_get_client_content":
                # Parse: "client_name" or "client_name, document_name"
                parts = [part.strip() for part in tool_input.split(",", 1)]

                if len(parts) == 2:
                    client_name, document_name = parts
                    result = await tool_function(
                        client_name, document_name, agent_name=agent_name
                    )
                    return self._normalize_tool_result(
                        tool_name, result, tool_metadata
                    )
                elif len(parts) == 1:
                    client_name = parts[0]
                    result = await tool_function(
                        client_name, agent_name=agent_name
                    )
                    return self._normalize_tool_result(
                        tool_name, result, tool_metadata
                    )
                else:
                    raise ValueError(
                        "rag_get_client_content requires format: 'client_name' or 'client_name, document_name'"
                    )

            elif tool_name == "perplexity_search":
                # Parse a structured input like: "topic=..., exclude_topics=[...], premium_sources=...|..., research_timeframe=last 7 days"
                raw = tool_input.strip()
                if "=" not in raw and "," not in raw and "\n" not in raw:
                    result = await tool_function(raw)
                    metadata = {"query": raw}
                    if tool_metadata:
                        metadata = {**tool_metadata, **metadata}
                    return self._normalize_tool_result(
                        tool_name, result, metadata
                    )
                parts = [p.strip() for p in raw.split(",") if p.strip()]
                params = {}
                for p in parts:
                    if "=" in p:
                        k, v = p.split("=", 1)
                        params[k.strip()] = v.strip()
                topic = params.get("topic") or params.get("query") or raw
                timeframe = params.get("research_timeframe", "")
                exclude = params.get("exclude_topics", "")
                sources = params.get("premium_sources", "")

                # Build site filters from premium_sources (pipe-separated URLs)
                domains = []
                for src in sources.split("|"):
                    src = src.strip()
                    if not src:
                        continue
                    if "://" in src:
                        host_and_path = src.split("://", 1)[1]
                    else:
                        host_and_path = src
                    domain = host_and_path.split("/", 1)[0]
                    if domain:
                        domains.append(domain)
                site_filter = ""
                if domains:
                    site_filter = (
                        " (" + " OR ".join([f"site:{d}" for d in domains]) + ")"
                    )

                # Exclude listing pages that cause generic/old info when filtering by site
                url_excludes = ""
                if domains:
                    url_excludes = " -inurl:/tag/ -inurl:/category/ -inurl:/topics/ -inurl:/newsletter -inurl:/newsletters"

                # Map timeframe to a natural-language hint for PPLX
                tf_hint = ""
                if timeframe:
                    if "7" in timeframe:
                        tf_hint = " past week"
                    elif "yesterday" in timeframe.lower():
                        tf_hint = " since yesterday"
                    elif "month" in timeframe.lower():
                        tf_hint = " past month"

                # Exclude topics
                ex_hint = ""
                if exclude:
                    # normalize list-like input
                    ex_items = []
                    if exclude.startswith("[") and exclude.endswith("]"):
                        ex_items = [
                            x.strip(" ' \"")
                            for x in exclude[1:-1].split(",")
                            if x.strip()
                        ]
                    else:
                        ex_items = [x.strip() for x in exclude.split("|") if x.strip()]
                    if ex_items:
                        ex_hint = " " + " ".join([f"-{x}" for x in ex_items])

                query = f"{topic}{site_filter}{url_excludes}{tf_hint}{ex_hint}".strip()
                result = await tool_function(query)
                metadata = {"query": query}
                if tool_metadata:
                    metadata = {**tool_metadata, **metadata}
                return self._normalize_tool_result(
                    tool_name, result, metadata
                )

            elif tool_name == "image_generation_tool":
                params: Dict[str, str] = {}
                current_key: Optional[str] = None
                for line in tool_input.splitlines():
                    stripped = line.strip()
                    if not stripped:
                        continue
                    if ":" in stripped:
                        key, value = stripped.split(":", 1)
                        current_key = key.strip().lower()
                        params[current_key] = value.strip()
                    elif current_key:
                        params[current_key] = (
                            params[current_key] + f"\n{stripped}"
                        ).strip()

                article_content = params.get("article_content", tool_input)
                image_style = params.get("image_style", "professional")
                image_provider = params.get("image_provider", "openai")

                result = await tool_function(
                    article_content=article_content,
                    image_style=image_style,
                    image_provider=image_provider,
                )
                metadata = {
                    "style": image_style,
                    "image_provider": image_provider,
                }
                if tool_metadata:
                    metadata = {**tool_metadata, **metadata}
                return self._normalize_tool_result(
                    tool_name, result, metadata
                )

            else:
                # Default behavior for other tools (single parameter)
                result = await tool_function(tool_input)
                return self._normalize_tool_result(
                    tool_name, result, tool_metadata
                )

        except Exception as e:
            # Enhanced error handling with fallback
            error_msg = f"Tool execution error: {str(e)}"

            # Provide intelligent fallback for rag_search_content
            if tool_name == "rag_search_content":
                try:
                    # Try to extract client name from input for fallback
                    parts = [part.strip() for part in tool_input.split(",", 1)]
                    client_name = "siebert"  # Default

                    if (
                        len(parts) >= 1
                        and parts[0]
                        and not any(
                            keyword in parts[0].lower()
                            for keyword in ["mark", "malek", "insight", "market"]
                        )
                    ):
                        # First part might be client name
                        client_name = parts[0]

                    # Fallback to rag_get_client_content
                    from core.infrastructure.tools.rag_tool import RAGTool

                    rag_tool = RAGTool()
                    fallback_result = await rag_tool.get_client_content(client_name)
                    fallback_text = (
                        "[FALLBACK] Search failed (")
                    fallback_text += f"{str(e)}), retrieved all {client_name} "
                    fallback_text += "content instead:\n"
                    fallback_text += fallback_result
                    return self._normalize_tool_result(
                        tool_name,
                        fallback_text,
                        tool_metadata,
                    )
                except Exception as fallback_error:
                    error_msg += f" | Fallback also failed: {str(fallback_error)}"

            raise Exception(error_msg)

    def _normalize_tool_result(
        self,
        tool_name: str,
        result: Any,
        tool_metadata: Optional[Dict[str, Any]] = None,
    ) -> ToolExecutionResult:
        """Convert heterogeneous tool outputs into a standard structure."""

        metadata: Dict[str, Any] = {}
        if tool_metadata:
            metadata.update(tool_metadata)

        if isinstance(result, ToolExecutionResult):
            combined_metadata = {**metadata, **(result.metadata or {})}
            return ToolExecutionResult(
                output_text=result.output_text,
                raw_output=result.raw_output,
                metadata=combined_metadata,
            )

        if isinstance(result, tuple) and len(result) == 2:
            output_text, extra = result
            if isinstance(extra, dict):
                metadata.update(extra)
            return ToolExecutionResult(
                output_text=str(output_text),
                raw_output=result,
                metadata=metadata,
            )

        if isinstance(result, dict):
            dict_copy = dict(result)
            extra_meta = dict_copy.pop("metadata", {}) if isinstance(
                dict_copy.get("metadata"), dict
            ) else {}

            for key in [
                "provider",
                "model",
                "cost_usd",
                "cost_per_call_usd",
                "cost_per_1k_tokens_usd",
                "cost_source",
                "token_cost_source",
                "usage_tokens",
                "duration_ms",
            ]:
                if key in dict_copy and key not in metadata:
                    metadata[key] = dict_copy[key]

            metadata.update(extra_meta)

            try:
                output_text = json.dumps(dict_copy, ensure_ascii=False, indent=2)
            except Exception:
                output_text = str(dict_copy)

            return ToolExecutionResult(
                output_text=output_text,
                raw_output=result,
                metadata=metadata,
            )

        # Default string representation
        output_text = str(result)
        return ToolExecutionResult(
            output_text=output_text,
            raw_output=result,
            metadata=metadata,
        )

    def _validate_tool_parameters(
        self, tool_name: str, tool_input: str
    ) -> tuple[bool, str]:
        """
        Validate tool parameters before execution.

        Args:
            tool_name: Name of the tool
            tool_input: Input parameters

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if tool_name == "rag_search_content":
                parts = [part.strip() for part in tool_input.split(",", 1)]

                # Check if we have at least a query
                if len(parts) == 0 or not any(part.strip() for part in parts):
                    return False, "rag_search_content requires at least a search query"

                # If only one part, it should be the query
                if len(parts) == 1:
                    query = parts[0].strip()
                    if not query:
                        return False, "Search query cannot be empty"

                # If two parts, validate both client_name and query
                elif len(parts) == 2:
                    client_name, query = [part.strip() for part in parts]
                    if not client_name:
                        return False, "Client name cannot be empty"
                    if not query:
                        return False, "Search query cannot be empty"

                return True, ""

            elif tool_name == "rag_get_client_content":
                parts = [part.strip() for part in tool_input.split(",", 1)]

                if len(parts) == 0 or not parts[0].strip():
                    return (
                        False,
                        "rag_get_client_content requires at least a client name",
                    )

                return True, ""

            elif tool_name == "image_generation_tool":
                if not tool_input.strip():
                    return False, "image_generation_tool requires article_content"
                return True, ""
            else:
                # Basic validation for other tools
                if not tool_input.strip():
                    return False, f"{tool_name} requires input parameters"

                return True, ""

        except Exception as e:
            return False, f"Parameter validation error: {str(e)}"

    def _get_dynamic_provider_config(self, context: Dict[str, Any]) -> ProviderConfig:
        """
        Get dynamic provider configuration from context or use default.

        This method checks the context for provider, model, and temperature
        settings and creates a new ProviderConfig if they exist, otherwise
        returns the default configuration.
        """
        # Check if context has provider configuration
        provider_name = context.get("provider")
        model = context.get("model")
        temperature = context.get("temperature")

        # If no dynamic config in context, use default
        if not provider_name and not model:
            return self.provider_config

        # Create dynamic config
        try:
            # Use provider from context or default
            if provider_name:
                from ...domain.value_objects.provider_config import LLMProvider

                provider = LLMProvider(provider_name)
            else:
                provider = self.provider_config.provider

            # Use model from context or default for provider
            if not model:
                # Get default model for the provider
                defaults = {
                    LLMProvider.OPENAI: "gpt-4o",
                    LLMProvider.ANTHROPIC: "claude-3-7-sonnet-latest",
                    LLMProvider.DEEPSEEK: "deepseek-chat",
                }
                model = defaults.get(provider, self.provider_config.model)

            # Use temperature from context or default
            if temperature is None:
                temperature = self.provider_config.temperature

            # Create new config with dynamic values
            dynamic_config = ProviderConfig(
                provider=provider,
                model=model,
                temperature=temperature,
                max_tokens=self.provider_config.max_tokens,
                top_p=self.provider_config.top_p,
                frequency_penalty=self.provider_config.frequency_penalty,
                presence_penalty=self.provider_config.presence_penalty,
                api_key=self.provider_config.api_key,
                base_url=self.provider_config.base_url,
                additional_params=self.provider_config.additional_params,
            )

            logger.debug(
                f"🔧 Using dynamic config: {provider.value}/{model} (temp: {temperature})"
            )
            return dynamic_config

        except Exception as e:
            logger.warning(f"⚠️ Failed to create dynamic config: {e}, using default")
            return self.provider_config

    def _extract_token_usage(self, llm_response) -> TokenUsage:
        """Extract real token usage from LLM API response."""
        try:
            # Check if response has usage information (handle both object and dataclass)
            usage_data = getattr(llm_response, "usage", None)
            if usage_data:
                usage = usage_data

                # Handle different response formats
                if isinstance(usage, dict):
                    return TokenUsage(
                        prompt_tokens=usage.get("prompt_tokens", 0),
                        completion_tokens=usage.get("completion_tokens", 0),
                        total_tokens=usage.get("total_tokens", 0),
                        reasoning_tokens=usage.get("reasoning_tokens", 0),
                        cached_tokens=usage.get("cached_tokens", 0),
                    )
                else:
                    # Handle object-style usage
                    return TokenUsage(
                        prompt_tokens=getattr(usage, "prompt_tokens", 0),
                        completion_tokens=getattr(usage, "completion_tokens", 0),
                        total_tokens=getattr(usage, "total_tokens", 0),
                        reasoning_tokens=getattr(usage, "reasoning_tokens", 0),
                        cached_tokens=getattr(usage, "cached_tokens", 0),
                    )

            # Fallback to estimation if no usage data
            logger.warning(
                "⚠️ No token usage data in LLM response, falling back to estimation"
            )
            return self._estimate_token_usage(llm_response)

        except Exception as e:
            logger.error(f"❌ Error extracting token usage: {e}")
            return self._estimate_token_usage(llm_response)

    def _estimate_token_usage(self, llm_response) -> TokenUsage:
        """Fallback token estimation when real usage is not available."""
        response_text = (
            llm_response.content
            if hasattr(llm_response, "content")
            else str(llm_response)
        )

        # Simple word-based estimation (rough approximation)
        estimated_completion_tokens = len(response_text.split())
        estimated_prompt_tokens = estimated_completion_tokens // 2  # Rough estimate

        return TokenUsage(
            prompt_tokens=estimated_prompt_tokens,
            completion_tokens=estimated_completion_tokens,
            total_tokens=estimated_prompt_tokens + estimated_completion_tokens,
        )
