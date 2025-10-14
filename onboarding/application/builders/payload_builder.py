"""Payload builder for constructing CGS payloads from snapshots.

Intelligent mapping from CompanySnapshot + answers to CGS input parameters.
"""

import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from onboarding.domain.models import CompanySnapshot, OnboardingGoal
from onboarding.domain.cgs_contracts import (
    CgsPayloadLinkedInPost,
    CgsPayloadNewsletter,
    LinkedInPostInput,
    NewsletterInput,
    CgsPayloadMetadata,
)

logger = logging.getLogger(__name__)


class PayloadBuilder:
    """
    Builder for constructing CGS payloads from company snapshots.
    
    Implements intelligent mapping logic to infer optimal parameters
    from snapshot data and user answers.
    """
    
    def build_payload(
        self,
        session_id: UUID,
        trace_id: str,
        snapshot: CompanySnapshot,
        goal: OnboardingGoal,
        dry_run: bool = False,
        requested_provider: Optional[str] = None,
    ) -> CgsPayloadLinkedInPost | CgsPayloadNewsletter:
        """
        Build CGS payload based on goal.
        
        Args:
            session_id: Session ID
            trace_id: Trace ID for correlation
            snapshot: Company snapshot with answers
            goal: Onboarding goal
            dry_run: Whether this is a dry run
            requested_provider: Optional LLM provider override
        
        Returns:
            CgsPayload (LinkedIn or Newsletter)
        """
        logger.info(f"Building payload for goal: {goal}")
        
        if goal == OnboardingGoal.LINKEDIN_POST:
            return self._build_linkedin_payload(
                session_id, trace_id, snapshot, dry_run, requested_provider
            )
        elif goal in {OnboardingGoal.NEWSLETTER, OnboardingGoal.NEWSLETTER_PREMIUM}:
            return self._build_newsletter_payload(
                session_id, trace_id, snapshot, dry_run, requested_provider
            )
        elif goal == OnboardingGoal.ARTICLE:
            # Article uses same workflow as LinkedIn but different params
            return self._build_linkedin_payload(
                session_id, trace_id, snapshot, dry_run, requested_provider,
                is_article=True
            )
        else:
            raise ValueError(f"Unsupported goal: {goal}")
    
    def _build_linkedin_payload(
        self,
        session_id: UUID,
        trace_id: str,
        snapshot: CompanySnapshot,
        dry_run: bool,
        requested_provider: Optional[str],
        is_article: bool = False,
    ) -> CgsPayloadLinkedInPost:
        """Build LinkedIn post payload."""
        
        # Extract topic from answers or infer from company
        topic = self._extract_topic(snapshot)
        
        # Extract target audience
        target_audience = snapshot.audience.primary or "Business professionals"
        
        # Extract tone
        tone = snapshot.voice.tone or "professional"
        
        # Extract word count from answers
        target_word_count = self._extract_word_count(snapshot, default=300 if not is_article else 800)
        
        # Build context from company description
        context = self._build_context(snapshot)
        
        # Extract key points
        key_points = snapshot.company.differentiators[:3] if snapshot.company.differentiators else []
        
        # Extract hashtags from company info
        hashtags = self._generate_hashtags(snapshot)
        
        # Check if user wants statistics
        include_statistics = self._extract_boolean_answer(snapshot, "statistic", default=True)
        include_examples = self._extract_boolean_answer(snapshot, "example", default=True)
        include_sources = self._extract_boolean_answer(snapshot, "source", default=True)
        
        # Build custom instructions
        custom_instructions = self._build_custom_instructions(snapshot)
        
        # Determine post format
        post_format = "thought_leadership" if not is_article else "article"
        
        # Build input
        linkedin_input = LinkedInPostInput(
            topic=topic,
            client_name=snapshot.company.name,
            client_profile="default",
            target_audience=target_audience,
            tone=tone,
            context=context,
            key_points=key_points,
            hashtags=hashtags,
            target_word_count=target_word_count,
            include_statistics=include_statistics,
            include_examples=include_examples,
            include_sources=include_sources,
            custom_instructions=custom_instructions,
            post_format=post_format,
        )
        
        # Build metadata
        metadata = CgsPayloadMetadata(
            source="onboarding_adapter",
            dry_run=dry_run,
            requested_provider=requested_provider,
            language="it",
        )
        
        # Build payload
        payload = CgsPayloadLinkedInPost(
            session_id=session_id,
            trace_id=trace_id,
            company_snapshot=snapshot,
            clarifying_answers=snapshot.clarifying_answers,
            input=linkedin_input,
            metadata=metadata,
        )
        
        logger.info(f"LinkedIn payload built: topic='{topic}', word_count={target_word_count}")
        
        return payload
    
    def _build_newsletter_payload(
        self,
        session_id: UUID,
        trace_id: str,
        snapshot: CompanySnapshot,
        dry_run: bool,
        requested_provider: Optional[str],
    ) -> CgsPayloadNewsletter:
        """Build newsletter payload."""
        
        # Extract topic
        topic = self._extract_topic(snapshot)
        newsletter_topic = topic  # Can be refined
        
        # Extract target audience
        target_audience = snapshot.audience.primary or "Business professionals"
        
        # Extract word count
        target_word_count = self._extract_word_count(snapshot, default=1200)
        
        # Extract premium sources from answers or company info
        premium_sources = self._extract_premium_sources(snapshot)
        
        # Build custom instructions
        custom_instructions = self._build_custom_instructions(snapshot)
        
        # Build input
        newsletter_input = NewsletterInput(
            topic=topic,
            newsletter_topic=newsletter_topic,
            client_name=snapshot.company.name,
            client_profile="default",
            target_audience=target_audience,
            target_word_count=target_word_count,
            premium_sources=premium_sources,
            custom_instructions=custom_instructions,
        )
        
        # Build metadata
        metadata = CgsPayloadMetadata(
            source="onboarding_adapter",
            dry_run=dry_run,
            requested_provider=requested_provider,
            language="it",
        )
        
        # Build payload
        payload = CgsPayloadNewsletter(
            session_id=session_id,
            trace_id=trace_id,
            company_snapshot=snapshot,
            clarifying_answers=snapshot.clarifying_answers,
            input=newsletter_input,
            metadata=metadata,
        )
        
        logger.info(f"Newsletter payload built: topic='{topic}', word_count={target_word_count}")
        
        return payload
    
    def _extract_topic(self, snapshot: CompanySnapshot) -> str:
        """Extract topic from answers or infer from company."""
        # Check answers for topic-related questions
        for q_id, answer in snapshot.clarifying_answers.items():
            question = next((q for q in snapshot.clarifying_questions if q.id == q_id), None)
            if question and "topic" in question.question.lower():
                return str(answer)
            if question and "focus" in question.question.lower():
                return str(answer)
        
        # Infer from company offerings
        if snapshot.company.key_offerings:
            return f"{snapshot.company.key_offerings[0]} for {snapshot.audience.primary or 'businesses'}"
        
        # Fallback to company description
        return snapshot.company.description[:100]
    
    def _extract_word_count(self, snapshot: CompanySnapshot, default: int) -> int:
        """Extract word count from answers."""
        for q_id, answer in snapshot.clarifying_answers.items():
            question = next((q for q in snapshot.clarifying_questions if q.id == q_id), None)
            if question and "length" in question.question.lower():
                # Parse answer like "medium (400-600 words)"
                answer_str = str(answer).lower()
                if "short" in answer_str:
                    return 250
                elif "medium" in answer_str:
                    return 500
                elif "long" in answer_str:
                    return 1000
                # Try to extract number
                import re
                numbers = re.findall(r'\d+', answer_str)
                if numbers:
                    return int(numbers[0])
        
        return default
    
    def _extract_boolean_answer(
        self, snapshot: CompanySnapshot, keyword: str, default: bool
    ) -> bool:
        """Extract boolean answer from questions containing keyword."""
        for q_id, answer in snapshot.clarifying_answers.items():
            question = next((q for q in snapshot.clarifying_questions if q.id == q_id), None)
            if question and keyword in question.question.lower():
                if isinstance(answer, bool):
                    return answer
                # Parse string answers
                answer_str = str(answer).lower()
                return answer_str in {"yes", "true", "si", "sì", "1"}
        
        return default
    
    def _build_context(self, snapshot: CompanySnapshot) -> str:
        """Build context string from snapshot."""
        parts = [snapshot.company.description]
        
        if snapshot.company.key_offerings:
            parts.append(f"Key offerings: {', '.join(snapshot.company.key_offerings[:3])}")
        
        if snapshot.insights.positioning:
            parts.append(f"Positioning: {snapshot.insights.positioning}")
        
        return " | ".join(parts)
    
    def _generate_hashtags(self, snapshot: CompanySnapshot) -> List[str]:
        """Generate hashtags from company info."""
        hashtags = []
        
        # From industry
        if snapshot.company.industry:
            # Clean industry name for hashtag
            industry_tag = snapshot.company.industry.replace("/", "").replace(" ", "")
            hashtags.append(industry_tag)
        
        # From key offerings (first 2)
        for offering in snapshot.company.key_offerings[:2]:
            tag = offering.replace(" ", "").replace("-", "")[:20]
            hashtags.append(tag)
        
        # Limit to 5 hashtags
        return hashtags[:5]
    
    def _build_custom_instructions(self, snapshot: CompanySnapshot) -> str:
        """Build custom instructions from snapshot."""
        instructions = []
        
        # Voice guidelines
        if snapshot.voice.style_guidelines:
            instructions.append(f"Style: {', '.join(snapshot.voice.style_guidelines[:2])}")
        
        # Key messages
        if snapshot.insights.key_messages:
            instructions.append(f"Key messages: {', '.join(snapshot.insights.key_messages[:2])}")
        
        # Forbidden phrases
        if snapshot.voice.forbidden_phrases:
            instructions.append(f"Avoid: {', '.join(snapshot.voice.forbidden_phrases)}")
        
        return " | ".join(instructions) if instructions else None
    
    def _extract_premium_sources(self, snapshot: CompanySnapshot) -> List[str]:
        """Extract premium sources for newsletter."""
        sources = []
        
        # From recent news
        if snapshot.insights.recent_news:
            sources.extend(snapshot.insights.recent_news[:3])
        
        # From evidence sources
        for evidence in snapshot.company.evidence[:3]:
            if evidence.source and evidence.source not in sources:
                sources.append(evidence.source)
        
        return sources[:5]

