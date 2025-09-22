"""Generate content use case."""

import logging
from typing import Optional, Dict, Any
from uuid import uuid4
from datetime import datetime

from ...domain.entities.content import Content
from ...domain.entities.workflow import Workflow, WorkflowType
from ...domain.entities.task import Task, TaskType, TaskPriority
from ...domain.entities.agent import Agent, AgentRole
from ...domain.repositories.content_repository import ContentRepository
from ...domain.repositories.workflow_repository import WorkflowRepository
from ...domain.repositories.agent_repository import AgentRepository
from ..dto.content_request import ContentGenerationRequest, ContentGenerationResponse, WorkflowMetrics
from ..interfaces.llm_provider_interface import LLMProviderInterface
from ..interfaces.rag_interface import RAGInterface
from ...infrastructure.orchestration.task_orchestrator import TaskOrchestrator
from ...infrastructure.orchestration.agent_executor import AgentExecutor
from ...infrastructure.tools.web_search_tool import WebSearchTool
from ...infrastructure.logging.agent_logger import agent_logger
from ...infrastructure.tools.rag_tool import RAGTool
from ...infrastructure.tools.perplexity_research_tool import PerplexityResearchTool
from ...infrastructure.workflows.registry import execute_dynamic_workflow, list_available_workflows
from ...infrastructure.database.supabase_tracker import get_tracker, SupabaseTracker

logger = logging.getLogger(__name__)


