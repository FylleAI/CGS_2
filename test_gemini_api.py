#!/usr/bin/env python3
"""Test Gemini via API endpoint."""

import asyncio
import httpx
import json

async def test_gemini_api():
    """Test Gemini through the API endpoint."""
    print("🧪 Testing Gemini via API...")
    
    # Test 1: Check available providers
    print("\n1. Testing available providers...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8001/api/v1/content/providers")
            
            if response.status_code == 200:
                data = response.json()
                providers = data.get('providers', [])
                provider_names = [p['name'] for p in providers]
                print(f"   ✅ Available providers: {provider_names}")

                gemini_provider = next((p for p in providers if p['name'] == 'gemini'), None)
                if gemini_provider:
                    print(f"   ✅ Gemini available: {gemini_provider['available']}")
                    print(f"   ✅ Gemini models: {gemini_provider['models']}")
                else:
                    print("   ❌ Gemini not found in providers")
                    return False
            else:
                print(f"   ❌ API request failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"   ❌ API test failed: {e}")
        return False
    
    # Test 2: Test content generation with Gemini
    print("\n2. Testing content generation with Gemini...")
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "topic": "Test Gemini Integration",
                "content_type": "article",
                "content_format": "markdown",
                "client_profile": "siebert",
                "workflow_type": "enhanced_article",
                "provider": "gemini",
                "model": "gemini-1.5-pro",
                "temperature": 0.7,
                "target_word_count": 200,
                "tone": "professional",
                "include_statistics": False,
                "include_examples": False,
                "target_audience": "developers",
                "include_sources": False,
                "client_name": "Test Client",
                "brand_voice": "Technical and informative",
                "custom_instructions": "Write a brief test article about Gemini AI integration."
            }
            
            response = await client.post(
                "http://localhost:8001/api/v1/content/generate",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Content generated successfully!")
                print(f"   ✅ Content length: {len(result.get('content', ''))} characters")
                print(f"   ✅ Provider used: {result.get('metadata', {}).get('provider', 'unknown')}")
                print(f"   ✅ Model used: {result.get('metadata', {}).get('model', 'unknown')}")
                
                # Show first 100 characters of content
                content = result.get('content', '')
                if content:
                    print(f"   ✅ Content preview: {content[:100]}...")
                else:
                    print("   ⚠️  No content in response")
                    
            else:
                print(f"   ❌ Content generation failed: {response.status_code}")
                print(f"   ❌ Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"   ❌ Content generation test failed: {e}")
        return False
    
    print("\n🎉 All API tests passed! Gemini is working through the API!")
    return True

if __name__ == "__main__":
    asyncio.run(test_gemini_api())
