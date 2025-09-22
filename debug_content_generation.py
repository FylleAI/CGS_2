#!/usr/bin/env python3
"""
CGSRef Content Generation Debug Script
=====================================

Direct testing of content generation workflow to identify why output is empty.
Tests the complete flow from API endpoint to LLM providers.

Author: Senior DevOps Engineer
Priority: CRITICAL - Fix empty content generation (0 words, 0.00647s)
"""

import sys
import os
import json
import time
import logging
import requests
from pathlib import Path
from typing import Dict, Any, Optional

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ContentGenerationDebugger:
    """Debug content generation issues."""

    def __init__(self):
        self.backend_url = "http://localhost:8001"
        self.test_requests = []

    def test_api_connectivity(self) -> bool:
        """Test basic API connectivity."""
        logger.info("🔍 Testing API connectivity...")

        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code == 200:
                logger.info("✅ API connectivity OK")
                return True
            else:
                logger.error(f"❌ API returned status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ API connectivity failed: {e}")
            return False

    def test_system_info(self) -> Dict[str, Any]:
        """Get system configuration info."""
        logger.info("🔍 Getting system info...")

        try:
            response = requests.get(
                f"{self.backend_url}/api/v1/system/config", timeout=10
            )
            if response.status_code == 200:
                config = response.json()
                logger.info("✅ System config retrieved")
                logger.info(f"   Providers: {config.get('providers', {})}")
                logger.info(f"   Default provider: {config.get('default_provider')}")
                logger.info(f"   Default model: {config.get('default_model')}")
                return config
            else:
                logger.error(f"❌ Failed to get system config: {response.status_code}")
                return {}
        except Exception as e:
            logger.error(f"❌ Error getting system config: {e}")
            return {}

    def test_simple_content_generation(self) -> Dict[str, Any]:
        """Test simple content generation request."""
        logger.info("🔍 Testing simple content generation...")

        # Simple test request
        test_request = {
            "topic": "Artificial Intelligence in Healthcare",
            "content_type": "article",
            "target_audience": "general",
            "tone": "informative",
            "length": "medium",
            "provider": "openai",
            "model": "gpt-4o",
        }

        logger.info(f"📤 Sending request: {json.dumps(test_request, indent=2)}")

        try:
            start_time = time.time()
            response = requests.post(
                f"{self.backend_url}/api/v1/content/generate",
                json=test_request,
                timeout=60,
                headers={"Content-Type": "application/json"},
            )
            end_time = time.time()

            duration = end_time - start_time
            logger.info(f"⏱️ Request completed in {duration:.3f}s")

            if response.status_code == 200:
                result = response.json()
                logger.info("✅ Content generation request successful")

                # Analyze the result
                content = result.get("content", "")
                word_count = len(content.split()) if content else 0

                logger.info(f"📊 Result analysis:")
                logger.info(f"   Status: {result.get('status', 'unknown')}")
                logger.info(f"   Content length: {len(content)} characters")
                logger.info(f"   Word count: {word_count} words")
                logger.info(f"   Duration: {duration:.3f}s")

                if word_count == 0:
                    logger.error("❌ PROBLEM FOUND: Content is empty!")
                    logger.error(f"   Full response: {json.dumps(result, indent=2)}")
                else:
                    logger.info("✅ Content generated successfully")
                    logger.info(f"   Preview: {content[:200]}...")

                return {
                    "success": True,
                    "result": result,
                    "word_count": word_count,
                    "duration": duration,
                    "status_code": response.status_code,
                }
            else:
                logger.error(f"❌ Content generation failed: {response.status_code}")
                logger.error(f"   Response: {response.text}")
                return {
                    "success": False,
                    "error": response.text,
                    "status_code": response.status_code,
                    "duration": duration,
                }

        except requests.exceptions.Timeout:
            logger.error("❌ Request timed out")
            return {"success": False, "error": "timeout"}
        except Exception as e:
            logger.error(f"❌ Request failed: {e}")
            return {"success": False, "error": str(e)}

    def test_workflow_generation(self) -> Dict[str, Any]:
        """Test workflow-based content generation."""
        logger.info("🔍 Testing workflow-based generation...")

        # Test with enhanced_article workflow
        workflow_request = {
            "workflow_id": "enhanced_article",
            "parameters": {
                "topic": "Machine Learning Best Practices",
                "target_audience": "developers",
                "tone": "professional",
                "include_examples": True,
                "include_references": True,
            },
        }

        logger.info(
            f"📤 Sending workflow request: {json.dumps(workflow_request, indent=2)}"
        )

        try:
            start_time = time.time()
            response = requests.post(
                f"{self.backend_url}/api/v1/workflows/execute",
                json=workflow_request,
                timeout=120,
                headers={"Content-Type": "application/json"},
            )
            end_time = time.time()

            duration = end_time - start_time
            logger.info(f"⏱️ Workflow completed in {duration:.3f}s")

            if response.status_code == 200:
                result = response.json()
                logger.info("✅ Workflow execution successful")

                # Analyze workflow result
                outputs = result.get("outputs", {})
                content = outputs.get("content", "") if outputs else ""
                word_count = len(content.split()) if content else 0

                logger.info(f"📊 Workflow result analysis:")
                logger.info(f"   Status: {result.get('status', 'unknown')}")
                logger.info(f"   Content length: {len(content)} characters")
                logger.info(f"   Word count: {word_count} words")
                logger.info(f"   Duration: {duration:.3f}s")

                if word_count == 0:
                    logger.error("❌ PROBLEM FOUND: Workflow content is empty!")
                    logger.error(f"   Full response: {json.dumps(result, indent=2)}")
                else:
                    logger.info("✅ Workflow content generated successfully")

                return {
                    "success": True,
                    "result": result,
                    "word_count": word_count,
                    "duration": duration,
                    "status_code": response.status_code,
                }
            else:
                logger.error(f"❌ Workflow execution failed: {response.status_code}")
                logger.error(f"   Response: {response.text}")
                return {
                    "success": False,
                    "error": response.text,
                    "status_code": response.status_code,
                    "duration": duration,
                }

        except Exception as e:
            logger.error(f"❌ Workflow request failed: {e}")
            return {"success": False, "error": str(e)}

    def test_direct_llm_call(self) -> Dict[str, Any]:
        """Test direct LLM provider call."""
        logger.info("🔍 Testing direct LLM provider call...")

        try:
            # Import and test LLM provider directly
            from core.infrastructure.llm.openai_provider import OpenAIProvider
            from core.infrastructure.config.settings import get_settings
            from core.domain.value_objects.provider_config import (
                ProviderConfig,
                LLMProvider,
            )

            settings = get_settings()

            if not settings.openai_api_key:
                logger.error("❌ OpenAI API key not configured")
                return {"success": False, "error": "no_api_key"}

            # Create provider config
            config = ProviderConfig(
                provider=LLMProvider.OPENAI,
                model="gpt-4o",
                api_key=settings.openai_api_key,
            )

            # Test direct provider call
            provider = OpenAIProvider(config)

            test_prompt = "Write a short paragraph about artificial intelligence."

            logger.info(f"📤 Testing direct LLM call with prompt: {test_prompt}")

            start_time = time.time()
            response = provider.generate_text(test_prompt)
            end_time = time.time()

            duration = end_time - start_time
            word_count = len(response.split()) if response else 0

            logger.info(f"⏱️ Direct LLM call completed in {duration:.3f}s")
            logger.info(f"📊 Direct LLM result:")
            logger.info(f"   Response length: {len(response)} characters")
            logger.info(f"   Word count: {word_count} words")

            if word_count == 0:
                logger.error("❌ PROBLEM FOUND: Direct LLM call returned empty!")
                logger.error(f"   Response: '{response}'")
            else:
                logger.info("✅ Direct LLM call successful")
                logger.info(f"   Preview: {response[:200]}...")

            return {
                "success": True,
                "response": response,
                "word_count": word_count,
                "duration": duration,
            }

        except Exception as e:
            logger.error(f"❌ Direct LLM call failed: {e}")
            return {"success": False, "error": str(e)}

    def run_full_debug(self) -> Dict[str, Any]:
        """Run complete content generation debugging."""
        logger.info("🚀 Starting Content Generation Debug Session")
        logger.info("=" * 60)

        results = {}

        # Test 1: API Connectivity
        results["api_connectivity"] = self.test_api_connectivity()

        # Test 2: System Info
        results["system_info"] = self.test_system_info()

        # Test 3: Simple Content Generation
        results["simple_generation"] = self.test_simple_content_generation()

        # Test 4: Workflow Generation
        results["workflow_generation"] = self.test_workflow_generation()

        # Test 5: Direct LLM Call
        results["direct_llm"] = self.test_direct_llm_call()

        # Summary
        logger.info("=" * 60)
        logger.info("📊 DEBUG SUMMARY")
        logger.info("=" * 60)

        successful_tests = sum(
            1
            for test in results.values()
            if isinstance(test, dict) and test.get("success", False)
        )
        total_tests = len(
            [
                test
                for test in results.values()
                if isinstance(test, dict) and "success" in test
            ]
        )

        logger.info(f"✅ Successful tests: {successful_tests}/{total_tests}")

        # Identify the root cause
        if not results.get("api_connectivity"):
            logger.error("🚨 ROOT CAUSE: API connectivity issue")
        elif results.get("direct_llm", {}).get("success"):
            logger.error("🚨 ROOT CAUSE: Issue in API layer or workflow processing")
        elif not results.get("direct_llm", {}).get("success"):
            logger.error("🚨 ROOT CAUSE: LLM provider configuration issue")
        else:
            logger.info("✅ All tests passed - issue may be intermittent")

        return results


def main():
    """Main debug function."""
    print("🔧 CGSRef Content Generation Debugger")
    print("=" * 50)
    print("Identifying why content generation returns empty results")
    print("=" * 50)

    debugger = ContentGenerationDebugger()
    results = debugger.run_full_debug()

    # Save results
    results_file = Path("content_debug_results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    logger.info(f"\n📄 Full debug results saved to: {results_file}")


if __name__ == "__main__":
    main()
