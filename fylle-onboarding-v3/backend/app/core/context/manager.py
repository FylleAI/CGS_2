"""
Context Manager for Fylle Onboarding v3
Aggregates user context from cards for brief generation.
"""

from typing import Any, Dict, List, Optional

from app.domain.entities import CardType


class ContextManager:
    """
    Aggregates user context from cards.
    
    This context is used for:
    - Generating brief questions (context-aware)
    - Generating briefs (full context)
    - Generating content (selected context)
    """
    
    def __init__(self, cards_repository: Any):
        self.cards_repo = cards_repository
    
    async def build_context(self, user_id: str) -> Dict[str, Any]:
        """
        Build comprehensive context from user's cards.
        
        Returns structured context organized by category.
        """
        cards = await self.cards_repo.get_by_user(user_id)
        
        context = {
            "company": {},
            "products": [],
            "targets": [],
            "brand_voice": {},
            "competitors": [],
            "topics": [],
            "performance": {},
            "feedback": [],
        }
        
        for card in cards:
            card_type = card.type
            data = card.data
            
            if card_type == CardType.PRODUCT:
                context["products"].append({
                    "title": card.title,
                    "value_proposition": data.get("valueProposition", ""),
                    "features": data.get("features", []),
                    "differentiators": data.get("differentiators", []),
                    "use_cases": data.get("useCases", []),
                })
            
            elif card_type == CardType.TARGET:
                context["targets"].append({
                    "name": data.get("icpName", card.title),
                    "description": data.get("description", ""),
                    "pain_points": data.get("painPoints", []),
                    "goals": data.get("goals", []),
                    "preferred_language": data.get("preferredLanguage", ""),
                    "channels": data.get("communicationChannels", []),
                })
            
            elif card_type == CardType.BRAND_VOICE:
                context["brand_voice"] = {
                    "tone": data.get("toneDescription", ""),
                    "style_guidelines": data.get("styleGuidelines", []),
                    "dos": data.get("dosExamples", []),
                    "donts": data.get("dontsExamples", []),
                    "terms_to_use": data.get("termsToUse", []),
                    "terms_to_avoid": data.get("termsToAvoid", []),
                }
            
            elif card_type == CardType.COMPETITOR:
                context["competitors"].append({
                    "name": data.get("competitorName", card.title),
                    "positioning": data.get("positioning", ""),
                    "key_messages": data.get("keyMessages", []),
                    "strengths": data.get("strengths", []),
                    "weaknesses": data.get("weaknesses", []),
                })
            
            elif card_type == CardType.TOPIC:
                context["topics"].append({
                    "title": card.title,
                    "description": data.get("description", ""),
                    "keywords": data.get("keywords", []),
                    "angles": data.get("angles", []),
                    "trends": data.get("trends", []),
                })
            
            elif card_type == CardType.CAMPAIGNS:
                # Add to company context
                context["company"]["recent_campaigns"] = {
                    "objective": data.get("objective", ""),
                    "key_messages": data.get("keyMessages", []),
                    "tone": data.get("tone", ""),
                    "learnings": data.get("learnings", []),
                }
            
            elif card_type == CardType.PERFORMANCE:
                context["performance"] = {
                    "period": data.get("period", ""),
                    "metrics": data.get("metrics", []),
                    "top_performing": data.get("topPerformingContent", []),
                    "insights": data.get("insights", []),
                }
            
            elif card_type == CardType.FEEDBACK:
                context["feedback"].append({
                    "source": data.get("source", ""),
                    "summary": data.get("summary", ""),
                    "action_items": data.get("actionItems", []),
                    "priority": data.get("priority", "medium"),
                })
        
        return context
    
    async def get_context_summary(self, user_id: str) -> str:
        """
        Get a human-readable summary of user context.
        Useful for displaying to users or for debugging.
        """
        context = await self.build_context(user_id)
        
        lines = []
        
        # Products
        if context["products"]:
            lines.append("**Prodotti/Servizi:**")
            for p in context["products"]:
                lines.append(f"- {p.get('title', 'Prodotto')}: {p.get('value_proposition', '')}")
        
        # Targets
        if context["targets"]:
            lines.append("\n**Target:**")
            for t in context["targets"]:
                lines.append(f"- {t.get('name', 'Target')}: {t.get('description', '')}")
        
        # Brand Voice
        if context["brand_voice"]:
            lines.append("\n**Brand Voice:**")
            lines.append(f"- Tono: {context['brand_voice'].get('tone', 'Non definito')}")
        
        # Topics
        if context["topics"]:
            lines.append("\n**Topic principali:**")
            for t in context["topics"]:
                lines.append(f"- {t.get('title', 'Topic')}")
        
        return "\n".join(lines)
    
    async def get_brief_context(
        self,
        user_id: str,
        include_sections: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Get filtered context for brief generation.
        
        Args:
            user_id: User ID
            include_sections: List of sections to include (default: all)
            
        Returns:
            Filtered context dictionary
        """
        full_context = await self.build_context(user_id)
        
        if not include_sections:
            return full_context
        
        return {
            key: value
            for key, value in full_context.items()
            if key in include_sections
        }
