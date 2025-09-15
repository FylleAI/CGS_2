"""Task orchestrator for workflow execution."""

import re
import logging
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime

from ...domain.entities.workflow import Workflow, WorkflowStatus
from ...domain.entities.task import Task, TaskStatus
from ...domain.repositories.workflow_repository import WorkflowRepository
from ..utils.template_utils import substitute_task_description

logger = logging.getLogger(__name__)


class TaskOrchestrator:
    """
    Orchestrator for executing workflows with task dependencies.
    
    This orchestrator manages the execution of workflow tasks,
    handling dependencies and propagating outputs between tasks.
    """
    
    def __init__(self, workflow_repository: WorkflowRepository):
        self.workflow_repository = workflow_repository
        self.task_outputs: Dict[str, str] = {}
        self.executed_tasks: set = set()
    
    async def execute_workflow(
        self,
        workflow: Workflow,
        context: Dict[str, Any] = None,
        verbose: bool = True,
        run_id: Optional[str] = None,
        tracker: Any = None,
    ) -> Dict[str, Any]:
        """
        Execute a workflow with all its tasks.
        
        Args:
            workflow: The workflow to execute
            context: Additional context for task execution
            verbose: Whether to log execution details
            
        Returns:
            Dictionary containing task outputs and execution results
        """
        logger.info(f"Starting workflow execution: {workflow.name}")
        
        # Update workflow status
        workflow.start()
        await self.workflow_repository.update(workflow)
        
        try:
            # Initialize context
            execution_context = context or {}
            execution_context.update({
                'workflow_id': str(workflow.id),
                'workflow_name': workflow.name,
                'client_profile': workflow.client_profile,
                'target_audience': workflow.target_audience,
                'context': workflow.context,
                'run_id': run_id,
                'tracker': tracker,
            })
            
            # Execute tasks in dependency order
            step_number = 0
            for task in workflow.tasks:
                step_number += 1
                execution_context['step_number'] = step_number
                await self._execute_task(task, execution_context, verbose)
            
            # Mark workflow as completed
            from ...domain.entities.workflow import WorkflowResult

            # Get final output (last task's output)
            final_output = ""
            if self.task_outputs:
                final_output = list(self.task_outputs.values())[-1]

            result = WorkflowResult(
                final_output=final_output,
                task_outputs={UUID(k): v for k, v in self.task_outputs.items()},
                execution_time=(datetime.utcnow() - workflow.started_at).total_seconds() if workflow.started_at else 0
            )
            workflow.complete(result)
            await self.workflow_repository.update(workflow)
            
            logger.info(f"Workflow execution completed: {workflow.name}")
            return {
                'success': True,
                'workflow_id': str(workflow.id),
                'task_outputs': self.task_outputs,
                'execution_time': workflow.result.execution_time if workflow.result else 0
            }
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            workflow.fail(str(e))
            await self.workflow_repository.update(workflow)
            
            return {
                'success': False,
                'workflow_id': str(workflow.id),
                'error': str(e),
                'task_outputs': self.task_outputs
            }
    
    async def _execute_task(
        self,
        task: Task,
        context: Dict[str, Any],
        verbose: bool = True
    ) -> str:
        """
        Execute a single task with dependency resolution.
        
        Args:
            task: The task to execute
            context: Execution context
            verbose: Whether to log execution details
            
        Returns:
            Task output string
        """
        task_id = str(task.id)
        
        # Check if task already executed
        if task_id in self.task_outputs:
            return self.task_outputs[task_id]
        
        # Execute dependencies first
        dependency_outputs = {}
        for dep_id in task.dependencies:
            if dep_id not in self.task_outputs:
                # Find and execute dependency task
                dep_task = self._find_task_by_id(dep_id, context.get('workflow_tasks', []))
                if dep_task:
                    dependency_outputs[dep_id] = await self._execute_task(dep_task, context, verbose)
            else:
                dependency_outputs[dep_id] = self.task_outputs[dep_id]
        
        # Resolve template variables in task description
        template_context = {**context, **dependency_outputs}

        if verbose:
            logger.info(f"🔧 Resolving template variables for task: {task.name}")
            logger.debug(f"Available template variables: {list(template_context.keys())}")

        resolved_description = self._resolve_template_variables(
            task.description,
            template_context
        )

        if verbose and resolved_description != task.description:
            logger.info(f"✅ Template variables resolved for task: {task.name}")
            logger.debug(f"Original description length: {len(task.description)}")
            logger.debug(f"Resolved description length: {len(resolved_description)}")
        elif verbose:
            logger.info(f"ℹ️ No template variables found in task: {task.name}")
        
        if verbose:
            logger.info(f"Executing task: {task.name}")
            logger.debug(f"Task description: {resolved_description}")
        
        # Mark task as running
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        
        try:
            # Execute the task (this would integrate with actual AI agents)
            output = await self._execute_task_logic(task, resolved_description, context)
            
            # Mark task as completed
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.output = output
            
            # Store output for future tasks
            self.task_outputs[task_id] = output
            self.executed_tasks.add(task_id)
            
            logger.info(f"Task completed: {task.name}")
            return output
            
        except Exception as e:
            logger.error(f"Task execution failed: {task.name} - {str(e)}")
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.utcnow()
            task.error_message = str(e)
            
            # Store error as output
            error_output = f"Task failed: {str(e)}"
            self.task_outputs[task_id] = error_output
            
            raise e
    
    def _resolve_template_variables(self, text: str, variables: Dict[str, Any]) -> str:
        """
        Resolve template variables in text using {{variable}} syntax.

        Args:
            text: Text containing template variables
            variables: Dictionary of variable values

        Returns:
            Text with resolved variables
        """
        logger.info(f"🔧 _resolve_template_variables called with {len(variables)} variables")
        logger.debug(f"Available variables: {list(variables.keys())}")

        try:
            # Use the enhanced template substitution utility
            result = substitute_task_description(text, variables)

            logger.info(f"✅ Template substitution completed successfully")
            logger.debug(f"Original length: {len(text)}, Result length: {len(result)}")

            # Check if any substitution actually happened
            if result != text:
                logger.info(f"🎯 Template variables were substituted!")
            else:
                logger.debug(f"ℹ️ No template variables were substituted")

            return result

        except Exception as e:
            logger.error(f"❌ Error resolving template variables: {str(e)}")
            logger.debug(f"Falling back to simple regex substitution")

            # Fallback to simple regex substitution
            def replace_variable(match):
                var_name = match.group(1)
                value = variables.get(var_name, f"{{{{{var_name}}}}}")
                return str(value) if value is not None else ''

            return re.sub(r"{{(\w+)}}", replace_variable, text)
    
    def _find_task_by_id(self, task_id: str, tasks: List[Task]) -> Optional[Task]:
        """Find a task by its ID in a list of tasks."""
        for task in tasks:
            if str(task.id) == task_id:
                return task
        return None
    
    async def _execute_task_logic(
        self,
        task: Task,
        description: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Execute the actual task logic using AI agents.

        Args:
            task: The task to execute
            description: Resolved task description
            context: Execution context

        Returns:
            Task output
        """
        logger.info(f"Executing task logic for: {task.name}")

        # Get agent executor from context if available
        agent_executor = context.get('agent_executor')
        if not agent_executor:
            logger.error(f"❌ CRITICAL: No agent executor available for task {task.name}")
            raise Exception(f"No agent executor available for task {task.name} - system cannot proceed without real agent execution")

        # Validate task has agent configuration
        if not getattr(task, 'agent_name', None) and not getattr(task, 'agent_role', None):
            logger.info(f"ℹ️ Task {task.name} has no agent_name or agent_role - using fallback")

        # Find appropriate agent for this task using AgentFactory
        from ..factories.agent_factory import AgentFactory
        agent_factory = AgentFactory(context.get('agent_repository'))
        agent = await agent_factory.get(
            name=getattr(task, 'agent_name', None),
            role=getattr(task, 'agent_role', None),
            ctx=context
        )
        if not agent:
            logger.error(f"❌ CRITICAL: No agent found for task {task.name}")
            raise Exception(f"No agent found for task {task.name} - check agent_name/agent_role configuration")

        try:
            # Add task and workflow context for agent logging
            enhanced_context = {
                **context,
                'task_id': str(task.id),
                'workflow_id': context.get('workflow_id', 'unknown')
            }

            # Execute agent with task description
            result = await agent_executor.execute_agent(
                agent=agent,
                task_description=description,
                context=enhanced_context
            )

            logger.info(f"Agent execution completed for task: {task.name}")
            return result

        except Exception as e:
            logger.error(f"❌ CRITICAL: Agent execution failed for task {task.name}: {str(e)}")
            logger.error("🚨 No fallback allowed - system must fail to prevent misinformation")
            raise Exception(f"Agent execution failed for task {task.name}: {str(e)} - no mock execution allowed")

    async def _get_agent_for_task(self, task: Task, context: Dict[str, Any]) -> Optional[Any]:
        """Deprecated: selection now happens via AgentFactory in _execute_task_logic."""
        # Keeping method for backward compatibility, but prefer AgentFactory path
        return None

    async def _mock_task_execution(
        self,
        task: Task,
        description: str,
        context: Dict[str, Any]
    ) -> str:
        """REMOVED: No mock execution allowed - system must fail to prevent misinformation."""
        logger.error(f"❌ CRITICAL: Mock task execution called for {task.name} - this should never happen")
        raise Exception(f"Mock task execution is disabled for {task.name} - system must use real agent execution only")

    def _generate_mock_brief(self, context: Dict[str, Any]) -> str:
        """REMOVED: No mock content allowed - system must fail to prevent misinformation."""
        logger.error("❌ CRITICAL: Mock brief generation called - this should never happen")
        raise Exception("Mock brief generation is disabled - system must use real agent execution only")

    def _generate_mock_research(self, context: Dict[str, Any]) -> str:
        """REMOVED: No mock content allowed - system must fail to prevent misinformation."""
        logger.error("❌ CRITICAL: Mock research generation called - this should never happen")
        raise Exception("Mock research generation is disabled - system must use real agent execution only")

    def _generate_mock_content(self, context: Dict[str, Any]) -> str:
        """REMOVED: No mock content allowed - system must fail to prevent misinformation."""
        logger.error("❌ CRITICAL: Mock content generation called - this should never happen")
        raise Exception("Mock content generation is disabled - system must use real agent execution only")
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get a summary of the current execution state."""
        return {
            'executed_tasks': len(self.executed_tasks),
            'task_outputs_count': len(self.task_outputs),
            'execution_status': 'completed' if self.task_outputs else 'not_started'
        }
