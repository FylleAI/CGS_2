#!/usr/bin/env python3
"""
Test script for CompanyContextRepository

This script tests the basic CRUD operations of the CompanyContextRepository.

Usage:
    python scripts/test_company_context_repository.py
"""

import asyncio
import sys
from pathlib import Path
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from onboarding.config.settings import get_onboarding_settings
from onboarding.infrastructure.repositories.company_context_repository import CompanyContextRepository
from onboarding.domain.models import (
    CompanySnapshot,
    CompanyInfo,
    AudienceInfo,
    VoiceInfo,
    InsightsInfo,
    ClarifyingQuestion,
)


def create_test_snapshot() -> CompanySnapshot:
    """Create a test CompanySnapshot."""
    return CompanySnapshot(
        company=CompanyInfo(
            name="Test Company",
            description="A test company for RAG testing",
            industry="Software",
            key_offerings=["Product A", "Product B", "Service C"],
            differentiators=["Fast", "Reliable", "Affordable"],
        ),
        audience=AudienceInfo(
            primary="Small businesses",
            pain_points=["High costs", "Complex setup"],
            demographics="SMBs with 10-50 employees",
        ),
        voice=VoiceInfo(
            tone="Professional yet friendly",
            style_guidelines=["Clear", "Concise", "Action-oriented"],
            forbidden_phrases=["Synergy", "Leverage"],
        ),
        insights=InsightsInfo(
            positioning="The affordable solution for SMBs",
            key_messages=["Save time", "Save money", "Easy to use"],
            content_opportunities=["Case studies", "How-to guides"],
        ),
        clarifying_questions=[
            ClarifyingQuestion(
                id="q1",
                question="What is your main topic?",
                reason="To understand the content focus",
                expected_response_type="string",
            )
        ],
    )


async def test_repository():
    """Test the CompanyContextRepository."""
    print("=" * 80)
    print("Testing CompanyContextRepository")
    print("=" * 80)
    print()
    
    # Initialize
    settings = get_onboarding_settings()
    repo = CompanyContextRepository(settings)
    
    print("✅ Repository initialized")
    print()
    
    # Test 1: RAG lookup (should not find)
    print("Test 1: RAG lookup for non-existent company")
    print("-" * 80)
    
    result = await repo.find_by_company_name("TestCompanyRAG")
    
    if result is None:
        print("✅ PASS: No context found (expected)")
    else:
        print("❌ FAIL: Found context when none should exist")
        return
    
    print()
    
    # Test 2: Create context
    print("Test 2: Create new company context")
    print("-" * 80)
    
    snapshot = create_test_snapshot()
    session_id = uuid4()
    
    context = await repo.create_context(
        company_name="TestCompanyRAG",
        company_display_name="Test Company RAG",
        website="https://testcompany.com",
        snapshot=snapshot,
        source_session_id=session_id,
    )
    
    print(f"✅ Context created:")
    print(f"   - context_id: {context['context_id']}")
    print(f"   - company_name: {context['company_name']}")
    print(f"   - version: {context['version']}")
    print(f"   - industry: {context['industry']}")
    print(f"   - tags: {context['tags']}")
    print()
    
    context_id = context['context_id']
    
    # Test 3: RAG lookup (should find)
    print("Test 3: RAG lookup for existing company")
    print("-" * 80)
    
    result = await repo.find_by_company_name("TestCompanyRAG")
    
    if result and result['context_id'] == context_id:
        print("✅ PASS: Found context")
        print(f"   - context_id: {result['context_id']}")
        print(f"   - usage_count: {result['usage_count']}")
    else:
        print("❌ FAIL: Context not found or wrong ID")
        return
    
    print()
    
    # Test 4: Increment usage
    print("Test 4: Increment usage count")
    print("-" * 80)
    
    await repo.increment_usage(context_id)
    
    result = await repo.get_by_id(context_id)
    
    if result and result['usage_count'] == 1:
        print("✅ PASS: Usage count incremented")
        print(f"   - usage_count: {result['usage_count']}")
        print(f"   - last_used_at: {result['last_used_at']}")
    else:
        print(f"❌ FAIL: Usage count not incremented (got {result['usage_count'] if result else 'None'})")
        return
    
    print()
    
    # Test 5: Name normalization
    print("Test 5: Name normalization (different formats should match)")
    print("-" * 80)
    
    test_names = [
        "TestCompanyRAG",
        "test company rag",
        "test-company-rag",
        "TEST COMPANY RAG",
        "Test-Company-RAG",
    ]
    
    for name in test_names:
        result = await repo.find_by_company_name(name)
        if result and result['context_id'] == context_id:
            print(f"✅ '{name}' → matched")
        else:
            print(f"❌ '{name}' → NOT matched")
            return
    
    print()
    
    # Test 6: Create new version
    print("Test 6: Create new version (should deactivate old)")
    print("-" * 80)
    
    new_snapshot = create_test_snapshot()
    new_snapshot.company.description = "Updated description"
    
    new_context = await repo.create_context(
        company_name="TestCompanyRAG",
        company_display_name="Test Company RAG",
        website="https://testcompany.com",
        snapshot=new_snapshot,
        source_session_id=uuid4(),
    )
    
    print(f"✅ New version created:")
    print(f"   - context_id: {new_context['context_id']}")
    print(f"   - version: {new_context['version']}")
    print(f"   - is_active: {new_context['is_active']}")
    print()
    
    # Check old version is deactivated
    old_context = await repo.get_by_id(context_id)
    
    if old_context and not old_context['is_active']:
        print("✅ Old version deactivated")
        print(f"   - version: {old_context['version']}")
        print(f"   - is_active: {old_context['is_active']}")
    else:
        print("❌ FAIL: Old version still active")
        return
    
    print()
    
    # Test 7: RAG lookup returns latest version
    print("Test 7: RAG lookup returns latest active version")
    print("-" * 80)
    
    result = await repo.find_by_company_name("TestCompanyRAG")
    
    if result and result['context_id'] == new_context['context_id']:
        print("✅ PASS: Latest version returned")
        print(f"   - context_id: {result['context_id']}")
        print(f"   - version: {result['version']}")
    else:
        print("❌ FAIL: Wrong version returned")
        return
    
    print()
    
    # Test 8: List contexts
    print("Test 8: List all contexts")
    print("-" * 80)
    
    contexts = await repo.list_contexts(limit=10)
    
    print(f"✅ Found {len(contexts)} contexts")
    for ctx in contexts[:3]:  # Show first 3
        print(f"   - {ctx['company_display_name']} (v{ctx['version']}, active={ctx['is_active']})")
    
    print()
    
    # Cleanup
    print("Cleanup: Deactivating test contexts")
    print("-" * 80)
    
    await repo.deactivate_context(new_context['context_id'])
    
    print("✅ Test contexts deactivated")
    print()
    
    # Final summary
    print("=" * 80)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  1. Verify contexts in Supabase Table Editor")
    print("  2. Proceed with Step 3: RAG Integration in Use Cases")


if __name__ == "__main__":
    asyncio.run(test_repository())

