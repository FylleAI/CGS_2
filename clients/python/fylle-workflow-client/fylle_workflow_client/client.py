"""
Fylle Workflow API Client.

Provides type-safe methods for executing workflows.
"""

import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential_jitter

from fylle_workflow_client.models import (
    ErrorResponse,
    WorkflowExecuteRequest,
    WorkflowExecuteResponse,
    WorkflowType,
)

logger = logging.getLogger(__name__)


class WorkflowAPIError(Exception):
    """Base exception for Workflow API errors."""

    def __init__(self, status_code: int, error: ErrorResponse):
        self.status_code = status_code
        self.error = error
        super().__init__(f"Workflow API error {status_code}: {error.error} - {error.detail}")


class WorkflowClient:
    """
    Client for Fylle Workflow API v1.
    
    Provides type-safe methods with automatic retry logic and header propagation.
    
    Args:
        base_url: Base URL of the Workflow API (e.g., "http://localhost:8001")
        tenant_id: Tenant ID for multi-tenant isolation (required)
        trace_id: Optional trace ID for distributed tracing
        session_id: Optional session ID for tracking
        timeout_connect: Connection timeout in seconds (default: 0.2)
        timeout_read: Read timeout in seconds (default: 5.0)
    """

    def __init__(
        self,
        base_url: str,
        tenant_id: str,
        trace_id: Optional[str] = None,
        session_id: Optional[str] = None,
        timeout_connect: float = 0.2,
        timeout_read: float = 5.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.tenant_id = tenant_id
        self.trace_id = trace_id
        self.session_id = session_id
        
        # Create httpx client with timeouts
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=httpx.Timeout(
                connect=timeout_connect,
                read=timeout_read,
                write=5.0,
                pool=5.0,
            ),
        )
    
    def _get_headers(self) -> Dict[str, str]:
        """Build headers for API requests."""
        headers = {
            "X-Tenant-ID": self.tenant_id,
            "Content-Type": "application/json",
        }
        
        if self.trace_id:
            headers["X-Trace-ID"] = self.trace_id
        
        if self.session_id:
            headers["X-Session-ID"] = self.session_id
        
        return headers
    
    def _handle_response(self, response: httpx.Response) -> Any:
        """Handle API response and raise errors if needed."""
        if response.status_code >= 400:
            try:
                error_data = response.json()
                error = ErrorResponse(**error_data)
            except Exception:
                error = ErrorResponse(
                    error="UnknownError",
                    detail=response.text,
                    request_id=None,
                )
            raise WorkflowAPIError(response.status_code, error)
        
        return response.json()
    
    @retry(
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.TimeoutException)),
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(initial=0.1, max=2.0),
        reraise=True,
    )
    def _request_with_retry(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make HTTP request with retry logic."""
        headers = self._get_headers()
        
        response = self.client.request(
            method=method,
            url=path,
            json=json,
            params=params,
            headers=headers,
        )
        
        return self._handle_response(response)
    
    def execute_workflow(
        self,
        workflow_type: WorkflowType,
        card_ids: Optional[List[UUID]] = None,
        context: Optional[Dict[str, Any]] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> WorkflowExecuteResponse:
        """
        Execute a workflow.
        
        **v1.0 Preferred**: Use `card_ids` to reference context cards.
        **v1.0 Legacy**: Use `context` dict (deprecated, warning headers).
        
        Args:
            workflow_type: Type of workflow to execute
            card_ids: List of card IDs for context (PREFERRED)
            context: Legacy context dict (DEPRECATED)
            parameters: Workflow-specific parameters
        
        Returns:
            WorkflowExecuteResponse with workflow_id, status, output, metrics
        
        Raises:
            WorkflowAPIError: If API returns an error
        
        Note:
            If using `context`, response will include deprecation warning headers:
            - X-API-Deprecation-Warning
            - X-API-Migration-Guide
        """
        request = WorkflowExecuteRequest(
            workflow_type=workflow_type,
            card_ids=card_ids,
            context=context,
            parameters=parameters or {},
        )
        
        data = self._request_with_retry(
            method="POST",
            path="/api/v1/workflow/execute",
            json=request.model_dump(mode="json", exclude_none=True),
        )
        
        return WorkflowExecuteResponse(**data)
    
    def get_workflow_status(self, workflow_id: UUID) -> WorkflowExecuteResponse:
        """
        Get workflow execution status.
        
        Args:
            workflow_id: Workflow ID
        
        Returns:
            WorkflowExecuteResponse with current status
        
        Raises:
            WorkflowAPIError: If workflow not found or API error
        """
        data = self._request_with_retry(
            method="GET",
            path=f"/api/v1/workflow/{workflow_id}",
        )
        
        return WorkflowExecuteResponse(**data)
    
    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()
    
    def __enter__(self) -> "WorkflowClient":
        """Context manager entry."""
        return self
    
    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()

