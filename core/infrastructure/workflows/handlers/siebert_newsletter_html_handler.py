"""Siebert newsletter workflow with HTML email output."""

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

HTML_DESIGN_SYSTEM_INSTRUCTIONS = """
HARD RULES - FOLLOW EXACTLY:
- Output exactly one root <div> container (no <html>, <head>, <body>, <style>, <script> tags)
- The root container must include style="max-width: 600px; margin: 0 auto; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;"
- Use ONLY inline styles; classes, ids, style blocks, external CSS, gradients, opacity > 0 are forbidden
- Preserve every emoji, URL, citation, and piece of copy from the approved markdown verbatim
- Never introduce em dashes - replace with hyphen if they appear in the source

LAYOUT MAP (EXACTLY 7 sections, in order):
1. Intro Greeting: dark background (#1a1a1a), white bold greeting (24px), intro copy in #e0e0e0
2. Feature Story: section header with background #1a1a1a, text #4ade80, font-size 18px, padding 12px 20px, border-radius 8px
3. Market Reality Check: same header styling, bullet points with dot character
4. By The Numbers: table for email compatibility - 2 columns, background #4ade80, dark text, 20px padding
5. Market Insights from Malek: light box (#f1f5f9) with 4px solid #4ade80 left border, 20px padding
6. Your Move This Week: light green background (#f0fdf4) with #4ade80 border, educational bullet points
7. Sign-off: dark background (#1a1a1a), white text centered, simple signature only

FORBIDDEN SECTIONS (DO NOT CREATE):
- NO Reader Spotlight section
- NO Quick Links section
- NO P.S. block
- NO Footer with P.S.
- NO Community Corner

ACCESSIBILITY & MOBILE-FIRST:
- Favor simple tables for multi-column layouts; avoid nested tables when unnecessary
- Use padding and margin inline styles to create breathing room; default to 16px for vertical rhythm
- Links: color #4ade80; no underline
- Ensure text contrast meets WCAG AA

DO / DON'T:
DO:
- Maintain semantic structure with headings
- Use <table> for the numbers grid
- Finish with an HTML comment named <!-- QUALITY CHECKLIST --> listing pass/fail for: root-container, inline-styles, banned-tags, color-palette, links-intact, citations-intact

DON'T:
- Use <html>, <head>, <body>, <style>, <script>, classes, ids
- Create Reader Spotlight, Quick Links, or P.S. sections
- Modify citations or URLs from the approved markdown

VALIDATION TARGETS:
- Regex enforcement expects "max-width: 600px"
- No banned tags: <html, <head, <body, <style, <script, class=, id=
- Links must remain full http(s) URLs
- EXACTLY 7 sections, no more
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
                logger.info(f"📊 Section word counts calculated from template")
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
            # Fallback word count distribution (7 sections only)
            total_words = context["target_word_count"]
            context["siebert_section_word_counts"] = {
                "intro_greeting": int(total_words * 0.055),
                "feature_story": int(total_words * 0.30),
                "market_reality_check": int(total_words * 0.225),
                "by_the_numbers": int(total_words * 0.135),
                "malek_insights": int(total_words * 0.145),
                "your_move_this_week": int(total_words * 0.165),
                "sign_off": int(total_words * 0.025),
            }

        # Process exclude_topics format
        exclude_topics = context.get("exclude_topics", [])
        if isinstance(exclude_topics, str) and exclude_topics:
            context["exclude_topics"] = [
                topic.strip() for topic in exclude_topics.split(",") if topic.strip()
            ]
        elif not isinstance(exclude_topics, list):
            context["exclude_topics"] = ["crypto day trading", "get rich quick", "penny stocks"]

        if not isinstance(context.get("cultural_trends", ""), str):
            context["cultural_trends"] = ""

        # Process premium_sources format
        premium_sources = context.get("premium_sources", "")
        if premium_sources and isinstance(premium_sources, str):
            sources_list = [s.strip() for s in premium_sources.split("\n") if s.strip()]
            context["premium_sources"] = "|".join(sources_list) if sources_list else ""
        else:
            context["premium_sources"] = ""

        # Validate research timeframe
        if context.get("research_timeframe") not in {"last 7 days", "yesterday", "last month"}:
            context["research_timeframe"] = "last 7 days"

        # Inject HTML design system instructions for Task 5
        context["html_design_system_instructions"] = HTML_DESIGN_SYSTEM_INSTRUCTIONS.strip()
        context["workflow_output_format"] = "html"

        logger.info("🔧 Context prepared for Siebert HTML workflow; design system injected")
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
            # 7-section structure (current)
            "Intro Greeting": "intro_greeting",
            "Feature Story": "feature_story",
            "Market Reality Check": "market_reality_check",
            "By The Numbers": "by_the_numbers",
            "Market Insights from Malek": "malek_insights",
            "Your Move This Week": "your_move_this_week",
            "Sign-off": "sign_off",
            # Legacy names (for backward compatibility only)
            "Community Greeting": "intro_greeting",
        }

        for section in sections:
            section_name = section.get("name", "")
            word_count_str = section.get("word_count", "")

            # Parse word count range (e.g., "50-60 words" -> average 55)
            if word_count_str:
                # Extract numbers from string like "50-60 words"
                numbers = re.findall(r"\d+", word_count_str)
                if len(numbers) >= 2:
                    avg_words = (int(numbers[0]) + int(numbers[1])) // 2
                elif len(numbers) == 1:
                    avg_words = int(numbers[0])
                else:
                    avg_words = 50  # default

                # Map to internal section name
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
        """Capture task outputs and run HTML validation after Task 5."""
        logger.info("🔧 POST-PROCESSING TASK: %s", task_id)

        if task_id == "task1_siebert_context_setup":
            context["siebert_brand_extracted"] = True
            context["template_structure_defined"] = True
        elif task_id == "task2_perplexity_research":
            context["perplexity_research_completed"] = True
            # CRITICAL: Extract REAL URLs from Perplexity JSON response
            verified_urls = self._extract_perplexity_urls(task_output)
            if verified_urls:
                context["perplexity_verified_urls"] = verified_urls
                context["perplexity_verified_urls_formatted"] = self._format_urls_for_prompt(verified_urls)
                logger.info(f"✅ Extracted {len(verified_urls)} verified URLs from Perplexity")
            else:
                context["perplexity_verified_urls"] = []
                context["perplexity_verified_urls_formatted"] = "NO VERIFIED URLS AVAILABLE"
                logger.warning("⚠️ No URLs extracted from Perplexity response")
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
                # Downgrade to non-fatal: record errors and proceed with best-effort HTML
                context["html_validation_errors"] = validation_errors
                logger.error("❌ HTML validation failed (non-fatal): %s", validation_errors)
                context["html_validation_passed"] = False
                context["final_html_container"] = task_output
            else:
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

    def _extract_perplexity_urls(self, task_output: str) -> List[str]:
        """Extract verified URLs from Perplexity JSON response.

        Searches for the [perplexity_search RESULT] block and extracts URLs from:
        1. The 'citations' array in the JSON
        2. The 'search_results' array URLs

        Returns:
            List of verified URLs from the actual Perplexity response
        """
        urls = []

        if not task_output:
            return urls

        try:
            # Find the perplexity_search RESULT block
            result_pattern = r"\[perplexity_search RESULT\](.*?)\[/perplexity_search RESULT\]"
            result_match = re.search(result_pattern, task_output, re.DOTALL)

            if not result_match:
                logger.warning("⚠️ No [perplexity_search RESULT] block found in task output")
                return urls

            result_content = result_match.group(1)

            # Try to parse as JSON
            try:
                # Find JSON object in the result
                json_match = re.search(r'\{.*\}', result_content, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(0))

                    # Extract from 'citations' array (direct URL list)
                    citations = data.get("citations", [])
                    if isinstance(citations, list):
                        for url in citations:
                            if isinstance(url, str) and url.startswith("http"):
                                if url not in urls:
                                    urls.append(url)
                                    logger.debug(f"📎 Extracted citation URL: {url}")

                    # Extract from 'search_results' array
                    search_results = data.get("search_results", [])
                    if isinstance(search_results, list):
                        for result in search_results:
                            if isinstance(result, dict):
                                url = result.get("url", "")
                                if url and url.startswith("http") and url not in urls:
                                    urls.append(url)
                                    logger.debug(f"📎 Extracted search_result URL: {url}")

                    # Also check 'data' wrapper if present
                    if "data" in data and isinstance(data["data"], dict):
                        inner_data = data["data"]
                        inner_citations = inner_data.get("citations", [])
                        if isinstance(inner_citations, list):
                            for url in inner_citations:
                                if isinstance(url, str) and url.startswith("http"):
                                    if url not in urls:
                                        urls.append(url)

                        inner_results = inner_data.get("search_results", [])
                        if isinstance(inner_results, list):
                            for result in inner_results:
                                if isinstance(result, dict):
                                    url = result.get("url", "")
                                    if url and url.startswith("http") and url not in urls:
                                        urls.append(url)

            except json.JSONDecodeError as e:
                logger.warning(f"⚠️ Failed to parse JSON from Perplexity result: {e}")
                # Fallback: try to extract URLs with regex from the raw content
                url_pattern = r'"url"\s*:\s*"(https?://[^"]+)"'
                citation_pattern = r'"citations"\s*:\s*\[(.*?)\]'

                # Extract from citations array
                citation_match = re.search(citation_pattern, result_content, re.DOTALL)
                if citation_match:
                    citation_urls = re.findall(r'"(https?://[^"]+)"', citation_match.group(1))
                    for url in citation_urls:
                        if url not in urls:
                            urls.append(url)

                # Extract from search_results URLs
                url_matches = re.findall(url_pattern, result_content)
                for url in url_matches:
                    if url not in urls:
                        urls.append(url)

        except Exception as e:
            logger.error(f"❌ Error extracting URLs from Perplexity response: {e}")

        logger.info(f"📊 Total extracted Perplexity URLs: {len(urls)}")

        # Prioritize and filter approved sources
        prioritized_urls = self._prioritize_approved_sources(urls)
        return prioritized_urls

    def _prioritize_approved_sources(self, urls: List[str]) -> List[str]:
        """Prioritize URLs from approved sources for Siebert compliance.

        Tier 1 (Official Government): federalreserve.gov, bls.gov, bea.gov, census.gov, treasury.gov, sec.gov
        Tier 2 (Financial Data): cmegroup.com, conference-board.org, freddiemac.com, bankrate.com, tradingeconomics.com
        Tier 3 (Approved News): reuters.com, wsj.com, nytimes.com, finance.yahoo.com, blog.siebert.com
        """
        TIER_1_DOMAINS = [
            'federalreserve.gov', 'bls.gov', 'bea.gov', 'census.gov',
            'treasury.gov', 'sec.gov'
        ]
        TIER_2_DOMAINS = [
            'cmegroup.com', 'conference-board.org', 'freddiemac.com',
            'bankrate.com', 'tradingeconomics.com', 'morningstar.com'
        ]
        TIER_3_DOMAINS = [
            'reuters.com', 'wsj.com', 'nytimes.com', 'finance.yahoo.com',
            'blog.siebert.com', 'siebert.com'
        ]

        tier1_urls = []
        tier2_urls = []
        tier3_urls = []
        other_urls = []

        for url in urls:
            url_lower = url.lower()
            if any(domain in url_lower for domain in TIER_1_DOMAINS):
                tier1_urls.append(url)
                logger.info(f"✅ TIER 1 (Official): {url}")
            elif any(domain in url_lower for domain in TIER_2_DOMAINS):
                tier2_urls.append(url)
                logger.info(f"✅ TIER 2 (Financial Data): {url}")
            elif any(domain in url_lower for domain in TIER_3_DOMAINS):
                tier3_urls.append(url)
                logger.info(f"✅ TIER 3 (Approved News): {url}")
            else:
                other_urls.append(url)
                logger.info(f"⚠️ OTHER (Non-approved): {url}")

        # Combine in priority order
        prioritized = tier1_urls + tier2_urls + tier3_urls + other_urls

        logger.info(f"📊 Source breakdown: Tier1={len(tier1_urls)}, Tier2={len(tier2_urls)}, Tier3={len(tier3_urls)}, Other={len(other_urls)}")

        return prioritized

    def _format_urls_for_prompt(self, urls: List[str]) -> str:
        """Format extracted URLs as a numbered list for injection into prompts.

        Args:
            urls: List of verified URLs (already prioritized by tier)

        Returns:
            Formatted string with numbered URLs ready for prompt injection
        """
        if not urls:
            return "NO VERIFIED URLS AVAILABLE FROM PERPLEXITY"

        TIER_1_DOMAINS = ['federalreserve.gov', 'bls.gov', 'bea.gov', 'census.gov', 'treasury.gov', 'sec.gov']
        TIER_2_DOMAINS = ['cmegroup.com', 'conference-board.org', 'freddiemac.com', 'bankrate.com', 'tradingeconomics.com', 'morningstar.com']
        TIER_3_DOMAINS = ['reuters.com', 'wsj.com', 'nytimes.com', 'finance.yahoo.com', 'blog.siebert.com', 'siebert.com']

        lines = ["═══════════════════════════════════════════════════════════════════════════════",
                 "VERIFIED PERPLEXITY URLS (USE ONLY THESE - DO NOT INVENT URLs)",
                 "═══════════════════════════════════════════════════════════════════════════════",
                 "",
                 "PRIORITIZE TIER 1 & 2 SOURCES FOR COMPLIANCE:"]

        for i, url in enumerate(urls, 1):
            url_lower = url.lower()
            if any(domain in url_lower for domain in TIER_1_DOMAINS):
                tier_label = "✅ TIER 1 (Official)"
            elif any(domain in url_lower for domain in TIER_2_DOMAINS):
                tier_label = "✅ TIER 2 (Financial)"
            elif any(domain in url_lower for domain in TIER_3_DOMAINS):
                tier_label = "✅ TIER 3 (News)"
            else:
                tier_label = "⚠️ OTHER"
            lines.append(f"{i}. {tier_label}: {url}")

        lines.append("")
        lines.append("═══════════════════════════════════════════════════════════════════════════════")
        lines.append("CITATION REQUIREMENTS:")
        lines.append("• Use 8-12 inline citations throughout the newsletter")
        lines.append("• Feature Story: minimum 3 citations")
        lines.append("• Market Reality Check: minimum 2 citations")
        lines.append("• By The Numbers: EVERY statistic must have a citation")
        lines.append("• Quick Links section: list 4-6 main sources with clickable URLs")
        lines.append("")
        lines.append("CRITICAL: You MUST use ONLY URLs from this list above.")
        lines.append("DO NOT create, fabricate, or modify any URLs.")
        lines.append("═══════════════════════════════════════════════════════════════════════════════")

        return "\n".join(lines)
