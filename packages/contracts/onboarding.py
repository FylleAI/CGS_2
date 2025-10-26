"""Shared onboarding contracts used across services."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ClarifyingAnswer(BaseModel):
    """Answer provided by the user during onboarding."""

    question_id: str = Field(..., description="Identifier of the clarifying question")
    answer: Any = Field(..., description="User provided answer value")
    question: Optional[str] = Field(default=None, description="Original question text")
    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Optional confidence score assigned by the system",
    )


class ClarifyingAnswers(BaseModel):
    """Collection of clarifying answers indexed by question id."""

    items: List[ClarifyingAnswer] = Field(default_factory=list)

    def to_mapping(self) -> Dict[str, Any]:
        """Return a mapping of question_id -> answer."""

        return {item.question_id: item.answer for item in self.items}

    @classmethod
    def from_mapping(cls, answers: Dict[str, Any]) -> "ClarifyingAnswers":
        """Create a collection from a mapping."""

        return cls(
            items=[
                ClarifyingAnswer(question_id=key, answer=value)
                for key, value in answers.items()
            ]
        )

    def merge(self, extra: Iterable[ClarifyingAnswer]) -> "ClarifyingAnswers":
        """Return a new instance merging current items with provided answers."""

        combined = {item.question_id: item for item in self.items}
        for answer in extra:
            combined[answer.question_id] = answer
        return ClarifyingAnswers(items=list(combined.values()))


class CompanyProfile(BaseModel):
    """Core company information produced during onboarding research."""

    name: str = Field(..., description="Common company name")
    description: str = Field(default="", description="Short description of the company")
    legal_name: Optional[str] = Field(default=None, description="Legal registered name")
    website: Optional[str] = Field(default=None, description="Primary website URL")
    industry: Optional[str] = Field(default=None, description="Industry classification")
    headquarters: Optional[str] = Field(
        default=None, description="Headquarters location"
    )
    size_range: Optional[str] = Field(default=None, description="Company size range")
    value_proposition: Optional[str] = Field(
        default=None, description="Primary value proposition"
    )
    differentiators: List[str] = Field(default_factory=list)
    key_offerings: List[str] = Field(default_factory=list)
    features: List[str] = Field(default_factory=list)
    use_cases: List[str] = Field(default_factory=list)
    target_market: Optional[str] = Field(default=None)
    metrics: Dict[str, Any] = Field(default_factory=dict)


class AudienceProfile(BaseModel):
    """Target audience information used for persona cards."""

    persona_name: str = Field(default="Target Audience")
    icp_profile: Optional[str] = Field(default=None)
    pain_points: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)
    preferred_language: Optional[str] = Field(default=None)
    communication_channels: List[str] = Field(default_factory=list)
    demographics: Dict[str, Any] = Field(default_factory=dict)
    psychographics: Dict[str, Any] = Field(default_factory=dict)


class VoiceProfile(BaseModel):
    """Brand voice preferences derived during onboarding."""

    tone: Optional[str] = Field(default=None)
    style_guidelines: List[str] = Field(default_factory=list)
    forbidden_phrases: List[str] = Field(default_factory=list)
    cta_preferences: List[str] = Field(default_factory=list)


class InsightProfile(BaseModel):
    """Market and topical insights used for topic cards."""

    topic_name: str = Field(default="Key Topics")
    keywords: List[str] = Field(default_factory=list)
    angles: List[str] = Field(default_factory=list)
    related_content: List[str] = Field(default_factory=list)
    trend_status: Optional[str] = Field(default=None)
    frequency: Optional[str] = Field(default=None)
    audience_interest: Optional[str] = Field(default=None)
    search_volume: Optional[float] = Field(default=None)
    trend_score: Optional[float] = Field(default=None)


class CampaignGoal(BaseModel):
    """Campaign level goal used to create campaign cards."""

    campaign_name: str = Field(default="Campaign")
    objective: Optional[str] = Field(default=None)
    key_messages: List[str] = Field(default_factory=list)
    tone: Optional[str] = Field(default=None)
    assets_produced: List[str] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)


class CompanySnapshot(BaseModel):
    """Shared representation of the onboarding snapshot artifact."""

    version: str = Field(default="1.0")
    snapshot_id: Optional[UUID] = None
    generated_at: Optional[datetime] = None
    trace_id: Optional[str] = None

    company: CompanyProfile
    audience: AudienceProfile = Field(default_factory=AudienceProfile)
    voice: VoiceProfile = Field(default_factory=VoiceProfile)
    insights: InsightProfile = Field(default_factory=InsightProfile)
    goal: Optional[CampaignGoal] = None

    clarifying_answers: ClarifyingAnswers = Field(default_factory=ClarifyingAnswers)
    source_metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_card_payload(self) -> Dict[str, Any]:
        """Serialize snapshot into the structure expected by Card Service."""

        return {
            "company_info": {
                "company_name": self.company.name,
                "value_proposition": self.company.value_proposition,
                "features": self.company.features,
                "differentiators": self.company.differentiators,
                "use_cases": self.company.use_cases,
                "target_market": self.company.target_market,
                "description": self.company.description,
                "industry": self.company.industry,
                "website": self.company.website,
                "metrics": self.company.metrics,
            },
            "audience_info": {
                "persona_name": self.audience.persona_name,
                "icp_profile": self.audience.icp_profile,
                "pain_points": self.audience.pain_points,
                "goals": self.audience.goals,
                "preferred_language": self.audience.preferred_language,
                "communication_channels": self.audience.communication_channels,
                "demographics": self.audience.demographics,
                "psychographics": self.audience.psychographics,
            },
            "goal": {
                "campaign_name": self.goal.campaign_name if self.goal else "Campaign",
                "objective": self.goal.objective if self.goal else None,
                "key_messages": self.goal.key_messages if self.goal else [],
                "tone": self.goal.tone if self.goal else None,
                "assets_produced": self.goal.assets_produced if self.goal else [],
                "metrics": self.goal.metrics if self.goal else {},
            },
            "insights": {
                "topic_name": self.insights.topic_name,
                "keywords": self.insights.keywords,
                "angles": self.insights.angles,
                "related_content": self.insights.related_content,
                "trend_status": self.insights.trend_status,
                "frequency": self.insights.frequency,
                "audience_interest": self.insights.audience_interest,
                "search_volume": self.insights.search_volume,
                "trend_score": self.insights.trend_score,
            },
            "clarifying_answers": self.clarifying_answers.to_mapping(),
            "metadata": self.source_metadata,
        }

    @classmethod
    def from_domain_snapshot(
        cls, snapshot: "DomainCompanySnapshot"
    ) -> "CompanySnapshot":
        """Build shared contract from onboarding domain snapshot."""

        return cls(
            version=snapshot.version,
            snapshot_id=snapshot.snapshot_id,
            generated_at=snapshot.generated_at,
            trace_id=snapshot.trace_id,
            company=CompanyProfile(
                name=snapshot.company.name,
                description=snapshot.company.description,
                legal_name=snapshot.company.legal_name,
                website=snapshot.company.website,
                industry=snapshot.company.industry,
                headquarters=snapshot.company.headquarters,
                size_range=snapshot.company.size_range,
                value_proposition=getattr(
                    snapshot.company, "value_proposition", None
                ),
                differentiators=snapshot.company.differentiators,
                key_offerings=snapshot.company.key_offerings,
                features=getattr(snapshot.company, "features", []),
                use_cases=getattr(snapshot.company, "use_cases", []),
                target_market=getattr(snapshot.company, "target_market", None),
                metrics=getattr(snapshot.company, "metrics", {}),
            ),
            audience=AudienceProfile(
                persona_name=(
                    snapshot.audience.primary
                    if getattr(snapshot.audience, "primary", None)
                    else "Target Audience"
                ),
                icp_profile=getattr(snapshot.audience, "primary", None),
                pain_points=snapshot.audience.pain_points,
                goals=snapshot.audience.desired_outcomes,
                preferred_language=getattr(snapshot.voice, "tone", None),
                communication_channels=getattr(
                    snapshot.audience, "communication_channels", []
                ),
                demographics=getattr(snapshot.audience, "demographics", {}),
                psychographics=getattr(snapshot.audience, "psychographics", {}),
            ),
            voice=VoiceProfile(
                tone=snapshot.voice.tone,
                style_guidelines=snapshot.voice.style_guidelines,
                forbidden_phrases=snapshot.voice.forbidden_phrases,
                cta_preferences=snapshot.voice.cta_preferences,
            ),
            insights=InsightProfile(
                topic_name=(
                    getattr(snapshot.insights, "positioning", None) or "Key Topics"
                ),
                keywords=getattr(snapshot.insights, "key_messages", []) or [],
                angles=getattr(snapshot.insights, "recent_news", []) or [],
                related_content=getattr(snapshot.insights, "related_content", []) or [],
                trend_status=getattr(snapshot.insights, "trend_status", None),
                frequency=getattr(snapshot.insights, "frequency", None),
                audience_interest=getattr(snapshot.insights, "audience_interest", None),
                search_volume=getattr(snapshot.insights, "search_volume", None),
                trend_score=getattr(snapshot.insights, "trend_score", None),
            ),
            goal=CampaignGoal(
                campaign_name=goal_data.get("campaign_name", "Campaign"),
                objective=goal_data.get("objective"),
                key_messages=goal_data.get("key_messages", []),
                tone=goal_data.get("tone"),
                assets_produced=goal_data.get("assets_produced", []),
                metrics=goal_data.get("metrics", {}),
            )
            if (goal_data := getattr(snapshot, "goal", None)) and isinstance(
                goal_data, dict
            )
            else None,
            clarifying_answers=ClarifyingAnswers.from_mapping(
                snapshot.clarifying_answers
            ),
            source_metadata={
                "sources": [
                    meta.model_dump() if hasattr(meta, "model_dump") else meta.dict()
                    for meta in snapshot.source_metadata
                ]
            },
        )


if TYPE_CHECKING:  # pragma: no cover - import only for type checking
    from services.onboarding.domain.models import CompanySnapshot as DomainCompanySnapshot
else:  # pragma: no cover - optional dependency during runtime packaging
    DomainCompanySnapshot = Any  # type: ignore
