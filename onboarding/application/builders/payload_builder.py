"""Payload builder for constructing CGS payloads from snapshots.

Intelligent mapping from CompanySnapshot + answers to CGS input parameters.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from onboarding.domain.models import CompanySnapshot, OnboardingGoal
from onboarding.domain.cgs_contracts import (
    CgsPayloadLinkedInPost,
    CgsPayloadNewsletter,
    CgsPayloadOnboardingContent,
    LinkedInPostInput,
    NewsletterInput,
    OnboardingContentInput,
    CgsPayloadMetadata,
)
from onboarding.domain.content_types import build_content_config
from onboarding.config.settings import get_onboarding_settings

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
    ) -> CgsPayloadOnboardingContent | CgsPayloadLinkedInPost | CgsPayloadNewsletter:
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
            CgsPayload (Unified Onboarding Content, LinkedIn, or Newsletter)
        """
        logger.info(f"Building payload for goal: {goal}")

        # NEW: Analytics workflow
        if goal == OnboardingGoal.COMPANY_ANALYTICS:
            return self._build_analytics_payload(
                session_id, trace_id, snapshot, goal, dry_run, requested_provider
            )

        # Unified onboarding content workflow for content goals
        elif goal in {
            OnboardingGoal.LINKEDIN_POST,
            OnboardingGoal.LINKEDIN_ARTICLE,
            OnboardingGoal.BLOG_POST,
            OnboardingGoal.NEWSLETTER,
            OnboardingGoal.NEWSLETTER_PREMIUM,
            OnboardingGoal.ARTICLE,
        }:
            return self._build_onboarding_content_payload(
                session_id, trace_id, snapshot, goal, dry_run, requested_provider
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
            client_profile="onboarding",  # Use generic onboarding profile
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
            requested_provider=requested_provider or "gemini",  # Default: Gemini Pro 2.5
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
            client_profile="onboarding",  # Use generic onboarding profile
            target_audience=target_audience,
            target_word_count=target_word_count,
            premium_sources=premium_sources,
            custom_instructions=custom_instructions,
        )

        # Build metadata
        metadata = CgsPayloadMetadata(
            source="onboarding_adapter",
            dry_run=dry_run,
            requested_provider=requested_provider or "gemini",  # Default: Gemini Pro 2.5
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

    # ========================================================================
    # NEW: Unified Onboarding Content Payload Builder
    # ========================================================================

    def _build_onboarding_content_payload(
        self,
        session_id: UUID,
        trace_id: str,
        snapshot: CompanySnapshot,
        goal: OnboardingGoal,
        dry_run: bool,
        requested_provider: Optional[str],
    ) -> CgsPayloadOnboardingContent:
        """
        Build unified onboarding content payload.

        This method builds a single unified payload that works for all content types
        via the onboarding_content_generator workflow.
        """
        logger.info(f"Building unified onboarding content payload for goal: {goal}")

        # Get settings
        settings = get_onboarding_settings()

        # Determine content type from goal
        content_type = settings.get_content_type(goal.value)

        logger.info(f"Mapped goal '{goal.value}' to content_type '{content_type}'")

        # Extract topic from answers
        topic = self._extract_topic(snapshot)

        # Extract target audience
        target_audience = snapshot.audience.primary or "Business professionals"

        # Extract tone
        tone = snapshot.voice.tone or "professional"

        # Build context string
        context = self._build_context(snapshot)

        # Build content config based on content type
        custom_params = self._extract_content_config_from_answers(snapshot, content_type)
        content_config = build_content_config(content_type, custom_params)

        # Build custom instructions
        custom_instructions = self._build_custom_instructions(snapshot, content_type)

        # Build unified input
        onboarding_input = OnboardingContentInput(
            content_type=content_type,
            topic=topic,
            client_name=snapshot.company.name,
            client_profile="onboarding",
            target_audience=target_audience,
            tone=tone,
            context=context,
            content_config=content_config,
            custom_instructions=custom_instructions,
        )

        # Build metadata
        metadata = CgsPayloadMetadata(
            source="onboarding_adapter",
            dry_run=dry_run,
            requested_provider=requested_provider or "gemini",
            language="it",
        )

        # Build payload
        payload = CgsPayloadOnboardingContent(
            session_id=session_id,
            trace_id=trace_id,
            workflow="onboarding_content_generator",
            goal=goal.value,
            company_snapshot=snapshot,
            clarifying_answers=snapshot.clarifying_answers,
            input=onboarding_input,
            metadata=metadata,
        )

        logger.info(
            f"Onboarding content payload built: "
            f"content_type={content_type}, topic='{topic}', "
            f"word_count={content_config.get('word_count')}"
        )

        return payload

    def _extract_content_config_from_answers(
        self, snapshot: CompanySnapshot, content_type: str
    ) -> Dict[str, Any]:
        """Extract content-specific config from clarifying answers."""

        custom_params = {}
        answers = snapshot.clarifying_answers

        # Extract word count if specified
        word_count = self._extract_word_count(snapshot, default=None)
        if word_count:
            custom_params["word_count"] = word_count

        # Content type specific extractions
        if content_type == "linkedin_post":
            # Check if user wants emoji/hashtags
            custom_params["include_emoji"] = self._extract_boolean_answer(
                snapshot, "emoji", default=True
            )
            custom_params["include_hashtags"] = self._extract_boolean_answer(
                snapshot, "hashtag", default=True
            )

        elif content_type == "linkedin_article":
            # Check if user wants statistics/examples
            custom_params["include_statistics"] = self._extract_boolean_answer(
                snapshot, "statistic", default=True
            )
            custom_params["include_examples"] = self._extract_boolean_answer(
                snapshot, "example", default=True
            )

        elif content_type == "newsletter":
            # Check number of sections
            num_sections = self._extract_number_answer(snapshot, "section", default=4)
            custom_params["num_sections"] = num_sections

        elif content_type == "blog_post":
            # Check if SEO optimized
            custom_params["seo_optimized"] = self._extract_boolean_answer(
                snapshot, "seo", default=True
            )

        return custom_params

    def _build_custom_instructions(
        self, snapshot: CompanySnapshot, content_type: str
    ) -> Optional[str]:
        """Build custom instructions from snapshot and content type."""

        instructions = []

        # Add differentiators if available
        if snapshot.company.differentiators:
            diff_text = ", ".join(snapshot.company.differentiators[:3])
            instructions.append(f"Highlight these differentiators: {diff_text}")

        # Add pain points if available
        if snapshot.audience.pain_points:
            pain_text = ", ".join(snapshot.audience.pain_points[:2])
            instructions.append(f"Address these pain points: {pain_text}")

        # Add style guidelines if available
        if snapshot.voice.style_guidelines:
            style_text = ", ".join(snapshot.voice.style_guidelines[:2])
            instructions.append(f"Follow these style guidelines: {style_text}")

        # Content type specific instructions
        if content_type == "linkedin_post":
            instructions.append("Focus on engagement and virality")
        elif content_type == "linkedin_article":
            instructions.append("Establish thought leadership and expertise")
        elif content_type == "newsletter":
            instructions.append("Provide curated, actionable insights")
        elif content_type == "blog_post":
            instructions.append("Optimize for search engines and comprehensive value")

        return " | ".join(instructions) if instructions else None

    def _extract_boolean_answer(
        self, snapshot: CompanySnapshot, keyword: str, default: bool = True
    ) -> bool:
        """Extract boolean answer from clarifying answers."""

        answers = snapshot.clarifying_answers

        # Search for keyword in answers
        for question_id, answer in answers.items():
            if keyword.lower() in question_id.lower():
                if isinstance(answer, bool):
                    return answer
                if isinstance(answer, str):
                    return answer.lower() in {"yes", "true", "si", "sì"}

        return default

    def _extract_number_answer(
        self, snapshot: CompanySnapshot, keyword: str, default: int
    ) -> int:
        """Extract number answer from clarifying answers."""

        answers = snapshot.clarifying_answers

        # Search for keyword in answers
        for question_id, answer in answers.items():
            if keyword.lower() in question_id.lower():
                if isinstance(answer, int):
                    return answer
                if isinstance(answer, str):
                    try:
                        return int(answer)
                    except ValueError:
                        pass

        return default

    def _build_analytics_payload(
        self,
        session_id: UUID,
        trace_id: str,
        snapshot: CompanySnapshot,
        goal: OnboardingGoal,
        dry_run: bool,
        requested_provider: Optional[str],
    ) -> CgsPayloadOnboardingContent:
        """
        Build analytics payload for company_analytics goal.

        Uses generic variables instead of content-specific questions.
        """
        settings = get_onboarding_settings()

        # Extract generic variables from clarifying answers
        variables = self._extract_analytics_variables(snapshot)

        # Build rich context with company snapshot + variables
        rich_context = {
            "company_snapshot": snapshot.model_dump(),
            "variables": variables,
        }

        # Build metadata
        metadata = CgsPayloadMetadata(
            source="onboarding_adapter",
            dry_run=dry_run,
            requested_provider=requested_provider or "gemini",
            language="it",
        )

        # Build analytics input
        # Note: context must be a JSON string, not a dict
        analytics_input = OnboardingContentInput(
            topic=f"Company analytics for {snapshot.company.name}",
            client_name=snapshot.company.name,
            context=json.dumps(rich_context, default=str),  # Convert dict to JSON string
            content_type="analytics",  # Special type for analytics
            content_config={},  # No content config needed for analytics
        )

        # Determine provider
        provider = requested_provider or settings.default_llm_provider

        # Build payload with all required fields
        payload = CgsPayloadOnboardingContent(
            session_id=session_id,
            goal=goal.value,  # Convert enum to string
            workflow="onboarding_analytics_generator",
            company_snapshot=snapshot,
            clarifying_answers=snapshot.clarifying_answers,
            input=analytics_input,
            metadata=metadata,
            trace_id=trace_id,
        )

        logger.info(
            f"✅ Built analytics payload: {snapshot.company.name}, "
            f"variables={len(variables)}, provider={provider}"
        )

        return payload

    def _extract_analytics_variables(self, snapshot: CompanySnapshot) -> Dict[str, str]:
        """
        Extract generic variables from clarifying answers.

        Maps specific questions to generic variable_1, variable_2, etc.
        """
        answers = snapshot.clarifying_answers

        variables = {}

        # Try to map answers to generic variables
        # Variable 1: Business Objective
        for key in ["objective", "goal", "business_objective", "primary_goal"]:
            if key in answers:
                variables["variable_1"] = str(answers[key])
                break

        # Variable 2: Target Market
        for key in ["market", "target_market", "audience", "target_audience"]:
            if key in answers:
                variables["variable_2"] = str(answers[key])
                break

        # Variable 3: Biggest Challenge
        for key in ["challenge", "biggest_challenge", "pain_point", "problem"]:
            if key in answers:
                variables["variable_3"] = str(answers[key])
                break

        # Variable 4: Unique Value
        for key in ["unique_value", "differentiator", "unique", "value_proposition"]:
            if key in answers:
                variables["variable_4"] = str(answers[key])
                break

        # Fallback: Use first 4 answers if no matches
        if not variables:
            answer_list = list(answers.items())
            for i, (key, value) in enumerate(answer_list[:4], start=1):
                variables[f"variable_{i}"] = str(value)

        logger.info(f"📊 Extracted {len(variables)} analytics variables")

        return variables

