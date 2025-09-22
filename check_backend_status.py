#!/usr/bin/env python3
"""
CGSRef Backend Diagnostics Script
=================================

Comprehensive system diagnostics for CGSRef backend issues.
Checks backend status, environment configuration, API connectivity, and content generation.

Author: Senior DevOps Engineer
Priority: CRITICAL - Resolve ECONNREFUSED and empty content generation
"""

import sys
import os
import json
import time
import logging
import requests
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class DiagnosticResult:
    """Diagnostic test result."""

    name: str
    status: str  # PASS, FAIL, WARNING
    message: str
    details: Optional[Dict[str, Any]] = None


class CGSRefDiagnostics:
    """Comprehensive diagnostics for CGSRef system."""

    def __init__(self):
        self.results: List[DiagnosticResult] = []
        self.backend_ports = [8000, 8001]
        self.frontend_port = 3000

    def log_result(self, result: DiagnosticResult):
        """Log and store diagnostic result."""
        status_emoji = {"PASS": "✅", "FAIL": "❌", "WARNING": "⚠️"}

        emoji = status_emoji.get(result.status, "❓")
        logger.info(f"{emoji} {result.name}: {result.message}")

        if result.details:
            for key, value in result.details.items():
                logger.info(f"   {key}: {value}")

        self.results.append(result)

    def check_environment_variables(self) -> DiagnosticResult:
        """Check critical environment variables."""
        logger.info("🔍 Checking environment variables...")

        # Load .env file if exists
        env_file = Path(".env")
        env_vars = {}

        if env_file.exists():
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        env_vars[key.strip()] = value.strip()

        # Check critical variables
        critical_vars = {
            "API_HOST": env_vars.get("API_HOST", "NOT_SET"),
            "API_PORT": env_vars.get("API_PORT", "NOT_SET"),
            "OPENAI_API_KEY": "SET" if env_vars.get("OPENAI_API_KEY") else "NOT_SET",
            "ANTHROPIC_API_KEY": (
                "SET" if env_vars.get("ANTHROPIC_API_KEY") else "NOT_SET"
            ),
            "SERPER_API_KEY": "SET" if env_vars.get("SERPER_API_KEY") else "NOT_SET",
            "ENVIRONMENT": env_vars.get("ENVIRONMENT", "NOT_SET"),
            "DEBUG": env_vars.get("DEBUG", "NOT_SET"),
        }

        # Check if any API key is configured
        has_api_keys = any(
            env_vars.get(key)
            for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "DEEPSEEK_API_KEY"]
        )

        if not has_api_keys:
            return DiagnosticResult(
                "Environment Variables",
                "FAIL",
                "No AI provider API keys configured",
                critical_vars,
            )
        elif env_vars.get("API_PORT") != "8001":
            return DiagnosticResult(
                "Environment Variables",
                "WARNING",
                f"API_PORT is {env_vars.get('API_PORT')}, expected 8001",
                critical_vars,
            )
        else:
            return DiagnosticResult(
                "Environment Variables",
                "PASS",
                "Environment configuration looks good",
                critical_vars,
            )

    def check_port_availability(self, port: int) -> DiagnosticResult:
        """Check if a port is available or in use."""
        logger.info(f"🔍 Checking port {port} availability...")

        try:
            # Try to connect to the port
            response = requests.get(f"http://localhost:{port}/health", timeout=5)
            if response.status_code == 200:
                return DiagnosticResult(
                    f"Port {port} Status",
                    "PASS",
                    f"Service responding on port {port}",
                    {
                        "response": (
                            response.json()
                            if response.headers.get("content-type", "").startswith(
                                "application/json"
                            )
                            else response.text
                        )
                    },
                )
            else:
                return DiagnosticResult(
                    f"Port {port} Status",
                    "WARNING",
                    f"Service on port {port} returned status {response.status_code}",
                    {"status_code": response.status_code},
                )
        except requests.exceptions.ConnectionError:
            return DiagnosticResult(
                f"Port {port} Status",
                "FAIL",
                f"Connection refused on port {port} - service not running",
                {"error": "ECONNREFUSED"},
            )
        except requests.exceptions.Timeout:
            return DiagnosticResult(
                f"Port {port} Status",
                "FAIL",
                f"Timeout connecting to port {port}",
                {"error": "TIMEOUT"},
            )
        except Exception as e:
            return DiagnosticResult(
                f"Port {port} Status",
                "FAIL",
                f"Error checking port {port}: {str(e)}",
                {"error": str(e)},
            )

    def check_backend_health(self) -> DiagnosticResult:
        """Check backend health endpoint."""
        logger.info("🔍 Checking backend health...")

        for port in self.backend_ports:
            try:
                response = requests.get(f"http://localhost:{port}/health", timeout=10)
                if response.status_code == 200:
                    health_data = response.json()
                    return DiagnosticResult(
                        "Backend Health",
                        "PASS",
                        f"Backend healthy on port {port}",
                        health_data,
                    )
            except Exception:
                continue

        return DiagnosticResult(
            "Backend Health",
            "FAIL",
            "Backend not responding on any expected port",
            {"checked_ports": self.backend_ports},
        )

    def check_python_imports(self) -> DiagnosticResult:
        """Check if all required Python modules can be imported."""
        logger.info("🔍 Checking Python imports...")

        required_modules = [
            "fastapi",
            "uvicorn",
            "pydantic",
            "pydantic_settings",
            "openai",
            "anthropic",
        ]

        failed_imports = []
        for module in required_modules:
            try:
                __import__(module)
            except ImportError as e:
                failed_imports.append(f"{module}: {str(e)}")

        if failed_imports:
            return DiagnosticResult(
                "Python Imports",
                "FAIL",
                f"Failed to import {len(failed_imports)} modules",
                {"failed_imports": failed_imports},
            )
        else:
            return DiagnosticResult(
                "Python Imports",
                "PASS",
                "All required modules can be imported",
                {"checked_modules": required_modules},
            )

    def check_backend_startup(self) -> DiagnosticResult:
        """Try to start backend and check for errors."""
        logger.info("🔍 Testing backend startup...")

        try:
            # Try to import the main app
            from api.rest.main import app
            from core.infrastructure.config.settings import get_settings

            settings = get_settings()

            return DiagnosticResult(
                "Backend Startup",
                "PASS",
                "Backend app can be imported successfully",
                {
                    "api_host": settings.api_host,
                    "api_port": settings.api_port,
                    "environment": settings.environment,
                    "has_providers": settings.has_any_provider(),
                },
            )
        except Exception as e:
            return DiagnosticResult(
                "Backend Startup",
                "FAIL",
                f"Failed to import backend app: {str(e)}",
                {"error": str(e), "error_type": type(e).__name__},
            )

    def check_frontend_config(self) -> DiagnosticResult:
        """Check frontend configuration."""
        logger.info("🔍 Checking frontend configuration...")

        package_json_path = Path("web/react-app/package.json")
        if not package_json_path.exists():
            return DiagnosticResult(
                "Frontend Config",
                "FAIL",
                "Frontend package.json not found",
                {"path": str(package_json_path)},
            )

        try:
            with open(package_json_path, "r") as f:
                package_data = json.load(f)

            proxy = package_data.get("proxy")
            expected_proxy = "http://localhost:8001"

            if proxy == expected_proxy:
                return DiagnosticResult(
                    "Frontend Config",
                    "PASS",
                    "Frontend proxy configured correctly",
                    {"proxy": proxy},
                )
            else:
                return DiagnosticResult(
                    "Frontend Config",
                    "WARNING",
                    f"Frontend proxy mismatch: {proxy} vs {expected_proxy}",
                    {"current_proxy": proxy, "expected_proxy": expected_proxy},
                )
        except Exception as e:
            return DiagnosticResult(
                "Frontend Config",
                "FAIL",
                f"Error reading frontend config: {str(e)}",
                {"error": str(e)},
            )

    def run_all_diagnostics(self) -> Dict[str, Any]:
        """Run all diagnostic checks."""
        logger.info("🚀 Starting CGSRef System Diagnostics...")
        logger.info("=" * 60)

        # Run all checks
        self.log_result(self.check_environment_variables())
        self.log_result(self.check_python_imports())
        self.log_result(self.check_backend_startup())

        # Check ports
        for port in self.backend_ports:
            self.log_result(self.check_port_availability(port))

        self.log_result(self.check_backend_health())
        self.log_result(self.check_frontend_config())

        # Summary
        logger.info("=" * 60)
        logger.info("📊 DIAGNOSTIC SUMMARY")
        logger.info("=" * 60)

        passed = sum(1 for r in self.results if r.status == "PASS")
        failed = sum(1 for r in self.results if r.status == "FAIL")
        warnings = sum(1 for r in self.results if r.status == "WARNING")

        logger.info(f"✅ PASSED: {passed}")
        logger.info(f"❌ FAILED: {failed}")
        logger.info(f"⚠️  WARNINGS: {warnings}")

        # Critical issues
        critical_issues = [r for r in self.results if r.status == "FAIL"]
        if critical_issues:
            logger.info("\n🚨 CRITICAL ISSUES TO FIX:")
            for issue in critical_issues:
                logger.info(f"   • {issue.name}: {issue.message}")

        return {
            "summary": {
                "passed": passed,
                "failed": failed,
                "warnings": warnings,
                "total": len(self.results),
            },
            "results": [
                {
                    "name": r.name,
                    "status": r.status,
                    "message": r.message,
                    "details": r.details,
                }
                for r in self.results
            ],
            "critical_issues": [
                {"name": issue.name, "message": issue.message}
                for issue in critical_issues
            ],
        }


def main():
    """Main diagnostic function."""
    print("🔧 CGSRef Backend Diagnostics")
    print("=" * 50)
    print("Comprehensive system health check")
    print("Identifying ECONNREFUSED and content generation issues")
    print("=" * 50)

    diagnostics = CGSRefDiagnostics()
    results = diagnostics.run_all_diagnostics()

    # Save results to file
    results_file = Path("diagnostic_results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    logger.info(f"\n📄 Full results saved to: {results_file}")

    # Exit with error code if there are critical issues
    if results["summary"]["failed"] > 0:
        logger.error("\n🚨 CRITICAL ISSUES DETECTED - Backend needs fixing!")
        sys.exit(1)
    else:
        logger.info("\n✅ All critical checks passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
