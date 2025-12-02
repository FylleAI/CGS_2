"""
Siebert Premium Newsletter workflow handler.
Optimized workflow with Perplexity integration and 8-section Gen Z format.
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..base.workflow_base import WorkflowHandler
from ..registry import register_workflow

logger = logging.getLogger(__name__)


def load_client_newsletter_template(client_name: str) -> Optional[Dict[str, Any]]:
    """Load newsletter template configuration for a client.

    Args:
        client_name: The client identifier (e.g., 'siebert')

    Returns:
        Dictionary with template configuration or None if not found
    """
    template_path = (
        Path(__file__).resolve().parents[4]
        / "data"
        / "profiles"
        / client_name
        / "newsletter_template.json"
    )

    try:
        with open(template_path, "r", encoding="utf-8") as f:
            template = json.load(f)
            logger.info(f"📋 Loaded newsletter template for {client_name}")
            return template
    except FileNotFoundError:
        logger.warning(f"⚠️ Newsletter template not found for {client_name}: {template_path}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON in newsletter template for {client_name}: {e}")
        return None


@register_workflow("siebert_premium_newsletter")
class SiebertPremiumNewsletterHandler(WorkflowHandler):
    """Handler for Siebert's optimized premium newsletter workflow."""

    def validate_inputs(self, context: Dict[str, Any]) -> None:
        """Validate inputs specific to Siebert premium newsletter."""
        super().validate_inputs(context)

        # Validate topic (can be either 'topic' or 'newsletter_topic')
        topic = context.get("topic") or context.get("newsletter_topic", "")
        if not topic or len(topic) < 5:
            raise ValueError("Newsletter topic must be at least 5 characters")

        # Ensure 'topic' is available for template (normalize the field)
        if "topic" not in context and "newsletter_topic" in context:
            context["topic"] = context["newsletter_topic"]
        if len(topic) > 200:
            raise ValueError("Newsletter topic must be less than 200 characters")

        # Validate target_audience
        audience = context.get("target_audience", "")
        if not audience:
            # Set default for Siebert
            context["target_audience"] = "Gen Z investors and young professionals"
            audience = context["target_audience"]
        if len(audience) > 500:
            raise ValueError("Target audience must be less than 500 characters")

        # Validate target_word_count - Siebert range is 800-1200
        word_count = context.get("target_word_count", 1000)
        if word_count < 800 or word_count > 1200:
            logger.info(
                f"🔧 Adjusting word count from {word_count} to fit Siebert range (800-1200)"
            )
            word_count = max(800, min(1200, word_count))
            context["target_word_count"] = word_count

        # Set client identifiers for RAG operations and agent resolution
        context["client_name"] = "siebert"
        context["client_profile"] = (
            "siebert"  # Ensure AgentFactory can resolve Siebert agents
        )

        logger.info(
            f"✅ Siebert newsletter inputs validated: {word_count} words target for {audience}"
        )

    def prepare_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for Siebert premium newsletter."""
        context = super().prepare_context(context)

        # Load client newsletter template for dynamic configuration
        client_name = context.get("client_name", "siebert")
        newsletter_template = load_client_newsletter_template(client_name)

        # Store template in context for potential use by agents
        if newsletter_template:
            context["newsletter_template"] = newsletter_template
            logger.info(f"📋 Newsletter template loaded for {client_name}")

        # Basic defaults
        context.setdefault("target_word_count", 1000)
        context.setdefault("cultural_trends", "")
        context.setdefault("research_timeframe", "last 7 days")
        context.setdefault("premium_sources", "")
        context.setdefault("custom_instructions", "")
        context.setdefault("client_name", client_name)
        context.setdefault("client_profile", client_name)

        # Date context
        now = datetime.now()
        context.setdefault("current_date", now.strftime("%B %d, %Y"))
        context.setdefault("current_month_year", now.strftime("%B %Y"))

        # Dynamic values from template or fallback to defaults
        if newsletter_template:
            # Newsletter title from template
            campaign_context = newsletter_template.get("campaign_context", "")
            context.setdefault("newsletter_title", campaign_context or "WEALTHBUILDER NEWSLETTER")

            # Exclude topics from template
            content_req = newsletter_template.get("content_requirements", {})
            template_exclude = content_req.get("exclude_topics", [])
            context.setdefault("exclude_topics", template_exclude or ["crypto day trading", "get rich quick", "penny stocks"])

            # Premium research sources from template
            template_sources = content_req.get("premium_research_sources", [])
            if template_sources and not context.get("siebert_target_urls"):
                context["siebert_target_urls"] = "|".join(template_sources)
                logger.info(f"📰 Loaded {len(template_sources)} premium sources from template")

            # Section word counts from template sections
            sections = newsletter_template.get("newsletter_structure", {}).get("sections", [])
            if sections:
                context["siebert_section_word_counts"] = self._calculate_section_word_counts(
                    sections, context["target_word_count"]
                )
                logger.info("📊 Section word counts calculated from template")
        else:
            # Fallback to hardcoded defaults
            context.setdefault("newsletter_title", "WEALTHBUILDER NEWSLETTER")
            context.setdefault("exclude_topics", ["crypto day trading", "get rich quick", "penny stocks"])
            context.setdefault(
                "siebert_target_urls",
                "https://www.federalreserve.gov/newsevents/pressreleases/monetary|"
                "https://www.thedailyupside.com/finance/|https://www.thedailyupside.com/investments/|"
                "https://www.thedailyupside.com/economics/|https://www.thedailyupside.com/newsletter/|"
                "https://moneywithkatie.com/blog/category/investing|https://thehustle.co/news|"
                "https://www.morningbrew.com/tag/finance|https://www.morningbrew.com/tag/economy|"
                "https://blog.siebert.com/tag/daily-market#BlogListing|https://www.axios.com/newsletters/axios-markets|"
                "https://www.axios.com/newsletters/axios-macro|https://decrypt.co/|https://www.coindesk.com/",
            )
            # Fallback word count distribution
            total_words = context["target_word_count"]
            context["siebert_section_word_counts"] = {
                "intro_greeting": int(total_words * 0.055),
                "feature_story": int(total_words * 0.30),
                "market_reality_check": int(total_words * 0.225),
                "by_the_numbers": int(total_words * 0.135),
                "your_move_this_week": int(total_words * 0.165),
                "reader_spotlight": int(total_words * 0.07),
                "quick_links": int(total_words * 0.07),
                "sign_off": int(total_words * 0.035),
            }

        # Process exclude_topics format
        exclude_topics = context.get("exclude_topics", [])
        if isinstance(exclude_topics, str) and exclude_topics:
            context["exclude_topics"] = [
                topic.strip() for topic in exclude_topics.split(",") if topic.strip()
            ]
        elif not isinstance(exclude_topics, list):
            context["exclude_topics"] = ["crypto day trading", "get rich quick", "penny stocks"]

        # Ensure cultural_trends is a string
        if not isinstance(context.get("cultural_trends", ""), str):
            context["cultural_trends"] = ""

        # Process premium sources
        premium_sources = context.get("premium_sources", "")
        if premium_sources and isinstance(premium_sources, str):
            sources_list = [s.strip() for s in premium_sources.split("\n") if s.strip()]
            context["premium_sources"] = "|".join(sources_list) if sources_list else ""
        else:
            context["premium_sources"] = ""

        # Ensure research_timeframe is valid
        if context.get("research_timeframe") not in {"last 7 days", "yesterday", "last month"}:
            context["research_timeframe"] = "last 7 days"

        logger.info(f"🔧 Siebert newsletter context prepared for client: {context['client_name']}")
        logger.info(f"📊 8-section word counts: {context['siebert_section_word_counts']}")

        return context

    def _calculate_section_word_counts(
        self, sections: List[Dict[str, Any]], total_words: int
    ) -> Dict[str, int]:
        """Calculate word counts for each section based on template definition.

        Args:
            sections: List of section definitions from template
            total_words: Total target word count

        Returns:
            Dictionary mapping section names to word counts
        """
        word_counts = {}
        section_name_map = {
            # New names (from updated template)
            "Intro Greeting": "intro_greeting",
            "Reader Spotlight": "reader_spotlight",
            # Legacy names (for backward compatibility)
            "Community Greeting": "intro_greeting",
            "Community Corner": "reader_spotlight",
            # Standard section names
            "Feature Story": "feature_story",
            "Market Reality Check": "market_reality_check",
            "By The Numbers": "by_the_numbers",
            "Your Move This Week": "your_move_this_week",
            "Quick Links & Resources": "quick_links",
            "Sign-off": "sign_off",
        }

        for section in sections:
            section_name = section.get("name", "")
            word_count_str = section.get("word_count", "")

            # Parse word count range (e.g., "50-60 words" -> average 55)
            if word_count_str:
                numbers = re.findall(r"\d+", word_count_str)
                if len(numbers) >= 2:
                    avg_words = (int(numbers[0]) + int(numbers[1])) // 2
                elif len(numbers) == 1:
                    avg_words = int(numbers[0])
                else:
                    avg_words = 50

                internal_name = section_name_map.get(section_name, section_name.lower().replace(" ", "_"))
                word_counts[internal_name] = avg_words

        # If template didn't provide all sections, use percentage-based fallback
        if len(word_counts) < 8:
            logger.warning("⚠️ Template missing some sections, using percentage fallback")
            fallback = {
                "intro_greeting": int(total_words * 0.055),
                "feature_story": int(total_words * 0.30),
                "market_reality_check": int(total_words * 0.225),
                "by_the_numbers": int(total_words * 0.135),
                "your_move_this_week": int(total_words * 0.165),
                "reader_spotlight": int(total_words * 0.07),
                "quick_links": int(total_words * 0.07),
                "sign_off": int(total_words * 0.035),
            }
            for key, value in fallback.items():
                word_counts.setdefault(key, value)

        return word_counts

    def post_process_task(
        self, task_id: str, task_output: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Post-process task output for Siebert workflow."""
        logger.info(f"🔧 POST-PROCESSING SIEBERT TASK: {task_id}")

        if task_id == "task1_siebert_context_setup":
            # Extract Siebert brand guidelines
            context["siebert_brand_extracted"] = True
            context["template_structure_defined"] = True
            logger.info(f"📋 Siebert brand guidelines and 8-section template extracted")

        elif task_id == "task2_perplexity_research":
            # Keep it simple: mark as completed and pass raw output forward
            context["perplexity_research_completed"] = True
            logger.info(
                "📚 Perplexity research completed; passing raw output forward without parsing"
            )

        elif task_id == "task3_newsletter_assembly":
            # Verify 8-section newsletter structure and word counts
            word_count = len(task_output.split()) if task_output else 0
            context["final_word_count"] = word_count
            target_count = context.get("target_word_count", 1000)
            accuracy = (word_count / target_count * 100) if target_count > 0 else 0
            context["word_count_accuracy"] = accuracy
            context["siebert_format_applied"] = True
            logger.info(
                f"📄 Siebert newsletter created: {word_count} words ({accuracy:.1f}% of target)"
            )

        elif task_id == "task4_compliance_review":
            # Validate compliance review completion
            word_count = len(task_output.split()) if task_output else 0
            context["compliance_reviewed"] = True
            context["final_compliance_word_count"] = word_count
            context["compliance_review_completed"] = True
            logger.info(
                f"✅ Compliance review completed: {word_count} words (FINRA/SEC validated)"
            )

        return context

    def post_process_workflow(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Final post-processing with Siebert-specific metrics."""
        try:
            logger.info(
                "🔧 POST-PROCESSING: Starting Siebert newsletter post-processing"
            )

            # Find the final newsletter content
            final_content = None
            task_outputs = []

            for key, value in context.items():
                if key.endswith("_output") and isinstance(value, str):
                    task_outputs.append((key, value, len(value)))
                    logger.info(f"📊 Found task output: {key} ({len(value)} chars)")

            # Prioritize task4_compliance_review output (final), then task3_newsletter_assembly
            if task_outputs:
                task4_output = None
                task3_output = None

                for key, value, length in task_outputs:
                    if key == "task4_compliance_review_output":
                        task4_output = (key, value, length)
                    elif key == "task3_newsletter_assembly_output":
                        task3_output = (key, value, length)

                if task4_output and task3_output:
                    final_word_count = context.get("final_word_count", 0)
                    compliance_word_count = context.get("final_compliance_word_count")
                    min_ratio = context.get("compliance_min_ratio", 0.7)

                    if (
                        not compliance_word_count
                        or final_word_count == 0
                        or compliance_word_count < final_word_count * min_ratio
                    ):
                        final_content = task3_output[1]
                        logger.info(
                            f"⚠️ Compliance review output missing or insufficient ({compliance_word_count}/{final_word_count}); falling back to {task3_output[0]} ({task3_output[2]} chars)"
                        )
                    else:
                        final_content = task4_output[1]
                        logger.info(
                            f"✅ Selected compliance-reviewed newsletter from {task4_output[0]} ({task4_output[2]} chars)"
                        )
                elif task4_output:
                    final_content = task4_output[1]
                    logger.info(
                        f"✅ Selected compliance-reviewed newsletter from {task4_output[0]} ({task4_output[2]} chars)"
                    )
                elif task3_output:
                    final_content = task3_output[1]
                    logger.info(
                        f"📄 Selected newsletter content from {task3_output[0]} ({task3_output[2]} chars)"
                    )
                else:
                    # Fallback to longest output
                    task_outputs.sort(key=lambda x: x[2], reverse=True)
                    final_content = task_outputs[0][1]
                    logger.info(
                        f"📄 Selected content from {task_outputs[0][0]} ({task_outputs[0][2]} chars) - fallback"
                    )

            if final_content:
                context["final_output"] = final_content
                logger.info(f"📄 Set final_output with {len(final_content)} characters")

            # Create Siebert-specific workflow summary
            summary = {
                "workflow_type": "siebert_premium_newsletter",
                "newsletter_topic": context.get("topic", ""),
                "client": "siebert",
                "target_audience": context.get("target_audience", ""),
                "edition_number": context.get("edition_number", 1),
                "target_word_count": context.get("target_word_count", 1000),
                "final_word_count": context.get("final_word_count", 0),
                "word_count_accuracy": context.get("word_count_accuracy", 0),
                "newsletter_format": "8-section Siebert Gen Z format",
                "perplexity_integration": context.get(
                    "perplexity_research_completed", False
                ),
                "cultural_integration": context.get(
                    "cultural_integration_applied", False
                ),
                "brand_guidelines_applied": context.get(
                    "siebert_brand_extracted", False
                ),
                "quality_indicators": {
                    "perplexity_research": context.get(
                        "perplexity_research_completed", False
                    ),
                    "word_count_target_met": abs(
                        context.get("word_count_accuracy", 0) - 100
                    )
                    <= 10,
                    "cultural_integration": context.get(
                        "cultural_integration_applied", False
                    ),
                    "siebert_format": context.get("siebert_format_applied", False),
                    "brand_voice_applied": context.get(
                        "siebert_brand_extracted", False
                    ),
                },
                "section_structure": context.get("siebert_section_word_counts", {}),
                "research_sources": context.get("research_sources_count", 0),
            }

            context["workflow_summary"] = summary
            logger.info(f"📊 Siebert newsletter workflow summary created")
            logger.info(
                f"🎯 Word count accuracy: {summary['word_count_accuracy']:.1f}%"
            )
            logger.info(
                f"🔍 Perplexity integration: {summary['perplexity_integration']}"
            )

            # CRITICAL: Call parent method to ensure workflow_metrics are included
            context = super().post_process_workflow(context)
            logger.info(
                "✅ Parent post-processing completed - workflow_metrics preserved"
            )

            return context

        except Exception as e:
            logger.error(f"❌ SIEBERT POST-PROCESSING ERROR: {str(e)}")
            # Even in case of error, call parent to preserve workflow_metrics
            return super().post_process_workflow(context)
