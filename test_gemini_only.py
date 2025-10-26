"""
Test CGS and Onboarding service integration.
"""
import asyncio
from services.onboarding.config.settings import get_onboarding_settings


async def test_configuration():
    """Test configuration loading."""
    print("\n" + "=" * 60)
    print("⚙️  Testing Configuration")
    print("=" * 60)

    settings = get_onboarding_settings()

    print(f"\n📋 Service Info:")
    print(f"   Name: {settings.service_name}")
    print(f"   Version: {settings.service_version}")

    print(f"\n🌐 API Configuration:")
    print(f"   CGS URL: {settings.cgs_api_url}")
    print(f"   Onboarding Port: {settings.onboarding_api_port}")

    print(f"\n🤖 LLM Configuration:")
    print(f"   Gemini Model: {settings.gemini_model}")
    print(f"   Use Vertex: {settings.use_vertex_gemini}")
    if settings.use_vertex_gemini:
        print(f"   GCP Project: {settings.gcp_project_id}")
        print(f"   GCP Location: {settings.gcp_location}")

    print(f"\n✅ Service Validation:")
    validation = settings.validate_required_services()
    for service, configured in validation.items():
        status = "✅" if configured else "❌"
        print(f"   {service.capitalize()}: {status}")

    return settings


async def test_cgs_connection(settings):
    """Test CGS backend connection."""
    print("\n" + "=" * 60)
    print("🔗 Testing CGS Connection")
    print("=" * 60)

    from services.onboarding.infrastructure.adapters.cgs_adapter import CgsAdapter

    try:
        adapter = CgsAdapter(settings)
        print(f"\n✓ Adapter initialized")
        print(f"   CGS URL: {settings.cgs_api_url}")
        print(f"   Timeout: {settings.cgs_api_timeout}s")

        print("\n🔍 Checking CGS health...")
        is_healthy = await adapter.health_check()

        if is_healthy:
            print("\n✅ CGS backend is healthy!")
            return True
        else:
            print("\n⚠️ CGS backend health check failed")
            return False

    except Exception as e:
        print(f"\n❌ CGS connection failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_api_endpoints(settings):
    """Test API endpoints."""
    print("\n" + "=" * 60)
    print("🌐 Testing API Endpoints")
    print("=" * 60)

    import aiohttp

    endpoints = [
        ("CGS Backend", f"{settings.cgs_api_url}/health"),
        ("Onboarding Service", f"http://localhost:{settings.onboarding_api_port}/health"),
    ]

    for name, url in endpoints:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        print(f"\n✅ {name}: OK")
                        print(f"   URL: {url}")
                        print(f"   Response: {data}")
                    else:
                        print(f"\n⚠️ {name}: HTTP {resp.status}")
        except Exception as e:
            print(f"\n❌ {name}: {str(e)}")


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("🧪 CGS & ONBOARDING INTEGRATION TEST")
    print("=" * 60)

    settings = await test_configuration()
    cgs_healthy = await test_cgs_connection(settings)
    await test_api_endpoints(settings)

    print("\n" + "=" * 60)
    if cgs_healthy:
        print("✅ All tests completed successfully!")
        print("\n🎉 Sistema pronto per l'uso!")
        print(f"\n📍 Servizi attivi:")
        print(f"   - CGS Backend: {settings.cgs_api_url}")
        print(f"   - Onboarding API: http://localhost:{settings.onboarding_api_port}")
    else:
        print("⚠️ Some tests failed - check configuration")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

