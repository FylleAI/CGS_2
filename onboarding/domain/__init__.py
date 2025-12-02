"""Domain layer for onboarding service."""

from onboarding.domain.models import (
    OnboardingGoal,
    SessionState,
    Evidence,
    CompanyInfo,
    AudienceInfo,
    VoiceInfo,
    InsightsInfo,
    QuestionCardMapping,
    ClarifyingQuestion,
    SourceMetadata,
    CompanySnapshot,
    OnboardingSession,
    OnboardingInput,
    OnboardingResponse,
)

from onboarding.domain.card_types import (
    CardType,
    CardFieldMapping,
    CardTypeConfig,
    CARD_TYPE_CONFIGS,
    QuestionCardMapping as CardQuestionMapping,
    QUESTION_FIELD_MAPPINGS,
    get_missing_fields_for_cards,
    build_question_context_for_gemini,
)

__all__ = [
    # Models
    "OnboardingGoal",
    "SessionState",
    "Evidence",
    "CompanyInfo",
    "AudienceInfo",
    "VoiceInfo",
    "InsightsInfo",
    "QuestionCardMapping",
    "ClarifyingQuestion",
    "SourceMetadata",
    "CompanySnapshot",
    "OnboardingSession",
    "OnboardingInput",
    "OnboardingResponse",
    # Card Types
    "CardType",
    "CardFieldMapping",
    "CardTypeConfig",
    "CARD_TYPE_CONFIGS",
    "CardQuestionMapping",
    "QUESTION_FIELD_MAPPINGS",
    "get_missing_fields_for_cards",
    "build_question_context_for_gemini",
]
