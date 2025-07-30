"""
Workflow completion reporting system for comprehensive analytics and cost tracking.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from uuid import uuid4

from .agent_logger import agent_logger, LogEntry, InteractionType
from .cost_calculator import CostBreakdown, TokenUsage

logger = logging.getLogger(__name__)


@dataclass
class AgentPerformance:
    """Performance metrics for a single agent."""
    agent_id: str
    agent_name: str
    task_count: int = 0
    total_duration_ms: float = 0.0
    total_tokens: int = 0
    total_cost: float = 0.0
    tool_calls: int = 0
    llm_calls: int = 0
    success_rate: float = 0.0
    avg_response_time_ms: float = 0.0


@dataclass
class WorkflowMetrics:
    """Comprehensive workflow execution metrics."""
    workflow_id: str
    workflow_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration_ms: float = 0.0
    
    # Token and cost metrics
    total_tokens: int = 0
    total_cost: float = 0.0
    cost_breakdown_by_provider: Dict[str, float] = None
    cost_breakdown_by_agent: Dict[str, float] = None
    
    # Agent metrics
    agents_used: List[AgentPerformance] = None
    total_agent_sessions: int = 0
    
    # Task metrics
    tasks_completed: int = 0
    tasks_failed: int = 0
    success_rate: float = 0.0
    
    # Tool usage metrics
    total_tool_calls: int = 0
    tool_usage_breakdown: Dict[str, int] = None
    
    # LLM usage metrics
    total_llm_calls: int = 0
    llm_usage_breakdown: Dict[str, int] = None
    
    # Quality metrics
    final_output_length: int = 0
    final_output_preview: str = ""
    
    def __post_init__(self):
        if self.cost_breakdown_by_provider is None:
            self.cost_breakdown_by_provider = {}
        if self.cost_breakdown_by_agent is None:
            self.cost_breakdown_by_agent = {}
        if self.agents_used is None:
            self.agents_used = []
        if self.tool_usage_breakdown is None:
            self.tool_usage_breakdown = {}
        if self.llm_usage_breakdown is None:
            self.llm_usage_breakdown = {}


class WorkflowReporter:
    """
    Comprehensive workflow reporting system.
    
    This class analyzes agent logs to generate detailed reports about
    workflow execution, costs, performance, and resource usage.
    """
    
    def __init__(self):
        self.active_workflows: Dict[str, WorkflowMetrics] = {}
        self.completed_workflows: List[WorkflowMetrics] = []
        logger.info("📊 Workflow reporter initialized")
    
    def start_workflow_tracking(
        self, 
        workflow_id: str, 
        workflow_type: str,
        context: Dict[str, Any] = None
    ) -> None:
        """Start tracking a new workflow execution."""
        context = context or {}
        
        metrics = WorkflowMetrics(
            workflow_id=workflow_id,
            workflow_type=workflow_type,
            start_time=datetime.utcnow()
        )
        
        self.active_workflows[workflow_id] = metrics
        
        logger.info(
            f"📈 Started tracking workflow: {workflow_type} "
            f"(ID: {workflow_id})"
        )
    
    def complete_workflow_tracking(
        self, 
        workflow_id: str,
        final_output: str = "",
        success: bool = True
    ) -> WorkflowMetrics:
        """Complete workflow tracking and generate comprehensive report."""
        if workflow_id not in self.active_workflows:
            logger.warning(f"⚠️ Workflow {workflow_id} not found in active tracking")
            return None
        
        metrics = self.active_workflows[workflow_id]
        metrics.end_time = datetime.utcnow()
        metrics.total_duration_ms = (
            metrics.end_time - metrics.start_time
        ).total_seconds() * 1000
        
        # Set final output information
        metrics.final_output_length = len(final_output)
        metrics.final_output_preview = (
            final_output[:200] + "..." if len(final_output) > 200 else final_output
        )
        
        # Analyze agent logs for this workflow
        self._analyze_workflow_logs(metrics)
        
        # Calculate success rate
        total_tasks = metrics.tasks_completed + metrics.tasks_failed
        if total_tasks > 0:
            metrics.success_rate = metrics.tasks_completed / total_tasks
        
        # Move to completed workflows
        self.completed_workflows.append(metrics)
        del self.active_workflows[workflow_id]
        
        # Log completion summary
        self._log_workflow_completion(metrics)
        
        return metrics
    
    def _analyze_workflow_logs(self, metrics: WorkflowMetrics) -> None:
        """Analyze agent logs to extract detailed metrics."""
        workflow_entries = [
            entry for entry in agent_logger.entries
            if entry.workflow_id == metrics.workflow_id
        ]
        
        if not workflow_entries:
            logger.warning(f"⚠️ No log entries found for workflow {metrics.workflow_id}")
            return
        
        # Track agents and their performance
        agent_sessions = {}
        agent_performance = {}
        
        # Analyze each log entry
        for entry in workflow_entries:
            self._process_log_entry(entry, metrics, agent_sessions, agent_performance)
        
        # Finalize agent performance metrics
        for agent_id, perf_data in agent_performance.items():
            if perf_data['llm_calls'] > 0:
                perf_data['avg_response_time_ms'] = (
                    perf_data['total_duration_ms'] / perf_data['llm_calls']
                )
            
            agent_perf = AgentPerformance(
                agent_id=agent_id,
                agent_name=perf_data['agent_name'],
                task_count=perf_data['task_count'],
                total_duration_ms=perf_data['total_duration_ms'],
                total_tokens=perf_data['total_tokens'],
                total_cost=perf_data['total_cost'],
                tool_calls=perf_data['tool_calls'],
                llm_calls=perf_data['llm_calls'],
                success_rate=perf_data['success_rate'],
                avg_response_time_ms=perf_data['avg_response_time_ms']
            )
            
            metrics.agents_used.append(agent_perf)
        
        metrics.total_agent_sessions = len(agent_sessions)
        
        logger.debug(
            f"📊 Analyzed {len(workflow_entries)} log entries for workflow {metrics.workflow_id}"
        )
    
    def _process_log_entry(
        self, 
        entry: LogEntry, 
        metrics: WorkflowMetrics,
        agent_sessions: Dict[str, Dict],
        agent_performance: Dict[str, Dict]
    ) -> None:
        """Process a single log entry to extract metrics."""
        
        # Initialize agent performance tracking
        if entry.agent_id and entry.agent_id not in agent_performance:
            agent_performance[entry.agent_id] = {
                'agent_name': entry.agent_name or 'Unknown',
                'task_count': 0,
                'total_duration_ms': 0.0,
                'total_tokens': 0,
                'total_cost': 0.0,
                'tool_calls': 0,
                'llm_calls': 0,
                'success_rate': 1.0,
                'avg_response_time_ms': 0.0
            }
        
        # Process different interaction types
        if entry.interaction_type == InteractionType.AGENT_START:
            session_id = entry.data.get('session_id')
            if session_id:
                agent_sessions[session_id] = {
                    'agent_id': entry.agent_id,
                    'start_time': entry.timestamp,
                    'success': True
                }
        
        elif entry.interaction_type == InteractionType.AGENT_END:
            session_id = entry.data.get('session_id')
            if session_id in agent_sessions:
                session = agent_sessions[session_id]
                success = entry.data.get('success', True)
                
                if success:
                    metrics.tasks_completed += 1
                else:
                    metrics.tasks_failed += 1
                
                # Update agent performance
                if entry.agent_id in agent_performance:
                    agent_performance[entry.agent_id]['task_count'] += 1
                    if not success:
                        agent_performance[entry.agent_id]['success_rate'] *= 0.9
        
        elif entry.interaction_type == InteractionType.LLM_RESPONSE:
            metrics.total_llm_calls += 1
            
            if entry.tokens_used:
                metrics.total_tokens += entry.tokens_used
            
            if entry.cost_usd:
                metrics.total_cost += entry.cost_usd
                
                # Track cost by provider
                provider = entry.data.get('provider', 'unknown')
                if provider not in metrics.cost_breakdown_by_provider:
                    metrics.cost_breakdown_by_provider[provider] = 0.0
                metrics.cost_breakdown_by_provider[provider] += entry.cost_usd
                
                # Track cost by agent
                if entry.agent_id:
                    if entry.agent_id not in metrics.cost_breakdown_by_agent:
                        metrics.cost_breakdown_by_agent[entry.agent_id] = 0.0
                    metrics.cost_breakdown_by_agent[entry.agent_id] += entry.cost_usd
            
            # Update agent performance
            if entry.agent_id in agent_performance:
                perf = agent_performance[entry.agent_id]
                perf['llm_calls'] += 1
                if entry.tokens_used:
                    perf['total_tokens'] += entry.tokens_used
                if entry.cost_usd:
                    perf['total_cost'] += entry.cost_usd
                if entry.duration_ms:
                    perf['total_duration_ms'] += entry.duration_ms
            
            # Track LLM usage
            model = entry.data.get('model', 'unknown')
            if model not in metrics.llm_usage_breakdown:
                metrics.llm_usage_breakdown[model] = 0
            metrics.llm_usage_breakdown[model] += 1
        
        elif entry.interaction_type == InteractionType.TOOL_RESPONSE:
            metrics.total_tool_calls += 1
            
            # Track tool usage
            tool_name = entry.tool_name or 'unknown'
            if tool_name not in metrics.tool_usage_breakdown:
                metrics.tool_usage_breakdown[tool_name] = 0
            metrics.tool_usage_breakdown[tool_name] += 1
            
            # Update agent performance
            if entry.agent_id in agent_performance:
                agent_performance[entry.agent_id]['tool_calls'] += 1
    
    def _log_workflow_completion(self, metrics: WorkflowMetrics) -> None:
        """Log comprehensive workflow completion summary."""
        logger.info("=" * 80)
        logger.info(f"🎉 WORKFLOW COMPLETED: {metrics.workflow_type}")
        logger.info("=" * 80)
        logger.info(f"📋 Workflow ID: {metrics.workflow_id}")
        logger.info(f"⏱️ Duration: {metrics.total_duration_ms/1000:.2f} seconds")
        logger.info(f"💰 Total Cost: ${metrics.total_cost:.6f}")
        logger.info(f"🔢 Total Tokens: {metrics.total_tokens:,}")
        logger.info(f"🤖 Agents Used: {len(metrics.agents_used)}")
        logger.info(f"✅ Tasks Completed: {metrics.tasks_completed}")
        logger.info(f"❌ Tasks Failed: {metrics.tasks_failed}")
        logger.info(f"📊 Success Rate: {metrics.success_rate:.1%}")
        logger.info(f"🛠️ Tool Calls: {metrics.total_tool_calls}")
        logger.info(f"🧠 LLM Calls: {metrics.total_llm_calls}")
        logger.info(f"📄 Output Length: {metrics.final_output_length:,} characters")
        
        # Cost breakdown by provider
        if metrics.cost_breakdown_by_provider:
            logger.info("💳 Cost by Provider:")
            for provider, cost in metrics.cost_breakdown_by_provider.items():
                logger.info(f"   {provider}: ${cost:.6f}")
        
        # Agent performance summary
        if metrics.agents_used:
            logger.info("🤖 Agent Performance:")
            for agent in metrics.agents_used:
                logger.info(
                    f"   {agent.agent_name}: "
                    f"{agent.task_count} tasks, "
                    f"${agent.total_cost:.6f}, "
                    f"{agent.total_tokens:,} tokens"
                )
        
        logger.info("=" * 80)
    
    def get_workflow_report(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed report for a specific workflow."""
        # Check active workflows
        if workflow_id in self.active_workflows:
            return asdict(self.active_workflows[workflow_id])
        
        # Check completed workflows
        for workflow in self.completed_workflows:
            if workflow.workflow_id == workflow_id:
                return asdict(workflow)
        
        return None
    
    def get_summary_report(self, days: int = 7) -> Dict[str, Any]:
        """Get summary report for recent workflows."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        recent_workflows = [
            w for w in self.completed_workflows
            if w.start_time >= cutoff_date
        ]
        
        if not recent_workflows:
            return {"message": f"No workflows completed in the last {days} days"}
        
        total_cost = sum(w.total_cost for w in recent_workflows)
        total_tokens = sum(w.total_tokens for w in recent_workflows)
        avg_duration = sum(w.total_duration_ms for w in recent_workflows) / len(recent_workflows)
        
        return {
            "period_days": days,
            "total_workflows": len(recent_workflows),
            "total_cost": total_cost,
            "total_tokens": total_tokens,
            "average_duration_seconds": avg_duration / 1000,
            "workflows": [asdict(w) for w in recent_workflows[-10:]]  # Last 10 workflows
        }


# Global workflow reporter instance
workflow_reporter = WorkflowReporter()
