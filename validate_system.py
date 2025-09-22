#!/usr/bin/env python3
"""
CGSRef System Validation Script
===============================

Final validation script to verify all fixes are working correctly.
Tests all critical functionality and provides a comprehensive report.

Author: Senior DevOps Engineer
Priority: PRODUCTION-READY - Final system validation
"""

import sys
import os
import json
import time
import logging
import requests
from pathlib import Path
from typing import Dict, Any, List

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SystemValidator:
    """Comprehensive system validation."""

    def __init__(self):
        self.backend_url = "http://localhost:8001"
        self.results = []

    def test_backend_health(self) -> Dict[str, Any]:
        """Test backend health endpoint."""
        logger.info("🔍 Testing backend health...")

        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    "test": "Backend Health",
                    "status": "PASS",
                    "message": "Backend is healthy and responding",
                    "details": data,
                }
            else:
                return {
                    "test": "Backend Health",
                    "status": "FAIL",
                    "message": f"Backend returned status {response.status_code}",
                    "details": {"status_code": response.status_code},
                }
        except Exception as e:
            return {
                "test": "Backend Health",
                "status": "FAIL",
                "message": f"Backend health check failed: {str(e)}",
                "details": {"error": str(e)},
            }

    def test_content_generation(self) -> Dict[str, Any]:
        """Test content generation functionality."""
        logger.info("🔍 Testing content generation...")

        test_request = {
            "topic": "Artificial Intelligence in Modern Healthcare",
            "content_type": "article",
            "target_audience": "healthcare professionals",
            "tone": "professional",
            "length": "medium",
            "provider": "openai",
            "model": "gpt-4o",
        }

        try:
            start_time = time.time()
            response = requests.post(
                f"{self.backend_url}/api/v1/content/generate",
                json=test_request,
                timeout=60,
            )
            end_time = time.time()

            if response.status_code == 200:
                result = response.json()

                # Validate response structure
                if (
                    result.get("success")
                    and result.get("body")
                    and len(result.get("body", "")) > 100
                ):
                    word_count = len(result.get("body", "").split())
                    return {
                        "test": "Content Generation",
                        "status": "PASS",
                        "message": f"Content generated successfully ({word_count} words)",
                        "details": {
                            "word_count": word_count,
                            "character_count": result.get("character_count", 0),
                            "execution_time": end_time - start_time,
                            "title": result.get("title", "")[:50] + "...",
                            "workflow_id": result.get("workflow_id"),
                            "tasks_completed": result.get("tasks_completed", 0),
                        },
                    }
                else:
                    return {
                        "test": "Content Generation",
                        "status": "FAIL",
                        "message": "Content generation returned empty or invalid result",
                        "details": {
                            "success": result.get("success"),
                            "error_message": result.get("error_message"),
                            "body_length": len(result.get("body", "")),
                        },
                    }
            else:
                return {
                    "test": "Content Generation",
                    "status": "FAIL",
                    "message": f"Content generation failed with status {response.status_code}",
                    "details": {
                        "status_code": response.status_code,
                        "response": response.text,
                    },
                }

        except Exception as e:
            return {
                "test": "Content Generation",
                "status": "FAIL",
                "message": f"Content generation request failed: {str(e)}",
                "details": {"error": str(e)},
            }

    def test_system_config(self) -> Dict[str, Any]:
        """Test system configuration endpoint."""
        logger.info("🔍 Testing system configuration...")

        try:
            response = requests.get(
                f"{self.backend_url}/api/v1/system/config", timeout=10
            )
            if response.status_code == 200:
                config = response.json()

                # Check if providers are configured
                providers = config.get("providers", {})
                configured_providers = [k for k, v in providers.items() if v]

                if configured_providers:
                    return {
                        "test": "System Configuration",
                        "status": "PASS",
                        "message": f"System configured with {len(configured_providers)} providers",
                        "details": {
                            "providers": providers,
                            "default_provider": config.get("default_provider"),
                            "default_model": config.get("default_model"),
                            "environment": config.get("environment"),
                        },
                    }
                else:
                    return {
                        "test": "System Configuration",
                        "status": "FAIL",
                        "message": "No AI providers configured",
                        "details": config,
                    }
            else:
                return {
                    "test": "System Configuration",
                    "status": "FAIL",
                    "message": f"Config endpoint returned status {response.status_code}",
                    "details": {"status_code": response.status_code},
                }
        except Exception as e:
            return {
                "test": "System Configuration",
                "status": "FAIL",
                "message": f"System config test failed: {str(e)}",
                "details": {"error": str(e)},
            }

    def test_workflow_endpoints(self) -> Dict[str, Any]:
        """Test workflow endpoints."""
        logger.info("🔍 Testing workflow endpoints...")

        try:
            # Test workflow execution endpoint
            test_request = {
                "workflow_id": "enhanced_article",
                "parameters": {
                    "topic": "Machine Learning Best Practices",
                    "target_audience": "developers",
                    "tone": "professional",
                    "client_name": "Test Client",  # Add required parameter
                },
            }

            response = requests.post(
                f"{self.backend_url}/api/v1/workflows/execute",
                json=test_request,
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return {
                        "test": "Workflow Endpoints",
                        "status": "PASS",
                        "message": "Workflow execution endpoint working",
                        "details": {
                            "workflow_id": result.get("workflow_id"),
                            "status": result.get("status"),
                            "execution_time": result.get("execution_time"),
                        },
                    }
                else:
                    return {
                        "test": "Workflow Endpoints",
                        "status": "PARTIAL",
                        "message": f"Workflow endpoint accessible but execution failed: {result.get('error_message')}",
                        "details": result,
                    }
            else:
                return {
                    "test": "Workflow Endpoints",
                    "status": "FAIL",
                    "message": f"Workflow endpoint returned status {response.status_code}",
                    "details": {
                        "status_code": response.status_code,
                        "response": response.text,
                    },
                }

        except Exception as e:
            return {
                "test": "Workflow Endpoints",
                "status": "FAIL",
                "message": f"Workflow endpoint test failed: {str(e)}",
                "details": {"error": str(e)},
            }

    def run_validation(self) -> Dict[str, Any]:
        """Run complete system validation."""
        logger.info("🚀 Starting CGSRef System Validation")
        logger.info("=" * 60)

        # Run all tests
        tests = [
            self.test_backend_health,
            self.test_system_config,
            self.test_content_generation,
            self.test_workflow_endpoints,
        ]

        for test_func in tests:
            result = test_func()
            self.results.append(result)

            # Log result
            status_emoji = {"PASS": "✅", "FAIL": "❌", "PARTIAL": "⚠️"}
            emoji = status_emoji.get(result["status"], "❓")
            logger.info(f"{emoji} {result['test']}: {result['message']}")

        # Summary
        logger.info("=" * 60)
        logger.info("📊 VALIDATION SUMMARY")
        logger.info("=" * 60)

        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        partial = sum(1 for r in self.results if r["status"] == "PARTIAL")

        logger.info(f"✅ PASSED: {passed}")
        logger.info(f"❌ FAILED: {failed}")
        logger.info(f"⚠️  PARTIAL: {partial}")
        logger.info(f"📊 TOTAL: {len(self.results)}")

        # Overall status
        if failed == 0 and passed >= 3:
            overall_status = "SYSTEM HEALTHY"
            logger.info(f"\n🎉 {overall_status} - All critical tests passed!")
        elif failed <= 1:
            overall_status = "SYSTEM MOSTLY HEALTHY"
            logger.info(f"\n⚠️ {overall_status} - Minor issues detected")
        else:
            overall_status = "SYSTEM ISSUES"
            logger.info(f"\n🚨 {overall_status} - Multiple failures detected")

        return {
            "overall_status": overall_status,
            "summary": {
                "passed": passed,
                "failed": failed,
                "partial": partial,
                "total": len(self.results),
            },
            "test_results": self.results,
        }


def main():
    """Main validation function."""
    print("🔧 CGSRef System Validation")
    print("=" * 50)
    print("Comprehensive validation of all system components")
    print("=" * 50)

    validator = SystemValidator()
    results = validator.run_validation()

    # Save results
    results_file = Path("validation_results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    logger.info(f"\n📄 Full results saved to: {results_file}")

    # Exit with appropriate code
    if results["summary"]["failed"] == 0:
        logger.info("\n✅ All validations passed!")
        sys.exit(0)
    else:
        logger.error(f"\n❌ {results['summary']['failed']} validation(s) failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
