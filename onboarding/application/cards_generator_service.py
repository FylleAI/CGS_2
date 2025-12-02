"""Cards Generator Service - Orchestrates card generation from onboarding data.

This service:
1. Takes onboarding input + user answers to clarifying questions
2. Uses existing Perplexity + Gemini adapters
3. Generates a complete CardsSnapshot with all 8 card types
"""

import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from onboarding.config.settings import OnboardingSettings
from onboarding.domain.card_types import CardType, CARD_TYPE_CONFIGS
from onboarding.domain.models import CompanySnapshot

logger = logging.getLogger(__name__)


class CardMetadata:
    """Metadata for generated card quality tracking."""
    
    def __init__(
        self,
        confidence: str = "high",
        incomplete_fields: Optional[List[str]] = None,
        data_sources: Optional[List[str]] = None,
        requires_review: bool = False,
        message: Optional[str] = None,
    ):
        self.confidence = confidence
        self.incomplete_fields = incomplete_fields or []
        self.data_sources = data_sources or ["gemini"]
        self.requires_review = requires_review
        self.message = message
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "confidence": self.confidence,
            "incomplete_fields": self.incomplete_fields,
            "data_sources": self.data_sources,
            "requires_review": self.requires_review,
            "message": self.message,
        }


class CardsSnapshot:
    """Output container for generated cards."""
    
    def __init__(
        self,
        session_id: str,
        cards: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.session_id = session_id
        self.generated_at = datetime.utcnow().isoformat()
        self.cards = cards
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sessionId": self.session_id,
            "generatedAt": self.generated_at,
            "cards": self.cards,
            "metadata": self.metadata,
        }