class GenerateContentUseCase:
    """
    Use case for generating content.
    
    This use case orchestrates the entire content generation process,
    from workflow selection to final content creation.
    """
    
    def __init__(
        self,
        content_repository: ContentRepository,
        workflow_repository: WorkflowRepository,
        agent_repository: AgentRepository,
        llm_provider: LLMProviderInterface,
        provider_config: Any,
        rag_service: Optional[RAGInterface] = None,
        serper_api_key: Optional[str] = None,
        perplexity_api_key: Optional[str] = None
    ):
        self.content_repository = content_repository
        self.workflow_repository = workflow_repository
        self.agent_repository = agent_repository
        self.llm_provider = llm_provider
        self.provider_config = provider_config
        self.rag_service = rag_service

        # Initialize orchestration components
        self.task_orchestrator = TaskOrchestrator(workflow_repository)
        self.agent_executor = AgentExecutor(agent_repository, llm_provider, provider_config)

        # Initialize tools
        self.web_search_tool = WebSearchTool(serper_api_key)
        self.rag_tool = RAGTool()
        # Do not pull provider model from env; pass explicitly if needed
        self.perplexity_tool = PerplexityResearchTool(perplexity_api_key)

        # Register tools with agent executor
        self._register_tools()

        # Optional tracking
        self.tracker: Optional[SupabaseTracker] = get_tracker()

    async def execute(self, request: ContentGenerationRequest) -> ContentGenerationResponse:
        """
        Execute content generation using dynamic workflow system.

        Args:
            request: Content generation request

        Returns:
            Content generation response
        """
        try:
            logger.info(f"Starting content generation for topic: {request.topic}")
            start_time = datetime.utcnow()

            # Initialize tracking (start run)
            run_id: Optional[str] = None
            if self.tracker is not None:
                try:
                    # Get agent executor info for tracking
                    agent_executor_info = f"{self.agent_executor.__class__.__name__}({self.provider_config.provider.value})"

                    run_id = self.tracker.start_workflow_run(
                        client_name=request.client_profile or "default",
                        workflow_name=request.workflow_type or "content_generation",
                        topic=request.topic,
                        agent_executor=agent_executor_info
                    )
                    self.tracker.add_log(run_id, "INFO", f"Started content generation for topic: {request.topic}")
                    if request.provider_config:
                        self.tracker.add_log(run_id, "INFO", f"Provider: {request.provider_config.provider.value}")
                        if request.provider_config.model:
                            self.tracker.add_log(run_id, "INFO", f"Model: {request.provider_config.model}")
                except Exception as track_err:
                    logger.warning(f"Tracking initialization failed: {track_err}")
                    run_id = None

            # 1. Build dynamic context from request
            context = await self._build_dynamic_context(request)
            if run_id:
                context['run_id'] = run_id
                context['tracker'] = self.tracker
                if self.tracker:
                    agent_logger.set_tracker(self.tracker, run_id)
                    self.rag_tool.set_run(run_id, self.tracker)

            # 2. Execute dynamic workflow
            # Default to enhanced_article if workflow_type is None or not specified
            workflow_type = request.workflow_type
            if not workflow_type or workflow_type == 'None':
                workflow_type = 'enhanced_article'
                logger.info(f"🔧 No workflow_type specified, defaulting to: {workflow_type}")

            workflow_result = await self._execute_dynamic_workflow(workflow_type, context)

            # Minimal log of completion before saving content
            if self.tracker is not None and run_id:
                self.tracker.add_log(run_id, "INFO", f"Dynamic workflow '{workflow_type}' completed")

            # 3. Create content entity from workflow result
            content = await self._create_content_from_dynamic_result(
                workflow_result, request
            )

            # 4. Save content
            saved_content = await self.content_repository.save(content)
            if self.tracker is not None and run_id:
                try:
                    self.tracker.save_run_content(
                        run_id=run_id,
                        client_name=request.client_profile or "default",
                        workflow_name=workflow_type,
                        title=saved_content.title,
                        content=saved_content.body,
                        metadata=saved_content.metadata,
                    )
                except Exception as track_err:
                    logger.warning(f"Saving run content failed: {track_err}")

            # 5. Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds()

            # 6. Extract workflow metrics from result
            workflow_metrics = None
            if 'workflow_metrics' in workflow_result:
                metrics_data = workflow_result['workflow_metrics']
                workflow_metrics = WorkflowMetrics(
                    total_cost=metrics_data.get('total_cost', 0.0),
                    total_tokens=metrics_data.get('total_tokens', 0),
                    duration_seconds=metrics_data.get('duration_seconds', 0.0),
                    agents_used=metrics_data.get('agents_used', 0),
                    success_rate=metrics_data.get('success_rate', 1.0),
                    tasks_completed=metrics_data.get('tasks_completed', 0),
                    tasks_failed=metrics_data.get('tasks_failed', 0),
                    tool_calls=metrics_data.get('tool_calls', 0),
                    llm_calls=metrics_data.get('llm_calls', 0)
                )

            # 7. Create response
            response = ContentGenerationResponse(
                content_id=saved_content.id,
                title=saved_content.title,
                body=saved_content.body,
                content_type=saved_content.content_type,
                content_format=saved_content.content_format,
                workflow_id=workflow_result.get('workflow_id', 'dynamic'),
                generation_time_seconds=execution_time,
                word_count=saved_content.metrics.word_count,
                character_count=saved_content.metrics.character_count,
                reading_time_minutes=saved_content.metrics.reading_time_minutes,
                tasks_completed=workflow_result.get('tasks_completed', 0),
                total_tasks=workflow_result.get('total_tasks', 0),
                success=True,
                workflow_metrics=workflow_metrics,
                metadata={
                    "workflow_type": request.workflow_type,
                    "client_profile": request.client_profile,
                    "provider": request.provider_config.provider.value if request.provider_config else None,
                    "dynamic_workflow": True,
                    "workflow_summary": workflow_result.get('workflow_summary', {}),
                    "html_email_container": workflow_result.get('html_email_container'),
                    "compliance_markdown": workflow_result.get('compliance_markdown'),
                    "workflow_output_format": workflow_result.get('workflow_output_format'),
                    "generated_image": workflow_result.get('generated_image'),
                    "image_metadata": workflow_result.get('image_metadata'),
                    "image_generation_failed": workflow_result.get('image_generation_failed'),
                    "image_generation_warning": workflow_result.get('image_generation_warning')
                },
                generated_image=workflow_result.get('generated_image'),
                image_metadata=workflow_result.get('image_metadata')
            )

            # Complete tracking (success)
            if self.tracker is not None and run_id:
                try:
                    total_cost = 0.0
                    total_tokens = 0
                    if workflow_metrics:
                        total_cost = workflow_metrics.total_cost
                        total_tokens = workflow_metrics.total_tokens
                    self.tracker.complete_workflow_run(
                        run_id=run_id,
                        status="completed",
                        cost=total_cost,
                        tokens=total_tokens,
                    )
                    self.tracker.add_log(
                        run_id, "INFO", f"Content generation completed successfully in {execution_time:.2f}s"
                    )
                except Exception as track_err:
                    logger.warning(f"Tracking completion failed: {track_err}")

            logger.info(f"Content generation completed successfully in {execution_time:.2f}s")
            return response

        except Exception as e:
            # Complete tracking (failure)
            try:
                if self.tracker is not None and 'run_id' in locals() and run_id:
                    self.tracker.complete_workflow_run(
                        run_id=run_id,
                        status="failed",
                        error=str(e),
                    )
                    self.tracker.add_log(run_id, "ERROR", f"Content generation failed: {str(e)}")
            except Exception as track_err:  # pragma: no cover
                logger.warning(f"Tracking failure logging failed: {track_err}")

            logger.error(f"Content generation failed: {str(e)}")
            return ContentGenerationResponse(
                content_id=uuid4(),
                title="",
                body="",
                content_type=request.content_type,
                content_format=request.content_format,
                success=False,
                error_message=str(e)
            )

    async def _build_dynamic_context(self, request: ContentGenerationRequest) -> Dict[str, Any]:
        """
        Build dynamic context from request with all variables.

        Args:
            request: Content generation request

        Returns:
            Dynamic context dictionary
        """
        # Base context
        context = {
            'topic': request.topic,
            'client_name': request.client_profile or 'default',
            'client_profile': request.client_profile or 'default',
            'context': request.context or '',
            'workflow_type': request.workflow_type,
            'workflow_id': str(uuid4()),
            'workflow_name': f"content_generation_{str(uuid4())[:8]}"
        }

        # Add ALL generation parameters dynamically
        if request.generation_params:
            params_dict = request.generation_params.__dict__
            for key, value in params_dict.items():
                if value is not None:  # Only add non-None values
                    context[key] = value

        # Add provider config if available
        if request.provider_config:
            context['provider'] = request.provider_config.provider.value
            context['model'] = request.provider_config.model
            context['temperature'] = request.provider_config.temperature

        # Add agent executor and repository to context for task execution
        context['agent_executor'] = self.agent_executor
        context['agent_repository'] = self.agent_repository

        logger.info(f"🔧 Built dynamic context with {len(context)} variables")
        logger.debug(f"📊 Context keys: {list(context.keys())}")

        return context

    async def _execute_dynamic_workflow(self, workflow_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute workflow using dynamic workflow system.

        Args:
            workflow_type: Type of workflow to execute
            context: Dynamic context

        Returns:
            Workflow execution results
        """
        try:
            # Check if workflow type is available
            available_workflows = list_available_workflows()
            if workflow_type not in available_workflows:
                logger.warning(f"⚠️ Dynamic workflow not found: {workflow_type}")
                logger.info(f"📋 Available workflows: {list(available_workflows.keys())}")

                # Fallback to legacy workflow execution
                return await self._execute_legacy_workflow(workflow_type, context)

            # Execute dynamic workflow
            logger.info(f"🚀 Executing dynamic workflow: {workflow_type}")
            result = await execute_dynamic_workflow(workflow_type, context)

            logger.info(f"✅ Dynamic workflow completed: {workflow_type}")
            return result

        except Exception as e:
            logger.error(f"❌ Dynamic workflow execution failed: {str(e)}")
            logger.info("🔄 Falling back to legacy workflow execution")
            return await self._execute_legacy_workflow(workflow_type, context)

    async def _get_or_create_workflow(self, request: ContentGenerationRequest) -> Workflow:
        """Get existing workflow or create new one based on request."""
        if request.workflow_type:
            # Try to get existing workflow template
            workflows = await self.workflow_repository.get_by_type(
                WorkflowType(request.workflow_type)
            )
            if workflows:
                # Clone the template for this execution
                template = workflows[0]
                workflow = await self.workflow_repository.clone_workflow(
                    template.id, f"{template.name}_{uuid4().hex[:8]}"
                )
                return workflow

    async def _execute_legacy_workflow(self, workflow_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback to legacy workflow execution.

        Args:
            workflow_type: Type of workflow
            context: Execution context

        Returns:
            Legacy workflow results
        """
        logger.info(f"🔄 Executing legacy workflow: {workflow_type}")

        # Create legacy workflow
        workflow = await self._create_legacy_workflow(workflow_type, context)

        # Save workflow to repository so it can be found later
        try:
            saved_workflow = await self.workflow_repository.save(workflow)
            logger.info(f"✅ Workflow saved to repository: {saved_workflow.id}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to save workflow to repository: {e}")
            # Continue with execution even if save fails
            saved_workflow = workflow

        # Execute using task orchestrator
        result = await self.task_orchestrator.execute_workflow(
            saved_workflow,
            context,
            verbose=True,
            run_id=context.get('run_id'),
            tracker=context.get('tracker'),
        )

        return {
            'workflow_id': saved_workflow.id,
            'tasks_completed': len(saved_workflow.tasks),
            'total_tasks': len(saved_workflow.tasks),
            'final_output': result.get('final_output', ''),
            'task_outputs': result.get('task_outputs', {}),
            'legacy_execution': True
        }

    async def _create_legacy_workflow(self, workflow_type: str, context: Dict[str, Any]) -> Workflow:
        """Create workflow using legacy hardcoded approach."""
        if workflow_type in {"enhanced_article", "enhanced_article_with_image"}:
            return await self._create_enhanced_article_workflow(context)
        else:
            # Default workflow - create a simple workflow with basic tasks
            workflow = Workflow(
                name=f"default_{workflow_type}",
                description=f"Default workflow for {workflow_type}"
            )

            # Add a simple content generation task
            from core.domain.entities.task import Task, TaskType, TaskPriority
            from core.domain.entities.agent import AgentRole
            from uuid import uuid4

            task = Task(
                id=uuid4(),
                name="Generate Content",
                description=f"Generate {workflow_type} content about: {context.get('topic', 'the given topic')}",
                expected_output=f"A well-written {workflow_type} in markdown format",
                task_type=TaskType.WRITING,
                agent_role=AgentRole.WRITER,
                priority=TaskPriority.HIGH
            )

            workflow.add_task(task)
            workflow.mark_ready()  # CRITICAL: Mark as ready so it can be executed

            return workflow

    async def _create_enhanced_article_workflow(self, context: Dict[str, Any]) -> Workflow:
        """Create enhanced article workflow with research and writing tasks."""
        from core.domain.entities.task import Task, TaskType, TaskPriority
        from core.domain.entities.agent import AgentRole
        from uuid import uuid4

        workflow = Workflow(
            name="enhanced_article_workflow",
            description="Enhanced article generation with research and quality assurance"
        )

        # Task 1: Research
        task1 = Task(
            id=uuid4(),
            name="Research Topic",
            description=f"""
Research comprehensive information about: {context.get('topic', 'the given topic')}

RESEARCH REQUIREMENTS:
- Find current trends and developments
- Identify key statistics and data points
- Gather expert opinions and quotes
- Look for real-world examples and case studies
- Verify information accuracy and credibility

TARGET AUDIENCE: {context.get('target_audience', 'general audience')}
TONE: {context.get('tone', 'professional')}
            """,
            expected_output="Comprehensive research notes with verified facts, statistics, and examples",
            task_type=TaskType.RESEARCH,
            agent_role=AgentRole.RESEARCHER,
            priority=TaskPriority.HIGH
        )

        # Task 2: Content Generation
        task2 = Task(
            id=uuid4(),
            name="Generate Article",
            description=f"""
Create a high-quality article about: {context.get('topic', 'the given topic')}

CONTENT REQUIREMENTS:
- Use research findings from previous task
- Structure with clear headings and subheadings
- Include relevant examples and case studies
- Add statistics and data points where appropriate
- Maintain consistent tone throughout
- Ensure content is engaging and informative

TARGET AUDIENCE: {context.get('target_audience', 'general audience')}
TONE: {context.get('tone', 'professional')}
LENGTH: {context.get('length', 'medium')} length article
            """,
            expected_output="Well-structured article in markdown format with proper headings",
            task_type=TaskType.WRITING,
            agent_role=AgentRole.WRITER,
            dependencies=[task1.id],
            priority=TaskPriority.HIGH
        )

        # Add tasks to workflow
        workflow.add_task(task1)
        workflow.add_task(task2)
        workflow.mark_ready()  # CRITICAL: Mark as ready so it can be executed

        return workflow

    async def _create_content_from_dynamic_result(
        self,
        workflow_result: Dict[str, Any],
        request: ContentGenerationRequest
    ) -> Content:
        """
        Create content entity from dynamic workflow result.

        Args:
            workflow_result: Result from dynamic workflow execution
            request: Original request

        Returns:
            Content entity
        """
        # Extract final content from workflow result
        final_output = workflow_result.get('final_output', '')

        # If no final output, try to get from task outputs
        if not final_output:
            task_outputs = workflow_result.get('task_outputs', {})
            # Get the last task output as final content
            if task_outputs:
                final_output = list(task_outputs.values())[-1]

        # Debug logging to see what we're getting
        logger.info(f"🔍 Workflow result keys: {list(workflow_result.keys())}")
        logger.info(f"🔍 Final output length: {len(final_output) if final_output else 0}")
        if final_output:
            logger.info(f"🔍 Final output preview: {final_output[:200]}...")
        else:
            logger.warning("⚠️ No final output found in workflow result")

        # Create content entity
        content = Content(
            title=self._extract_title_from_content(final_output, request.topic),
            body=final_output,
            content_type=request.content_type,
            content_format=request.content_format,
            client_profile=request.client_profile,
            workflow_id=workflow_result.get('workflow_id'),
            metadata={
                'workflow_type': request.workflow_type,
                'generation_params': request.generation_params.to_dict() if request.generation_params else {},
                'workflow_summary': workflow_result.get('workflow_summary', {}),
                'dynamic_workflow': True,
                'generated_image': workflow_result.get('generated_image'),
                'image_metadata': workflow_result.get('image_metadata')
            }
        )

        return content

    def _extract_title_from_content(self, content: str, fallback_topic: str) -> str:
        """
        Extract title from content or use fallback.

        Args:
            content: Generated content
            fallback_topic: Fallback topic to use as title

        Returns:
            Extracted or generated title
        """
        if not content:
            return f"Article: {fallback_topic}"

        # Try to extract title from first line if it looks like a title
        lines = content.split('\n')
        first_line = lines[0].strip() if lines else ""

        # Check if first line looks like a title (starts with #, is short, etc.)
        if first_line.startswith('#'):
            return first_line.replace('#', '').strip()
        elif len(first_line) < 100 and not first_line.endswith('.'):
            return first_line
        else:
            # Generate title from topic
            return f"Article: {fallback_topic}"

    def _register_tools(self) -> None:
        """Register tools with the agent executor."""
        from ...infrastructure.tools.tool_names import ToolNames
        from ...infrastructure.tools.image_generation_tool import image_generation_tool
        self.agent_executor.register_tools({
            ToolNames.WEB_SEARCH_SERPER: {
                'function': self.web_search_tool.search,
                'description': 'Search the web for current information and trends'
            },
            ToolNames.RAG_GET_CLIENT_CONTENT: {
                'function': self.rag_tool.get_client_content,
                'description': 'Retrieve content from client knowledge base'
            },
            ToolNames.RAG_SEARCH_CONTENT: {
                'function': self.rag_tool.search_content,
                'description': 'Search within client knowledge base'
            },
            ToolNames.WEB_SEARCH_PERPLEXITY: {
                'function': self.perplexity_tool.search,
                'description': 'Search using Perplexity AI'
            },
            ToolNames.IMAGE_GENERATION: {
                'function': image_generation_tool,
                'description': 'Generate contextual images for enhanced articles'
            }
        })

    async def _configure_workflow_agents(self, workflow: Workflow, request: ContentGenerationRequest) -> None:
        """Configure agents for the workflow."""
        # Load or create agents based on workflow type
        if request.workflow_type in {"enhanced_article", "enhanced_article_with_image"}:
            await self._setup_enhanced_article_agents(workflow, request)
        elif request.workflow_type == "newsletter_premium":
            await self._setup_newsletter_premium_agents(workflow, request)
        else:
            await self._setup_default_agents(workflow, request)
    
    async def _execute_workflow(self, workflow: Workflow, request: ContentGenerationRequest) -> str:
        """Execute the workflow using the task orchestrator."""
        try:
            # Build execution context with comprehensive variable mapping
            context = {
                'topic': request.topic,
                'client_name': request.client_profile or 'default',
                'context': request.context or '',
                'workflow_type': request.workflow_type,
                'generation_params': request.generation_params.__dict__ if request.generation_params else {}
            }

            # Add generation parameters as direct context variables for template substitution
            if request.generation_params:
                params = request.generation_params

                # Map common parameters
                context.update({
                    'target_audience': getattr(params, 'target_audience', '') or getattr(params, 'target', ''),
                    'target': getattr(params, 'target', ''),
                    'tone': getattr(params, 'tone', ''),
                    'target_word_count': getattr(params, 'target_word_count', ''),
                    'include_statistics': getattr(params, 'include_statistics', False),
                    'include_examples': getattr(params, 'include_examples', False),
                    'include_sources': getattr(params, 'include_sources', False),
                    'custom_instructions': getattr(params, 'custom_instructions', ''),
                    'image_style': getattr(params, 'image_style', ''),
                    'image_provider': getattr(params, 'image_provider', ''),
                })

                # Newsletter specific parameters
                if hasattr(params, 'newsletter_topic'):
                    context['newsletter_topic'] = getattr(params, 'newsletter_topic', '')
                if hasattr(params, 'edition_number'):
                    context['edition_number'] = getattr(params, 'edition_number', '')
                if hasattr(params, 'featured_sections'):
                    context['featured_sections'] = getattr(params, 'featured_sections', [])

            # Ensure target_audience is set (fallback to target if not set)
            if not context.get('target_audience') and context.get('target'):
                context['target_audience'] = context['target']

            # Add agent executor and repository to context
            context['agent_executor'] = self.agent_executor
            context['agent_repository'] = self.agent_repository

            # Execute workflow through handler (which uses orchestrator internally)
            handler = self.workflow_registry.get_handler(workflow_type)
            execution_result = await handler.execute(context)

            # Check if handler set a final_output in context (intelligent selection)
            if 'final_output' in execution_result and execution_result['final_output']:
                final_output = execution_result['final_output']
                logger.info(f"✅ Using handler-selected final output ({len(final_output)} chars)")
                return final_output

            # Fallback to task outputs if no handler final_output
            task_outputs = {}
            for key, value in execution_result.items():
                if key.endswith('_output') and isinstance(value, str):
                    task_outputs[key] = value

            if task_outputs:
                # Return the last task's output as fallback
                final_output = list(task_outputs.values())[-1]
                logger.info(f"⚠️ Using fallback final output ({len(final_output)} chars)")
                return final_output
            else:
                return "No content generated from workflow execution"

        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            raise
    
    def _build_generation_context(self, request: ContentGenerationRequest) -> str:
        """Build context for content generation."""
        context_parts = []
        
        if request.generation_params:
            context_parts.append(request.generation_params.get_generation_context())
            context_parts.append(request.generation_params.get_content_requirements())
        
        if request.client_profile and self.rag_service:
            # Would retrieve client-specific context from RAG
            pass
        
        return "\n\n".join(context_parts)
    
    def _build_generation_prompt(self, request: ContentGenerationRequest, context: str) -> str:
        """Build the generation prompt."""
        prompt_parts = [
            f"Generate a {request.content_type.value} about: {request.topic}",
            "",
            "Context:",
            context,
            "",
            "Requirements:",
            f"- Format: {request.content_format.value}",
            f"- Type: {request.content_type.value}"
        ]
        
        if request.custom_instructions:
            prompt_parts.extend(["", "Additional Instructions:", request.custom_instructions])
        
        return "\n".join(prompt_parts)
    
    async def _create_content_from_result(
        self, 
        result: str, 
        request: ContentGenerationRequest, 
        workflow_id: Optional[str]
    ) -> Content:
        """Create content entity from generation result."""
        # Extract title from result (simplified)
        lines = result.split('\n')
        title = lines[0].strip('#').strip() if lines else request.topic
        
        content = Content(
            title=title,
            body=result,
            content_type=request.content_type,
            content_format=request.content_format,
            workflow_id=workflow_id,
            client_profile=request.client_profile,
            target_audience=request.generation_params.target_audience if request.generation_params else "",
            topic=request.topic
        )
        
        return content

    async def _setup_enhanced_article_agents(self, workflow: Workflow, request: ContentGenerationRequest) -> None:
        """Setup agents for Enhanced Article workflow."""
        # Create RAG Specialist Agent
        rag_specialist = Agent(
            name="rag_specialist",
            role=AgentRole.RESEARCHER,
            goal="Retrieve and analyze client knowledge base content to create comprehensive project briefs",
            backstory="You are an expert at analyzing client documentation and creating detailed project briefs that guide content creation.",
            system_message="You specialize in retrieving relevant information from knowledge bases and creating structured briefs.",
            tools=["rag_get_client_content", "rag_search_content"]
        )

        # Create Web Searcher Agent
        web_searcher = Agent(
            name="web_searcher",
            role=AgentRole.RESEARCHER,
            goal="Find current web information and trends to enhance content with up-to-date insights",
            backstory="You are an expert web researcher who finds the most current and relevant information to enhance content.",
            system_message="You specialize in web research and finding current trends and information.",
            tools=["web_search", "web_search_financial"]
        )

        # Create Copywriter Agent
        copywriter = Agent(
            name="copywriter",
            role=AgentRole.WRITER,
            goal="Create engaging, well-structured content that aligns with brand guidelines and speaks to the target audience",
            backstory="You are an expert copywriter who creates compelling content tailored to specific audiences and brand voices.",
            system_message="You specialize in creating high-quality, engaging content that meets specific requirements and brand guidelines.",
            tools=[]
        )

        # Save agents
        await self.agent_repository.save(rag_specialist)
        await self.agent_repository.save(web_searcher)
        await self.agent_repository.save(copywriter)

        # Create Enhanced Article tasks
        await self._create_enhanced_article_tasks(workflow, request)

    async def _create_enhanced_article_tasks(self, workflow: Workflow, request: ContentGenerationRequest) -> None:
        """Create tasks for Enhanced Article workflow."""
        # Task 1: RAG Specialist - Brief Creation
        task1 = Task(
            name="task1_brief",
            description=f"""
TASK 1 - SETTING & BRIEF CREATION:
Recupera tutto il contenuto del cliente selezionato e crea un brief di lavoro completo che integri:

INPUT SOURCES:
- Topic richiesto: {{topic}}
- Contesto aggiuntivo: {{context}}
- Target audience: {{target_audience}}
- Cliente selezionato: {{client_name}}
- Knowledge base del cliente (utilizzando RAG Content Retriever)

STEP 1: RETRIEVE CLIENT CONTENT
Prima di tutto, usa il tool RAG per recuperare il contenuto del cliente:
[rag_get_client_content] {{client_name}} [/rag_get_client_content]

STEP 2: ANALYZE AND CREATE BRIEF
Analizza il contenuto recuperato e crea un brief strutturato che includa:

OBIETTIVI:
1. Analizza la knowledge base del cliente per comprendere brand voice, style guidelines, e contenuti esistenti
2. Integra le informazioni dall'interfaccia (topic, contesto, target)
3. Crea un brief strutturato che serva da riferimento per gli altri agent
4. Definisci chiaramente ruoli, obiettivi e output richiesto

STRUTTURA DEL BRIEF:
- Executive Summary del progetto
- Brand Context & Guidelines (dal RAG)
- Topic Analysis & Objectives
- Target Audience Profile
- Content Requirements & Specifications
- Agent Roles & Responsibilities
- Success Criteria & Expected Output
            """,
            expected_output="A comprehensive project brief in markdown format containing all specified sections",
            task_type=TaskType.RESEARCH,
            agent_role=AgentRole.RESEARCHER,
            priority=TaskPriority.HIGH
        )

        # Task 2: Web Searcher - Research Enhancement
        task2 = Task(
            name="task2_research",
            description=f"""
TASK 2 - WEB RESEARCH & BRIEF ENHANCEMENT:
Ricevi il brief creato nel Task precedente e arricchiscilo con ricerche web aggiornate e pertinenti.

CONTEXT FROM PREVIOUS TASK:
Il task precedente ha creato un brief completo. Utilizza questo brief come base e arricchiscilo.

INPUT:
{{{{task1_brief}}}}

STEP 1: ANALYZE BRIEF
Analizza il brief ricevuto per identificare gap informativi e aree che necessitano di ricerca web.

STEP 2: CONDUCT WEB RESEARCH
Conduci ricerche web mirate utilizzando questi tool calls:

Per informazioni generali:
[web_search] {{topic}} trends 2025 latest developments [/web_search]

Per contenuti finanziari (se applicabile):
[web_search_financial] {{topic}}, crypto,day_trading [/web_search_financial]

Per statistiche e dati:
[web_search] {{topic}} statistics data recent studies [/web_search]

STEP 3: INTEGRATE FINDINGS
Integra le informazioni trovate nel brief esistente e crea un brief arricchito.

OBIETTIVI:
1. Analizza il brief ricevuto per identificare gap informativi
2. Conduci ricerche web mirate su:
   - Trend attuali relativi a {{topic}}
   - Statistiche e dati recenti
   - Best practices del settore
   - Casi studio rilevanti
3. Integra le informazioni trovate nel brief esistente
4. Affina e migliora le sezioni del brief con dati aggiornati

FOCUS AREAS:
- Cerca informazioni che supportino gli obiettivi definiti nel brief
- Identifica opportunità per differenziare il contenuto
- Trova dati e statistiche che rafforzino i messaggi chiave
            """,
            expected_output="Enhanced brief with web research integration in markdown format",
            task_type=TaskType.RESEARCH,
            agent_role=AgentRole.RESEARCHER,
            dependencies=[task1.id],
            priority=TaskPriority.HIGH
        )

        # Task 3: Copywriter - Final Content Creation
        task3 = Task(
            name="task3_content",
            description=f"""
TASK 3 - FINAL CONTENT CREATION:
Utilizzando il brief arricchito del task precedente, crea l'articolo finale che rispetti tutti i requisiti definiti.

CONTEXT FROM PREVIOUS TASKS:
Hai accesso al brief originale e alla ricerca web integrata. Utilizza entrambi per creare contenuto eccellente.

INPUT:
{{{{task2_research}}}}

OBIETTIVI:
1. Analizza il brief arricchito per comprendere tutti i requirements
2. Struttura l'articolo seguendo le guidelines del brand
3. Integra seamlessly le informazioni di ricerca con il brand voice
4. Crea contenuto engaging che parli direttamente al target audience: {{target_audience}}
5. Assicura coerenza con tutti i criteri di successo definiti nel brief

CONTENT CREATION GUIDELINES:
- Segui scrupolosamente il brand voice definito nel brief
- Utilizza la terminologia specifica del cliente {{client_name}}
- Integra naturalmente dati e statistiche dalla ricerca
- Mantieni focus su obiettivi e target audience definiti
- Crea un flow narrativo coinvolgente e professionale
- Include call-to-action appropriati

QUALITY ASSURANCE:
- Verifica allineamento con brand guidelines
- Controlla coerenza del tone of voice
- Assicura che tutti i key messages siano inclusi
- Valida la rilevanza per il target audience
            """,
            expected_output="A polished, publication-ready article in markdown format",
            task_type=TaskType.WRITING,
            agent_role=AgentRole.WRITER,
            dependencies=[task2.id],
            priority=TaskPriority.HIGH
        )

        # Add tasks to workflow
        workflow.add_task(task1)
        workflow.add_task(task2)
        workflow.add_task(task3)
        workflow.mark_ready()

    async def _setup_newsletter_premium_agents(self, workflow: Workflow, request: ContentGenerationRequest) -> None:
        """Setup agents for Newsletter Premium workflow."""
        # Similar to enhanced article but with newsletter-specific tasks
        pass

    async def _setup_default_agents(self, workflow: Workflow, request: ContentGenerationRequest) -> None:
        """Setup default agents for basic workflows."""
        # Create simple research and writing tasks
        pass
