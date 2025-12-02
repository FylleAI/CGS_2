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
        min_questions: int = 3,
        max_questions: int = 5,
    ) -> str:
        """Build prompt for company snapshot synthesis with dynamic questions."""
        prompt = f"""You are an expert business analyst synthesizing company research into a structured snapshot.

COMPANY: {brand_name}
"""
        if website:
            prompt += f"WEBSITE: {website}\n"

        prompt += f"""
RESEARCH DATA:
{research_content}

YOUR TASK:
1. Analyze the research data and identify what information is available vs missing
2. Generate a structured snapshot with all available data
3. Generate {min_questions} to {max_questions} TARGETED clarifying questions to fill data gaps

CARD TYPES TO POPULATE (each question should help fill these):
- ProductCard: valueProposition, features, differentiators, useCases
- TargetCard: icpName, painPoints, goals, communicationChannels, demographics
- BrandVoiceCard: toneDescription, styleGuidelines, dosExamples, dontsExamples
- CompetitorCard: competitorName, positioning, strengths, weaknesses
- TopicCard: description, keywords, angles, trends
- CampaignsCard: objective, keyMessages, tone, assets

OUTPUT JSON SCHEMA:

{{
  "company": {{
    "name": "{brand_name}",
    "legal_name": "string or null",
    "website": "{website or 'null'}",
    "industry": "string or null",
    "headquarters": "string or null",
    "size_range": "string or null",
    "description": "concise company description (2-3 sentences)",
    "key_offerings": ["offering1", "offering2"],
    "differentiators": ["differentiator1", "differentiator2"],
    "evidence": [{{"source": "source_reference", "excerpt": "relevant quote", "confidence": 0.9}}]
  }},
  "audience": {{
    "primary": "primary target audience",
    "secondary": ["secondary audience 1"],
    "pain_points": ["pain point 1", "pain point 2"],
    "desired_outcomes": ["outcome 1", "outcome 2"]
  }},
  "voice": {{
    "tone": "professional|conversational|authoritative|playful|bold",
    "style_guidelines": ["guideline 1"],
    "forbidden_phrases": ["phrase to avoid"],
    "cta_preferences": ["preferred CTA style"]
  }},
  "insights": {{
    "positioning": "market positioning statement",
    "key_messages": ["message 1", "message 2"],
    "recent_news": ["news item 1"],
    "competitors": ["competitor 1", "competitor 2"]
  }},
  "clarifying_questions": [
    {{
      "id": "q1",
      "question": "Qual è il tono di comunicazione che preferisci per il tuo brand?",
      "reason": "Per definire correttamente la brand voice e lo stile dei contenuti",
      "expected_response_type": "select",
      "options": ["Professionale e autorevole", "Amichevole e conversazionale", "Audace e provocatorio", "Informativo e educativo", "Altro"],
      "required": true,
      "maps_to": [
        {{"card_type": "brand_voice", "field_name": "toneDescription"}},
        {{"card_type": "campaigns", "field_name": "tone"}}
      ]
    }},
    {{
      "id": "q2",
      "question": "Qual è l'obiettivo principale dei tuoi contenuti?",
      "reason": "Per allineare le campagne e i topic agli obiettivi di business",
      "expected_response_type": "select",
      "options": ["Generare lead e nuovi clienti", "Aumentare brand awareness", "Fidelizzare clienti esistenti", "Educare il mercato", "Lanciare nuovi prodotti/servizi", "Altro"],
      "required": true,
      "maps_to": [
        {{"card_type": "target", "field_name": "goals"}},
        {{"card_type": "campaigns", "field_name": "objective"}}
      ]
    }},
    {{
      "id": "q3",
      "question": "Su quali canali comunichi principalmente con i tuoi clienti?",
      "reason": "Per personalizzare i contenuti per i canali giusti",
      "expected_response_type": "select",
      "options": ["LinkedIn e social professionali", "Instagram e social visual", "Email e newsletter", "Blog e sito web", "Eventi e webinar", "Mix di tutti"],
      "required": true,
      "maps_to": [
        {{"card_type": "target", "field_name": "communicationChannels"}},
        {{"card_type": "campaigns", "field_name": "assets"}}
      ]
    }}
  ]
}}

QUESTION GENERATION RULES:
1. Generate {min_questions} to {max_questions} questions based on DATA GAPS identified
2. Each question MUST include "maps_to" array linking to specific card fields
3. Prioritize questions that fill MULTIPLE card fields (high value)
4. Use ITALIAN language for question text and options
5. **ALL QUESTIONS MUST BE MULTIPLE CHOICE** - expected_response_type MUST ALWAYS be "select"
6. Every question MUST have 4-6 clear, mutually exclusive options in "options" array
7. Include an option like "Altro" or "Non applicabile" if needed for completeness
8. Focus on questions that enable better card generation

CRITICAL - QUESTION WORDING RULES:
- Questions must be STANDALONE and self-contained
- The USER HAS NO VISIBILITY into the research data - they only see the questions
- NEVER reference "data found", "information mentioned", "channels specified", or similar
- NEVER say "oltre a quelli identificati", "oltre ai canali specificati", etc.
- BAD: "Oltre ai competitor già identificati, ce ne sono altri?" (user doesn't know what was identified)
- GOOD: "Chi sono i tuoi principali competitor?" (standalone question)
- BAD: "Vuoi aggiungere altri canali oltre a quelli emersi?" (user doesn't know what emerged)
- GOOD: "Su quali canali comunichi con i tuoi clienti?" (standalone question)
- Questions should feel like a first conversation, not a follow-up to hidden context

QUESTION PRIORITY (ask about missing data first):
1. Brand voice/tone (if not clear from research) → BrandVoiceCard
2. Target goals/pain points (if incomplete) → TargetCard
3. Competitors (if none identified) → CompetitorCard
4. Content preferences/topics → TopicCard, CampaignsCard
5. Communication channels → TargetCard

Return ONLY valid JSON, no markdown or explanations.
"""
        return prompt
    
    async def synthesize_snapshot(
        self,
        brand_name: str,
        research_result: Dict[str, Any],
        trace_id: Optional[str] = None,
        min_questions: Optional[int] = None,
        max_questions: Optional[int] = None,
    ) -> CompanySnapshot:
        """
        Synthesize company snapshot from research.

        Args:
            brand_name: Company name
            research_result: Research result from Perplexity
            trace_id: Optional trace ID for correlation
            min_questions: Minimum questions to generate (default from settings)
            max_questions: Maximum questions to generate (default from settings)

        Returns:
            CompanySnapshot with structured data and clarifying questions
        """
        # Use settings defaults if not specified
        min_q = min_questions or self.settings.min_clarifying_questions
        max_q = max_questions or self.settings.max_clarifying_questions

        logger.info(
            f"Synthesizing snapshot for: {brand_name} "
            f"(questions: {min_q}-{max_q})"
        )

        # Build synthesis prompt
        prompt = self._build_synthesis_prompt(
            brand_name=brand_name,
            research_content=research_result.get("raw_content", ""),
            website=research_result.get("website"),
            min_questions=min_q,
            max_questions=max_q,
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

