"""
Onboarding Content Generator workflow handler.

Generic workflow for onboarding content generation supporting multiple content types:
- linkedin_post: Short engaging post (200-400 words)
- linkedin_article: Long-form thought leadership (800-1500 words)
- newsletter: Multi-section newsletter (1000-1500 words)
- blog_post: SEO-optimized blog article (1200-2000 words)
"""

import json
import logging
from typing import Dict, Any, Optional

from ..base.workflow_base import WorkflowHandler
from ..registry import register_workflow

logger = logging.getLogger(__name__)


@register_workflow("onboarding_content_generator")
class OnboardingContentHandler(WorkflowHandler):
    """
    Generic workflow handler for onboarding content generation.

    Routes to appropriate sub-workflow based on content_type in context.
    """

    def load_template(self) -> Dict[str, Any]:
        """
        Override to skip template loading.

        This handler doesn't use a JSON template - it implements
        the workflow logic directly in Python.
        """
        logger.info(f"📋 Content handler doesn't require JSON template")
        return {}  # Return empty dict instead of loading from file

    def validate_inputs(self, context: Dict[str, Any]) -> None:
        """Validate inputs for onboarding content generation."""
        super().validate_inputs(context)

        # CRITICAL FIX: Look for content_type at root level first
        # because prepare_context() hasn't been called yet
        content_type = context.get("content_type")

        # Fallback to context["context"] if it's already a dict (shouldn't happen in normal flow)
        if not content_type:
            rich_context = context.get("context", {})
            if isinstance(rich_context, dict):
                content_type = rich_context.get("content_type")

        # Convert ContentType enum to string if needed (BEFORE checking if it exists)
        if hasattr(content_type, 'value'):
            content_type = content_type.value

        if not content_type:
            raise ValueError("content_type is required in context")

        valid_types = ["linkedin_post", "linkedin_article", "newsletter", "blog_post", "analytics", "company_snapshot"]
        if content_type not in valid_types:
            raise ValueError(
                f"Invalid content_type: {content_type}. "
                f"Must be one of: {', '.join(valid_types)}"
            )

        # Validate required fields
        if not context.get("topic") and content_type not in ["analytics", "company_snapshot"]:
            raise ValueError("topic is required")

        if not context.get("client_name"):
            raise ValueError("client_name is required")

        logger.info(f"✅ Onboarding content validation passed (type: {content_type})")
    
    def prepare_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for onboarding content generation."""
        context = super().prepare_context(context)

        # Extract rich context (parse JSON if needed)
        rich_context_raw = context.get("context", {})

        # Parse JSON if it's a string
        if isinstance(rich_context_raw, str):
            try:
                rich_context = json.loads(rich_context_raw)
                logger.debug("✅ Parsed context from JSON string in prepare_context")
                # CRITICAL FIX: Update context["context"] with parsed dictionary
                # This ensures template engine can access context.get() without errors
                context["context"] = rich_context
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse context JSON in prepare_context: {e}")
                rich_context = {}
        else:
            rich_context = rich_context_raw

        content_type = rich_context.get("content_type", "linkedin_post")
        content_config = rich_context.get("content_config", {})
        
        # Set defaults based on content type
        if content_type == "linkedin_post":
            context.setdefault("target_word_count", content_config.get("word_count", 300))
            context.setdefault("tone", "conversational")
            context["include_emoji"] = content_config.get("include_emoji", True)
            context["include_hashtags"] = content_config.get("include_hashtags", True)
            context["include_cta"] = content_config.get("include_cta", True)
        
        elif content_type == "linkedin_article":
            context.setdefault("target_word_count", content_config.get("word_count", 1200))
            context.setdefault("tone", "thought_leadership")
            context["include_headings"] = content_config.get("include_headings", True)
            context["include_statistics"] = content_config.get("include_statistics", True)
            context["include_examples"] = content_config.get("include_examples", True)
        
        elif content_type == "newsletter":
            context.setdefault("target_word_count", content_config.get("word_count", 1200))
            context.setdefault("tone", "informative")
            context["num_sections"] = content_config.get("num_sections", 4)
            context["include_links"] = content_config.get("include_links", True)
            context["include_cta"] = content_config.get("include_cta", True)
        
        elif content_type == "blog_post":
            context.setdefault("target_word_count", content_config.get("word_count", 1500))
            context.setdefault("tone", "informative")
            context["seo_optimized"] = content_config.get("seo_optimized", True)
            context["include_headings"] = content_config.get("include_headings", True)
            context["include_faq"] = content_config.get("include_faq", True)
        
        # Store content type for routing
        context["content_type"] = content_type
        
        logger.info(
            f"🎯 Prepared context for {content_type} "
            f"(word_count: {context.get('target_word_count')})"
        )
        
        return context
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute onboarding content generation workflow.

        Routes to appropriate sub-workflow based on content_type.
        """
        logger.info("🚀 Executing onboarding_content_generator workflow")

        # Get content type
        content_type = context.get("content_type", "linkedin_post")

        # Convert ContentType enum to string if needed
        if hasattr(content_type, 'value'):
            content_type = content_type.value

        logger.info(f"📝 Content type: {content_type}")

        # Route to appropriate sub-workflow
        if content_type == "linkedin_post":
            return await self._generate_linkedin_post(context)
        elif content_type == "linkedin_article":
            return await self._generate_linkedin_article(context)
        elif content_type == "newsletter":
            return await self._generate_newsletter(context)
        elif content_type == "blog_post":
            return await self._generate_blog_post(context)
        elif content_type == "analytics":
            return await self._generate_analytics(context)
        elif content_type == "company_snapshot":
            return await self._generate_company_snapshot(context)
        else:
            raise ValueError(f"Unsupported content type: {content_type}")
    
    async def _generate_linkedin_post(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate LinkedIn post (200-400 words).

        Structure:
        - Hook (1 sentence, max 15 words)
        - Problem statement (2-3 sentences)
        - Solution (2-3 sentences, highlight differentiators)
        - Proof point (1 data point or example)
        - CTA (1 sentence, actionable)
        - Hashtags (3-5 relevant)
        """
        logger.info("📱 Generating LinkedIn post")

        # Extract company snapshot (parse JSON if needed)
        rich_context_raw = context.get("context", {})

        # Parse JSON if it's a string
        if isinstance(rich_context_raw, str):
            try:
                rich_context = json.loads(rich_context_raw)
                logger.debug("✅ Parsed context from JSON string")
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse context JSON: {e}")
                rich_context = {}
        else:
            rich_context = rich_context_raw

        company_snapshot = rich_context.get("company_snapshot", {})
        
        # Extract key information
        company_name = context.get("client_name", "")
        topic = context.get("topic", "")
        target_audience = context.get("target_audience", "Business professionals")
        tone = context.get("tone", "conversational")
        
        # Extract differentiators from snapshot
        differentiators = []
        if company_snapshot:
            company_info = company_snapshot.get("company", {})
            differentiators = company_info.get("differentiators", [])
        
        # Build custom instructions
        custom_instructions = self._build_linkedin_post_instructions(
            company_name=company_name,
            topic=topic,
            target_audience=target_audience,
            differentiators=differentiators,
            include_emoji=context.get("include_emoji", True),
            include_hashtags=context.get("include_hashtags", True),
            include_cta=context.get("include_cta", True),
        )
        
        # Add to context
        context["custom_instructions"] = custom_instructions
        context["content_format"] = "linkedin_post"
        
        # Execute standard workflow
        result = await self._execute_standard_workflow(context)
        
        logger.info("✅ LinkedIn post generated successfully")
        
        return result
    
    async def _generate_linkedin_article(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate LinkedIn article (800-1500 words).

        Structure:
        - Title (SEO-friendly)
        - Intro (Hook + context)
        - Section 1: Problem/Challenge
        - Section 2: Analysis/Insights
        - Section 3: Solution/Framework
        - Section 4: Examples/Case studies
        - Conclusion (Recap + CTA)
        """
        logger.info("📄 Generating LinkedIn article")

        # Extract company snapshot (parse JSON if needed)
        rich_context_raw = context.get("context", {})

        # Parse JSON if it's a string
        if isinstance(rich_context_raw, str):
            try:
                rich_context = json.loads(rich_context_raw)
                logger.debug("✅ Parsed context from JSON string")
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse context JSON: {e}")
                rich_context = {}
        else:
            rich_context = rich_context_raw

        company_snapshot = rich_context.get("company_snapshot", {})
        
        # Extract key information
        company_name = context.get("client_name", "")
        topic = context.get("topic", "")
        target_audience = context.get("target_audience", "Business professionals")
        
        # Build custom instructions
        custom_instructions = self._build_linkedin_article_instructions(
            company_name=company_name,
            topic=topic,
            target_audience=target_audience,
            include_statistics=context.get("include_statistics", True),
            include_examples=context.get("include_examples", True),
        )
        
        # Add to context
        context["custom_instructions"] = custom_instructions
        context["content_format"] = "linkedin_article"
        
        # Execute standard workflow
        result = await self._execute_standard_workflow(context)
        
        logger.info("✅ LinkedIn article generated successfully")
        
        return result
    
    async def _generate_newsletter(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate newsletter (1000-1500 words).
        
        Structure:
        - Subject line
        - Intro (Welcome + theme)
        - Section 1: Trend/News
        - Section 2: Insight/Analysis
        - Section 3: Tip/Practical advice
        - Section 4: Resources/Links
        - Outro (CTA + signature)
        """
        logger.info("📧 Generating newsletter")
        
        # Extract key information
        company_name = context.get("client_name", "")
        topic = context.get("topic", "")
        num_sections = context.get("num_sections", 4)
        
        # Build custom instructions
        custom_instructions = self._build_newsletter_instructions(
            company_name=company_name,
            topic=topic,
            num_sections=num_sections,
            include_links=context.get("include_links", True),
        )
        
        # Add to context
        context["custom_instructions"] = custom_instructions
        context["content_format"] = "newsletter"
        
        # Execute standard workflow
        result = await self._execute_standard_workflow(context)
        
        logger.info("✅ Newsletter generated successfully")

        return result

    async def _generate_blog_post(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate blog post (1200-2000 words).

        Structure:
        - SEO Title (keyword-optimized)
        - Meta Description (150-160 chars)
        - Intro (Hook + preview)
        - H2 sections with H3 subsections
        - Conclusion (Recap + CTA)
        - FAQ (3-5 questions)
        """
        logger.info("📝 Generating blog post")

        # Extract key information
        company_name = context.get("client_name", "")
        topic = context.get("topic", "")

        # Build custom instructions
        custom_instructions = self._build_blog_post_instructions(
            company_name=company_name,
            topic=topic,
            seo_optimized=context.get("seo_optimized", True),
            include_faq=context.get("include_faq", True),
        )

        # Add to context
        context["custom_instructions"] = custom_instructions
        context["content_format"] = "blog_post"

        # Execute standard workflow
        result = await self._execute_standard_workflow(context)

        logger.info("✅ Blog post generated successfully")

        return result

    async def _execute_standard_workflow(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute standard content generation workflow."""
        # This will use the parent class's execute method
        # which orchestrates agents based on client_profile
        # NOTE: parent class will call prepare_context() automatically
        result = await super().execute(context)

        # Set display_type for frontend rendering in metadata
        if "content" in result and isinstance(result["content"], dict):
            if "metadata" not in result["content"]:
                result["content"]["metadata"] = {}
            result["content"]["metadata"]["display_type"] = "content_preview"

            # CRITICAL: Also add to root metadata for CGS use case to pick up
            result["metadata"] = result["content"]["metadata"].copy()

        return result

    # ========================================================================
    # Instruction Builders
    # ========================================================================

    def _build_linkedin_post_instructions(
        self,
        company_name: str,
        topic: str,
        target_audience: str,
        differentiators: list,
        include_emoji: bool,
        include_hashtags: bool,
        include_cta: bool,
    ) -> str:
        """Build custom instructions for LinkedIn post generation."""

        instructions = f"""
Create a high-impact LinkedIn post for {company_name}.

TOPIC: {topic}
TARGET AUDIENCE: {target_audience}

STRUCTURE (200-400 words):
1. HOOK: One powerful sentence (max 15 words) that stops scrolling
2. PROBLEM: Describe the pain point your audience faces (2-3 sentences)
3. SOLUTION: How {company_name} addresses this (2-3 sentences)
4. PROOF: One concrete data point or example
5. CTA: Clear, actionable call-to-action (1 sentence)
"""

        if differentiators:
            diff_text = "\n".join(f"- {d}" for d in differentiators[:3])
            instructions += f"\nKEY DIFFERENTIATORS:\n{diff_text}\n"

        if include_emoji:
            instructions += "\n✅ Use 3-4 strategic emojis for visual appeal"

        if include_hashtags:
            instructions += "\n✅ End with 3-5 relevant hashtags"

        if include_cta:
            instructions += "\n✅ Include a clear call-to-action"

        instructions += """

TONE: Conversational, engaging, authentic
FORMAT: Use line breaks for readability (max 2-3 sentences per paragraph)
GOAL: Drive engagement (likes, comments, shares)
"""

        return instructions.strip()

    def _build_linkedin_article_instructions(
        self,
        company_name: str,
        topic: str,
        target_audience: str,
        include_statistics: bool,
        include_examples: bool,
    ) -> str:
        """Build custom instructions for LinkedIn article generation."""

        instructions = f"""
Create a thought leadership LinkedIn article for {company_name}.

TOPIC: {topic}
TARGET AUDIENCE: {target_audience}

STRUCTURE (800-1500 words):
1. TITLE: SEO-friendly, compelling (60-80 chars)
2. INTRO: Hook + context + article preview (100-150 words)
3. SECTION 1 (H2): The Problem/Challenge
4. SECTION 2 (H2): Analysis & Insights
5. SECTION 3 (H2): Solution/Framework
6. SECTION 4 (H2): Examples & Applications
7. CONCLUSION: Key takeaways + CTA (100-150 words)

REQUIREMENTS:
✅ Use H2 headings for main sections
✅ Use H3 headings for subsections
✅ Include bullet points and lists for readability
"""

        if include_statistics:
            instructions += "✅ Include relevant data and statistics\n"

        if include_examples:
            instructions += "✅ Include concrete examples and case studies\n"

        instructions += """
TONE: Professional, authoritative, insightful
GOAL: Establish thought leadership and expertise
"""

        return instructions.strip()

    def _build_newsletter_instructions(
        self,
        company_name: str,
        topic: str,
        num_sections: int,
        include_links: bool,
    ) -> str:
        """Build custom instructions for newsletter generation."""

        instructions = f"""
Create a curated newsletter for {company_name}.

TOPIC: {topic}

STRUCTURE (1000-1500 words):
1. SUBJECT LINE: Catchy, curiosity-driven (40-60 chars)
2. INTRO: Welcome message + theme introduction (50-100 words)
3. MAIN SECTIONS ({num_sections} sections):
   - Section 1: Latest Trend/News
   - Section 2: Deep Dive/Analysis
   - Section 3: Practical Tip/How-to
   - Section 4: Resources/Recommendations
4. OUTRO: Call-to-action + signature (50-100 words)

REQUIREMENTS:
✅ Each section has a clear heading
✅ Use emojis for visual breaks
✅ Scannable format (short paragraphs, bullets)
"""

        if include_links:
            instructions += "✅ Include relevant external links\n"

        instructions += """
TONE: Informative, curated, valuable
GOAL: Provide actionable insights and resources
"""

        return instructions.strip()

    def _build_blog_post_instructions(
        self,
        company_name: str,
        topic: str,
        seo_optimized: bool,
        include_faq: bool,
    ) -> str:
        """Build custom instructions for blog post generation."""

        instructions = f"""
Create an SEO-optimized blog post for {company_name}.

TOPIC: {topic}

STRUCTURE (1200-2000 words):
1. SEO TITLE: Keyword-optimized (50-60 chars)
2. META DESCRIPTION: Compelling summary (150-160 chars)
3. INTRO: Hook + problem + article preview (150-200 words)
4. MAIN CONTENT:
   - H2 Section 1: [Main topic aspect 1]
     - H3 Subsection
     - H3 Subsection
   - H2 Section 2: [Main topic aspect 2]
     - H3 Subsection
     - H3 Subsection
   - H2 Section 3: [Main topic aspect 3]
5. CONCLUSION: Summary + CTA (100-150 words)
"""

        if include_faq:
            instructions += "6. FAQ: 3-5 common questions with answers\n"

        if seo_optimized:
            instructions += """
SEO REQUIREMENTS:
✅ Include target keyword in title, first paragraph, and H2s
✅ Use semantic keywords throughout
✅ Optimize for featured snippets (lists, tables)
✅ Include internal and external links
"""

        instructions += """
TONE: Informative, comprehensive, authoritative
GOAL: Rank well in search and provide comprehensive value
"""

        return instructions.strip()

    async def _generate_analytics(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate company analytics report.

        Uses the standard workflow system with a specialized analytics agent.
        Returns structured analytics data with display_type for dashboard rendering.
        """
        logger.info("📊 Generating company analytics")

        # Extract company snapshot (parse JSON if needed)
        rich_context_raw = context.get("context", {})

        # Parse JSON if it's a string
        if isinstance(rich_context_raw, str):
            try:
                rich_context = json.loads(rich_context_raw)
                logger.debug("✅ Parsed context from JSON string")
                # CRITICAL FIX: Update context["context"] with parsed dictionary
                # This ensures prepare_context() can work with it later
                context["context"] = rich_context
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse context JSON: {e}")
                rich_context = {}
        else:
            rich_context = rich_context_raw

        company_snapshot = rich_context.get("company_snapshot", {})

        # Extract key information
        company_name = context.get("client_name", "")
        company_info = company_snapshot.get("company", {})
        industry = company_info.get("industry", "Unknown")
        description = company_info.get("description", "")
        differentiators = company_info.get("differentiators", [])

        # Extract audience info
        audience_info = company_snapshot.get("audience", {})
        target_audience = audience_info.get("primary", "General audience")
        pain_points = audience_info.get("pain_points", [])

        # Extract user variables from clarifying answers
        variables = rich_context.get("variables", {})

        # Build analytics instructions
        custom_instructions = self._build_analytics_instructions(
            company_name=company_name,
            industry=industry,
            description=description,
            differentiators=differentiators,
            target_audience=target_audience,
            pain_points=pain_points,
            user_variables=variables,
        )

        # Add to context
        context["custom_instructions"] = custom_instructions
        context["content_format"] = "analytics"
        context["topic"] = f"Company Analytics Report: {company_name}"

        # Execute standard workflow
        result = await self._execute_standard_workflow(context)

        # Parse analytics JSON from body and add to metadata
        if "content" in result and isinstance(result["content"], dict):
            # Initialize metadata if not present
            if "metadata" not in result["content"]:
                result["content"]["metadata"] = {}

            # Try to parse JSON from body
            try:
                body = result["content"].get("body", "")

                # Remove markdown code blocks if present
                if body.strip().startswith("```"):
                    # Extract JSON from markdown code block
                    lines = body.strip().split("\n")
                    # Remove first line (```json or ```)
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    # Remove last line (```)
                    if lines and lines[-1].strip() == "```":
                        lines = lines[:-1]
                    body = "\n".join(lines)

                # Parse JSON
                analytics_data = json.loads(body.strip())

                # Validate structure
                required_keys = ["company_score", "content_opportunities", "optimization_insights"]
                if not all(k in analytics_data for k in required_keys):
                    logger.warning(f"⚠️ Analytics JSON missing required keys: {required_keys}")
                    # Still use it, but log warning

                # Add to metadata (both in content.metadata and root metadata)
                result["content"]["metadata"]["analytics_data"] = analytics_data
                result["content"]["metadata"]["display_type"] = "analytics_dashboard"

                # CRITICAL: Also add to root metadata for CGS use case to pick up
                result["metadata"] = result["content"]["metadata"].copy()

                logger.info("✅ Analytics JSON parsed successfully")
                logger.info(f"📦 Analytics data keys: {list(analytics_data.keys())}")

            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse analytics JSON: {e}")
                logger.error(f"Body preview: {body[:200]}...")
                # Fallback: keep as text, use content_preview
                result["content"]["metadata"]["display_type"] = "content_preview"
                result["metadata"] = {"display_type": "content_preview"}
            except Exception as e:
                logger.error(f"❌ Unexpected error parsing analytics: {e}")
                result["content"]["metadata"]["display_type"] = "content_preview"
                result["metadata"] = {"display_type": "content_preview"}

        logger.info("✅ Analytics generated successfully")

        return result

    def _build_analytics_instructions(
        self,
        company_name: str,
        industry: str,
        description: str,
        differentiators: list,
        target_audience: str,
        pain_points: list,
        user_variables: dict,
    ) -> str:
        """Build custom instructions for analytics generation."""

        instructions = f"""
Create a comprehensive company analytics report for {company_name}.

COMPANY INFORMATION:
- Name: {company_name}
- Industry: {industry}
- Description: {description}
- Key Differentiators: {', '.join(differentiators) if differentiators else 'Not specified'}
- Target Audience: {target_audience}
- Audience Pain Points: {', '.join(pain_points) if pain_points else 'Not specified'}

USER CONTEXT:
"""

        # Add user variables dynamically
        for key, value in user_variables.items():
            instructions += f"- {key}: {value}\n"

        instructions += """

TASK:
Generate a comprehensive analytics report in JSON format with the following structure:

{
  "company_score": <integer 0-100>,
  "content_opportunities": [
    {
      "type": "linkedin_post|blog_post|newsletter|linkedin_article",
      "topic": "specific topic suggestion",
      "priority": "high|medium|low",
      "estimated_reach": <integer>,
      "engagement_potential": <float 0-10>,
      "rationale": "why this is valuable"
    }
  ],
  "optimization_insights": {
    "brand_voice": {
      "score": <integer 0-100>,
      "status": "strong|good|needs_improvement",
      "recommendation": "specific recommendation",
      "quick_wins": ["action 1", "action 2"]
    },
    "seo": {
      "score": <integer 0-100>,
      "status": "strong|good|needs_improvement",
      "recommendation": "specific recommendation",
      "quick_wins": ["action 1", "action 2"]
    },
    "messaging": {
      "score": <integer 0-100>,
      "status": "strong|good|needs_improvement",
      "recommendation": "specific recommendation",
      "quick_wins": ["action 1", "action 2"]
    },
    "social_strategy": {
      "score": <integer 0-100>,
      "status": "strong|good|needs_improvement",
      "recommendation": "specific recommendation",
      "quick_wins": ["action 1", "action 2"]
    }
  },
  "competitors": [
    {
      "name": "competitor name",
      "market_position": "leader|challenger|niche",
      "strengths": ["strength 1", "strength 2"],
      "weaknesses": ["weakness 1", "weakness 2"],
      "your_advantage": "how you differentiate"
    }
  ],
  "quick_wins": [
    {
      "action": "specific actionable task",
      "estimated_time": "X hours",
      "impact": "high|medium|low",
      "difficulty": "low|medium|high",
      "category": "seo|content|social|analytics"
    }
  ],
  "full_report": "# Company Analytics Report\\n\\n[Full markdown report with all sections]"
}

REQUIREMENTS:
1. Company Score: Calculate based on brand voice, SEO, messaging, social strategy
2. Content Opportunities: Suggest 8-12 specific content pieces across different types
3. Optimization Insights: Analyze 4 areas with scores and actionable recommendations
4. Competitors: Identify 3-5 main competitors with analysis
5. Quick Wins: List 6-8 actionable tasks with time estimates
6. Full Report: Comprehensive markdown report (1500-2000 words) with:
   - Executive Summary
   - Content Opportunities Analysis
   - Optimization Insights (detailed)
   - Competitor Intelligence
   - Actionable Recommendations
   - KPIs to track

Be specific, actionable, and data-driven. Use the user variables to personalize recommendations.

CRITICAL OUTPUT INSTRUCTIONS:
- Return ONLY valid JSON
- Do NOT wrap in markdown code blocks (no ```json or ```)
- Do NOT add any explanatory text before or after the JSON
- Start directly with { and end with }
- Ensure all strings are properly escaped
- Use double quotes for all keys and string values
"""

        return instructions.strip()

    async def _generate_company_snapshot(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate company snapshot card view.

        This method doesn't generate new content - it prepares the existing
        company snapshot for display in the CompanySnapshotCard UI component.

        Use case: Show company snapshot in a beautiful card format instead of
        raw text/markdown.
        """
        logger.info("🏢 Generating company snapshot card view")

        # Extract company snapshot from context
        rich_context_raw = context.get("context", {})

        # Parse JSON if it's a string
        if isinstance(rich_context_raw, str):
            try:
                rich_context = json.loads(rich_context_raw)
                logger.debug("✅ Parsed context from JSON string")
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse context JSON: {e}")
                rich_context = {}
        else:
            rich_context = rich_context_raw

        company_snapshot = rich_context.get("company_snapshot", {})

        if not company_snapshot:
            logger.warning("⚠️ No company snapshot found in context")
            # Return minimal result
            return {
                "content": {
                    "title": "Company Snapshot",
                    "body": "No company snapshot available.",
                    "metadata": {
                        "display_type": "content_preview"
                    }
                },
                "metadata": {
                    "display_type": "content_preview"
                },
                "workflow_id": context.get("run_id", "dynamic")
            }

        # Extract company name for title
        company_name = company_snapshot.get("company", {}).get("name", "Unknown Company")

        # Prepare result with metadata for frontend
        result = {
            "content": {
                "title": f"Company Snapshot: {company_name}",
                "body": "Company snapshot loaded successfully. View the card below.",
                "metadata": {
                    "display_type": "company_snapshot",
                    "company_snapshot": company_snapshot,
                    "view_mode": "card",
                    "interactive": True,
                }
            },
            "metadata": {
                "display_type": "company_snapshot",
                "company_snapshot": company_snapshot,
                "view_mode": "card",
                "interactive": True,
            },
            "workflow_id": context.get("run_id", "dynamic"),  # Include workflow_id for tracking
            "final_output": f"Company Snapshot: {company_name}\n\nCompany snapshot loaded successfully. View the card below."  # ← ADDED: Required for Content entity creation
        }

        logger.info(f"✅ Company snapshot card view prepared for: {company_name}")
        logger.info(f"📦 Snapshot ID: {company_snapshot.get('snapshot_id', 'N/A')}")
        logger.info(f"📦 Workflow ID: {context.get('run_id', 'dynamic')}")

        return result

