"""
Fylle Cards API Client.

Provides type-safe methods for interacting with the Cards API.
"""

import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential_jitter

from fylle_cards_client.models import (
    CardBatchResponse,
    CardListResponse,
    CardType,
    ContextCard,
    CreateCardRequest,
    CreateCardsBatchRequest,
    ErrorResponse,
    RetrieveCardsRequest,
    TrackUsageRequest,
)

logger = logging.getLogger(__name__)


def _should_retry_on_error(exception: Exception) -> bool:
    """
    Determine if request should be retried based on exception.

    Retry on:
    - Timeout exceptions
    - 429 (rate limit)
    - 5xx (server errors)

    Do NOT retry on:
    - 4xx (client errors, except 429)

    Args:
        exception: Exception raised during request

    Returns:
        True if should retry, False otherwise
    """
    # Always retry on timeout
    if isinstance(exception, httpx.TimeoutException):
        return True

    # Retry on specific HTTP status codes
    if isinstance(exception, httpx.HTTPStatusError):
        status_code = exception.response.status_code
        # Retry on 429 (rate limit) and 5xx (server errors)
        return status_code == 429 or status_code >= 500

    return False


class CardsAPIError(Exception):
    """Base exception for Cards API errors."""

    def __init__(self, status_code: int, error: ErrorResponse):
        self.status_code = status_code
        self.error = error
        super().__init__(f"Cards API error {status_code}: {error.error} - {error.detail}")


