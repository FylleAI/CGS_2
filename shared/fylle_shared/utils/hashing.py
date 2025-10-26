"""
Fylle Shared Hashing Utils

Utilities for content hashing and idempotency key generation.
"""

import hashlib
import json
from typing import Any, Optional


def generate_content_hash(payload: Any, *, type_hint: Optional[str] = None) -> str:
    """
    Generate deterministic hash for content deduplication.
    
    Args:
        payload: Content to hash (dict, list, str, etc.)
        type_hint: Optional type hint to avoid cross-type collisions
        
    Returns:
        SHA-256 hex digest
        
    Example:
        >>> generate_content_hash({"name": "Acme"}, type_hint="company")
        'a1b2c3d4...'
    """
    # Normalize and wrap with type to avoid collisions across different types
    wrapped = {"__type__": type_hint or "unknown", "payload": payload}
    normalized = json.dumps(
        wrapped,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    )
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def generate_idempotency_key(entity_id: str, operation: str) -> str:
    """
    Generate idempotency key for safe retries.
    
    Args:
        entity_id: Unique identifier (e.g., session_id, user_id)
        operation: Operation name (e.g., "batch", "create")
        
    Returns:
        Idempotency key in format: "{operation}-{entity_id}"
        
    Example:
        >>> generate_idempotency_key("123e4567-...", "batch")
        'batch-123e4567-...'
    """
    return f"{operation}-{entity_id}"

