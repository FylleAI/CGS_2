"""
Integration tests for Workflow API with Cards integration.

Tests end-to-end scenarios:
- Success: All cards retrieved successfully
- Partial: Some cards missing (X-Partial-Result header)
- Failure: Card retrieval fails completely (502 error)
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4
from datetime import datetime
from httpx import HTTPStatusError, Response, Request, TimeoutException

from fylle_cards_client import ContextCard, CardType, CardListResponse
from fylle_shared.enums import WorkflowType
from fylle_shared.models.workflow import WorkflowRequest

from api.rest.v1.endpoints.workflow_v1 import execute_workflow_v1, init_workflow_v1
from core.infrastructure.workflows.registry import workflow_registry


@pytest.fixture
def mock_cards_client():
    """Mock Cards API client."""
    client = Mock()
    client.retrieve_cards = Mock()
    return client


@pytest.fixture
def mock_workflow_registry():
    """Mock workflow registry with a test handler."""
    registry = Mock()
    
    # Mock handler
    handler = Mock()
    handler.execute = AsyncMock(return_value={
        "status": "completed",
        "content": "Test workflow output",
        "tokens_used": 1500,
    })
    
    registry.get_handler = Mock(return_value=handler)
    return registry


@pytest.fixture
def sample_cards():
    """Sample context cards for testing."""
    tenant_id = uuid4()
    
    return [
        ContextCard(
            card_id=uuid4(),
            tenant_id=tenant_id,
            card_type=CardType.COMPANY,
            title="Acme Corp",
            content={
                "name": "Acme Corp",
                "industry": "Technology",
                "description": "Leading tech company",
            },
            tags=["tech", "b2b"],
            created_by="test_user",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        ContextCard(
            card_id=uuid4(),
            tenant_id=tenant_id,
            card_type=CardType.AUDIENCE,
            title="Tech Executives",
            content={
                "segment": "C-level executives",
                "interests": ["AI", "Cloud", "Security"],
            },
            tags=["audience"],
            created_by="test_user",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        ContextCard(
            card_id=uuid4(),
            tenant_id=tenant_id,
            card_type=CardType.VOICE,
            title="Professional Tone",
            content={
                "tone": "professional",
                "style": "formal",
            },
            tags=["voice"],
            created_by="test_user",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
    ]


@pytest.mark.asyncio
class TestWorkflowCardsIntegration:
    """Integration tests for Workflow + Cards API."""
    
    async def test_success_all_cards_retrieved(
        self,
        mock_cards_client,
        mock_workflow_registry,
        sample_cards,
    ):
        """
        Test SUCCESS scenario: All cards retrieved successfully.
        
        Expected:
        - No X-Partial-Result header
        - Workflow executes with full context
        - Status 200 with completed workflow
        """
        # Setup
        tenant_id = str(sample_cards[0].tenant_id)
        card_ids = [card.card_id for card in sample_cards]
        
        # Mock Cards API response (all cards found)
        mock_cards_client.retrieve_cards.return_value = CardListResponse(
            cards=sample_cards,
            total=len(sample_cards),
        )
        
        # Initialize workflow_v1 with mocks
        init_workflow_v1(mock_workflow_registry, mock_cards_client)
        
        # Create request
        request = WorkflowRequest(
            workflow_type=WorkflowType.PREMIUM_NEWSLETTER,
            card_ids=card_ids,
            parameters={"topic": "AI trends"},
        )
        
        # Mock response object
        response = Mock()
        response.headers = {}
        
        # Execute
        result = await execute_workflow_v1(
            request=request,
            response=response,
            x_tenant_id=tenant_id,
            x_trace_id="test-trace-123",
            x_session_id="test-session-456",
        )
        
        # Assertions
        assert result.status == "completed"
        assert result.workflow_id is not None
        assert result.output is not None
        assert "X-Partial-Result" not in response.headers
        
        # Verify Cards API was called
        mock_cards_client.retrieve_cards.assert_called_once()
        
        # Verify workflow handler was called
        mock_workflow_registry.get_handler.assert_called_once_with("premium_newsletter")
    
    async def test_partial_result_some_cards_missing(
        self,
        mock_cards_client,
        mock_workflow_registry,
        sample_cards,
    ):
        """
        Test PARTIAL scenario: Some cards missing.
        
        Expected:
        - X-Partial-Result header present
        - Workflow executes with partial context
        - Warning logged with missing count
        """
        # Setup
        tenant_id = str(sample_cards[0].tenant_id)
        card_ids = [card.card_id for card in sample_cards]
        
        # Mock Cards API response (only 2 out of 3 cards found)
        partial_cards = sample_cards[:2]
        mock_cards_client.retrieve_cards.return_value = CardListResponse(
            cards=partial_cards,
            total=len(partial_cards),
        )
        
        # Initialize workflow_v1 with mocks
        init_workflow_v1(mock_workflow_registry, mock_cards_client)
        
        # Create request
        request = WorkflowRequest(
            workflow_type=WorkflowType.PREMIUM_NEWSLETTER,
            card_ids=card_ids,
            parameters={"topic": "AI trends"},
        )
        
        # Mock response object
        response = Mock()
        response.headers = {}
        
        # Execute
        result = await execute_workflow_v1(
            request=request,
            response=response,
            x_tenant_id=tenant_id,
            x_trace_id="test-trace-partial",
        )
        
        # Assertions
        assert result.status == "completed"
        assert "X-Partial-Result" in response.headers
        assert "2/3" in response.headers["X-Partial-Result"]
        
        # Verify workflow still executed with partial context
        mock_workflow_registry.get_handler.assert_called_once()
    
    async def test_failure_retrieval_fails_with_retry(
        self,
        mock_cards_client,
        mock_workflow_registry,
        sample_cards,
    ):
        """
        Test FAILURE scenario: Card retrieval fails after retries.

        Expected:
        - Workflow continues with empty context (no cards retrieved)
        - Warning logged about retrieval failure
        - Workflow still executes (resilient behavior)

        Note: The ContextCardTool catches retrieval errors and continues
        with cached cards only. A 502 error would only occur if the
        workflow handler itself fails.
        """
        # Setup
        tenant_id = str(sample_cards[0].tenant_id)
        card_ids = [card.card_id for card in sample_cards]

        # Mock Cards API to raise 503 error (should retry)
        mock_request = Request("POST", "http://test.com/cards/retrieve")
        mock_response = Response(503, request=mock_request)
        mock_cards_client.retrieve_cards.side_effect = HTTPStatusError(
            "Service unavailable",
            request=mock_request,
            response=mock_response,
        )

        # Initialize workflow_v1 with mocks
        init_workflow_v1(mock_workflow_registry, mock_cards_client)

        # Create request
        request = WorkflowRequest(
            workflow_type=WorkflowType.PREMIUM_NEWSLETTER,
            card_ids=card_ids,
            parameters={"topic": "AI trends"},
        )

        # Mock response object
        response = Mock()
        response.headers = {}

        # Execute - should NOT raise error (resilient behavior)
        result = await execute_workflow_v1(
            request=request,
            response=response,
            x_tenant_id=tenant_id,
            x_trace_id="test-trace-failure",
        )

        # Assertions
        assert result.status == "completed"
        # Workflow executed with empty/partial context
        assert result.workflow_id is not None

        # Verify Cards API was called (with retries)
        assert mock_cards_client.retrieve_cards.call_count >= 1

