"""
Brief Entity for Fylle Onboarding v3
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class BriefSection(BaseModel):
    """A section of the brief."""
    
    title: str
    content: str
    items: List[str] = Field(default_factory=list)


class BrandVoiceSpec(BaseModel):
    """Brand voice specification in brief."""
    
    voice: str = ""
    style_rules: List[str] = Field(default_factory=list)
    emoji_policy: str = ""
    opening: str = ""
    banned_phrasing: List[str] = Field(default_factory=list)


class EditorialStructureSpec(BaseModel):
    """Editorial structure specification in brief."""
    
    format: str = ""
    sections: List[str] = Field(default_factory=list)
    section_details: Dict[str, str] = Field(default_factory=dict)


class CitationRulesSpec(BaseModel):
    """Citation rules specification in brief."""
    
    format: str = ""
    placement: str = ""
    sources: List[str] = Field(default_factory=list)
    date_rules: str = ""


class BriefDocument(BaseModel):
    """Complete brief document structure."""
    
    purpose: str = ""
    non_negotiables: Dict[str, str] = Field(default_factory=dict)
    brand_voice: BrandVoiceSpec = Field(default_factory=BrandVoiceSpec)
    glossary: Dict[str, str] = Field(default_factory=dict)
    editorial_structure: EditorialStructureSpec = Field(default_factory=EditorialStructureSpec)
    citation_rules: CitationRulesSpec = Field(default_factory=CitationRulesSpec)


class Brief(BaseModel):
    """Brief domain entity."""
    
    id: UUID
    user_id: UUID
    pack_id: UUID
    title: Optional[str] = None
    content: BriefDocument = Field(default_factory=BriefDocument)
    answers: Dict[str, str] = Field(default_factory=dict)
    context_snapshot: Dict[str, Any] = Field(default_factory=dict)
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    generation_time_ms: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class CreateBriefRequest(BaseModel):
    """Request to create a new brief."""
    
    user_id: str
    pack_id: str


class BriefQuestionRequest(BaseModel):
    """Request brief generation questions."""
    
    pack_id: str


class BriefAnswersRequest(BaseModel):
    """Submit answers to generate brief."""
    
    answers: Dict[str, str]


class BriefResponse(BaseModel):
    """Brief response model."""
    
    id: str
    user_id: str
    pack_id: str
    title: Optional[str] = None
    content: Dict[str, Any]
    created_at: str
    
    @classmethod
    def from_entity(cls, brief: Brief) -> "BriefResponse":
        return cls(
            id=str(brief.id),
            user_id=str(brief.user_id),
            pack_id=str(brief.pack_id),
            title=brief.title,
            content=brief.content.model_dump(),
            created_at=brief.created_at.isoformat(),
        )


class BriefQuestion(BaseModel):
    """A question for brief generation."""
    
    id: str
    question: str
    options: List[str]
    required: bool = True
    section: str  # brand_voice, editorial_structure, citations, non_negotiables
    reason: Optional[str] = None


class BriefQuestionsResponse(BaseModel):
    """Response with brief questions."""
    
    brief_session_id: str
    questions: List[BriefQuestion]
    message: str
