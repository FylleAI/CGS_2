"""
Example usage of the onboarding service.

This demonstrates the complete onboarding flow:
1. Research company via Perplexity
2. Synthesize snapshot via Gemini
3. Display clarifying questions
4. Collect user answers
5. Build CGS payload
6. Execute workflow
"""

import asyncio
import json
from pathlib import Path

from services.onboarding.config.settings import get_onboarding_settings
from services.onboarding.infrastructure.adapters.perplexity_adapter import PerplexityAdapter
from services.onboarding.infrastructure.adapters.gemini_adapter import GeminiSynthesisAdapter
from services.onboarding.infrastructure.adapters.cgs_adapter import CgsAdapter
from services.onboarding.domain.models import (
    OnboardingGoal,
    OnboardingSession,
    SessionState,
)
from services.onboarding.domain.cgs_contracts import (
    CgsPayloadLinkedInPost,
    LinkedInPostInput,
    CgsPayloadMetadata,
)


async def example_onboarding_flow():
    """Complete onboarding flow example."""
    
    print("=" * 80)
    print("🚀 ONBOARDING SERVICE - EXAMPLE FLOW")
    print("=" * 80)
    
    # 1. Initialize settings
    print("\n📋 Step 1: Loading configuration...")
    settings = get_onboarding_settings()
    
    # Validate services
    services = settings.validate_required_services()
    print(f"   ✓ Perplexity: {'✅' if services['perplexity'] else '❌'}")
    print(f"   ✓ Gemini: {'✅' if services['gemini'] else '❌'}")
    print(f"   ✓ CGS: {'✅' if services['cgs'] else '❌'}")
    print(f"   ✓ Brevo: {'✅' if services['brevo'] else '❌'}")
    print(f"   ✓ Supabase: {'✅' if services['supabase'] else '❌'}")
    
    # 2. Create onboarding session
    print("\n📝 Step 2: Creating onboarding session...")
    session = OnboardingSession(
        brand_name="Fylle AI",
        website="https://fylle.ai",
        goal=OnboardingGoal.LINKEDIN_POST,
        user_email="davide@fylle.ai",
    )
    print(f"   Session ID: {session.session_id}")
    print(f"   Trace ID: {session.trace_id}")
    print(f"   Goal: {session.goal}")
    print(f"   State: {session.state}")
    
    # 3. Research company with Perplexity
    print("\n🔍 Step 3: Researching company with Perplexity...")
    session.update_state(SessionState.RESEARCHING)
    
    perplexity = PerplexityAdapter(settings)
    research_result = await perplexity.research_company(
        brand_name=session.brand_name,
        website=session.website,
        additional_context="Focus on AI-powered content generation capabilities",
    )
    
    print(f"   ✓ Research completed")
    print(f"   Model: {research_result['model_used']}")
    print(f"   Tokens: {research_result['usage_tokens']}")
    print(f"   Cost: ${research_result['cost_usd']:.4f}")
    print(f"   Duration: {research_result['duration_ms']}ms")
    print(f"\n   Preview (first 300 chars):")
    print(f"   {research_result['raw_content'][:300]}...")
    
    # 4. Synthesize snapshot with Gemini
    print("\n🧠 Step 4: Synthesizing company snapshot with Gemini...")
    session.update_state(SessionState.SYNTHESIZING)
    
    gemini = GeminiSynthesisAdapter(settings)
    snapshot = await gemini.synthesize_snapshot(
        brand_name=session.brand_name,
        research_result=research_result,
        trace_id=session.trace_id,
    )
    
    session.snapshot = snapshot
    
    print(f"   ✓ Snapshot synthesized")
    print(f"   Snapshot ID: {snapshot.snapshot_id}")
    print(f"\n   📊 Company Info:")
    print(f"      Name: {snapshot.company.name}")
    print(f"      Industry: {snapshot.company.industry}")
    print(f"      Description: {snapshot.company.description[:150]}...")
    print(f"      Key Offerings: {len(snapshot.company.key_offerings)} items")
    print(f"      Differentiators: {len(snapshot.company.differentiators)} items")
    
    print(f"\n   👥 Audience:")
    print(f"      Primary: {snapshot.audience.primary}")
    print(f"      Pain Points: {len(snapshot.audience.pain_points)} identified")
    
    print(f"\n   🎨 Voice:")
    print(f"      Tone: {snapshot.voice.tone}")
    print(f"      Style Guidelines: {len(snapshot.voice.style_guidelines)} items")
    
    # 5. Display clarifying questions
    print("\n❓ Step 5: Clarifying questions generated...")
    session.update_state(SessionState.AWAITING_USER)
    
    for i, question in enumerate(snapshot.clarifying_questions, 1):
        print(f"\n   Question {i} (ID: {question.id}):")
        print(f"   Q: {question.question}")
        print(f"   Reason: {question.reason}")
        print(f"   Type: {question.expected_response_type}")
        if question.options:
            print(f"   Options: {', '.join(question.options)}")
        print(f"   Required: {'Yes' if question.required else 'No'}")
    
    # 6. Simulate user answers
    print("\n💬 Step 6: Collecting user answers (simulated)...")
    
    # Simulate answers based on question types
    for question in snapshot.clarifying_questions:
        if question.expected_response_type == "string":
            answer = "AI-powered content generation and automation"
        elif question.expected_response_type == "enum" and question.options:
            answer = question.options[1]  # Pick middle option
        elif question.expected_response_type == "boolean":
            answer = True
        elif question.expected_response_type == "number":
            answer = 500
        else:
            answer = "Default answer"
        
        snapshot.add_answer(question.id, answer)
        print(f"   ✓ {question.id}: {answer}")
    
    print(f"\n   Snapshot complete: {snapshot.is_complete()}")
    
    # 7. Build CGS payload
    print("\n📦 Step 7: Building CGS payload...")
    session.update_state(SessionState.PAYLOAD_READY)
    
    # Build LinkedIn post input from snapshot
    linkedin_input = LinkedInPostInput(
        topic="AI-powered content generation for modern businesses",
        client_name=snapshot.company.name,
        client_profile="default",
        target_audience=snapshot.audience.primary or "Business professionals",
        tone=snapshot.voice.tone or "professional",
        context=snapshot.company.description,
        key_points=snapshot.company.differentiators[:3],
        target_word_count=300,
        include_statistics=True,
        include_examples=True,
        include_sources=True,
        custom_instructions=f"Focus on: {', '.join(snapshot.company.key_offerings[:2])}",
    )
    
    payload = CgsPayloadLinkedInPost(
        session_id=session.session_id,
        trace_id=session.trace_id,
        company_snapshot=snapshot,
        clarifying_answers=snapshot.clarifying_answers,
        input=linkedin_input,
        metadata=CgsPayloadMetadata(
            source="onboarding_adapter",
            dry_run=False,
            language="it",
        ),
    )
    
    session.cgs_payload = payload.model_dump()
    
    print(f"   ✓ Payload built")
    print(f"   Workflow: {payload.workflow}")
    print(f"   Goal: {payload.goal}")
    print(f"   Topic: {payload.input.topic}")
    print(f"   Target audience: {payload.input.target_audience}")
    print(f"   Tone: {payload.input.tone}")
    print(f"   Word count: {payload.input.target_word_count}")
    
    # 8. Save payload to file (for inspection)
    print("\n💾 Step 8: Saving artifacts...")
    
    output_dir = Path("data/onboarding/examples")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save snapshot
    snapshot_file = output_dir / f"snapshot_{session.session_id}.json"
    with open(snapshot_file, "w") as f:
        json.dump(snapshot.model_dump(mode="json"), f, indent=2, default=str)
    print(f"   ✓ Snapshot saved: {snapshot_file}")
    
    # Save payload
    payload_file = output_dir / f"payload_{session.session_id}.json"
    with open(payload_file, "w") as f:
        json.dump(payload.model_dump(mode="json"), f, indent=2, default=str)
    print(f"   ✓ Payload saved: {payload_file}")
    
    # Save session
    session_file = output_dir / f"session_{session.session_id}.json"
    with open(session_file, "w") as f:
        json.dump(session.model_dump(mode="json"), f, indent=2, default=str)
    print(f"   ✓ Session saved: {session_file}")
    
    # 9. Execute CGS workflow (optional - commented out to avoid actual execution)
    print("\n🎯 Step 9: CGS workflow execution...")
    print("   ⚠️  Skipping actual CGS execution in example")
    print("   To execute, uncomment the code below:")
    print()
    print("   ```python")
    print("   session.update_state(SessionState.EXECUTING)")
    print("   cgs = CgsAdapter(settings)")
    print("   result = await cgs.execute_workflow(payload)")
    print("   session.cgs_response = result.model_dump()")
    print("   ```")
    
    # Simulate success
    session.update_state(SessionState.DONE)
    
    print("\n" + "=" * 80)
    print("✅ ONBOARDING FLOW COMPLETED")
    print("=" * 80)
    print(f"\nSession ID: {session.session_id}")
    print(f"Final State: {session.state}")
    print(f"\nArtifacts saved to: {output_dir}")
    print("\nNext steps:")
    print("1. Review generated snapshot and payload files")
    print("2. Uncomment CGS execution to test full flow")
    print("3. Add Brevo delivery for email sending")
    print("4. Persist session to Supabase for tracking")
    print()


