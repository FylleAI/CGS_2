"""
Tests for Fylle Shared Headers Utils
"""

import pytest

from fylle_shared.utils.headers import (
    TENANT_HEADER,
    TRACE_HEADER,
    SESSION_HEADER,
    IDEMPOTENCY_HEADER,
    propagate_headers,
)


class TestPropagateHeaders:
    """Tests for propagate_headers"""
    
    def test_propagate_all_headers(self):
        """Test propagating all important headers"""
        incoming = {
            TENANT_HEADER: "tenant-123",
            TRACE_HEADER: "trace-456",
            SESSION_HEADER: "session-789",
            IDEMPOTENCY_HEADER: "idem-abc",
            "Content-Type": "application/json",
            "Authorization": "Bearer token"
        }
        result = propagate_headers(incoming)
        assert result == {
            TENANT_HEADER: "tenant-123",
            TRACE_HEADER: "trace-456",
            SESSION_HEADER: "session-789",
            IDEMPOTENCY_HEADER: "idem-abc"
        }
    
    def test_propagate_partial_headers(self):
        """Test propagating only some headers"""
        incoming = {
            TENANT_HEADER: "tenant-123",
            TRACE_HEADER: "trace-456",
            "Content-Type": "application/json"
        }
        result = propagate_headers(incoming)
        assert result == {
            TENANT_HEADER: "tenant-123",
            TRACE_HEADER: "trace-456"
        }
    
    def test_propagate_no_relevant_headers(self):
        """Test when no relevant headers present"""
        incoming = {
            "Content-Type": "application/json",
            "Authorization": "Bearer token"
        }
        result = propagate_headers(incoming)
        assert result == {}
    
    def test_propagate_none_headers(self):
        """Test when headers is None"""
        result = propagate_headers(None)
        assert result == {}
    
    def test_propagate_empty_headers(self):
        """Test when headers is empty dict"""
        result = propagate_headers({})
        assert result == {}