class CardsGeneratorService:
    """
    Service that generates CardsSnapshot from onboarding data.
    
    Uses existing adapters (PerplexityAdapter, GeminiSynthesisAdapter)
    to research and synthesize, then generates all 8 card types.
    """
    
    def __init__(self, settings: OnboardingSettings):
        """Initialize with settings - adapters created lazily."""
        self.settings = settings
        self._perplexity_adapter = None
        self._gemini_adapter = None
        
        logger.info("CardsGeneratorService initialized")
    
    @property
    def perplexity_adapter(self):
        """Lazy load PerplexityAdapter."""
        if self._perplexity_adapter is None:
            from onboarding.infrastructure.adapters.perplexity_adapter import (
                PerplexityAdapter,
            )
            self._perplexity_adapter = PerplexityAdapter(self.settings)
        return self._perplexity_adapter
    
    @property
    def gemini_adapter(self):
        """Lazy load GeminiSynthesisAdapter."""
        if self._gemini_adapter is None:
            from onboarding.infrastructure.adapters.gemini_adapter import (
                GeminiSynthesisAdapter,
            )
            self._gemini_adapter = GeminiSynthesisAdapter(self.settings)
        return self._gemini_adapter
    
    async def generate_cards(
        self,
        session_id: str,
        snapshot: CompanySnapshot,
        answers: Dict[str, Any],
    ) -> CardsSnapshot:
        """
        Generate complete CardsSnapshot from snapshot + answers.
        
        Args:
            session_id: Onboarding session ID
            snapshot: CompanySnapshot from synthesis phase
            answers: User answers to clarifying questions
        
        Returns:
            CardsSnapshot with all 8 card types
        """
        start_time = time.time()
        logger.info(f"Generating cards for session: {session_id}")
        
        # Merge snapshot data with user answers
        merged_data = self._merge_data(snapshot, answers)
        
        # Generate each card type
        cards = []
        warnings = []
        
        # Generate cards using Gemini
        generated = await self._generate_all_cards(merged_data, session_id)
        cards.extend(generated["cards"])
        warnings.extend(generated.get("warnings", []))
        
        # Calculate completeness score
        completeness = self._calculate_completeness(cards)
        
        generation_time = int((time.time() - start_time) * 1000)
        
        return CardsSnapshot(
            session_id=session_id,
            cards=cards,
            metadata={
                "generation_time_ms": generation_time,
                "ai_models_used": ["gemini", "perplexity"],
                "completeness_score": completeness,
                "warnings": warnings if warnings else None,
                "language": self.settings.cards_default_language,
            },
        )

    def _merge_data(
        self,
        snapshot: CompanySnapshot,
        answers: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge snapshot data with user answers based on maps_to."""
        merged = {
            "company": snapshot.company.model_dump() if snapshot.company else {},
            "audience": snapshot.audience.model_dump() if snapshot.audience else {},
            "voice": snapshot.voice.model_dump() if snapshot.voice else {},
            "insights": snapshot.insights.model_dump() if snapshot.insights else {},
            "answers": answers,
        }

        # Map answers to card fields using maps_to from questions
        for question in snapshot.clarifying_questions:
            answer = answers.get(question.id)
            if answer is None:
                continue

            for mapping in question.maps_to:
                card_type = mapping.card_type
                field_name = mapping.field_name

                # Store mapped answer for card generation
                if "mapped_answers" not in merged:
                    merged["mapped_answers"] = {}
                if card_type not in merged["mapped_answers"]:
                    merged["mapped_answers"][card_type] = {}

                merged["mapped_answers"][card_type][field_name] = answer

        return merged

    async def _generate_all_cards(
        self,
        merged_data: Dict[str, Any],
        session_id: str,
    ) -> Dict[str, Any]:
        """Generate all card types using Gemini."""
        import json

        prompt = self._build_cards_generation_prompt(merged_data, session_id)

        try:
            response = await self.gemini_adapter.adapter.generate_content(
                prompt=prompt,
                config=self.gemini_adapter.config,
            )

            # Parse JSON response
            content = response.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            data = json.loads(content)

            return {
                "cards": data.get("cards", []),
                "warnings": data.get("warnings", []),
            }

        except Exception as e:
            logger.error(f"Card generation failed: {e}")
            # Return minimal fallback cards
            return self._generate_fallback_cards(merged_data, session_id)

    def _build_cards_generation_prompt(
        self,
        merged_data: Dict[str, Any],
        session_id: str,
    ) -> str:
        """Build prompt for generating all cards."""
        import json

        prompt = f"""Generate a complete CardsSnapshot with all 8 card types.

SESSION ID: {session_id}

AVAILABLE DATA:
{json.dumps(merged_data, indent=2, ensure_ascii=False)}

CARD TYPES TO GENERATE:
1. product (1 card) - valueProposition, features, differentiators, useCases
2. target (1-5 cards) - icpName, description, painPoints, goals, channels
3. brand_voice (1 card) - toneDescription, styleGuidelines, dos, donts
4. competitor (0-10 cards) - competitorName, positioning, strengths, weaknesses
5. topic (1-5 cards) - description, keywords, angles, trends
6. campaigns (1-3 cards) - objective, keyMessages, tone, assets
7. performance (1 card) - PLACEHOLDER with status: "awaiting_data"
8. feedback (1 card) - PLACEHOLDER with status: "awaiting_data"

OUTPUT FORMAT:
{{
  "cards": [
    {{
      "id": "card-product-001",
      "type": "product",
      "title": "...",
      "valueProposition": "...",
      "features": [...],
      "differentiators": [...],
      "useCases": [...],
      "performanceMetrics": [],
      "createdAt": "{datetime.utcnow().isoformat()}",
      "updatedAt": "{datetime.utcnow().isoformat()}",
      "sessionId": "{session_id}",
      "_metadata": {{
        "confidence": "high|medium|low",
        "data_sources": ["user_input", "perplexity", "gemini"],
        "requires_review": false
      }}
    }},
    ...
  ],
  "warnings": ["optional warning messages"]
}}

RULES:
1. Use Italian language for all content
2. Generate ALL required card types (8 total minimum)
3. Set confidence based on data quality: high (complete), medium (partial), low (inferred)
4. For performance and feedback cards, create placeholders with status: "awaiting_data"
5. Never leave required fields empty - generate reasonable defaults if needed
6. Be specific, avoid generic phrases

Return ONLY valid JSON, no markdown or explanations.
"""
        return prompt

    def _generate_fallback_cards(
        self,
        merged_data: Dict[str, Any],
        session_id: str,
    ) -> Dict[str, Any]:
        """Generate minimal fallback cards if Gemini fails."""
        now = datetime.utcnow().isoformat()
        company = merged_data.get("company", {})

        return {
            "cards": [
                {
                    "id": f"card-product-{str(uuid4())[:8]}",
                    "type": "product",
                    "title": company.get("name", "Prodotto"),
                    "valueProposition": company.get("description", ""),
                    "features": company.get("key_offerings", []),
                    "differentiators": company.get("differentiators", []),
                    "useCases": [],
                    "performanceMetrics": [],
                    "createdAt": now,
                    "updatedAt": now,
                    "sessionId": session_id,
                    "_metadata": {
                        "confidence": "low",
                        "data_sources": ["fallback"],
                        "requires_review": True,
                        "message": "Card generata con dati minimi. Completa i dettagli.",
                    },
                },
                {
                    "id": f"card-performance-placeholder",
                    "type": "performance",
                    "title": "Performance Campagne",
                    "period": "In attesa di dati",
                    "metrics": [],
                    "topPerformingContent": [],
                    "insights": [],
                    "createdAt": now,
                    "updatedAt": now,
                    "sessionId": session_id,
                    "_metadata": {
                        "status": "awaiting_data",
                        "message": "Si popolerà con le metriche delle campagne",
                    },
                },
                {
                    "id": f"card-feedback-placeholder",
                    "type": "feedback",
                    "title": "Feedback & Learnings",
                    "source": "other",
                    "summary": "In attesa di feedback",
                    "details": "",
                    "actionItems": [],
                    "priority": "medium",
                    "createdAt": now,
                    "updatedAt": now,
                    "sessionId": session_id,
                    "_metadata": {
                        "status": "awaiting_data",
                        "message": "I feedback verranno raccolti dalle attività",
                    },
                },
            ],
            "warnings": ["Generazione fallback: alcune card potrebbero essere incomplete"],
        }

    def _calculate_completeness(self, cards: List[Dict[str, Any]]) -> int:
        """Calculate completeness score (0-100) based on card quality."""
        if not cards:
            return 0

        total_score = 0
        for card in cards:
            metadata = card.get("_metadata", {})
            confidence = metadata.get("confidence", "medium")

            if confidence == "high":
                total_score += 100
            elif confidence == "medium":
                total_score += 70
            elif confidence == "low":
                total_score += 40
            elif metadata.get("status") == "awaiting_data":
                total_score += 50  # Placeholders are expected

        return int(total_score / len(cards))