class CardsClient:
    """
    Client for Fylle Cards API v1.
    
    Provides type-safe methods with automatic retry logic and header propagation.
    
    Args:
        base_url: Base URL of the Cards API (e.g., "http://localhost:8002")
        tenant_id: Tenant ID for multi-tenant isolation (required)
        trace_id: Optional trace ID for distributed tracing
        session_id: Optional session ID for tracking
        timeout_connect: Connection timeout in seconds (default: 0.2)
        timeout_read: Read timeout in seconds (default: 0.8)
    """

    def __init__(
        self,
        base_url: str,
        tenant_id: str,
        trace_id: Optional[str] = None,
        session_id: Optional[str] = None,
        timeout_connect: float = 0.2,
        timeout_read: float = 0.8,
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
    
    def _get_headers(self, idempotency_key: Optional[str] = None) -> Dict[str, str]:
        """Build headers for API requests."""
        headers = {
            "X-Tenant-ID": self.tenant_id,
            "Content-Type": "application/json",
        }
        
        if self.trace_id:
            headers["X-Trace-ID"] = self.trace_id
        
        if self.session_id:
            headers["X-Session-ID"] = self.session_id
        
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        
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
            raise CardsAPIError(response.status_code, error)
        
        return response.json()
    
    @retry(
        retry=retry_if_exception(_should_retry_on_error),
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
        idempotency_key: Optional[str] = None,
    ) -> Any:
        """Make HTTP request with retry logic."""
        headers = self._get_headers(idempotency_key=idempotency_key)
        
        response = self.client.request(
            method=method,
            url=path,
            json=json,
            params=params,
            headers=headers,
        )
        
        return self._handle_response(response)
    
    def create_card(
        self,
        card_type: CardType,
        title: str,
        content: Dict[str, Any],
        created_by: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        source_session_id: Optional[UUID] = None,
    ) -> ContextCard:
        """
        Create a single card.
        
        Args:
            card_type: Type of card (company, audience, voice, insight)
            title: Card title (1-200 chars)
            content: Card content (flexible JSONB)
            created_by: Creator identifier
            description: Optional description (max 1000 chars)
            tags: Optional list of tags
            source_session_id: Optional source session ID
        
        Returns:
            Created ContextCard
        
        Raises:
            CardsAPIError: If API returns an error
        """
        request = CreateCardRequest(
            tenant_id=UUID(self.tenant_id),
            card_type=card_type,
            title=title,
            description=description,
            content=content,
            tags=tags or [],
            source_session_id=source_session_id,
            created_by=created_by,
        )
        
        data = self._request_with_retry(
            method="POST",
            path="/api/v1/cards",
            json=request.model_dump(mode="json"),
        )
        
        return ContextCard(**data)
    
    def create_cards_batch(
        self,
        company_snapshot: Dict[str, Any],
        source_session_id: UUID,
        created_by: str,
        idempotency_key: Optional[str] = None,
    ) -> CardBatchResponse:
        """
        Create multiple cards from CompanySnapshot (idempotent).
        
        Args:
            company_snapshot: CompanySnapshot from onboarding
            source_session_id: Source session ID
            created_by: Creator identifier
            idempotency_key: Optional idempotency key for safe retries
        
        Returns:
            CardBatchResponse with created cards
        
        Raises:
            CardsAPIError: If API returns an error
        """
        request = CreateCardsBatchRequest(
            tenant_id=UUID(self.tenant_id),
            company_snapshot=company_snapshot,
            source_session_id=source_session_id,
            created_by=created_by,
        )
        
        data = self._request_with_retry(
            method="POST",
            path="/api/v1/cards/batch",
            json=request.model_dump(mode="json"),
            idempotency_key=idempotency_key,
        )
        
        return CardBatchResponse(**data)
    
    def get_card(self, card_id: UUID) -> ContextCard:
        """
        Get card by ID.
        
        Args:
            card_id: Card ID
        
        Returns:
            ContextCard
        
        Raises:
            CardsAPIError: If card not found or API error
        """
        data = self._request_with_retry(
            method="GET",
            path=f"/api/v1/cards/{card_id}",
        )
        
        return ContextCard(**data)
    
    def list_cards(
        self,
        card_type: Optional[CardType] = None,
        is_active: bool = True,
        page: int = 1,
        page_size: int = 20,
    ) -> CardListResponse:
        """
        List cards with filtering.
        
        Args:
            card_type: Optional filter by card type
            is_active: Filter by active status (default: True)
            page: Page number (default: 1)
            page_size: Page size (default: 20, max: 100)
        
        Returns:
            CardListResponse with cards and pagination
        
        Raises:
            CardsAPIError: If API returns an error
        """
        params: Dict[str, Any] = {
            "is_active": is_active,
            "page": page,
            "page_size": page_size,
        }
        
        if card_type:
            params["card_type"] = card_type.value
        
        data = self._request_with_retry(
            method="GET",
            path="/api/v1/cards",
            params=params,
        )
        
        return CardListResponse(**data)
    
    def retrieve_cards(self, card_ids: List[UUID]) -> CardListResponse:
        """
        Retrieve cards by IDs for workflow execution.
        
        Best-effort: Returns available cards even if some IDs are missing.
        Check response headers for X-Partial-Result: true.
        
        Args:
            card_ids: List of card IDs to retrieve
        
        Returns:
            CardListResponse with available cards
        
        Raises:
            CardsAPIError: If API returns an error
        """
        request = RetrieveCardsRequest(
            tenant_id=UUID(self.tenant_id),
            card_ids=card_ids,
        )
        
        data = self._request_with_retry(
            method="POST",
            path="/api/v1/cards/retrieve",
            json=request.model_dump(mode="json"),
        )
        
        return CardListResponse(**data)
    
    def track_usage(
        self,
        card_id: UUID,
        workflow_id: Optional[UUID] = None,
        workflow_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Track card usage in workflow.
        
        Args:
            card_id: Card ID
            workflow_id: Optional workflow ID
            workflow_type: Optional workflow type
            metadata: Optional metadata
        
        Raises:
            CardsAPIError: If API returns an error
        """
        request = TrackUsageRequest(
            workflow_id=workflow_id,
            workflow_type=workflow_type,
            metadata=metadata or {},
        )
        
        self._request_with_retry(
            method="POST",
            path=f"/api/v1/cards/{card_id}/usage",
            json=request.model_dump(mode="json"),
        )
    
    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()
    
    def __enter__(self) -> "CardsClient":
        """Context manager entry."""
        return self
    
    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()

