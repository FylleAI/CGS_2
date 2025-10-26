"""WorkflowContext contract - shared between Card Service and Content Workflow."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from .company_snapshot import CompanySnapshot
from .card_summary import CardSummary


class WorkflowContext(BaseModel):
    """Context for content generation workflows.
    
    This is passed from Card Service to Content Workflow Service
    and contains all information needed to generate content.
    """
    
    # Snapshot information
    snapshot: CompanySnapshot = Field(..., description="Company snapshot")
    
    # Cards created from snapshot
    cards: List[CardSummary] = Field(
        default_factory=list,
        description="Atomic cards created from snapshot"
    )
    
    # Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    
    # Workflow configuration
    workflow_type: Optional[str] = Field(
        None,
        description="Type of workflow to execute"
    )
    
    workflow_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Workflow-specific configuration"
    )
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "snapshot": {
                    "version": "1.0",
                    "snapshot_id": "550e8400-e29b-41d4-a716-446655440000",
                    "generated_at": "2025-10-26T18:00:00Z",
                    "company": {
                        "name": "Acme Corp",
                        "industry": "Technology",
                    },
                    "audience": {
                        "primary_segment": "Enterprise",
                    },
                    "voice": {
                        "tone": "Professional",
                    },
                    "insights": {},
                },
                "cards": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440001",
                        "tenant_id": "550e8400-e29b-41d4-a716-446655440002",
                        "card_type": "product",
                        "title": "Acme Product",
                        "content": {},
                        "created_at": "2025-10-26T18:00:00Z",
                        "updated_at": "2025-10-26T18:00:00Z",
                        "is_active": True,
                    }
                ],
                "metadata": {
                    "source": "onboarding",
                    "user_id": "user@example.com",
                },
                "workflow_type": "content_generation",
                "workflow_config": {
                    "channels": ["email", "social"],
                },
            }
        }

