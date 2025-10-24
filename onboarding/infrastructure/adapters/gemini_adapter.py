"""Gemini adapter for snapshot synthesis and question generation.

Wraps the CGS GeminiAdapter for onboarding-specific synthesis tasks.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from core.infrastructure.external_services.gemini_adapter import GeminiAdapter as CgsGeminiAdapter
from core.domain.value_objects.provider_config import ProviderConfig, LLMProvider
from onboarding.config.settings import OnboardingSettings
from onboarding.domain.models import (
    CompanySnapshot,
    CompanyInfo,
    AudienceInfo,
    VoiceInfo,
    InsightsInfo,
    ClarifyingQuestion,
    SourceMetadata,
    Evidence,
)

logger = logging.getLogger(__name__)


class GeminiSynthesisAdapter:
    """
    Adapter for Gemini synthesis in onboarding flow.
    
    Reuses CGS GeminiAdapter with onboarding-specific prompts.
    """
    
    def __init__(self, settings: OnboardingSettings):
        """
        Initialize Gemini synthesis adapter.
        
        Args:
            settings: Onboarding settings with Gemini configuration
        """
        self.settings = settings
        
        if not settings.is_gemini_configured():
            raise ValueError("Gemini not configured (API key or Vertex required)")
        
        # Initialize CGS Gemini adapter
        self.adapter = CgsGeminiAdapter(
            api_key=settings.gemini_api_key,
            project_id=settings.gcp_project_id,
            location=settings.gcp_location,
            use_vertex=settings.use_vertex_gemini,
            sa_credentials_path=settings.google_application_credentials,
        )
        
        # Create provider config
        self.config = ProviderConfig(
            provider=LLMProvider.GEMINI,
            model=settings.gemini_model,
            temperature=settings.gemini_temperature,
            max_tokens=settings.gemini_max_tokens,
        )
        
        logger.info(
            f"Gemini synthesis adapter initialized: model={settings.gemini_model}, "
            f"vertex={settings.use_vertex_gemini}"
        )
    
    def _build_synthesis_prompt(
        self,
        brand_name: str,
        research_content: str,
        website: Optional[str] = None,
    ) -> str:
        """Build prompt for company snapshot synthesis."""
        prompt = f"""You are an expert business analyst synthesizing company research into a structured snapshot.

COMPANY: {brand_name}
"""
        if website:
            prompt += f"WEBSITE: {website}\n"
        
        prompt += f"""
RESEARCH DATA:
{research_content}

YOUR TASK:
Analyze the research and produce a structured JSON response with the following schema:

{{
  "company": {{
    "name": "{brand_name}",
    "legal_name": "string or null",
    "website": "{website or 'null'}",
    "industry": "string or null",
    "headquarters": "string or null",
    "size_range": "string or null (e.g., '50-200 employees')",
    "description": "concise company description (2-3 sentences)",
    "key_offerings": ["offering1", "offering2", ...],
    "differentiators": ["differentiator1", "differentiator2", ...],
    "evidence": [
      {{"source": "source_reference", "excerpt": "relevant quote", "confidence": 0.9}}
    ]
  }},
  "audience": {{
    "primary": "primary target audience",
    "secondary": ["secondary audience 1", "secondary audience 2"],
    "pain_points": ["pain point 1", "pain point 2"],
    "desired_outcomes": ["outcome 1", "outcome 2"]
  }},
  "voice": {{
    "tone": "professional|conversational|authoritative|playful|bold",
    "style_guidelines": ["guideline 1", "guideline 2"],
    "forbidden_phrases": ["phrase to avoid"],
    "cta_preferences": ["preferred CTA style"]
  }},
  "insights": {{
    "positioning": "market positioning statement",
    "key_messages": ["message 1", "message 2"],
    "recent_news": ["news item 1", "news item 2"],
    "competitors": ["competitor 1", "competitor 2"]
  }},
  "clarifying_questions": [
    {{
      "id": "q1",
      "question": "What specific aspect of [topic] should we focus on?",
      "reason": "To tailor content to business priorities",
      "expected_response_type": "string",
      "options": null,
      "required": true
    }},
    {{
      "id": "q2",
      "question": "What is your preferred content length?",
      "reason": "To match audience attention span",
      "expected_response_type": "enum",
      "options": ["short (200-300 words)", "medium (400-600 words)", "long (800+ words)"],
      "required": true
    }},
    {{
      "id": "q3",
      "question": "Should we include data/statistics?",
      "reason": "To determine content depth and credibility approach",
      "expected_response_type": "boolean",
      "options": null,
      "required": false
    }}
  ]
}}

IMPORTANT GUIDELINES:
1. Generate EXACTLY 3 clarifying questions (no more, no less)
2. Questions should be specific, actionable, and relevant to content creation
3. Use question IDs: q1, q2, q3
4. expected_response_type must be one of: string, enum, boolean, number
5. **CRITICAL**: For enum types, you MUST provide 3-5 clear, specific options in the "options" array
   - Options should be complete, actionable choices (e.g., "short (200-300 words)", not just "short")
   - Each option should be self-explanatory and mutually exclusive
   - NEVER leave options as null for enum types
6. For string types, set options to null
7. For boolean types, set options to null (Yes/No is automatic)
8. For number types, set options to null
9. Extract evidence with source references where possible
10. Infer brand voice from communication style in research
11. Be concise but comprehensive

**VALIDATION RULES**:
- If expected_response_type is "enum", options MUST be a non-empty array
- If expected_response_type is NOT "enum", options MUST be null

Return ONLY valid JSON, no markdown formatting or explanations.
"""
        return prompt
    
    async def synthesize_snapshot(
        self,
        brand_name: str,
        research_result: Dict[str, Any],
        trace_id: Optional[str] = None,
    ) -> CompanySnapshot:
        """
        Synthesize company snapshot from research.
        
        Args:
            brand_name: Company name
            research_result: Research result from Perplexity
            trace_id: Optional trace ID for correlation
        
        Returns:
            CompanySnapshot with structured data and clarifying questions
        """
        logger.info(f"Synthesizing snapshot for: {brand_name}")
        
        # Build synthesis prompt
        prompt = self._build_synthesis_prompt(
            brand_name=brand_name,
            research_content=research_result.get("raw_content", ""),
            website=research_result.get("website"),
        )
        
        try:
            # Call Gemini via CGS adapter
            response = await self.adapter.generate_content(
                prompt=prompt,
                config=self.config,
            )
            
            # Parse JSON response
            content = response.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            data = json.loads(content)
            
            # Build CompanySnapshot from parsed data
            snapshot = CompanySnapshot(
                trace_id=trace_id,
                company=CompanyInfo(**data["company"]),
                audience=AudienceInfo(**data.get("audience", {})),
                voice=VoiceInfo(**data.get("voice", {})),
                insights=InsightsInfo(**data.get("insights", {})),
                clarifying_questions=[
                    ClarifyingQuestion(**q) for q in data["clarifying_questions"]
                ],
                source_metadata=[
                    SourceMetadata(
                        tool="perplexity",
                        cost_usd=research_result.get("cost_usd"),
                        token_usage=research_result.get("usage_tokens"),
                    )
                ],
            )
            
            logger.info(
                f"Snapshot synthesized: {len(snapshot.clarifying_questions)} questions"
            )
            
            return snapshot
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini JSON response: {str(e)}")
            logger.debug(f"Raw response: {response[:500]}...")
            raise ValueError(f"Invalid JSON from Gemini: {str(e)}")
        except Exception as e:
            logger.error(f"Snapshot synthesis failed: {str(e)}")
            raise

