"""Utility helpers for the card service API layer."""

import hashlib
from uuid import UUID


def normalize_tenant_id(tenant_id: str) -> str:
    """Normalize tenant identifier supporting email, UUID and admin shortcut."""

    if not tenant_id or tenant_id.strip() == "":
        raise ValueError("tenant_id cannot be empty")

    tenant_id = tenant_id.strip()

    if tenant_id.lower() == "admin":
        return tenant_id

    try:
        UUID(tenant_id)
        return tenant_id
    except ValueError:
        pass

    digest = hashlib.md5(f"fylle:{tenant_id}".encode()).hexdigest()
    return str(UUID(digest))
