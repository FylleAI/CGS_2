#!/usr/bin/env python3
"""Test tracking integration (manual test).

Prerequisiti:
- pip install supabase>=2.0.0
- .env configurato con SUPABASE_URL, SUPABASE_ANON_KEY, USE_SUPABASE=true

Esecuzione:
- python test_tracking_integration.py
"""
from __future__ import annotations

import asyncio
import sys

from api.cli.main import get_use_case
from core.application.dto.content_request import ContentGenerationRequest
from core.domain.entities.content import ContentType, ContentFormat
from core.domain.value_objects.provider_config import ProviderConfig, LLMProvider


async def test_tracking_integration() -> bool:
    print("🧪 Testing tracking integration...")
    try:
        request = ContentGenerationRequest(
            topic="Test AI Article for Tracking",
            content_type=ContentType.ARTICLE,
            content_format=ContentFormat.MARKDOWN,
            client_profile="siebert",
            workflow_type="enhanced_article",
            provider_config=ProviderConfig(
                provider=LLMProvider.OPENAI,
                model="gpt-4o-mini",
                temperature=0.7,
            ),
        )

        use_case = get_use_case()
        response = await use_case.execute(request)

        if response.success:
            print("✅ Content generated successfully!")
            print(f"   Content ID: {response.content_id}")
            print(f"   Word count: {response.word_count}")
            if response.generation_time_seconds is not None:
                print(f"   Generation time: {response.generation_time_seconds:.2f}s")
            print("\n📊 Check tracking with: python -m api.cli.main tracking history")
            return True
        else:
            print(f"❌ Generation failed: {response.error_message}")
            return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_tracking_integration())
    sys.exit(0 if success else 1)

