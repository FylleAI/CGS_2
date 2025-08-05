#!/usr/bin/env python3
"""Test script for Gemini integration."""

import asyncio
import os
from core.infrastructure.config.settings import Settings
from core.infrastructure.factories.provider_factory import LLMProviderFactory
from core.domain.value_objects.provider_config import LLMProvider, ProviderConfig

async def test_gemini_integration():
    """Test Gemini integration with API key."""
    print("🧪 Testing Gemini Integration...")

    # Test 1: Check if Gemini is in LLMProvider enum
    print("\n1. Testing LLMProvider enum...")
    try:
        gemini_provider = LLMProvider.GEMINI
        print(f"   ✅ GEMINI provider found: {gemini_provider.value}")
    except AttributeError:
        print("   ❌ GEMINI provider not found in enum")
        return False

    # Test 2: Check ProviderConfig helper method
    print("\n2. Testing ProviderConfig helper method...")
    try:
        config = ProviderConfig.create_gemini_config()
        print(f"   ✅ Gemini config created: {config.provider.value}, model: {config.model}")
    except Exception as e:
        print(f"   ❌ Failed to create Gemini config: {e}")
        return False

    # Test 3: Check Settings integration
    print("\n3. Testing Settings integration...")
    try:
        settings = Settings()
        available_providers = settings.get_available_providers()
        print(f"   ✅ Available providers: {list(available_providers.keys())}")
        print(f"   ✅ Gemini available: {available_providers.get('gemini', False)}")

        # Check API key
        gemini_key = settings.get_provider_api_key('gemini')
        if gemini_key:
            print(f"   ✅ Gemini API key configured: {gemini_key[:10]}...")
        else:
            print("   ❌ Gemini API key not found")
            return False

    except Exception as e:
        print(f"   ❌ Settings test failed: {e}")
        return False

    # Test 4: Check ProviderFactory integration
    print("\n4. Testing ProviderFactory integration...")
    try:
        factory_providers = LLMProviderFactory.get_available_providers(settings)
        print(f"   ✅ Factory providers: {list(factory_providers.keys())}")
        print(f"   ✅ Gemini in factory: {'gemini' in factory_providers}")
    except Exception as e:
        print(f"   ❌ ProviderFactory test failed: {e}")
        return False

    # Test 5: Test GeminiAdapter import
    print("\n5. Testing GeminiAdapter import...")
    try:
        from core.infrastructure.external_services.gemini_adapter import GeminiAdapter
        adapter = GeminiAdapter()
        print("   ✅ GeminiAdapter imported and instantiated successfully")
    except Exception as e:
        print(f"   ❌ GeminiAdapter import failed: {e}")
        return False

    # Test 6: Test provider creation with API key
    print("\n6. Testing provider creation with API key...")
    try:
        provider = LLMProviderFactory.create_provider(LLMProvider.GEMINI, settings)
        print("   ✅ Gemini provider created successfully")
    except Exception as e:
        print(f"   ❌ Provider creation failed: {e}")
        return False

    # Test 7: Test config creation with factory
    print("\n7. Testing config creation with factory...")
    try:
        config = LLMProviderFactory.create_provider_config(
            LLMProvider.GEMINI,
            settings,
            model="gemini-1.5-pro"
        )
        print(f"   ✅ Config created: {config.provider.value}, model: {config.model}")
    except Exception as e:
        print(f"   ❌ Config creation failed: {e}")
        return False

    # Test 8: Test actual content generation
    print("\n8. Testing content generation...")
    try:
        response = await provider.generate_content(
            prompt="Hello! Please respond with 'Gemini is working correctly!'",
            config=config
        )
        print(f"   ✅ Content generated: {response[:100]}...")

        if "gemini" in response.lower() or "working" in response.lower():
            print("   ✅ Response seems appropriate")
        else:
            print("   ⚠️  Response might be unexpected but generation worked")

    except Exception as e:
        print(f"   ❌ Content generation failed: {e}")
        return False

    # Test 9: Test detailed response
    print("\n9. Testing detailed response...")
    try:
        detailed_response = await provider.generate_content_detailed(
            prompt="What is 2+2?",
            config=config
        )
        print(f"   ✅ Detailed response: {detailed_response.content[:50]}...")
        print(f"   ✅ Usage info: {detailed_response.usage}")
        print(f"   ✅ Model: {detailed_response.model}")

    except Exception as e:
        print(f"   ❌ Detailed response failed: {e}")
        return False

    # Test 10: Test available models
    print("\n10. Testing available models...")
    try:
        models = await provider.get_available_models(config)
        print(f"   ✅ Available models: {models[:3]}...")  # Show first 3

    except Exception as e:
        print(f"   ❌ Models fetch failed: {e}")
        return False

    print("\n🎉 All tests passed! Gemini integration is fully functional!")
    print("\n📊 Gemini Provider Summary:")
    print(f"   • Provider: {config.provider.value}")
    print(f"   • Default Model: {config.model}")
    print(f"   • API Key: Configured ✅")
    print(f"   • Content Generation: Working ✅")
    print(f"   • Detailed Responses: Working ✅")
    print(f"   • Available Models: {len(models)} models found")

    return True

if __name__ == "__main__":
    asyncio.run(test_gemini_integration())
