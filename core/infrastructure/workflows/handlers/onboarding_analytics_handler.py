"""
Onboarding Analytics Generator workflow handler.

Generates comprehensive company analytics reports including:
- Company readiness score (0-100)
- Content opportunities analysis
- Optimization insights (brand, SEO, messaging, social)
- Competitor intelligence
- Quick wins and actionable recommendations
- Full strategic report
"""

import logging
import json
from typing import Dict, Any, Optional

from ..base.workflow_base import WorkflowHandler
from ..registry import register_workflow

logger = logging.getLogger(__name__)


@register_workflow("onboarding_analytics_generator")
class OnboardingAnalyticsHandler(WorkflowHandler):
    """
    Analytics workflow handler for onboarding.

    Generates strategic insights and recommendations instead of content.
    """

    def load_template(self) -> Dict[str, Any]:
        """
        Override to skip template loading.

        This handler doesn't use a JSON template - it implements
        the workflow logic directly in Python.
        """
        logger.info(f"📋 Analytics handler doesn't require JSON template")
        return {}  # Return empty dict instead of loading from file

    def validate_inputs(self, context: Dict[str, Any]) -> None:
        """Validate inputs for analytics generation."""
        super().validate_inputs(context)
        
        # Validate required fields
        if not context.get("client_name"):
            raise ValueError("client_name is required")
        
        # Rich context with company snapshot
        rich_context = context.get("context", {})
        if not rich_context.get("company_snapshot"):
            logger.warning("⚠️ No company_snapshot provided - analytics will be limited")
        
        logger.info(f"✅ Analytics validation passed for {context.get('client_name')}")
    
    def prepare_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for analytics generation."""
        context = super().prepare_context(context)
        
        # Extract rich context
        rich_context = context.get("context", {})
        company_snapshot = rich_context.get("company_snapshot", {})
        variables = rich_context.get("variables", {})
        
        # Extract company info from snapshot
        company_info = company_snapshot.get("company", {})
        context["company_name"] = company_info.get("name", context.get("client_name"))
        context["industry"] = company_info.get("industry", "Unknown")
        context["description"] = company_info.get("description", "")
        context["differentiators"] = company_info.get("differentiators", [])
        
        # Extract audience info
        audience_info = company_snapshot.get("audience", {})
        context["target_audience"] = audience_info.get("primary", "General audience")
        context["pain_points"] = audience_info.get("pain_points", [])
        
        # Extract voice info
        voice_info = company_snapshot.get("voice", {})
        context["brand_tone"] = voice_info.get("tone", "professional")
        
        # Store variables for analysis
        context["user_variables"] = variables
        
        logger.info(
            f"🎯 Prepared analytics context for {context['company_name']} "
            f"(industry: {context['industry']})"
        )
        
        return context
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute analytics generation workflow."""
        logger.info("🚀 Executing onboarding_analytics_generator workflow")
        
        # Prepare context
        context = self.prepare_context(context)
        
        # Generate analytics report
        analytics_report = await self._generate_analytics_report(context)
        
        # Format output
        result = {
            "status": "completed",
            "content": {
                "title": f"Company Analytics Report: {context['company_name']}",
                "body": analytics_report.get("full_report", ""),
                "format": "json",
                "metadata": {
                    "company_score": analytics_report.get("company_score", 0),
                    "total_opportunities": len(analytics_report.get("content_opportunities", [])),
                    "quick_wins_count": len(analytics_report.get("quick_wins", [])),
                    "competitors_analyzed": len(analytics_report.get("competitors", [])),
                },
                "analytics_data": analytics_report,  # Full structured data
            },
        }
        
        logger.info(
            f"✅ Analytics generated: score={analytics_report.get('company_score')}, "
            f"opportunities={len(analytics_report.get('content_opportunities', []))}"
        )
        
        return result
    
    async def _generate_analytics_report(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive analytics report using LLM."""
        
        # Build analytics prompt
        prompt = self._build_analytics_prompt(context)
        
        # Call LLM
        llm_response = await self.call_llm(
            prompt=prompt,
            context=context,
            temperature=0.7,
            max_tokens=8000,
        )
        
        # Parse JSON response
        try:
            analytics_data = self._parse_analytics_response(llm_response)
        except Exception as e:
            logger.error(f"Failed to parse analytics response: {e}")
            # Fallback to basic structure
            analytics_data = self._create_fallback_analytics(context, llm_response)
        
        return analytics_data
    
    def _build_analytics_prompt(self, context: Dict[str, Any]) -> str:
        """Build comprehensive analytics prompt."""
        
        company_name = context.get("company_name", "the company")
        industry = context.get("industry", "Unknown")
        description = context.get("description", "")
        differentiators = context.get("differentiators", [])
        target_audience = context.get("target_audience", "")
        pain_points = context.get("pain_points", [])
        user_variables = context.get("user_variables", {})
        
        prompt = f"""You are a strategic business analyst generating a comprehensive company analytics report.

COMPANY INFORMATION:
- Name: {company_name}
- Industry: {industry}
- Description: {description}
- Key Differentiators: {', '.join(differentiators) if differentiators else 'Not specified'}
- Target Audience: {target_audience}
- Audience Pain Points: {', '.join(pain_points) if pain_points else 'Not specified'}

USER CONTEXT:
- Variable 1 (Business Objective): {user_variables.get('variable_1', 'Not provided')}
- Variable 2 (Target Market): {user_variables.get('variable_2', 'Not provided')}
- Variable 3 (Biggest Challenge): {user_variables.get('variable_3', 'Not provided')}
- Variable 4 (Unique Value): {user_variables.get('variable_4', 'Not provided')}

TASK:
Generate a comprehensive analytics report in JSON format with the following structure:

{{
  "company_score": <integer 0-100>,
  "content_opportunities": [
    {{
      "type": "linkedin_post|blog_post|newsletter|linkedin_article",
      "topic": "specific topic suggestion",
      "priority": "high|medium|low",
      "estimated_reach": <integer>,
      "engagement_potential": <float 0-10>,
      "rationale": "why this is valuable"
    }}
  ],
  "optimization_insights": {{
    "brand_voice": {{
      "score": <integer 0-100>,
      "status": "strong|good|needs_improvement",
      "recommendation": "specific recommendation",
      "quick_wins": ["action 1", "action 2"]
    }},
    "seo": {{
      "score": <integer 0-100>,
      "status": "strong|good|needs_improvement",
      "recommendation": "specific recommendation",
      "quick_wins": ["action 1", "action 2"]
    }},
    "messaging": {{
      "score": <integer 0-100>,
      "status": "strong|good|needs_improvement",
      "recommendation": "specific recommendation",
      "quick_wins": ["action 1", "action 2"]
    }},
    "social_strategy": {{
      "score": <integer 0-100>,
      "status": "strong|good|needs_improvement",
      "recommendation": "specific recommendation",
      "quick_wins": ["action 1", "action 2"]
    }}
  }},
  "competitors": [
    {{
      "name": "competitor name",
      "market_position": "leader|challenger|niche",
      "strengths": ["strength 1", "strength 2"],
      "weaknesses": ["weakness 1", "weakness 2"],
      "your_advantage": "how you differentiate"
    }}
  ],
  "quick_wins": [
    {{
      "action": "specific actionable task",
      "estimated_time": "X hours",
      "impact": "high|medium|low",
      "difficulty": "low|medium|high",
      "category": "seo|content|social|analytics"
    }}
  ],
  "content_distribution": {{
    "linkedin_post": <count>,
    "blog_post": <count>,
    "newsletter": <count>,
    "linkedin_article": <count>
  }},
  "metrics": {{
    "estimated_total_reach": <integer>,
    "engagement_potential": <float 0-10>,
    "seo_score": <integer 0-100>,
    "brand_consistency": <integer 0-100>,
    "content_readiness": <integer 0-100>,
    "competitive_advantage": <float 0-10>
  }},
  "full_report": "# Company Analytics Report: {company_name}\\n\\n[Full markdown report with all sections]"
}}

REQUIREMENTS:
1. Company Score: Calculate based on brand voice, SEO, messaging, social strategy, and market position
2. Content Opportunities: Suggest 8-12 specific content pieces across different types
3. Optimization Insights: Analyze 4 areas with scores and actionable recommendations
4. Competitors: Identify 3-5 main competitors with analysis
5. Quick Wins: List 6-8 actionable tasks with time estimates
6. Full Report: Comprehensive markdown report (1500-2000 words) with:
   - Executive Summary
   - Content Opportunities Analysis
   - Optimization Insights (detailed)
   - Competitor Intelligence
   - Actionable Recommendations (quick wins, medium-term, long-term)
   - KPIs to track

Be specific, actionable, and data-driven. Use the user variables to personalize recommendations.

OUTPUT ONLY THE JSON - NO ADDITIONAL TEXT."""

        return prompt
    
    def _parse_analytics_response(self, llm_response: str) -> Dict[str, Any]:
        """Parse LLM response into structured analytics data."""
        
        # Try to extract JSON from response
        response_text = llm_response.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Parse JSON
        analytics_data = json.loads(response_text)
        
        # Validate required fields
        required_fields = [
            "company_score",
            "content_opportunities",
            "optimization_insights",
            "competitors",
            "quick_wins",
            "full_report",
        ]
        
        for field in required_fields:
            if field not in analytics_data:
                raise ValueError(f"Missing required field: {field}")
        
        return analytics_data
    
    def _create_fallback_analytics(
        self, context: Dict[str, Any], llm_response: str
    ) -> Dict[str, Any]:
        """Create fallback analytics structure if parsing fails."""
        
        logger.warning("Using fallback analytics structure")
        
        return {
            "company_score": 70,
            "content_opportunities": [
                {
                    "type": "linkedin_post",
                    "topic": f"Introduction to {context.get('company_name')}",
                    "priority": "high",
                    "estimated_reach": 1000,
                    "engagement_potential": 7.0,
                    "rationale": "Build brand awareness",
                }
            ],
            "optimization_insights": {
                "brand_voice": {
                    "score": 70,
                    "status": "good",
                    "recommendation": "Continue developing consistent brand voice",
                    "quick_wins": ["Review brand guidelines"],
                },
                "seo": {
                    "score": 60,
                    "status": "needs_improvement",
                    "recommendation": "Focus on keyword optimization",
                    "quick_wins": ["Optimize meta tags"],
                },
                "messaging": {
                    "score": 70,
                    "status": "good",
                    "recommendation": "Clarify value proposition",
                    "quick_wins": ["Update homepage copy"],
                },
                "social_strategy": {
                    "score": 65,
                    "status": "good",
                    "recommendation": "Increase posting frequency",
                    "quick_wins": ["Create content calendar"],
                },
            },
            "competitors": [],
            "quick_wins": [
                {
                    "action": "Optimize website meta tags",
                    "estimated_time": "2 hours",
                    "impact": "medium",
                    "difficulty": "low",
                    "category": "seo",
                }
            ],
            "content_distribution": {
                "linkedin_post": 4,
                "blog_post": 3,
                "newsletter": 2,
                "linkedin_article": 1,
            },
            "metrics": {
                "estimated_total_reach": 10000,
                "engagement_potential": 7.0,
                "seo_score": 60,
                "brand_consistency": 70,
                "content_readiness": 70,
                "competitive_advantage": 7.0,
            },
            "full_report": llm_response,  # Use raw LLM response as fallback
        }

