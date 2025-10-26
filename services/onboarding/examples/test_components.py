"""
Test individual onboarding components.

Quick tests for each adapter without running the full flow.
"""

import asyncio
from services.onboarding.config.settings import get_onboarding_settings


async def test_settings():
    """Test settings configuration."""
    print("\n" + "=" * 60)
    print("🔧 Testing Settings Configuration")
    print("=" * 60)
    
    settings = get_onboarding_settings()
    
    print(f"\n📋 Service Info:")
    print(f"   Name: {settings.service_name}")
    print(f"   Version: {settings.service_version}")
    
    print(f"\n🌐 API Configuration:")
    print(f"   CGS URL: {settings.cgs_api_url}")
    print(f"   CGS Timeout: {settings.cgs_api_timeout}s")
    print(f"   Onboarding API: {settings.onboarding_api_host}:{settings.onboarding_api_port}")
    
    print(f"\n🤖 LLM Configuration:")
    print(f"   Perplexity Model: {settings.perplexity_model}")
    print(f"   Gemini Model: {settings.gemini_model}")
    print(f"   Use Vertex: {settings.use_vertex_gemini}")
    
    print(f"\n📧 Brevo Configuration:")
    print(f"   Sender: {settings.brevo_sender_name} <{settings.brevo_sender_email}>")
    
    print(f"\n⚙️  Workflow Settings:")
    print(f"   Max Questions: {settings.max_clarifying_questions}")
    print(f"   Session Timeout: {settings.session_timeout_minutes} min")
    print(f"   Auto Delivery: {settings.enable_auto_delivery}")
    
    print(f"\n✅ Service Validation:")
    services = settings.validate_required_services()
    for service, configured in services.items():
        status = "✅ Configured" if configured else "❌ Not configured"
        print(f"   {service.capitalize()}: {status}")
    
    print(f"\n📁 Storage Directories:")
    print(f"   Data: {settings.onboarding_data_dir}")
    print(f"   Sessions: {settings.onboarding_sessions_dir}")
    print(f"   Snapshots: {settings.onboarding_snapshots_dir}")
    
    print(f"\n🗺️  Workflow Mappings:")
    for goal, workflow in settings.default_workflow_mappings.items():
        print(f"   {goal} → {workflow}")


async def test_perplexity():
    """Test Perplexity adapter."""
    print("\n" + "=" * 60)
    print("🔍 Testing Perplexity Adapter")
    print("=" * 60)
    
    settings = get_onboarding_settings()
    
    if not settings.is_perplexity_configured():
        print("\n⚠️  Perplexity not configured. Set PERPLEXITY_API_KEY in .env")
        return
    
    from services.onboarding.infrastructure.adapters.perplexity_adapter import PerplexityAdapter
    
    adapter = PerplexityAdapter(settings)
    print(f"\n✓ Adapter initialized")
    print(f"  Model: {settings.perplexity_model}")
    print(f"  Timeout: {settings.perplexity_timeout}s")
    
    print(f"\n🔎 Researching 'Fylle AI'...")
    
    try:
        result = await adapter.research_company(
            brand_name="Fylle AI",
            website="https://fylle.ai",
            additional_context="Focus on AI content generation",
        )
        
        print(f"\n✅ Research completed!")
        print(f"   Model: {result['model_used']}")
        print(f"   Tokens: {result['usage_tokens']}")
        print(f"   Cost: ${result['cost_usd']:.4f}")
        print(f"   Duration: {result['duration_ms']}ms")
        print(f"\n   Content preview (first 200 chars):")
        print(f"   {result['raw_content'][:200]}...")
        
    except Exception as e:
        print(f"\n❌ Research failed: {str(e)}")


async def test_gemini():
    """Test Gemini adapter."""
    print("\n" + "=" * 60)
    print("🧠 Testing Gemini Adapter")
    print("=" * 60)
    
    settings = get_onboarding_settings()
    
    if not settings.is_gemini_configured():
        print("\n⚠️  Gemini not configured. Set GEMINI_API_KEY or Vertex credentials")
        return
    
    from services.onboarding.infrastructure.adapters.gemini_adapter import GeminiSynthesisAdapter
    
    adapter = GeminiSynthesisAdapter(settings)
    print(f"\n✓ Adapter initialized")
    print(f"  Model: {settings.gemini_model}")
    print(f"  Use Vertex: {settings.use_vertex_gemini}")
    print(f"  Temperature: {settings.gemini_temperature}")
    
    # Create mock research result
    mock_research = {
        "brand_name": "Fylle AI",
        "website": "https://fylle.ai",
        "raw_content": """
        Fylle AI is an enterprise-grade AI content generation platform that helps 
        marketing teams automate content creation at scale. The platform uses 
        multi-agent workflows and supports multiple LLM providers including OpenAI, 
        Anthropic, and Google Gemini. Key features include clean architecture, 
        modular design, and comprehensive cost tracking. Target audience includes 
        marketing teams, content creators, and enterprise clients looking to 
        maintain brand voice while scaling content production.
        """,
        "model_used": "sonar-pro",
        "usage_tokens": 500,
        "cost_usd": 0.05,
    }
    
    print(f"\n🔄 Synthesizing snapshot from mock research...")
    
    try:
        snapshot = await adapter.synthesize_snapshot(
            brand_name="Fylle AI",
            research_result=mock_research,
            trace_id="test-trace-123",
        )
        
        print(f"\n✅ Snapshot synthesized!")
        print(f"   Snapshot ID: {snapshot.snapshot_id}")
        print(f"   Company: {snapshot.company.name}")
        print(f"   Industry: {snapshot.company.industry}")
        print(f"   Description: {snapshot.company.description[:100]}...")
        print(f"   Questions: {len(snapshot.clarifying_questions)}")
        
        print(f"\n❓ Clarifying Questions:")
        for q in snapshot.clarifying_questions:
            print(f"   - {q.id}: {q.question}")
            print(f"     Type: {q.expected_response_type}")
        
    except Exception as e:
        print(f"\n❌ Synthesis failed: {str(e)}")


