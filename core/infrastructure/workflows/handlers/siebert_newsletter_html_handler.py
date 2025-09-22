"""Siebert newsletter workflow with HTML email output."""

import logging
import re
from datetime import datetime
from typing import Any, Dict, List

from ..base.workflow_base import WorkflowHandler
from ..registry import register_workflow

logger = logging.getLogger(__name__)

HTML_DESIGN_SYSTEM_INSTRUCTIONS = """
HARD RULES — FOLLOW EXACTLY:
- Output exactly one root <div> container (no <html>, <head>, <body>, <style>, <script> tags)
- The root container must include style="max-width: 600px; margin: 0 auto; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;"
- Use ONLY inline styles; classes, ids, style blocks, external CSS, gradients, opacity > 0 are forbidden
- Preserve every emoji, URL, citation, and piece of copy from the approved markdown verbatim
- Never introduce em dashes — replace with hyphen if they appear in the source (already enforced upstream)

LAYOUT MAP (8 sections, in order):
1. Header: dark background (#1a1a1a), white bold greeting (24px), intro copy in #e0e0e0
2. Topic Sections (Feature Story, Market Reality Check, etc.): section headers with background #1a1a1a, text #4ade80, font-size 18px, padding 12px 20px, border-radius 8px
3. Key Numbers Grid: implement with table for email compatibility — 2 columns desktop, graceful stacking on mobile; background #4ade80, dark text, 20px padding, generous spacing between rows
4. Expert Insights (Quote): light box (#f1f5f9) with 4px solid #4ade80 left border, 20px padding, italicized quote text
5. Action Items: light green background (#f0fdf4) with #4ade80 border, inline-styled checkmark (✅) positioned via relative container and left padding (simulate absolute positioning safely)
6. Community Section: lavender background (#fef7ff) with #d8b4fe border, 25px padding
7. Quick Hits/Links: bullet list with green bullet character (•) and padding-left 15px; links colored #4ade80, no underline
8. Footer with P.S.: dark background (#1a1a1a), white text centered, top border #333 on P.S. block

ACCESSIBILITY & MOBILE-FIRST:
- Favor simple tables for multi-column layouts; avoid nested tables when unnecessary
- Use padding and margin inline styles to create breathing room; default to 16px for vertical rhythm, 20-24px for primary sections
- Links: color #4ade80; no underline (email clients rarely support hover styles)
- Ensure text contrast meets WCAG AA; do not lighten mandated colors

DO / DON'T:
DO:
- Maintain semantic structure with headings (use <h1>/<h2>/<h3> only when absolutely needed, otherwise styled <p> tags)
- Use <table> for the numbers grid and for any horizontal layout that must stay aligned across clients
- Include alt attributes on images (if any appear)
- Finish with an HTML comment named <!-- QUALITY CHECKLIST --> listing pass/fail for: root-container, inline-styles, banned-tags, color-palette, links-intact, citations-intact

DON'T:
- Use <html>, <head>, <body>, <style>, <script>, classes, ids, gradients, opacity attributes
- Wrap content in additional outer containers beyond the single root <div>
- Modify or remove citations, URLs, emojis, or editorial formatting from the approved markdown

VALIDATION TARGETS:
- Regex enforcement expects the output to contain "max-width: 600px"
- No banned tags/attributes: <html, <head, <body, <style, <script, class=, id=
- Links must remain full http(s) URLs
- Citations/parenthetical references must match the compliance-approved markdown exactly
"""


