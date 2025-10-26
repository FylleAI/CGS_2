#!/usr/bin/env python3
"""
CGSRef Backend Debug Startup Script
===================================

Enhanced backend startup with detailed logging for troubleshooting.
Includes request/response logging, performance monitoring, and error tracking.

Author: Senior DevOps Engineer
Priority: PRODUCTION-READY - Enhanced logging for troubleshooting
"""

import sys
import os
import uvicorn
import logging
import time
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# Configure enhanced logging
def setup_enhanced_logging():
    """Setup enhanced logging configuration."""

    # Create logs directory
    os.makedirs("logs", exist_ok=True)

    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
        handlers=[
            # Console handler
            logging.StreamHandler(sys.stdout),
            # File handler for all logs
            logging.FileHandler(
                f"logs/cgsref_backend_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            ),
            # Error-only file handler
            logging.FileHandler("logs/cgsref_errors.log", mode="a"),
        ],
    )

    # Set specific log levels for different components
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.DEBUG)

    # Enhanced logging for our modules
    logging.getLogger("services.content_workflow.application").setLevel(logging.DEBUG)
    logging.getLogger("services.content_workflow.infrastructure").setLevel(logging.DEBUG)
    logging.getLogger("api.rest").setLevel(logging.DEBUG)

    # Suppress noisy third-party logs
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.INFO)
    logging.getLogger("anthropic").setLevel(logging.INFO)


def log_startup_info():
    """Log startup information."""
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("🚀 CGSRef Backend Starting in DEBUG Mode")
    logger.info("=" * 60)
    logger.info(f"📅 Startup Time: {datetime.now().isoformat()}")
    logger.info(f"🐍 Python Version: {sys.version}")
    logger.info(f"📁 Working Directory: {os.getcwd()}")
    logger.info(f"🔧 Environment Variables:")

    # Log important environment variables (without sensitive data)
    env_vars = [
        "API_HOST",
        "API_PORT",
        "ENVIRONMENT",
        "DEBUG",
        "DEFAULT_PROVIDER",
        "DEFAULT_MODEL",
    ]

    for var in env_vars:
        value = os.getenv(var, "NOT_SET")
        logger.info(f"   {var}: {value}")

    # Log API key status (without revealing keys)
    api_keys = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "DEEPSEEK_API_KEY",
        "SERPER_API_KEY",
    ]
    logger.info(f"🔑 API Keys Status:")
    for key in api_keys:
        status = "SET" if os.getenv(key) else "NOT_SET"
        logger.info(f"   {key}: {status}")

    logger.info("=" * 60)


def log_performance_metrics():
    """Log performance metrics periodically."""
    import psutil
    import threading

    def log_metrics():
        logger = logging.getLogger("performance")
        while True:
            try:
                # System metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage("/")

                logger.info(f"📊 Performance Metrics:")
                logger.info(f"   CPU Usage: {cpu_percent}%")
                logger.info(
                    f"   Memory Usage: {memory.percent}% ({memory.used / 1024**3:.1f}GB / {memory.total / 1024**3:.1f}GB)"
                )
                logger.info(
                    f"   Disk Usage: {disk.percent}% ({disk.used / 1024**3:.1f}GB / {disk.total / 1024**3:.1f}GB)"
                )

                time.sleep(300)  # Log every 5 minutes
            except Exception as e:
                logger.error(f"Error logging performance metrics: {e}")
                time.sleep(60)  # Retry after 1 minute on error

    # Start performance monitoring in background thread
    thread = threading.Thread(target=log_metrics, daemon=True)
    thread.start()


def main():
    """Main function to start the backend with enhanced logging."""

    # Setup enhanced logging
    setup_enhanced_logging()
    logger = logging.getLogger(__name__)

    try:
        # Log startup information
        log_startup_info()

        # Start performance monitoring
        log_performance_metrics()

        # Import the app (this will trigger all initialization)
        logger.info("📦 Importing FastAPI application...")
        from api.rest.main import app

        logger.info("✅ FastAPI application imported successfully")

        # Get settings
        from services.content_workflow.infrastructure.config.settings import get_settings

        settings = get_settings()

        logger.info(f"⚙️ Configuration loaded:")
        logger.info(f"   API Host: {settings.api_host}")
        logger.info(f"   API Port: {settings.api_port}")
        logger.info(f"   Environment: {settings.environment}")
        logger.info(f"   Debug Mode: {settings.debug}")
        logger.info(f"   Available Providers: {settings.get_available_providers()}")

        # Start the server
        logger.info("🌐 Starting Uvicorn server...")
        logger.info(
            f"🔗 Server will be available at: http://{settings.api_host}:{settings.api_port}"
        )
        logger.info(
            f"📚 API Documentation: http://{settings.api_host}:{settings.api_port}/docs"
        )
        logger.info(
            f"💚 Health Check: http://{settings.api_host}:{settings.api_port}/health"
        )

        uvicorn.run(
            app,
            host=settings.api_host,
            port=settings.api_port,
            log_level="debug",
            reload=False,  # Disable reload in debug mode for stability
            access_log=True,
            use_colors=True,
        )

    except KeyboardInterrupt:
        logger.info("🛑 Received shutdown signal (Ctrl+C)")
        logger.info("👋 CGSRef Backend shutting down gracefully...")

    except Exception as e:
        logger.error(f"❌ Fatal error during startup: {e}")
        logger.error("💥 Stack trace:", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