async def test_cgs_health():
    """Test CGS adapter health check."""
    print("\n" + "=" * 60)
    print("🏥 Testing CGS Health Check")
    print("=" * 60)
    
    settings = get_onboarding_settings()
    
    from services.onboarding.infrastructure.adapters.cgs_adapter import CgsAdapter
    
    adapter = CgsAdapter(settings)
    print(f"\n✓ Adapter initialized")
    print(f"  CGS URL: {settings.cgs_api_url}")
    print(f"  Timeout: {settings.cgs_api_timeout}s")
    
    print(f"\n🔍 Checking CGS health...")
    
    try:
        healthy = await adapter.health_check()
        
        if healthy:
            print(f"\n✅ CGS is healthy!")
        else:
            print(f"\n⚠️  CGS health check failed")
        
    except Exception as e:
        print(f"\n❌ Health check error: {str(e)}")


async def test_models():
    """Test domain models."""
    print("\n" + "=" * 60)
    print("📦 Testing Domain Models")
    print("=" * 60)
    
    from services.onboarding.domain.models import (
        OnboardingSession,
        OnboardingGoal,
        SessionState,
        CompanySnapshot,
        CompanyInfo,
        ClarifyingQuestion,
    )
    
    # Test session
    print(f"\n1️⃣  Creating OnboardingSession...")
    session = OnboardingSession(
        brand_name="Test Company",
        website="https://test.com",
        goal=OnboardingGoal.LINKEDIN_POST,
        user_email="test@test.com",
    )
    
    print(f"   ✓ Session ID: {session.session_id}")
    print(f"   ✓ State: {session.state}")
    print(f"   ✓ Goal: {session.goal}")
    
    # Test state transitions
    print(f"\n2️⃣  Testing state transitions...")
    session.update_state(SessionState.RESEARCHING)
    print(f"   ✓ State: {session.state}")
    
    session.update_state(SessionState.SYNTHESIZING)
    print(f"   ✓ State: {session.state}")
    
    # Test snapshot
    print(f"\n3️⃣  Creating CompanySnapshot...")
    snapshot = CompanySnapshot(
        company=CompanyInfo(
            name="Test Company",
            description="A test company",
            key_offerings=["Service 1", "Service 2"],
            differentiators=["Unique 1", "Unique 2"],
        ),
        clarifying_questions=[
            ClarifyingQuestion(
                id="q1",
                question="What is your focus?",
                reason="To tailor content",
                expected_response_type="string",
                required=True,
            ),
        ],
    )
    
    print(f"   ✓ Snapshot ID: {snapshot.snapshot_id}")
    print(f"   ✓ Company: {snapshot.company.name}")
    print(f"   ✓ Questions: {len(snapshot.clarifying_questions)}")
    
    # Test answers
    print(f"\n4️⃣  Adding answers...")
    snapshot.add_answer("q1", "AI automation")
    print(f"   ✓ Answer added: {snapshot.clarifying_answers}")
    print(f"   ✓ Complete: {snapshot.is_complete()}")
    
    # Test payload
    print(f"\n5️⃣  Creating CGS Payload...")
    from services.onboarding.domain.cgs_contracts import (
        CgsPayloadLinkedInPost,
        LinkedInPostInput,
    )
    
    payload = CgsPayloadLinkedInPost(
        session_id=session.session_id,
        trace_id=session.trace_id,
        company_snapshot=snapshot,
        clarifying_answers=snapshot.clarifying_answers,
        input=LinkedInPostInput(
            topic="Test topic",
            client_name="Test Company",
            target_audience="Test audience",
        ),
    )
    
    print(f"   ✓ Payload version: {payload.version}")
    print(f"   ✓ Workflow: {payload.workflow}")
    print(f"   ✓ Goal: {payload.goal}")
    
    print(f"\n✅ All models working correctly!")


async def run_all_tests():
    """Run all component tests."""
    await test_settings()
    await test_models()
    await test_cgs_health()
    
    # Optional: uncomment to test external APIs
    # await test_perplexity()
    # await test_gemini()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
    print("\nTo test external APIs, uncomment:")
    print("  - test_perplexity()")
    print("  - test_gemini()")
    print()


if __name__ == "__main__":
    asyncio.run(run_all_tests())

