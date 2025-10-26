"""Environment configuration utilities."""

import os
from enum import Enum
from typing import Optional


class Environment(Enum):
    """Application environments."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


def get_environment() -> Environment:
    """Get current environment from environment variable."""
    env_str = os.getenv("ENVIRONMENT", "development").lower()
    try:
        return Environment(env_str)
    except ValueError:
        return Environment.DEVELOPMENT


def is_development() -> bool:
    """Check if running in development environment."""
    return get_environment() == Environment.DEVELOPMENT


def is_production() -> bool:
    """Check if running in production environment."""
    return get_environment() == Environment.PRODUCTION


def is_testing() -> bool:
    """Check if running in testing environment."""
    return get_environment() == Environment.TESTING


def get_env_var(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get environment variable with optional default."""
    return os.getenv(key, default)


def get_env_var_bool(key: str, default: bool = False) -> bool:
    """Get boolean environment variable."""
    value = os.getenv(key, str(default)).lower()
    return value in ("true", "1", "yes", "on")


def get_env_var_int(key: str, default: int = 0) -> int:
    """Get integer environment variable."""
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default


def get_env_var_float(key: str, default: float = 0.0) -> float:
    """Get float environment variable."""
    try:
        return float(os.getenv(key, str(default)))
    except ValueError:
        return default
