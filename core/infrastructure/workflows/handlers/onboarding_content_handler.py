"""
Onboarding Content Generator workflow handler.

Generic workflow for onboarding content generation supporting multiple content types:
- linkedin_post: Short engaging post (200-400 words)
- linkedin_article: Long-form thought leadership (800-1500 words)
- newsletter: Multi-section newsletter (1000-1500 words)
- blog_post: SEO-optimized blog article (1200-2000 words)
"""

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
        
        # Validate content_type
        rich_context = context.get("context", {})
        content_type = rich_context.get("content_type")
        
        if not content_type:
            raise ValueError("content_type is required in context")
        
        valid_types = ["linkedin_post", "linkedin_article", "newsletter", "blog_post"]
        if content_type not in valid_types:
            raise ValueError(
                f"Invalid content_type: {content_type}. "
                f"Must be one of: {', '.join(valid_types)}"
            )
        
        # Validate required fields
        if not context.get("topic"):
            raise ValueError("topic is required")
        
        if not context.get("client_name"):
            raise ValueError("client_name is required")
        
        logger.info(f"✅ Onboarding content validation passed (type: {content_type})")
    
    def prepare_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for onboarding content generation."""
        context = super().prepare_context(context)
        
        # Extract rich context
        rich_context = context.get("context", {})
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
        
        # Extract company snapshot
        rich_context = context.get("context", {})
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
        
        # Extract company snapshot
        rich_context = context.get("context", {})
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
        # This will use the parent class's execute_workflow method
        # which orchestrates agents based on client_profile
        return await self.execute_workflow(context)

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

