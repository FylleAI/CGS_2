"""
Fylle Shared Tracing Utils

Utilities for distributed tracing across microservices.
"""

import uuid
from typing import Mapping, Optional


TRACE_HEADER = "X-Trace-ID"


def get_trace_id(headers: Optional[Mapping[str, str]] = None) -> str:
    """
    Extract or generate trace ID for distributed tracing.
    
    Args:
        headers: HTTP headers dict (optional)
        
    Returns:
        Trace ID (existing from headers or newly generated)
        
    Example:
        >>> get_trace_id({"X-Trace-ID": "trace-123"})
        'trace-123'
        >>> get_trace_id()  # No headers
        'a1b2c3d4-...'  # Generated UUID
    """
    if headers and TRACE_HEADER in headers:
        return headers[TRACE_HEADER]
    return str(uuid.uuid4())

