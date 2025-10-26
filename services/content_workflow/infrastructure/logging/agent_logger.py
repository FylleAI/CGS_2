"""Advanced logging system for AI agents and tools interactions."""

import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from enum import Enum


class LogLevel(Enum):
    """Log levels for agent interactions."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class InteractionType(Enum):
    """Types of interactions to log."""

    AGENT_START = "agent_start"
    AGENT_END = "agent_end"
    AGENT_THINKING = "agent_thinking"
    TOOL_CALL = "tool_call"
    TOOL_RESPONSE = "tool_response"
    TOOL_ERROR = "tool_error"
    LLM_REQUEST = "llm_request"
    LLM_RESPONSE = "llm_response"
    LLM_ERROR = "llm_error"
    CONTEXT_UPDATE = "context_update"
    DECISION_POINT = "decision_point"


@dataclass
class LogEntry:
    """Structured log entry for agent interactions."""

    id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    interaction_type: InteractionType = InteractionType.AGENT_START
    level: LogLevel = LogLevel.INFO
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None
    tool_name: Optional[str] = None
    task_id: Optional[str] = None
    workflow_id: Optional[str] = None
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    duration_ms: Optional[float] = None
    tokens_used: Optional[int] = None
    cost_usd: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "interaction_type": self.interaction_type.value,
            "level": self.level.value,
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "tool_name": self.tool_name,
            "task_id": self.task_id,
            "workflow_id": self.workflow_id,
            "message": self.message,
            "data": self.data,
            "duration_ms": self.duration_ms,
            "tokens_used": self.tokens_used,
            "cost_usd": self.cost_usd,
        }


class AgentLogger:
    """Advanced logger for AI agents and tools interactions."""

    def __init__(
        self, name: str = "agent_logger", tracker=None, run_id: Optional[str] = None
    ):
        self.name = name
        self.logger = logging.getLogger(name)
        self.entries: List[LogEntry] = []
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.tracker = tracker
        self.run_id = run_id

        # Configure detailed formatting
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.DEBUG)

    def set_tracker(self, tracker, run_id: str) -> None:
        """Attach Supabase tracker and run identifier."""
        self.tracker = tracker
        self.run_id = run_id

    def start_agent_session(
        self,
        agent_id: str,
        agent_name: str,
        task_id: str,
        workflow_id: str,
        task_description: str,
    ) -> str:
        """Start a new agent execution session."""
        session_id = str(uuid4())

        self.active_sessions[session_id] = {
            "agent_id": agent_id,
            "agent_name": agent_name,
            "task_id": task_id,
            "workflow_id": workflow_id,
            "start_time": time.time(),
            "tool_calls": 0,
            "llm_calls": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
        }

        entry = LogEntry(
            interaction_type=InteractionType.AGENT_START,
            level=LogLevel.INFO,
            agent_id=agent_id,
            agent_name=agent_name,
            task_id=task_id,
            workflow_id=workflow_id,
            message=f"🤖 AGENT STARTED: {agent_name}",
            data={
                "session_id": session_id,
                "task_description": task_description,
                "agent_role": agent_name,
            },
        )

        self._log_entry(entry)
        return session_id

    def end_agent_session(
        self,
        session_id: str,
        success: bool = True,
        final_output: str = "",
        error_message: str = "",
    ):
        """End an agent execution session."""
        if session_id not in self.active_sessions:
            return

        session = self.active_sessions[session_id]
        duration = (time.time() - session["start_time"]) * 1000

        entry = LogEntry(
            interaction_type=InteractionType.AGENT_END,
            level=LogLevel.INFO if success else LogLevel.ERROR,
            agent_id=session["agent_id"],
            agent_name=session["agent_name"],
            task_id=session["task_id"],
            workflow_id=session["workflow_id"],
            message=(
                f"✅ AGENT COMPLETED: {session['agent_name']}"
                if success
                else f"❌ AGENT FAILED: {session['agent_name']}"
            ),
            data={
                "session_id": session_id,
                "success": success,
                "final_output_length": len(final_output),
                "final_output_preview": (
                    final_output[:200] + "..."
                    if len(final_output) > 200
                    else final_output
                ),
                "error_message": error_message,
                "tool_calls_made": session["tool_calls"],
                "llm_calls_made": session["llm_calls"],
                "total_tokens_used": session["total_tokens"],
                "total_cost_usd": session["total_cost"],
            },
            duration_ms=duration,
            tokens_used=session["total_tokens"],
            cost_usd=session["total_cost"],
        )

        self._log_entry(entry)
        del self.active_sessions[session_id]

    def log_agent_thinking(
        self, session_id: str, thought: str, reasoning: str = "", next_action: str = ""
    ):
        """Log agent's thinking process."""
        session = self.active_sessions.get(session_id, {})

        entry = LogEntry(
            interaction_type=InteractionType.AGENT_THINKING,
            level=LogLevel.DEBUG,
            agent_id=session.get("agent_id"),
            agent_name=session.get("agent_name"),
            task_id=session.get("task_id"),
            workflow_id=session.get("workflow_id"),
            message=f"💭 THINKING: {thought}",
            data={
                "session_id": session_id,
                "thought": thought,
                "reasoning": reasoning,
                "next_action": next_action,
            },
        )

        self._log_entry(entry)
        if self.tracker and self.run_id:
            self.tracker.add_log(
                self.run_id, "THINK", thought, session.get("agent_name")
            )

    def log_tool_call(
        self,
        session_id: str,
        tool_name: str,
        tool_input: Any,
        tool_description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Log a tool call start."""
        call_id = str(uuid4())
        session = self.active_sessions.get(session_id, {})

        if session_id in self.active_sessions:
            self.active_sessions[session_id]["tool_calls"] += 1

        data = {
            "session_id": session_id,
            "call_id": call_id,
            "tool_input": (
                str(tool_input)[:500] + "..."
                if len(str(tool_input)) > 500
                else str(tool_input)
            ),
            "tool_description": tool_description,
            "call_number": session.get("tool_calls", 0),
        }
        if metadata:
            data.update(metadata)

        entry = LogEntry(
            interaction_type=InteractionType.TOOL_CALL,
            level=LogLevel.INFO,
            agent_id=session.get("agent_id"),
            agent_name=session.get("agent_name"),
            task_id=session.get("task_id"),
            workflow_id=session.get("workflow_id"),
            tool_name=tool_name,
            message=f"🛠️ TOOL CALL: {tool_name}",
            data=data,
        )

        self._log_entry(entry)
        return call_id

    def log_tool_response(
        self,
        session_id: str,
        call_id: str,
        tool_name: str,
        tool_output: Any,
        duration_ms: float,
        success: bool = True,
        cost_usd: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Log a tool call response."""
        session = self.active_sessions.get(session_id, {})

        if session_id in self.active_sessions and cost_usd:
            self.active_sessions[session_id]["total_cost"] += cost_usd

        data = {
            "session_id": session_id,
            "call_id": call_id,
            "tool_output": (
                str(tool_output)[:500] + "..."
                if len(str(tool_output)) > 500
                else str(tool_output)
            ),
            "output_length": len(str(tool_output)),
            "success": success,
        }
        if metadata:
            data.update(metadata)

        entry = LogEntry(
            interaction_type=InteractionType.TOOL_RESPONSE,
            level=LogLevel.INFO if success else LogLevel.WARNING,
            agent_id=session.get("agent_id"),
            agent_name=session.get("agent_name"),
            task_id=session.get("task_id"),
            workflow_id=session.get("workflow_id"),
            tool_name=tool_name,
            message=(
                f"✅ TOOL RESPONSE: {tool_name}"
                if success
                else f"⚠️ TOOL WARNING: {tool_name}"
            ),
            data=data,
            duration_ms=duration_ms,
            cost_usd=cost_usd,
        )

        self._log_entry(entry)

    def log_tool_error(
        self,
        session_id: str,
        call_id: str,
        tool_name: str,
        error: Exception,
        duration_ms: float,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Log a tool call error."""
        session = self.active_sessions.get(session_id, {})

        data = {
            "session_id": session_id,
            "call_id": call_id,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "error_details": getattr(error, "args", []),
        }
        if metadata:
            data.update(metadata)

        entry = LogEntry(
            interaction_type=InteractionType.TOOL_ERROR,
            level=LogLevel.ERROR,
            agent_id=session.get("agent_id"),
            agent_name=session.get("agent_name"),
            task_id=session.get("task_id"),
            workflow_id=session.get("workflow_id"),
            tool_name=tool_name,
            message=f"❌ TOOL ERROR: {tool_name} - {str(error)}",
            data=data,
            duration_ms=duration_ms,
        )

        self._log_entry(entry)

    def log_llm_request(
        self,
        session_id: str,
        provider: str,
        model: str,
        prompt: str,
        system_message: str = "",
    ) -> str:
        """Log an LLM request."""
        request_id = str(uuid4())
        session = self.active_sessions.get(session_id, {})

        if session_id in self.active_sessions:
            self.active_sessions[session_id]["llm_calls"] += 1

        entry = LogEntry(
            interaction_type=InteractionType.LLM_REQUEST,
            level=LogLevel.INFO,
            agent_id=session.get("agent_id"),
            agent_name=session.get("agent_name"),
            task_id=session.get("task_id"),
            workflow_id=session.get("workflow_id"),
            message=f"🧠 LLM REQUEST: {provider}/{model}",
            data={
                "session_id": session_id,
                "request_id": request_id,
                "provider": provider,
                "model": model,
                "prompt_length": len(prompt),
                "prompt_preview": prompt[:200] + "..." if len(prompt) > 200 else prompt,
                "system_message_length": len(system_message),
                "system_message_preview": (
                    system_message[:100] + "..."
                    if len(system_message) > 100
                    else system_message
                ),
                "call_number": session.get("llm_calls", 0),
            },
        )

        self._log_entry(entry)
        return request_id

    def log_llm_response(
        self,
        session_id: str,
        request_id: str,
        provider: str,
        model: str,
        response: str,
        tokens_used: int,
        cost_usd: float,
        duration_ms: float,
    ):
        """Log an LLM response."""
        session = self.active_sessions.get(session_id, {})

        if session_id in self.active_sessions:
            self.active_sessions[session_id]["total_tokens"] += tokens_used
            self.active_sessions[session_id]["total_cost"] += cost_usd

        entry = LogEntry(
            interaction_type=InteractionType.LLM_RESPONSE,
            level=LogLevel.INFO,
            agent_id=session.get("agent_id"),
            agent_name=session.get("agent_name"),
            task_id=session.get("task_id"),
            workflow_id=session.get("workflow_id"),
            message=f"✅ LLM RESPONSE: {provider}/{model} ({tokens_used} tokens, ${cost_usd:.4f})",
            data={
                "session_id": session_id,
                "request_id": request_id,
                "provider": provider,
                "model": model,
                "response_length": len(response),
                "response_preview": (
                    response[:300] + "..." if len(response) > 300 else response
                ),
                "tokens_used": tokens_used,
                "cost_usd": cost_usd,
            },
            duration_ms=duration_ms,
            tokens_used=tokens_used,
            cost_usd=cost_usd,
        )

        self._log_entry(entry)

    def log_llm_error(
        self,
        session_id: str,
        request_id: str,
        provider: str,
        model: str,
        error: Exception,
        duration_ms: float,
    ):
        """Log an LLM error."""
        session = self.active_sessions.get(session_id, {})

        entry = LogEntry(
            interaction_type=InteractionType.LLM_ERROR,
            level=LogLevel.ERROR,
            agent_id=session.get("agent_id"),
            agent_name=session.get("agent_name"),
            task_id=session.get("task_id"),
            workflow_id=session.get("workflow_id"),
            message=f"❌ LLM ERROR: {provider}/{model} - {str(error)}",
            data={
                "session_id": session_id,
                "request_id": request_id,
                "provider": provider,
                "model": model,
                "error_type": type(error).__name__,
                "error_message": str(error),
            },
            duration_ms=duration_ms,
        )

        self._log_entry(entry)

    def _log_entry(self, entry: LogEntry):
        """Internal method to log an entry."""
        self.entries.append(entry)

        # Format message for console output
        prefix = self._get_interaction_prefix(entry.interaction_type)
        agent_info = f"[{entry.agent_name}]" if entry.agent_name else ""
        tool_info = f"[{entry.tool_name}]" if entry.tool_name else ""

        formatted_message = f"{prefix} {agent_info}{tool_info} {entry.message}"

        # Log to standard logger
        if entry.level == LogLevel.DEBUG:
            self.logger.debug(formatted_message)
        elif entry.level == LogLevel.INFO:
            self.logger.info(formatted_message)
        elif entry.level == LogLevel.WARNING:
            self.logger.warning(formatted_message)
        elif entry.level == LogLevel.ERROR:
            self.logger.error(formatted_message)
        elif entry.level == LogLevel.CRITICAL:
            self.logger.critical(formatted_message)

    def _get_interaction_prefix(self, interaction_type: InteractionType) -> str:
        """Get emoji prefix for interaction type."""
        prefixes = {
            InteractionType.AGENT_START: "🚀",
            InteractionType.AGENT_END: "🏁",
            InteractionType.AGENT_THINKING: "💭",
            InteractionType.TOOL_CALL: "🛠️",
            InteractionType.TOOL_RESPONSE: "✅",
            InteractionType.TOOL_ERROR: "❌",
            InteractionType.LLM_REQUEST: "🧠",
            InteractionType.LLM_RESPONSE: "💬",
            InteractionType.LLM_ERROR: "🚨",
            InteractionType.CONTEXT_UPDATE: "📝",
            InteractionType.DECISION_POINT: "🤔",
        }
        return prefixes.get(interaction_type, "ℹ️")

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of a session."""
        if session_id not in self.active_sessions:
            return {}

        session = self.active_sessions[session_id]
        return {
            "session_id": session_id,
            "agent_name": session["agent_name"],
            "duration_seconds": time.time() - session["start_time"],
            "tool_calls": session["tool_calls"],
            "llm_calls": session["llm_calls"],
            "total_tokens": session["total_tokens"],
            "total_cost": session["total_cost"],
        }

    def export_logs(self, format: str = "json") -> str:
        """Export all logs in specified format."""
        if format == "json":
            return json.dumps([entry.to_dict() for entry in self.entries], indent=2)
        else:
            return "\n".join(
                [f"{entry.timestamp} | {entry.message}" for entry in self.entries]
            )


# Global logger instance
agent_logger = AgentLogger("agent_interactions")
