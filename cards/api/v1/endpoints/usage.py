"""
Usage tracking endpoints for Cards API.

Tracks card usage by workflows with deduplication per run.
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Response
from prometheus_client import Counter, Histogram
from pydantic import BaseModel, Field

from cards.infrastructure.database import DatabaseConnection

logger = logging.getLogger(__name__)

# Prometheus metrics
usage_events_total = Counter(
    "card_usage_events_total",
    "Total number of card usage events tracked",
    ["card_type", "workflow_type"],
)

usage_write_duration = Histogram(
    "cards_usage_write_duration_ms",
    "Duration of usage write operations in milliseconds",
    buckets=[5, 10, 25, 50, 100, 250, 500, 1000],
)

# Router
router = APIRouter()

# Global database connection (injected by main.py)
db_connection: Optional[DatabaseConnection] = None


def init_usage_endpoints(db: DatabaseConnection):
    """Initialize usage endpoints with database connection."""
    global db_connection
    db_connection = db
    logger.info("✅ Usage endpoints initialized")


# Request/Response Models
class TrackUsageRequest(BaseModel):
    """Request model for tracking card usage."""

    workflow_id: str = Field(..., description="Workflow execution ID")
    workflow_type: str = Field(..., description="Type of workflow (e.g., premium_newsletter)")
    session_id: Optional[str] = Field(None, description="Optional session ID for grouping")


class TrackUsageResponse(BaseModel):
    """Response model for usage tracking."""

    card_id: str
    usage_count: int
    last_used_at: str
    event_recorded: bool


# Endpoints
@router.post("/{card_id}/usage", response_model=TrackUsageResponse, status_code=200)
async def track_card_usage(
    card_id: str,
    request: TrackUsageRequest,
    response: Response,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
    x_trace_id: Optional[str] = Header(None, alias="X-Trace-ID"),
):
    """
    Track card usage by a workflow.

    **Deduplication**: Prevents duplicate usage events for the same (workflow_id, card_id) pair.

    **Headers**:
    - X-Tenant-ID (required): Tenant identifier
    - X-Trace-ID (optional): Trace ID for distributed tracing

    **Body**:
    - workflow_id: Workflow execution ID
    - workflow_type: Type of workflow
    - session_id: Optional session ID

    **Returns**:
    - card_id: Card ID
    - usage_count: Updated usage count
    - last_used_at: Timestamp of last usage
    - event_recorded: Whether a new event was recorded (false if duplicate)
    """
    if not db_connection:
        raise HTTPException(status_code=503, detail="Database not initialized")

    # Validate UUID format
    try:
        tenant_id = UUID(x_tenant_id)
        card_uuid = UUID(card_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid UUID format: {e}")

    logger.info(
        f"📊 Tracking usage: card_id={card_id}, workflow_id={request.workflow_id}, "
        f"workflow_type={request.workflow_type}, tenant_id={tenant_id}, trace_id={x_trace_id}"
    )

    with usage_write_duration.time():
        try:
            # Check for duplicate usage event (deduplication per run)
            check_duplicate_query = """
                SELECT 1 FROM card_usage
                WHERE card_id = $1 AND workflow_id = $2 AND tenant_id = $3
                LIMIT 1
            """

            async with db_connection.acquire(tenant_id=str(tenant_id)) as conn:
                # Check for duplicate
                duplicate = await conn.fetchval(
                    check_duplicate_query, card_uuid, request.workflow_id, tenant_id
                )

                event_recorded = False

                if duplicate:
                    logger.info(
                        f"⚠️ Duplicate usage event detected: workflow_id={request.workflow_id}, "
                        f"card_id={card_id} - Skipping event insertion"
                    )
                else:
                    # Insert usage event (new event)
                    insert_event_query = """
                        INSERT INTO card_usage (
                            card_id,
                            tenant_id,
                            workflow_id,
                            workflow_type,
                            session_id,
                            used_at
                        )
                        VALUES ($1, $2, $3, $4, $5, NOW())
                    """

                    await conn.execute(
                        insert_event_query,
                        card_uuid,
                        tenant_id,
                        request.workflow_id,
                        request.workflow_type,
                        request.session_id,
                    )

                    event_recorded = True
                    logger.info(f"✅ Usage event recorded: card_id={card_id}, workflow_id={request.workflow_id}")

                # Update card usage_count and last_used_at (always update, even for duplicates)
                update_card_query = """
                    UPDATE cards
                    SET 
                        usage_count = usage_count + 1,
                        last_used_at = NOW(),
                        updated_at = NOW()
                    WHERE card_id = $1 AND tenant_id = $2
                    RETURNING usage_count, last_used_at
                """

                row = await conn.fetchrow(update_card_query, card_uuid, tenant_id)

                if not row:
                    raise HTTPException(status_code=404, detail=f"Card not found: {card_id}")

                usage_count = row["usage_count"]
                last_used_at = row["last_used_at"].isoformat()

            # Get card type for metrics
            card_type_query = """
                SELECT card_type FROM cards
                WHERE card_id = $1 AND tenant_id = $2
            """

            async with db_connection.acquire(tenant_id=str(tenant_id)) as conn:
                card_type = await conn.fetchval(card_type_query, card_uuid, tenant_id)

            # Update Prometheus metrics
            if event_recorded:
                usage_events_total.labels(card_type=card_type, workflow_type=request.workflow_type).inc()

            logger.info(
                f"✅ Usage tracked: card_id={card_id}, usage_count={usage_count}, "
                f"event_recorded={event_recorded}"
            )

            # Add custom header to indicate if event was recorded
            response.headers["X-Event-Recorded"] = "true" if event_recorded else "false"

            return TrackUsageResponse(
                card_id=card_id,
                usage_count=usage_count,
                last_used_at=last_used_at,
                event_recorded=event_recorded,
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Failed to track usage: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to track usage: {str(e)}")

