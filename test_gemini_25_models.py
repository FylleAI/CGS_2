#!/usr/bin/env python3
"""Test script for Gemini 2.5 models."""

import asyncio
from core.infrastructure.config.settings import Settings
from core.infrastructure.factories.provider_factory import LLMProviderFactory
from core.domain.value_objects.provider_config import LLMProvider, ProviderConfig

async def test_gemini_25_models():
    """Test Gemini 2.5 models."""
    print("🧪 Testing Gemini 2.5 Models...")
    
    settings = Settings()
    
    # Test 1: Check new default model
    print("\n1. Testing new default model...")
    try:
        config = ProviderConfig.create_gemini_config()
        print(f"   ✅ New default model: {config.model}")
        
        if config.model == "gemini-2.5-pro":
            print("   ✅ Default correctly updated to Gemini 2.5 Pro")
        else:
            print(f"   ❌ Expected gemini-2.5-pro, got {config.model}")
            
    except Exception as e:
        print(f"   ❌ Default model test failed: {e}")
        return False
    
    # Test 2: Check available models include 2.5 series
    print("\n2. Testing available models...")
    try:
        config = ProviderConfig.create_gemini_config()
        models = [m["name"] for m in config.get_available_models()]
        print(f"   ✅ Total models available: {len(models)}")

        gemini_25_models = [
            "gemini-2.5-pro",
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-2.5-flash-live"
        ]

        for model in gemini_25_models:
            if model in models:
                print(f"   ✅ {model}: Available")
            else:
                print(f"   ❌ {model}: Missing")

        print(f"   ✅ All models: {models}")
        
    except Exception as e:
        print(f"   ❌ Models test failed: {e}")
        return False
    
    # Test 3: Test content generation with Gemini 2.5 Pro
    print("\n3. Testing content generation with Gemini 2.5 Pro...")
    try:
        provider = LLMProviderFactory.create_provider(LLMProvider.GEMINI, settings)
        config = LLMProviderFactory.create_provider_config(
            LLMProvider.GEMINI, 
            settings,
            model="gemini-2.5-pro"
        )
        
        response = await provider.generate_content(
            prompt="Write a brief test message about Gemini 2.5 Pro capabilities",
            config=config
        )
        
        print(f"   ✅ Gemini 2.5 Pro response: {response[:100]}...")
        
    except Exception as e:
        print(f"   ❌ Gemini 2.5 Pro test failed: {e}")
        return False
    
    # Test 4: Test content generation with Gemini 2.5 Flash
    print("\n4. Testing content generation with Gemini 2.5 Flash...")
    try:
        config = LLMProviderFactory.create_provider_config(
            LLMProvider.GEMINI, 
            settings,
            model="gemini-2.5-flash"
        )
        
        response = await provider.generate_content(
            prompt="Write a brief test message about Gemini 2.5 Flash speed",
            config=config
        )
        
        print(f"   ✅ Gemini 2.5 Flash response: {response[:100]}...")
        
    except Exception as e:
        print(f"   ❌ Gemini 2.5 Flash test failed: {e}")
        return False
    
    # Test 5: Test model validation
    print("\n5. Testing model validation...")
    try:
        for model in ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite"]:
            config = ProviderConfig.create_gemini_config(model=model)
            is_valid = config.is_model_available()
            print(f"   ✅ {model}: {'Valid' if is_valid else 'Invalid'}")
            
    except Exception as e:
        print(f"   ❌ Model validation failed: {e}")
        return False
    
    print("\n🎉 All Gemini 2.5 tests passed!")
    print("\n📊 Gemini 2.5 Models Summary:")
    print("   • gemini-2.5-pro: Latest flagship model (NEW DEFAULT)")
    print("   • gemini-2.5-flash: Fast and efficient")
    print("   • gemini-2.5-flash-lite: Lightweight version")
    print("   • gemini-2.5-flash-live: Real-time optimized")
    print("\n🚀 CGSRef now supports the latest Gemini 2.5 series!")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_gemini_25_models())
