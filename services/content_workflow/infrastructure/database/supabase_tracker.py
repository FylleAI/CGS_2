"""Supabase tracker implementation for workflow runs and agent execution logging.

This module is optional. It's enabled only when USE_SUPABASE=true and
both SUPABASE_URL and SUPABASE_ANON_KEY are configured in environment.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.infrastructure.config.settings import get_settings

logger = logging.getLogger(__name__)

try:
    # supabase>=2
    from supabase import create_client, Client
except Exception:  # pragma: no cover - optional dependency
    create_client = None  # type: ignore
    Client = object  # type: ignore


class SupabaseTracker:
    def __init__(self) -> None:
        settings = get_settings()
        if not (settings.supabase_url and settings.supabase_anon_key):
            raise ValueError("Supabase credentials not configured")
        if create_client is None:
            raise RuntimeError(
                "supabase package not installed. Run: pip install supabase>=2.0.0"
            )

        self.client: Client = create_client(
            settings.supabase_url, settings.supabase_anon_key
        )

    # ------------- Workflow run lifecycle -------------
    def start_workflow_run(
        self,
        client_name: str,
        workflow_name: str,
        topic: str,
        agent_executor: str = None,
    ) -> str:
        """Start tracking a new workflow run, returns run_id (UUID string)."""
        run_data = {
            "client_name": client_name,
            "workflow_name": workflow_name,
            "topic": topic,
            "status": "running",
        }

        # Add agent_executor if provided
        if agent_executor:
            run_data["agent_executor"] = agent_executor

        result = self.client.table("workflow_runs").insert(run_data).execute()
        run_id = result.data[0]["id"]
        logger.info(f"Started tracking run: {run_id}")
        return run_id

    def complete_workflow_run(
        self,
        run_id: str,
        status: str = "completed",
        error: Optional[str] = None,
        cost: Optional[float] = None,
        tokens: Optional[int] = None,
    ) -> None:
        """Complete a workflow run with optional metrics."""
        update_data: Dict[str, Any] = {
            "status": status,
            "completed_at": datetime.utcnow().isoformat() + "Z",
        }
        if error:
            update_data["error_message"] = error
        if cost is not None:
            update_data["total_cost_usd"] = cost
        if tokens is not None:
            update_data["total_tokens"] = tokens
        try:
            self.client.table("workflow_runs").update(update_data).eq(
                "id", run_id
            ).execute()
        except Exception as e:  # pragma: no cover
            logger.warning(f"Error completing workflow run {run_id}: {e}")

    # ------------- Detailed logging -------------
    def log_agent_execution(
        self,
        run_id: str,
        agent_name: str,
        step: int,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        thoughts: Optional[str] = None,
        tokens: Optional[int] = None,
        cost: Optional[float] = None,
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None,
        duration_seconds: Optional[float] = None,
    ) -> None:
        data: Dict[str, Any] = {
            "run_id": run_id,
            "agent_name": agent_name,
            "step_number": step,
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat() + "Z",
        }
        if input_data is not None:
            data["input_data"] = input_data
        if output_data is not None:
            data["output_data"] = output_data
        if thoughts is not None:
            data["thoughts"] = thoughts
        if tokens is not None:
            data["tokens_used"] = tokens
        if cost is not None:
            data["cost_usd"] = cost
        if provider_name:
            data["provider_name"] = provider_name
        if model_name:
            data["model_name"] = model_name
        if duration_seconds is not None:
            # Store fractional seconds with up to 3 decimals (DB is NUMERIC(10,3))
            try:
                data["duration_seconds"] = round(float(duration_seconds), 3)
            except Exception:
                data["duration_seconds"] = None
        try:
            self.client.table("agent_executions").insert(data).execute()
        except Exception as e:  # pragma: no cover
            logger.warning(f"Error logging agent execution for run {run_id}: {e}")

    def add_log(
        self,
        run_id: str,
        level: str,
        message: str,
        agent_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        data: Dict[str, Any] = {
            "run_id": run_id,
            "level": level.upper(),
            "message": message,
        }
        if agent_name:
            data["agent_name"] = agent_name
        if metadata:
            data["metadata"] = metadata
        try:
            self.client.table("run_logs").insert(data).execute()
        except Exception as e:  # pragma: no cover
            logger.warning(f"Error adding log for run {run_id}: {e}")

    # ------------- Cost event logging (LLM & Tools) -------------
    def log_llm_call(
        self,
        run_id: str,
        agent_name: Optional[str],
        provider_name: str,
        model_name: str,
        tokens_prompt: Optional[int] = None,
        tokens_completion: Optional[int] = None,
        tokens_total: Optional[int] = None,
        cost_usd: Optional[float] = None,
        duration_seconds: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log a single LLM call as a cost event (granular ledger)."""
        data: Dict[str, Any] = {
            "run_id": run_id,
            "event_type": "llm",
            "agent_name": agent_name,
            "provider_name": provider_name,
            "model_name": model_name,
            "tokens_prompt": tokens_prompt,
            "tokens_completion": tokens_completion,
            "tokens_total": tokens_total,
            "cost_usd": cost_usd,
            "metadata": metadata or {},
        }
        if duration_seconds is not None:
            try:
                data["duration_seconds"] = round(float(duration_seconds), 3)
            except Exception:
                data["duration_seconds"] = None
        try:
            self.client.table("run_cost_events").insert(data).execute()
        except Exception as e:  # pragma: no cover
            logger.warning(f"Error logging LLM cost event for run {run_id}: {e}")

    def log_tool_execution(
        self,
        run_id: str,
        agent_name: Optional[str],
        tool_name: str,
        provider_name: Optional[str] = None,
        units: Optional[float] = None,
        unit_cost_usd: Optional[float] = None,
        usage_tokens: Optional[int] = None,
        cost_per_1k_tokens_usd: Optional[float] = None,
        cost_usd: Optional[float] = None,
        cost_source: Optional[str] = None,
        duration_seconds: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log a single tool execution as a cost event (granular ledger)."""
        data: Dict[str, Any] = {
            "run_id": run_id,
            "event_type": "tool",
            "agent_name": agent_name,
            "tool_name": tool_name,
            "provider_name": provider_name,
            "units": units,
            "unit_cost_usd": unit_cost_usd,
            "usage_tokens": usage_tokens,
            "cost_per_1k_tokens_usd": cost_per_1k_tokens_usd,
            "cost_usd": cost_usd,
            "cost_source": cost_source,
            "metadata": metadata or {},
        }
        if duration_seconds is not None:
            try:
                data["duration_seconds"] = round(float(duration_seconds), 3)
            except Exception:
                data["duration_seconds"] = None
        try:
            self.client.table("run_cost_events").insert(data).execute()
        except Exception as e:  # pragma: no cover
            logger.warning(f"Error logging tool cost event for run {run_id}: {e}")

    # ------------- RAG document tracking -------------
    def log_rag_document(
        self,
        run_id: str,
        client_name: str,
        document_path: str,
        source_url: Optional[str] = None,
        agent_name: Optional[str] = None,
    ) -> None:
        data: Dict[str, Any] = {
            "run_id": run_id,
            "client_name": client_name,
            "document_path": document_path,
        }
        if source_url:
            data["source_url"] = source_url
        if agent_name:
            data["agent_name"] = agent_name
        try:
            self.client.table("run_documents").insert(data).execute()
        except Exception as e:  # pragma: no cover
            logger.warning(f"Error logging RAG document for run {run_id}: {e}")

    def log_rag_chunk(
        self,
        run_id: str,
        agent_name: str,
        document_id: str,
        chunk_text: str,
        score: Optional[float] = None,
    ) -> None:
        data: Dict[str, Any] = {
            "run_id": run_id,
            "agent_name": agent_name,
            "document_id": document_id,
            "chunk_text": chunk_text,
        }
        if score is not None:
            data["similarity_score"] = score
        try:
            self.client.table("run_document_chunks").insert(data).execute()
        except Exception as e:  # pragma: no cover
            logger.warning(f"Error logging RAG chunk for run {run_id}: {e}")

    def save_run_content(
        self,
        run_id: str,
        client_name: str,
        workflow_name: str,
        title: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        data: Dict[str, Any] = {
            "run_id": run_id,
            "title": title,
            "content": content,
            "topic": title,
            "metadata": (metadata or {})
            | {"client_name": client_name, "workflow_name": workflow_name},
        }
        try:
            self.client.table("content_generations").insert(data).execute()
        except Exception as e:  # pragma: no cover
            logger.warning(f"Error saving run content for run {run_id}: {e}")

    # ------------- Queries -------------
    def get_run_history(
        self,
        client_name: Optional[str] = None,
        workflow_name: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        try:
            query = (
                self.client.table("workflow_runs")
                .select("*")
                .order("started_at", desc=True)
                .limit(limit)
            )
            if client_name:
                query = query.eq("client_name", client_name)
            if workflow_name:
                query = query.eq("workflow_name", workflow_name)
            return query.execute().data
        except Exception as e:  # pragma: no cover
            logger.warning(f"Error getting run history: {e}")
            return []

    def get_run_details(self, run_id: str) -> Optional[Dict[str, Any]]:
        try:
            run = (
                self.client.table("workflow_runs")
                .select("*")
                .eq("id", run_id)
                .execute()
                .data
            )
            if not run:
                return None
            agents = (
                self.client.table("agent_executions")
                .select("*")
                .eq("run_id", run_id)
                .order("step_number")
                .execute()
                .data
            )
            logs = (
                self.client.table("run_logs")
                .select("*")
                .eq("run_id", run_id)
                .order("timestamp")
                .execute()
                .data
            )
            documents = (
                self.client.table("run_documents")
                .select("*")
                .eq("run_id", run_id)
                .execute()
                .data
            )
            chunks = (
                self.client.table("run_document_chunks")
                .select("*")
                .eq("run_id", run_id)
                .execute()
                .data
            )
            content = (
                self.client.table("content_generations")
                .select("title, content, metadata")
                .eq("run_id", run_id)
                .execute()
                .data
            )
            content_item = content[0] if content else None
            return {
                "run": run[0],
                "agents": agents,
                "logs": logs,
                "documents": documents,
                "chunks": chunks,
                "content": content_item,
            }
        except Exception as e:  # pragma: no cover
            logger.warning(f"Error getting run details: {e}")
            return None


# Factory function


def get_tracker() -> Optional[SupabaseTracker]:
    """Return a SupabaseTracker if enabled, else None."""
    try:
        settings = get_settings()
        if (
            settings.use_supabase
            and settings.supabase_url
            and settings.supabase_anon_key
        ):
            return SupabaseTracker()
        return None
    except Exception as e:  # pragma: no cover
        logger.info(f"Supabase tracker not available: {e}")
        return None
