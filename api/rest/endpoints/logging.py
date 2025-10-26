"""
REST API endpoints for logging and monitoring data.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from services.content_workflow.infrastructure.logging.agent_logger import agent_logger
from services.content_workflow.infrastructure.logging.workflow_reporter import workflow_reporter
from services.content_workflow.infrastructure.logging.system_monitor import system_monitor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/logs", tags=["logging"])


@router.get("/system/status")
async def get_system_status() -> Dict[str, Any]:
    """Get current system status and health metrics."""
    try:
        status = system_monitor.get_current_status()
        return {"success": True, "data": status}
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows/summary")
async def get_workflows_summary(
    days: int = Query(
        7, ge=1, le=30, description="Number of days to include in summary"
    )
) -> Dict[str, Any]:
    """Get workflow execution summary for the specified period."""
    try:
        summary = workflow_reporter.get_summary_report(days=days)
        return {"success": True, "data": summary}
    except Exception as e:
        logger.error(f"Error getting workflow summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows/{workflow_id}")
async def get_workflow_report(workflow_id: str) -> Dict[str, Any]:
    """Get detailed report for a specific workflow."""
    try:
        report = workflow_reporter.get_workflow_report(workflow_id)
        if not report:
            raise HTTPException(status_code=404, detail="Workflow not found")

        return {"success": True, "data": report}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/sessions")
async def get_agent_sessions(
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of sessions to return"
    ),
    agent_name: Optional[str] = Query(None, description="Filter by agent name"),
    workflow_id: Optional[str] = Query(None, description="Filter by workflow ID"),
) -> Dict[str, Any]:
    """Get agent session logs with optional filtering."""
    try:
        # Get all log entries
        entries = agent_logger.entries

        # Apply filters
        if agent_name:
            entries = [e for e in entries if e.agent_name == agent_name]

        if workflow_id:
            entries = [e for e in entries if e.workflow_id == workflow_id]

        # Sort by timestamp (most recent first) and limit
        entries = sorted(entries, key=lambda x: x.timestamp, reverse=True)[:limit]

        # Convert to dict format
        sessions = [entry.to_dict() for entry in entries]

        return {
            "success": True,
            "data": {
                "sessions": sessions,
                "total_count": len(sessions),
                "filters_applied": {
                    "agent_name": agent_name,
                    "workflow_id": workflow_id,
                    "limit": limit,
                },
            },
        }
    except Exception as e:
        logger.error(f"Error getting agent sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/performance")
async def get_agent_performance(
    hours: int = Query(24, ge=1, le=168, description="Number of hours to analyze")
) -> Dict[str, Any]:
    """Get agent performance analytics for the specified period."""
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        # Get recent entries
        recent_entries = [e for e in agent_logger.entries if e.timestamp >= cutoff_time]

        # Analyze performance by agent
        agent_stats = {}

        for entry in recent_entries:
            if not entry.agent_name:
                continue

            if entry.agent_name not in agent_stats:
                agent_stats[entry.agent_name] = {
                    "total_sessions": 0,
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "total_duration_ms": 0.0,
                    "tool_calls": 0,
                    "llm_calls": 0,
                    "errors": 0,
                }

            stats = agent_stats[entry.agent_name]

            if entry.interaction_type.value == "agent_start":
                stats["total_sessions"] += 1
            elif entry.interaction_type.value == "llm_response":
                stats["llm_calls"] += 1
                if entry.tokens_used:
                    stats["total_tokens"] += entry.tokens_used
                if entry.cost_usd:
                    stats["total_cost"] += entry.cost_usd
                if entry.duration_ms:
                    stats["total_duration_ms"] += entry.duration_ms
            elif entry.interaction_type.value == "tool_response":
                stats["tool_calls"] += 1
            elif entry.interaction_type.value in ["tool_error", "llm_error"]:
                stats["errors"] += 1

        # Calculate averages
        for agent_name, stats in agent_stats.items():
            if stats["llm_calls"] > 0:
                stats["avg_response_time_ms"] = (
                    stats["total_duration_ms"] / stats["llm_calls"]
                )
                stats["avg_tokens_per_call"] = (
                    stats["total_tokens"] / stats["llm_calls"]
                )
                stats["avg_cost_per_call"] = stats["total_cost"] / stats["llm_calls"]
            else:
                stats["avg_response_time_ms"] = 0.0
                stats["avg_tokens_per_call"] = 0.0
                stats["avg_cost_per_call"] = 0.0

        return {
            "success": True,
            "data": {
                "period_hours": hours,
                "agent_performance": agent_stats,
                "total_agents": len(agent_stats),
                "analysis_timestamp": datetime.utcnow().isoformat(),
            },
        }
    except Exception as e:
        logger.error(f"Error getting agent performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/costs/breakdown")
async def get_cost_breakdown(
    hours: int = Query(24, ge=1, le=168, description="Number of hours to analyze")
) -> Dict[str, Any]:
    """Get detailed cost breakdown by provider, model, and agent."""
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        # Get recent LLM response entries
        llm_entries = [
            e
            for e in agent_logger.entries
            if e.timestamp >= cutoff_time
            and e.interaction_type.value == "llm_response"
            and e.cost_usd is not None
        ]

        # Analyze costs
        cost_by_provider = {}
        cost_by_model = {}
        cost_by_agent = {}
        total_cost = 0.0
        total_tokens = 0

        for entry in llm_entries:
            provider = entry.data.get("provider", "unknown")
            model = entry.data.get("model", "unknown")
            agent = entry.agent_name or "unknown"
            cost = entry.cost_usd
            tokens = entry.tokens_used or 0

            total_cost += cost
            total_tokens += tokens

            # By provider
            if provider not in cost_by_provider:
                cost_by_provider[provider] = {"cost": 0.0, "tokens": 0, "calls": 0}
            cost_by_provider[provider]["cost"] += cost
            cost_by_provider[provider]["tokens"] += tokens
            cost_by_provider[provider]["calls"] += 1

            # By model
            model_key = f"{provider}/{model}"
            if model_key not in cost_by_model:
                cost_by_model[model_key] = {"cost": 0.0, "tokens": 0, "calls": 0}
            cost_by_model[model_key]["cost"] += cost
            cost_by_model[model_key]["tokens"] += tokens
            cost_by_model[model_key]["calls"] += 1

            # By agent
            if agent not in cost_by_agent:
                cost_by_agent[agent] = {"cost": 0.0, "tokens": 0, "calls": 0}
            cost_by_agent[agent]["cost"] += cost
            cost_by_agent[agent]["tokens"] += tokens
            cost_by_agent[agent]["calls"] += 1

        return {
            "success": True,
            "data": {
                "period_hours": hours,
                "total_cost": total_cost,
                "total_tokens": total_tokens,
                "total_llm_calls": len(llm_entries),
                "cost_by_provider": cost_by_provider,
                "cost_by_model": cost_by_model,
                "cost_by_agent": cost_by_agent,
                "analysis_timestamp": datetime.utcnow().isoformat(),
            },
        }
    except Exception as e:
        logger.error(f"Error getting cost breakdown: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/frontend")
async def log_frontend_event(log_data: Dict[str, Any]) -> Dict[str, Any]:
    """Receive and store frontend log events."""
    try:
        # Log the frontend event
        logger.info(
            f"Frontend log: {log_data.get('eventType')} - {log_data.get('message')}"
        )

        # Store critical frontend errors in system monitor
        if log_data.get("level") in ["ERROR", "CRITICAL"]:
            system_monitor.log_error(
                error_type="frontend_error",
                message=log_data.get("message", "Unknown frontend error"),
                details=log_data,
            )

        return {"success": True, "message": "Frontend log received"}
    except Exception as e:
        logger.error(f"Error processing frontend log: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export")
async def export_logs(
    format: str = Query("json", regex="^(json|csv)$", description="Export format"),
    hours: int = Query(24, ge=1, le=168, description="Number of hours to export"),
) -> Dict[str, Any]:
    """Export logs in specified format."""
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        # Get recent entries
        recent_entries = [e for e in agent_logger.entries if e.timestamp >= cutoff_time]

        if format == "json":
            export_data = {
                "export_timestamp": datetime.utcnow().isoformat(),
                "period_hours": hours,
                "total_entries": len(recent_entries),
                "logs": [entry.to_dict() for entry in recent_entries],
            }

            return {"success": True, "data": export_data}

        elif format == "csv":
            # For CSV, return a simplified format
            csv_data = []
            for entry in recent_entries:
                csv_data.append(
                    {
                        "timestamp": entry.timestamp.isoformat(),
                        "level": entry.level.value,
                        "interaction_type": entry.interaction_type.value,
                        "agent_name": entry.agent_name,
                        "message": entry.message,
                        "tokens_used": entry.tokens_used,
                        "cost_usd": entry.cost_usd,
                        "duration_ms": entry.duration_ms,
                    }
                )

            return {
                "success": True,
                "data": {
                    "format": "csv",
                    "headers": list(csv_data[0].keys()) if csv_data else [],
                    "rows": csv_data,
                },
            }

    except Exception as e:
        logger.error(f"Error exporting logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
