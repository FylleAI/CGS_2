"""
Base workflow handler for dynamic workflow execution.
"""

import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pathlib import Path

from ....domain.entities.task import Task, TaskStatus
from ....domain.entities.workflow import Workflow
from ...utils.template_utils import substitute_template
from ...logging.workflow_reporter import workflow_reporter

logger = logging.getLogger(__name__)


class WorkflowHandler(ABC):
    """
    Base class for all workflow handlers.
    
    Each workflow type should inherit from this class and implement
    the specific business logic methods.
    """
    
    def __init__(self, workflow_type: str):
        self.workflow_type = workflow_type
        self.template = self.load_template()
        logger.info(f"🏗️ Initialized workflow handler: {workflow_type}")
    
    def load_template(self) -> Dict[str, Any]:
        """Load workflow template from JSON file."""
        template_path = Path(__file__).parent.parent / "templates" / f"{self.workflow_type}.json"
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template = json.load(f)
                logger.debug(f"📋 Loaded template for {self.workflow_type}")
                return template
        except FileNotFoundError:
            logger.error(f"❌ Template not found: {template_path}")
            raise ValueError(f"Workflow template not found for: {self.workflow_type}")
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in template: {template_path} - {e}")
            raise ValueError(f"Invalid template format for: {self.workflow_type}")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the complete workflow with dynamic context.

        Args:
            context: Dynamic context with all variables from frontend

        Returns:
            Updated context with execution results
        """
        workflow_id = context.get('workflow_id', f"{self.workflow_type}_{int(time.time())}")
        logger.info(f"🚀 Starting workflow execution: {self.workflow_type} (ID: {workflow_id})")
        logger.debug(f"📊 Input context keys: {list(context.keys())}")

        # Start workflow tracking
        workflow_reporter.start_workflow_tracking(
            workflow_id=workflow_id,
            workflow_type=self.workflow_type,
            context=context
        )

        try:
            # 1. Validate inputs (can be overridden)
            self.validate_inputs(context)
            logger.debug("✅ Input validation passed")

            # 2. Prepare context (can be overridden)
            context = self.prepare_context(context)
            logger.debug("✅ Context preparation completed")

            # 3. Create workflow with dynamic tasks
            workflow = self.create_workflow(context)
            logger.debug(f"✅ Created workflow with {len(workflow.tasks)} tasks")

            # 4. Execute tasks with conditional logic
            execution_results = await self.execute_tasks(workflow, context)
            context.update(execution_results)

            # 5. Post-process results (can be overridden)
            print(f"🔧 CALLING POST-PROCESSING: {type(self).__name__}")
            context = self.post_process_workflow(context)
            print(f"🔧 POST-PROCESSING RETURNED: {type(context)}")
            logger.debug("✅ Post-processing completed")

            # Get final output for reporting
            final_output = context.get('final_content', context.get('content', ''))

            # Complete workflow tracking
            workflow_metrics = workflow_reporter.complete_workflow_tracking(
                workflow_id=workflow_id,
                final_output=final_output,
                success=True
            )

            # Add metrics to context for API response
            if workflow_metrics:
                context['workflow_metrics'] = {
                    'total_cost': workflow_metrics.total_cost,
                    'total_tokens': workflow_metrics.total_tokens,
                    'duration_seconds': workflow_metrics.total_duration_ms / 1000,
                    'agents_used': len(workflow_metrics.agents_used),
                    'success_rate': workflow_metrics.success_rate
                }

            logger.info(f"🎉 Workflow execution completed: {self.workflow_type}")
            return context

        except Exception as e:
            logger.error(f"❌ Workflow execution failed: {self.workflow_type} - {str(e)}")

            # Complete workflow tracking with error
            workflow_reporter.complete_workflow_tracking(
                workflow_id=workflow_id,
                final_output="",
                success=False
            )

            raise
    
    def create_workflow(self, context: Dict[str, Any]) -> Workflow:
        """Create workflow with dynamic tasks based on template and context."""
        workflow = Workflow(
            name=f"{self.workflow_type}_{context.get('workflow_id', 'unknown')}",
            description=self.template.get('description', f"Dynamic {self.workflow_type} workflow")
        )

        # Create tasks dynamically
        for task_template in self.template.get('tasks', []):
            task = self.create_task(task_template, context)
            if task:  # Only add if not skipped
                workflow.add_task(task)

        # CRITICAL FIX: Mark workflow as ready for execution
        workflow.mark_ready()
        logger.debug(f"✅ Workflow marked as ready: {workflow.name}")

        return workflow
    
    def create_task(self, task_template: Dict[str, Any], context: Dict[str, Any]) -> Optional[Task]:
        """
        Create a single task from template with dynamic substitution.
        
        Args:
            task_template: Task template from JSON
            context: Dynamic context for substitution
            
        Returns:
            Task instance or None if task should be skipped
        """
        task_id = task_template.get('id')
        
        # Check if task should be skipped (conditional logic)
        if self.should_skip_task(task_id, context):
            logger.info(f"⏭️ Skipping task: {task_id}")
            return None
        
        # Substitute template variables in description
        description_template = task_template.get('description_template', '')
        description = substitute_template(description_template, context)
        
        # Create task
        task = Task(
            id=task_id,
            name=task_template.get('name', task_id),
            description=description,
            agent_role=task_template.get('agent', 'default'),
            dependencies=task_template.get('dependencies', [])
        )
        
        logger.debug(f"📝 Created task: {task_id}")
        return task
    
    async def execute_tasks(self, workflow: Workflow, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute all tasks in the workflow with dependency management."""
        execution_results = {}
        task_outputs = {}
        
        for task in workflow.tasks:
            logger.info(f"🔄 Executing task: {task.name}")
            
            # Add previous task outputs to context
            enhanced_context = {**context, **task_outputs}
            
            # Execute task (this will be handled by the task orchestrator)
            task_output = await self.execute_single_task(task, enhanced_context)
            
            # Store task output
            task_outputs[task.id] = task_output
            execution_results[f"{task.id}_output"] = task_output
            
            # Post-process task (can be overridden)
            enhanced_context = self.post_process_task(task.id, task_output, enhanced_context)
            context.update(enhanced_context)
            
            logger.info(f"✅ Task completed: {task.name}")
        
        return execution_results
    
    async def execute_single_task(self, task: Task, context: Dict[str, Any]) -> str:
        """
        Execute a single task directly using the agent executor from context.

        This simplified approach removes the need for temporary workflows
        and executes tasks directly through the agent system.

        Args:
            task: Task to execute
            context: Execution context containing agent_executor

        Returns:
            Task execution result
        """
        logger.info(f"🚀 Executing task directly: {task.name}")

        # Get agent executor from context
        agent_executor = context.get('agent_executor')
        if not agent_executor:
            logger.error("❌ CRITICAL: No agent_executor found in context")
            raise Exception("No agent executor available - system cannot proceed without proper agent execution")

        # Check if agent_repository is available
        agent_repository = context.get('agent_repository')
        logger.debug(f"🔍 Agent repository available: {agent_repository is not None}")

        try:
            logger.debug(f"🔧 Direct execution for task: {task.name} with agent: {task.agent_role}")

            # Get the appropriate agent for this task
            agent = await self._get_agent_for_task(task, context)
            if not agent:
                logger.error(f"❌ CRITICAL: No agent found for task {task.name}")
                raise Exception(f"No agent available for task {task.name} - system cannot proceed without proper agent")

            # Execute task directly using agent executor
            # This bypasses the complex temporary workflow system completely
            enhanced_context = {
                **context,
                'task_id': str(task.id),
                'task_name': task.name,
                'workflow_id': context.get('workflow_id', 'unknown')
            }

            logger.info(f"🎯 Executing agent for task: {task.name}")
            result = await agent_executor.execute_agent(
                agent=agent,
                task_description=task.description,
                context=enhanced_context
            )

            logger.info(f"✅ Task completed successfully: {task.name}")
            logger.debug(f"📊 Result length: {len(result)} characters")
            return result

        except Exception as e:
            logger.error(f"❌ CRITICAL: Direct task execution failed: {task.name} - {str(e)}")
            logger.error("🚨 No fallback allowed - system must fail to prevent misinformation")
            raise Exception(f"Task execution failed for {task.name}: {str(e)} - no fallback content allowed")

    async def _generate_fallback_content(self, task: Task, context: Dict[str, Any]) -> str:
        """REMOVED: No fallback content allowed - system must fail to prevent misinformation."""
        logger.error("❌ CRITICAL: Fallback content generation called - this should never happen")
        raise Exception("Fallback content generation is disabled - system must use real agent execution only")

    async def _get_agent_for_task(self, task: Task, context: Dict[str, Any]) -> Optional['Agent']:
        """
        Get the appropriate agent for a task based on its role.

        Args:
            task: Task to find agent for
            context: Execution context

        Returns:
            Agent instance or None if not found
        """
        try:
            # Import here to avoid circular imports
            from ....domain.entities.agent import Agent, AgentRole
            from ....domain.repositories.agent_repository import AgentRepository

            # Get agent repository from context or create a mock one
            agent_repository = context.get('agent_repository')
            if not agent_repository:
                logger.warning("No agent repository in context, using mock agent")
                # Create a mock agent for the task
                return Agent(
                    name=f"mock_{task.agent_role}",
                    role=AgentRole(task.agent_role) if hasattr(AgentRole, task.agent_role) else AgentRole.WRITER,
                    description=f"Mock agent for {task.agent_role} tasks",
                    tools=[]
                )

            # Find agent by role, preferring client-specific agents
            client_profile = context.get('client_name', context.get('client_profile', 'default'))

            # First try to get client-specific agents
            if client_profile and client_profile != 'default':
                client_agents = await agent_repository.get_by_client_profile(client_profile)
                for agent in client_agents:
                    if agent.role.value.lower() == task.agent_role.lower():
                        logger.info(f"✅ Found client-specific agent: {agent.name} for role {task.agent_role}")
                        return agent

            # Fallback to general agents by role
            try:
                agent_role_enum = AgentRole(task.agent_role.upper())
                agents = await agent_repository.get_by_role(agent_role_enum)
                if agents:
                    logger.info(f"✅ Found general agent: {agents[0].name} for role {task.agent_role}")
                    return agents[0]  # Return first matching agent
            except ValueError:
                logger.warning(f"Invalid agent role: {task.agent_role}")

            logger.warning(f"No agent found for role: {task.agent_role}")
            return None

        except Exception as e:
            logger.error(f"Error getting agent for task: {str(e)}")
            return None

    # Methods that can be overridden by specific workflow handlers
    
    def validate_inputs(self, context: Dict[str, Any]) -> None:
        """
        Validate input context. Override in specific handlers.
        
        Args:
            context: Input context to validate
            
        Raises:
            ValueError: If validation fails
        """
        # Default validation based on template
        required_vars = []
        for var in self.template.get('variables', []):
            if var.get('required', False):
                required_vars.append(var['name'])
        
        missing_vars = [var for var in required_vars if not context.get(var)]
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")
        
        logger.debug(f"✅ Default validation passed for {len(required_vars)} required variables")
    
    def prepare_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare and enhance context before execution. Override in specific handlers.
        
        Args:
            context: Input context
            
        Returns:
            Enhanced context
        """
        # Default: add template metadata to context
        context['workflow_template'] = self.template.get('name', self.workflow_type)
        context['workflow_version'] = self.template.get('version', '1.0')
        
        logger.debug("✅ Default context preparation completed")
        return context
    
    def should_skip_task(self, task_id: str, context: Dict[str, Any]) -> bool:
        """
        Determine if a task should be skipped. Override in specific handlers.
        
        Args:
            task_id: ID of the task to check
            context: Current context
            
        Returns:
            True if task should be skipped
        """
        return False
    
    def post_process_task(self, task_id: str, task_output: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post-process task output. Override in specific handlers.
        
        Args:
            task_id: ID of the completed task
            task_output: Output from the task
            context: Current context
            
        Returns:
            Updated context
        """
        return context
    
    def post_process_workflow(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post-process entire workflow. Override in specific handlers.

        Args:
            context: Final context after all tasks

        Returns:
            Final processed context
        """
        print("🔧 BASE POST-PROCESSING: Called workflow base post-processing")
        return context
