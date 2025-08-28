"""Agent executor for task execution."""

import logging
import json
import time
import re
import inspect
from typing import Dict, Any, List, Optional
from uuid import UUID

from ...domain.entities.agent import Agent, AgentRole
from ...domain.repositories.agent_repository import AgentRepository
from ...application.interfaces.llm_provider_interface import LLMProviderInterface
from ...domain.value_objects.provider_config import ProviderConfig
from ..logging.agent_logger import agent_logger, LogLevel, InteractionType
from ..logging.cost_calculator import cost_calculator, TokenUsage, CostBreakdown

logger = logging.getLogger(__name__)


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
        provider_config: ProviderConfig
    ):
        self.agent_repository = agent_repository
        self.llm_provider = llm_provider
        self.provider_config = provider_config
        self.tools_registry = {}
    
    def register_tool(self, tool_name: str, tool_function: callable, description: str):
        """Register a tool for agent use."""
        self.tools_registry[tool_name] = {
            'function': tool_function,
            'description': description
        }
    
    def register_tools(self, tools: Dict[str, Dict[str, Any]]):
        """Register multiple tools at once."""
        for tool_name, tool_info in tools.items():
            self.register_tool(
                tool_name, 
                tool_info['function'], 
                tool_info.get('description', f"Tool: {tool_name}")
            )
    
    async def execute_agent(
        self,
        agent: Agent,
        task_description: str,
        context: Dict[str, Any] = None
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
            task_id=context.get('task_id', 'unknown'),
            workflow_id=context.get('workflow_id', 'unknown'),
            task_description=task_description
        )

        try:
            # Log agent thinking process
            agent_logger.log_agent_thinking(
                session_id=session_id,
                thought=f"Starting task execution for: {task_description[:100]}...",
                reasoning=f"Agent role: {agent.role.value}, Available tools: {len(agent.tools)}",
                next_action="Preparing system message and prompt"
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
                    next_action="Preparing prompt with tool instructions"
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
                system_message=system_message
            )

            # Execute LLM call with timing
            start_time = time.time()
            llm_response = await self.llm_provider.generate_content(
                prompt=prompt,
                config=dynamic_config,
                system_message=system_message
            )
            duration_ms = (time.time() - start_time) * 1000

            # Extract actual response content
            response = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)

            # Get real token usage from API response
            token_usage = self._extract_token_usage(llm_response)

            # Calculate accurate cost
            cost_breakdown = cost_calculator.calculate_cost(
                provider=dynamic_config.provider.value,
                model=dynamic_config.model,
                token_usage=token_usage
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
                duration_ms=duration_ms
            )

            # Process tool calls if any
            final_response = await self.process_tool_calls(response, session_id)

            # End agent session successfully
            agent_logger.end_agent_session(
                session_id=session_id,
                success=True,
                final_output=final_response
            )

            return final_response

        except Exception as e:
            # End agent session with error
            agent_logger.end_agent_session(
                session_id=session_id,
                success=False,
                error_message=str(e)
            )
            raise
    
    def _prepare_system_message(self, agent: Agent, context: Dict[str, Any] = None) -> str:
        """Prepare system message for the agent."""
        context = context or {}
        
        # Start with agent's system message
        if agent.system_message:
            system_message = agent.system_message
        else:
            # Default system messages based on role
            role_messages = {
                AgentRole.RESEARCHER: "You are an expert researcher who finds accurate, relevant information and presents it clearly.",
                AgentRole.WRITER: "You are an expert writer who creates engaging, well-structured content tailored to specific audiences.",
                AgentRole.EDITOR: "You are an expert editor who refines content for clarity, coherence, and alignment with style guidelines.",
                AgentRole.ANALYST: "You are an expert analyst who examines data and information to extract meaningful insights.",
                AgentRole.PLANNER: "You are an expert planner who organizes complex tasks into clear, actionable steps.",
                AgentRole.COMPLIANCE_REVIEWER: "You are an expert compliance reviewer who ensures content meets regulatory standards and risk management requirements."
            }
            system_message = role_messages.get(agent.role, "You are an AI assistant helping with content generation.")
        
        # Add agent backstory if available
        if agent.backstory:
            system_message += f"\n\n{agent.backstory}"
        
        # Add agent goal if available
        if agent.goal:
            system_message += f"\n\nYour goal is: {agent.goal}"
        
        # Add context-specific information
        if context.get('client_profile'):
            system_message += f"\n\nYou are working for client: {context.get('client_profile')}"
        
        if context.get('target_audience'):
            system_message += f"\n\nThe target audience is: {context.get('target_audience')}"
        
        # Add tools information
        tools_info = self._get_agent_tools_descriptions(agent)
        if tools_info:
            system_message += f"\n\nYou have access to the following tools:\n{tools_info}"
            from ..tools.tool_names import ToolNames
            system_message += "\n\nIMPORTANT: When you need to use a tool, format your response EXACTLY like this:"
            system_message += f"\n[{ToolNames.RAG_GET_CLIENT_CONTENT}] client_name [/{ToolNames.RAG_GET_CLIENT_CONTENT}]"
            system_message += f"\n[{ToolNames.RAG_GET_CLIENT_CONTENT}] client_name, document_name [/{ToolNames.RAG_GET_CLIENT_CONTENT}]"
            system_message += f"\n[{ToolNames.RAG_SEARCH_CONTENT}] client_name, search_query [/{ToolNames.RAG_SEARCH_CONTENT}]"
            system_message += f"\n[{ToolNames.RAG_SEARCH_CONTENT}] search_query [/{ToolNames.RAG_SEARCH_CONTENT}] (defaults to 'siebert' client)"
            system_message += f"\n[{ToolNames.WEB_SEARCH}] your search query [/{ToolNames.WEB_SEARCH}]"
            system_message += f"\n[{ToolNames.RESEARCH_PREMIUM_FINANCIAL}] topic=your topic, exclude_topics=topics to exclude [/{ToolNames.RESEARCH_PREMIUM_FINANCIAL}]"
            system_message += "\n\nCRITICAL RULES:"
            system_message += "\n- Use EXACT tool names from the list above"
            system_message += "\n- For rag_search_content: ALWAYS provide a specific search query"
            system_message += "\n- For multi-parameter tools: separate parameters with commas"
            system_message += "\n- Do NOT use generic placeholders like 'TOOL_NAME'"

        return system_message
    
    def _prepare_prompt(
        self, 
        task_description: str, 
        context: Dict[str, Any] = None,
        tools: List[str] = None
    ) -> str:
        """Prepare the prompt for the agent."""
        context = context or {}
        prompt_parts = [task_description]
        
        # Add context information
        if context:
            context_str = "\n\n## Context Information\n"
            for key, value in context.items():
                if key not in ['client_profile', 'target_audience'] and value:
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
                elif tool == ToolNames.WEB_SEARCH:
                    tools_reminder += f"- {tool}: Use [{ToolNames.WEB_SEARCH}] your search query [/{ToolNames.WEB_SEARCH}] to search the web for current information\n"
                elif tool == ToolNames.WEB_SEARCH_FINANCIAL:
                    tools_reminder += f"- {tool}: Use [{ToolNames.WEB_SEARCH_FINANCIAL}] topic, exclude_topics [/{ToolNames.WEB_SEARCH_FINANCIAL}] for financial content\n"
                elif tool == ToolNames.RESEARCH_PREMIUM_FINANCIAL:
                    tools_reminder += f"- {tool}: Use [{ToolNames.RESEARCH_PREMIUM_FINANCIAL}] topic, exclude_topics [/{ToolNames.RESEARCH_PREMIUM_FINANCIAL}] for premium financial research with Perplexity\n"
                elif tool == ToolNames.RESEARCH_CLIENT_SOURCES:
                    tools_reminder += f"- {tool}: Use [{ToolNames.RESEARCH_CLIENT_SOURCES}] client_name, topic, days_back [/{ToolNames.RESEARCH_CLIENT_SOURCES}] for client-specific source research\n"
                elif tool == ToolNames.RESEARCH_GENERAL_TOPIC:
                    tools_reminder += f"- {tool}: Use [{ToolNames.RESEARCH_GENERAL_TOPIC}] topic [/{ToolNames.RESEARCH_GENERAL_TOPIC}] for general topic research with Perplexity\n"
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
                description = self.tools_registry[canonical]['description']
                tool_descriptions.append(f"- {canonical}: {description}")

        return "\n".join(tool_descriptions)

    async def process_tool_calls(self, agent_response: str, session_id: str = None) -> str:
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
        tool_pattern = r'\[(\w+)\](.*?)\[/\1\]'
        tool_calls = re.findall(tool_pattern, agent_response, re.DOTALL)

        if not tool_calls:
            if session_id:
                agent_logger.log_agent_thinking(
                    session_id=session_id,
                    thought="No tool calls detected in response",
                    reasoning="Agent provided direct response without using tools",
                    next_action="Returning response as-is"
                )
            return agent_response

        if session_id:
            agent_logger.log_agent_thinking(
                session_id=session_id,
                thought=f"Detected {len(tool_calls)} tool calls",
                reasoning=f"Tools to execute: {[call[0] for call in tool_calls]}",
                next_action="Processing tool calls sequentially"
            )

        # Process each tool call
        for tool_name, tool_input in tool_calls:
            from ..tools.tool_names import ALIASES
            original_tool_name = tool_name
            canonical_tool_name = ALIASES.get(original_tool_name, original_tool_name)

            if canonical_tool_name in self.tools_registry:
                # Log tool call start
                call_id = None
                if session_id:
                    call_id = agent_logger.log_tool_call(
                        session_id=session_id,
                        tool_name=original_tool_name,
                        tool_input=tool_input.strip(),
                        tool_description=self.tools_registry[canonical_tool_name]['description']
                    )

                try:
                    # Execute the tool with timing
                    start_time = time.time()
                    tool_function = self.tools_registry[canonical_tool_name]['function']

                    # Parse tool input based on tool type
                    tool_result = await self._execute_tool_with_params(canonical_tool_name, tool_function, tool_input.strip())
                    duration_ms = (time.time() - start_time) * 1000

                    # Log successful tool response
                    if session_id and call_id:
                        agent_logger.log_tool_response(
                            session_id=session_id,
                            call_id=call_id,
                            tool_name=original_tool_name,
                            tool_output=tool_result,
                            duration_ms=duration_ms,
                            success=True
                        )

                    # Replace the tool call with the result
                    tool_call = f"[{original_tool_name}]{tool_input}[/{original_tool_name}]"
                    tool_result_text = f"[{original_tool_name} RESULT]\n{tool_result}\n[/{original_tool_name} RESULT]"
                    agent_response = agent_response.replace(tool_call, tool_result_text)

                except Exception as e:
                    duration_ms = (time.time() - start_time) * 1000 if 'start_time' in locals() else 0

                    # Log tool error
                    if session_id and call_id:
                        agent_logger.log_tool_error(
                            session_id=session_id,
                            call_id=call_id,
                            tool_name=tool_name,
                            error=e,
                            duration_ms=duration_ms
                        )

                    # Replace with error message
                    tool_call = f"[{tool_name}]{tool_input}[/{tool_name}]"
                    error_text = f"[{tool_name} ERROR] {str(e)} [/{tool_name} ERROR]"
                    agent_response = agent_response.replace(tool_call, error_text)
            else:
                # Tool not found - log error
                if session_id:
                    call_id = agent_logger.log_tool_call(
                        session_id=session_id,
                        tool_name=tool_name,
                        tool_input=tool_input.strip(),
                        tool_description="Tool not found"
                    )

                    agent_logger.log_tool_error(
                        session_id=session_id,
                        call_id=call_id,
                        tool_name=tool_name,
                        error=Exception(f"Tool '{tool_name}' not found in registry"),
                        duration_ms=0
                    )

                tool_call = f"[{tool_name}]{tool_input}[/{tool_name}]"
                error_text = f"[{tool_name} ERROR] Tool not found [/{tool_name} ERROR]"
                agent_response = agent_response.replace(tool_call, error_text)

        return agent_response

    async def _execute_tool_with_params(self, tool_name: str, tool_function: callable, tool_input: str) -> str:
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
                parts = [part.strip() for part in tool_input.split(',', 1)]

                if len(parts) == 2:
                    client_name, query = parts
                elif len(parts) == 1:
                    # Default to 'siebert' if only query provided
                    client_name = "siebert"
                    query = parts[0]
                else:
                    raise ValueError("rag_search_content requires format: 'client_name, search_query' or just 'search_query'")

                if not query.strip():
                    raise ValueError("Search query cannot be empty")

                return await tool_function(client_name, query)

            elif tool_name == "rag_get_client_content":
                # Parse: "client_name" or "client_name, document_name"
                parts = [part.strip() for part in tool_input.split(',', 1)]

                if len(parts) == 2:
                    client_name, document_name = parts
                    return await tool_function(client_name, document_name)
                elif len(parts) == 1:
                    client_name = parts[0]
                    return await tool_function(client_name)
                else:
                    raise ValueError("rag_get_client_content requires format: 'client_name' or 'client_name, document_name'")

            else:
                # Default behavior for other tools (single parameter)
                return await tool_function(tool_input)

        except Exception as e:
            # Enhanced error handling with fallback
            error_msg = f"Tool execution error: {str(e)}"

            # Provide intelligent fallback for rag_search_content
            if tool_name == "rag_search_content":
                try:
                    # Try to extract client name from input for fallback
                    parts = [part.strip() for part in tool_input.split(',', 1)]
                    client_name = "siebert"  # Default

                    if len(parts) >= 1 and parts[0] and not any(keyword in parts[0].lower() for keyword in ['mark', 'malek', 'insight', 'market']):
                        # First part might be client name
                        client_name = parts[0]

                    # Fallback to rag_get_client_content
                    from core.infrastructure.tools.rag_tool import RAGTool
                    rag_tool = RAGTool()
                    fallback_result = await rag_tool.get_client_content(client_name)
                    return f"[FALLBACK] Search failed ({str(e)}), retrieved all {client_name} content instead:\n{fallback_result}"
                except Exception as fallback_error:
                    error_msg += f" | Fallback also failed: {str(fallback_error)}"

            raise Exception(error_msg)

    def _validate_tool_parameters(self, tool_name: str, tool_input: str) -> tuple[bool, str]:
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
                parts = [part.strip() for part in tool_input.split(',', 1)]

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
                parts = [part.strip() for part in tool_input.split(',', 1)]

                if len(parts) == 0 or not parts[0].strip():
                    return False, "rag_get_client_content requires at least a client name"

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
        provider_name = context.get('provider')
        model = context.get('model')
        temperature = context.get('temperature')

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
                    LLMProvider.DEEPSEEK: "deepseek-chat"
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
                additional_params=self.provider_config.additional_params
            )

            logger.debug(f"🔧 Using dynamic config: {provider.value}/{model} (temp: {temperature})")
            return dynamic_config

        except Exception as e:
            logger.warning(f"⚠️ Failed to create dynamic config: {e}, using default")
            return self.provider_config

    def _extract_token_usage(self, llm_response) -> TokenUsage:
        """Extract real token usage from LLM API response."""
        try:
            # Check if response has usage information (handle both object and dataclass)
            usage_data = getattr(llm_response, 'usage', None)
            if usage_data:
                usage = usage_data

                # Handle different response formats
                if isinstance(usage, dict):
                    return TokenUsage(
                        prompt_tokens=usage.get('prompt_tokens', 0),
                        completion_tokens=usage.get('completion_tokens', 0),
                        total_tokens=usage.get('total_tokens', 0),
                        reasoning_tokens=usage.get('reasoning_tokens', 0),
                        cached_tokens=usage.get('cached_tokens', 0)
                    )
                else:
                    # Handle object-style usage
                    return TokenUsage(
                        prompt_tokens=getattr(usage, 'prompt_tokens', 0),
                        completion_tokens=getattr(usage, 'completion_tokens', 0),
                        total_tokens=getattr(usage, 'total_tokens', 0),
                        reasoning_tokens=getattr(usage, 'reasoning_tokens', 0),
                        cached_tokens=getattr(usage, 'cached_tokens', 0)
                    )

            # Fallback to estimation if no usage data
            logger.warning("⚠️ No token usage data in LLM response, falling back to estimation")
            return self._estimate_token_usage(llm_response)

        except Exception as e:
            logger.error(f"❌ Error extracting token usage: {e}")
            return self._estimate_token_usage(llm_response)

    def _estimate_token_usage(self, llm_response) -> TokenUsage:
        """Fallback token estimation when real usage is not available."""
        response_text = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)

        # Simple word-based estimation (rough approximation)
        estimated_completion_tokens = len(response_text.split())
        estimated_prompt_tokens = estimated_completion_tokens // 2  # Rough estimate

        return TokenUsage(
            prompt_tokens=estimated_prompt_tokens,
            completion_tokens=estimated_completion_tokens,
            total_tokens=estimated_prompt_tokens + estimated_completion_tokens
        )
