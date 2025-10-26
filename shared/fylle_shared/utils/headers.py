"""
Fylle Shared Headers Utils

Utilities for HTTP header propagation across microservices.
"""

from typing import Mapping, Optional


TENANT_HEADER = "X-Tenant-ID"
TRACE_HEADER = "X-Trace-ID"
SESSION_HEADER = "X-Session-ID"
IDEMPOTENCY_HEADER = "Idempotency-Key"


def propagate_headers(incoming: Optional[Mapping[str, str]]) -> dict:
    """
    Propagate important headers to downstream services.
    
    Extracts tenant, trace, session, and idempotency headers from incoming
    request and returns them as a dict for downstream calls.
    
    Args:
        incoming: Incoming HTTP headers (optional)
        
    Returns:
        Dict with headers to propagate
        
    Example:
        >>> headers = {
        ...     "X-Tenant-ID": "tenant-123",
        ...     "X-Trace-ID": "trace-456",
        ...     "Content-Type": "application/json"
        ... }
        >>> propagate_headers(headers)
        {'X-Tenant-ID': 'tenant-123', 'X-Trace-ID': 'trace-456'}
    """
    if not incoming:
        return {}
    
    out = {}
    for header in (TENANT_HEADER, TRACE_HEADER, SESSION_HEADER, IDEMPOTENCY_HEADER):
        if (value := incoming.get(header)):
            out[header] = value
    
    return out