@register_workflow("siebert_newsletter_html")
class SiebertNewsletterHtmlHandler(WorkflowHandler):
    """Handler for Siebert's HTML email newsletter workflow."""

    banned_pattern = re.compile(r"<(?:html|head|body|style|script)\b", re.IGNORECASE)
    forbidden_attributes = re.compile(r"\b(?:class|id)\s*=", re.IGNORECASE)

    def validate_inputs(self, context: Dict[str, Any]) -> None:
        """Validate base newsletter inputs (topic, word count, audience)."""
        super().validate_inputs(context)

        topic = context.get("topic") or context.get("newsletter_topic", "")
        if not topic or len(topic) < 5:
            raise ValueError("Newsletter topic must be at least 5 characters")
        if len(topic) > 200:
            raise ValueError("Newsletter topic must be less than 200 characters")
        if "topic" not in context and "newsletter_topic" in context:
            context["topic"] = context["newsletter_topic"]

        audience = context.get("target_audience", "")
        if not audience:
            context["target_audience"] = "Gen Z investors and young professionals"
            audience = context["target_audience"]
        if len(audience) > 500:
            raise ValueError("Target audience must be less than 500 characters")

        word_count = context.get("target_word_count", 1000)
        if word_count < 800 or word_count > 1200:
            logger.info(
                "🔧 Adjusting word count from %s to Siebert range (800-1200)",
                word_count,
            )
            word_count = max(800, min(1200, word_count))
            context["target_word_count"] = word_count

        context["client_name"] = "siebert"
        context["client_profile"] = "siebert"
        logger.info(
            "✅ Inputs validated for Siebert HTML newsletter: %s words", word_count
        )

    def prepare_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare execution context and inject design system instructions."""
        context = super().prepare_context(context)

        context.setdefault("target_word_count", 1000)
        context.setdefault(
            "exclude_topics", ["crypto day trading", "get rich quick", "penny stocks"]
        )
        context.setdefault("cultural_trends", "")
        context.setdefault("research_timeframe", "last 7 days")
        context.setdefault("premium_sources", "")
        context.setdefault("custom_instructions", "")
        context.setdefault("client_name", "siebert")
        context.setdefault("client_profile", "siebert")

        now = datetime.now()
        context.setdefault("current_date", now.strftime("%B %d, %Y"))
        context.setdefault("current_month_year", now.strftime("%B %Y"))
        context.setdefault("community_name", "Wealthbuilder")
        context.setdefault("newsletter_title", "WEALTHBUILDER NEWSLETTER")

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

        total_words = context["target_word_count"]
        context["siebert_section_word_counts"] = {
            "community_greeting": int(total_words * 0.055),
            "feature_story": int(total_words * 0.30),
            "market_reality_check": int(total_words * 0.225),
            "by_the_numbers": int(total_words * 0.135),
            "your_move_this_week": int(total_words * 0.165),
            "community_corner": int(total_words * 0.07),
            "quick_links": int(total_words * 0.07),
            "sign_off": int(total_words * 0.035),
        }

        exclude_topics = context.get("exclude_topics", [])
        if isinstance(exclude_topics, str) and exclude_topics:
            context["exclude_topics"] = [
                topic.strip() for topic in exclude_topics.split(",") if topic.strip()
            ]
        elif not isinstance(exclude_topics, list):
            context["exclude_topics"] = [
                "crypto day trading",
                "get rich quick",
                "penny stocks",
            ]

        if not isinstance(context.get("cultural_trends", ""), str):
            context["cultural_trends"] = ""

        premium_sources = context.get("premium_sources", "")
        if premium_sources and isinstance(premium_sources, str):
            sources_list = [s.strip() for s in premium_sources.split("\n") if s.strip()]
            context["premium_sources"] = "|".join(sources_list) if sources_list else ""
        else:
            context["premium_sources"] = ""

        if context.get("research_timeframe") not in {
            "last 7 days",
            "yesterday",
            "last month",
        }:
            context["research_timeframe"] = "last 7 days"

        # Inject HTML design system instructions for Task 5
        context["html_design_system_instructions"] = (
            HTML_DESIGN_SYSTEM_INSTRUCTIONS.strip()
        )
        context["workflow_output_format"] = "html"

        logger.info(
            "🔧 Context prepared for Siebert HTML workflow; design system injected"
        )
        return context

    def post_process_task(
        self, task_id: str, task_output: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Capture task outputs and run HTML validation after Task 5."""
        logger.info("🔧 POST-PROCESSING TASK: %s", task_id)

        if task_id == "task1_siebert_context_setup":
            context["siebert_brand_extracted"] = True
            context["template_structure_defined"] = True
        elif task_id == "task2_perplexity_research":
            context["perplexity_research_completed"] = True
        elif task_id == "task3_newsletter_assembly":
            word_count = len(task_output.split()) if task_output else 0
            context["final_word_count"] = word_count
            target_count = context.get("target_word_count", 1000)
            context["word_count_accuracy"] = (
                (word_count / target_count * 100) if target_count else 0
            )
            context["siebert_format_applied"] = True
        elif task_id == "task4_compliance_review":
            context["compliance_reviewed"] = True
            context["final_compliance_word_count"] = (
                len(task_output.split()) if task_output else 0
            )
            context["compliance_review_completed"] = True
            context["compliance_approved_markdown"] = task_output
        elif task_id == "task5_html_builder":
            validation_errors = self._validate_html_output(task_output or "")
            if validation_errors:
                context["html_validation_errors"] = validation_errors
                logger.error("❌ HTML validation failed: %s", validation_errors)
                raise ValueError(f"HTML validation failed: {validation_errors}")
            context["html_validation_passed"] = True
            context["final_html_container"] = task_output

        return context

    def post_process_workflow(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Select final outputs and build summary, preserving markdown + HTML."""
        try:
            logger.info("🔧 POST-PROCESSING WORKFLOW: siebert_newsletter_html")

            final_html = context.get("final_html_container")
            if not final_html:
                final_html = context.get("task5_html_builder_output")
            if not final_html:
                fallback = context.get("task4_compliance_review_output") or context.get(
                    "task3_newsletter_assembly_output"
                )
                final_html = fallback or ""
                logger.warning(
                    "⚠️ Falling back to pre-HTML output; HTML builder did not produce output"
                )

            context["final_output"] = final_html
            context["html_email_container"] = final_html
            context["compliance_markdown"] = context.get(
                "compliance_approved_markdown", ""
            )

            summary = {
                "workflow_type": "siebert_newsletter_html",
                "client": "siebert",
                "newsletter_topic": context.get("topic", ""),
                "target_audience": context.get("target_audience", ""),
                "target_word_count": context.get("target_word_count", 1000),
                "final_word_count": context.get("final_word_count", 0),
                "word_count_accuracy": context.get("word_count_accuracy", 0),
                "perplexity_research": context.get(
                    "perplexity_research_completed", False
                ),
                "compliance_reviewed": context.get(
                    "compliance_review_completed", False
                ),
                "html_validation_passed": context.get("html_validation_passed", False),
            }
            context["workflow_summary"] = summary

            context = super().post_process_workflow(context)
            logger.info("✅ Siebert HTML workflow post-processing complete")
            return context

        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error("❌ Post-processing error in Siebert HTML workflow: %s", exc)
            return super().post_process_workflow(context)

    def _validate_html_output(self, html: str) -> List[str]:
        """Run guardrail checks on the generated HTML."""
        errors: List[str] = []
        if not html.strip():
            errors.append("HTML output is empty")
            return errors

        if not html.strip().startswith("<div"):
            errors.append("Output must start with a single <div> root container")

        if self.banned_pattern.search(html):
            errors.append(
                "Contains banned structural tags (<html>, <head>, <body>, <style>, <script>)"
            )

        if self.forbidden_attributes.search(html):
            errors.append("Contains forbidden attributes (class/id)")

        if "max-width: 600px" not in html:
            errors.append("Root container must define max-width: 600px inline")

        if "style=" not in html.split(">", 1)[0]:
            errors.append("Root container must include inline styles")

        if "<!-- QUALITY CHECKLIST" not in html:
            errors.append(
                "Missing required <!-- QUALITY CHECKLIST --> audit comment at end of HTML output"
            )

        if "—" in html:
            errors.append("Em dash detected; should not appear in HTML output")

        hrefs = re.findall(r"href=\"([^\"]+)\"", html)
        for href in hrefs:
            if not href.startswith(("http://", "https://", "mailto:")):
                errors.append(f"Invalid link href detected: {href}")

        if (
            "<html" in html.lower() or "<body" in html.lower()
        ):  # redundant but explicit guard
            errors.append("HTML should not include <html> or <body> tags")

        return errors