async def example_payload_inspection():
    """Example: Inspect a generated payload structure."""
    
    print("\n" + "=" * 80)
    print("📋 PAYLOAD STRUCTURE EXAMPLE")
    print("=" * 80)
    
    from services.onboarding.domain.models import (
        CompanyInfo,
        AudienceInfo,
        VoiceInfo,
        InsightsInfo,
        ClarifyingQuestion,
        CompanySnapshot,
    )
    
    # Create example snapshot
    snapshot = CompanySnapshot(
        company=CompanyInfo(
            name="Fylle AI",
            website="https://fylle.ai",
            industry="AI/SaaS",
            description="AI-powered content generation platform",
            key_offerings=["Content automation", "Multi-agent workflows"],
            differentiators=["Clean architecture", "Multi-provider support"],
        ),
        audience=AudienceInfo(
            primary="Marketing teams and content creators",
            pain_points=["Time-consuming content creation", "Consistency issues"],
        ),
        voice=VoiceInfo(
            tone="professional",
            style_guidelines=["Clear and concise", "Data-driven"],
        ),
        insights=InsightsInfo(
            positioning="Enterprise-grade AI content platform",
            key_messages=["Automate content at scale", "Maintain brand voice"],
        ),
        clarifying_questions=[
            ClarifyingQuestion(
                id="q1",
                question="What topic should we focus on?",
                reason="To tailor content",
                expected_response_type="string",
                required=True,
            ),
        ],
    )
    
    # Add answer
    snapshot.add_answer("q1", "AI automation benefits")
    
    # Create payload
    payload = CgsPayloadLinkedInPost(
        session_id="00000000-0000-0000-0000-000000000000",
        trace_id="example-trace",
        company_snapshot=snapshot,
        clarifying_answers=snapshot.clarifying_answers,
        input=LinkedInPostInput(
            topic="AI automation in content marketing",
            client_name="Fylle AI",
            target_audience="Marketing professionals",
            tone="professional",
            target_word_count=300,
        ),
    )
    
    # Display structure
    print("\n📦 Payload Structure:")
    print(json.dumps(payload.model_dump(mode="json"), indent=2, default=str))


if __name__ == "__main__":
    print("\n🎬 Starting onboarding service examples...\n")
    
    # Run main flow
    asyncio.run(example_onboarding_flow())
    
    # Show payload structure
    asyncio.run(example_payload_inspection())

