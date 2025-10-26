"""Card Creation Service - Maps CompanySnapshot to 4 atomic ContextCards.

This service transforms a CompanySnapshot into 4 typed cards:
- company: name, domain, industry, description, key_offerings, differentiators
- audience: primary, segments, pain_points, desired_outcomes
- voice: tone, style_guidelines, do_dont
- insight: facts, sources, confidence

Each card includes a content_hash for type-aware deduplication.
"""

import hashlib
import json
import logging
from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID

from fylle_shared.enums import CardType
from onboarding.domain.models import CompanySnapshot

logger = logging.getLogger(__name__)


class CardCreationService:
    """Service to create cards from CompanySnapshot."""

    def create_cards_from_snapshot(
        self,
        snapshot: CompanySnapshot,
        tenant_id: UUID,
        session_id: UUID,
        created_by: str = "onboarding-api",
    ) -> List[Dict[str, Any]]:
        """
        Create 4 atomic cards from CompanySnapshot.

        Args:
            snapshot: CompanySnapshot with research data
            tenant_id: Tenant ID
            session_id: Session ID for tracking
            created_by: Creator identifier

        Returns:
            List of 4 CreateCardRequest dicts ready for Cards API
        """
        logger.info(f"Creating cards from snapshot {snapshot.snapshot_id}")

        cards = []

        # 1. COMPANY CARD
        company_content = {
            "name": snapshot.company.name,
            "domain": snapshot.company.website or "",
            "industry": snapshot.company.industry or "",
            "description": snapshot.company.description,
            "key_offerings": snapshot.company.key_offerings,
            "differentiators": snapshot.company.differentiators,
            # Optional fields
            "legal_name": snapshot.company.legal_name,
            "headquarters": snapshot.company.headquarters,
            "size_range": snapshot.company.size_range,
        }

        cards.append({
            "tenant_id": str(tenant_id),
            "card_type": CardType.COMPANY.value,
            "title": f"{snapshot.company.name} - Company Profile",
            "description": f"Company information for {snapshot.company.name}",
            "content": company_content,
            "tags": ["company", "profile", snapshot.company.industry or "general"],
            "source_session_id": str(session_id),
            "created_by": created_by,
        })

        # 2. AUDIENCE CARD
        audience_content = {
            "primary": snapshot.audience.primary or "",
            "segments": snapshot.audience.secondary,  # secondary → segments
            "pain_points": snapshot.audience.pain_points,
            "desired_outcomes": snapshot.audience.desired_outcomes,
        }

        cards.append({
            "tenant_id": str(tenant_id),
            "card_type": CardType.AUDIENCE.value,
            "title": f"{snapshot.company.name} - Target Audience",
            "description": f"Target audience for {snapshot.company.name}",
            "content": audience_content,
            "tags": ["audience", "targeting", snapshot.audience.primary or "general"],
            "source_session_id": str(session_id),
            "created_by": created_by,
        })

        # 3. VOICE CARD
        voice_content = {
            "tone": snapshot.voice.tone or "",
            "style_guidelines": snapshot.voice.style_guidelines,
            "do_dont": {
                "forbidden_phrases": snapshot.voice.forbidden_phrases,
                "cta_preferences": snapshot.voice.cta_preferences,
            },
            # Optional compliance notes
            "compliance_notes": None,
        }

        cards.append({
            "tenant_id": str(tenant_id),
            "card_type": CardType.VOICE.value,
            "title": f"{snapshot.company.name} - Brand Voice",
            "description": f"Brand voice and style for {snapshot.company.name}",
            "content": voice_content,
            "tags": ["voice", "style", snapshot.voice.tone or "professional"],
            "source_session_id": str(session_id),
            "created_by": created_by,
        })

        # 4. INSIGHT CARD
        # Extract facts from insights and evidence
        facts = []
        sources = []

        # Add positioning as fact
        if snapshot.insights.positioning:
            facts.append(f"Positioning: {snapshot.insights.positioning}")

        # Add key messages
        facts.extend(snapshot.insights.key_messages)

        # Add recent news
        facts.extend(snapshot.insights.recent_news)

        # Add competitors
        if snapshot.insights.competitors:
            facts.append(f"Competitors: {', '.join(snapshot.insights.competitors)}")

        # Extract sources from evidence
        for evidence in snapshot.company.evidence:
            if evidence.source not in sources:
                sources.append(evidence.source)

        # Calculate confidence from evidence
        confidence = 0.8  # Default
        if snapshot.company.evidence:
            avg_confidence = sum(
                e.confidence for e in snapshot.company.evidence if e.confidence
            ) / len(snapshot.company.evidence)
            confidence = avg_confidence if avg_confidence > 0 else 0.8

        insight_content = {
            "facts": facts,
            "sources": sources,
            "confidence": confidence,
            "last_observed_at": snapshot.generated_at.isoformat(),
        }

        cards.append({
            "tenant_id": str(tenant_id),
            "card_type": CardType.INSIGHT.value,
            "title": f"{snapshot.company.name} - Market Insights",
            "description": f"Market insights and positioning for {snapshot.company.name}",
            "content": insight_content,
            "tags": ["insight", "market", "research"],
            "source_session_id": str(session_id),
            "created_by": created_by,
        })

        logger.info(f"✅ Created {len(cards)} cards from snapshot")
        return cards

    def compute_content_hash(self, card_type: str, content: Dict[str, Any]) -> str:
        """
        Compute type-aware content hash for deduplication.

        Args:
            card_type: Card type (company, audience, voice, insight)
            content: Card content dict

        Returns:
            SHA256 hash of normalized content
        """
        # Normalize content for hashing
        normalized = json.dumps(content, sort_keys=True, ensure_ascii=False)
        hash_input = f"{card_type}:{normalized}"
        return hashlib.sha256(hash_input.encode()).hexdigest()

