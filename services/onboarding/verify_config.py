#!/usr/bin/env python3
"""
Verify Onboarding Service Configuration

Checks that all required environment variables and files are properly configured.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def check_env_var(var_name: str, required: bool = True) -> Tuple[bool, str]:
    """Check if an environment variable is set."""
    value = os.getenv(var_name)
    if value:
        # Mask sensitive values
        if "KEY" in var_name or "SECRET" in var_name:
            masked = value[:8] + "..." if len(value) > 8 else "***"
            return True, f"✅ {var_name}={masked}"
        else:
            return True, f"✅ {var_name}={value}"
    else:
        status = "❌" if required else "⚠️"
        return not required, f"{status} {var_name} not set"


def check_file(file_path: str) -> Tuple[bool, str]:
    """Check if a file exists."""
    path = Path(file_path)
    if path.exists():
        return True, f"✅ File exists: {file_path}"
    else:
        return False, f"❌ File not found: {file_path}"


def main():
    """Run configuration verification."""
    print("=" * 70)
    print("🔍 Onboarding Service Configuration Verification")
    print("=" * 70)
    print()
    
    # Load .env file if exists
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        print(f"📄 Loading environment from: {env_file}")
        # Simple .env parser
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value
        print()
    else:
        print(f"⚠️  No .env file found at: {env_file}")
        print("   Checking system environment variables...")
        print()
    
    results: List[Tuple[bool, str]] = []
    
    # Service Configuration
    print("📋 Service Configuration")
    print("-" * 70)
    results.append(check_env_var("ONBOARDING_SERVICE_NAME", required=False))
    results.append(check_env_var("ONBOARDING_API_PORT", required=False))
    print()
    
    # CGS Integration
    print("🔗 CGS Integration")
    print("-" * 70)
    results.append(check_env_var("CGS_API_URL", required=True))
    results.append(check_env_var("CGS_API_KEY", required=True))
    results.append(check_env_var("CGS_API_TIMEOUT", required=False))
    print()
    
    # Perplexity
    print("🔍 Perplexity Research")
    print("-" * 70)
    results.append(check_env_var("PERPLEXITY_API_KEY", required=True))
    results.append(check_env_var("PERPLEXITY_MODEL", required=False))
    print()
    
    # Gemini / Vertex AI
    print("🤖 Gemini / Vertex AI")
    print("-" * 70)
    results.append(check_env_var("GEMINI_API_KEY", required=True))
    use_vertex = os.getenv("USE_VERTEX_GEMINI", "false").lower() == "true"
    results.append(check_env_var("USE_VERTEX_GEMINI", required=False))
    
    if use_vertex:
        print("   → Vertex AI mode enabled")
        results.append(check_env_var("GCP_PROJECT_ID", required=True))
        results.append(check_env_var("GCP_LOCATION", required=False))
        
        creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if creds_path:
            results.append(check_file(creds_path))
        else:
            results.append((False, "❌ GOOGLE_APPLICATION_CREDENTIALS not set"))
    print()
    
    # Brevo
    print("📧 Brevo Email Delivery")
    print("-" * 70)
    results.append(check_env_var("BREVO_API_KEY", required=True))
    results.append(check_env_var("BREVO_SENDER_EMAIL", required=False))
    print()
    
    # Supabase
    print("🗄️  Supabase Database")
    print("-" * 70)
    results.append(check_env_var("SUPABASE_URL", required=True))
    results.append(check_env_var("SUPABASE_ANON_KEY", required=True))
    results.append(check_env_var("USE_SUPABASE", required=False))
    print()
    
    # Summary
    print("=" * 70)
    print("📊 Summary")
    print("=" * 70)
    
    total = len(results)
    passed = sum(1 for ok, _ in results if ok)
    failed = total - passed
    
    for ok, msg in results:
        print(msg)
    
    print()
    print(f"Total checks: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print()
    
    if failed == 0:
        print("🎉 All checks passed! Configuration is complete.")
        print()
        print("Next steps:")
        print("1. Setup Supabase database (run SQL schema)")
        print("2. Start the service:")
        print("   uvicorn services.onboarding.api.main:app --reload --port 8001")
        print("3. Test with: curl http://localhost:8001/health")
        return 0
    else:
        print("⚠️  Some checks failed. Please fix the configuration.")
        print()
        print("See SETUP_CGS_INTEGRATION.md for detailed setup instructions.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

