"""Shared contracts between services.

This package contains domain models and contracts that are shared across
multiple services (Onboarding, Card Service, Content Workflow).

These models define the interfaces and data structures that services use
to communicate with each other.
"""

from .company_snapshot import (
    CompanyInfo,
    AudienceInfo,
    VoiceInfo,
    InsightsInfo,
    ClarifyingQuestion,
    SourceMetadata,
    CompanySnapshot,
)

from .card_summary import (
    CardType,
    CardSummary,
)

from .workflow_context import (
    WorkflowContext,
)

__all__ = [
    # CompanySnapshot
    "CompanyInfo",
    "AudienceInfo",
    "VoiceInfo",
    "InsightsInfo",
    "ClarifyingQuestion",
    "SourceMetadata",
    "CompanySnapshot",
    # CardSummary
    "CardType",
    "CardSummary",
    # WorkflowContext
    "WorkflowContext",
]

