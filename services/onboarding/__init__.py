"""
Onboarding Service - External adapter for automated client services.onboarding.

This service orchestrates the onboarding flow:
1. Research company via Perplexity
2. Synthesize snapshot via Gemini
3. Generate clarifying questions
4. Collect user responses
5. Build CGS payload
6. Execute CGS workflow
7. Deliver content via Brevo
8. Persist to Supabase

Architecture:
- Domain: Entities and value objects (CompanySnapshot, OnboardingSession)
- Application: Use cases and DTOs
- Infrastructure: External adapters (Perplexity, Gemini, Brevo, CGS, Supabase)
- API: FastAPI endpoints for onboarding flow
"""

__version__ = "1.0.0"

