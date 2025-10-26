"""
Tests for Fylle Shared Tracing Utils
"""

import uuid

import pytest

from fylle_shared.utils.tracing import get_trace_id, TRACE_HEADER


class TestGetTraceId:
    """Tests for get_trace_id"""
    
    def test_extract_existing_trace_id(self):
        """Test extracting trace ID from headers"""
        headers = {TRACE_HEADER: "trace-123"}
        trace_id = get_trace_id(headers)
        assert trace_id == "trace-123"
    
    def test_generate_new_trace_id_no_headers(self):
        """Test generating new trace ID when no headers"""
        trace_id = get_trace_id()
        # Should be valid UUID
        assert uuid.UUID(trace_id)
    
    def test_generate_new_trace_id_empty_headers(self):
        """Test generating new trace ID when headers empty"""
        trace_id = get_trace_id({})
        # Should be valid UUID
        assert uuid.UUID(trace_id)
    
    def test_generate_new_trace_id_missing_header(self):
        """Test generating new trace ID when trace header missing"""
        headers = {"Content-Type": "application/json"}
        trace_id = get_trace_id(headers)
        # Should be valid UUID
        assert uuid.UUID(trace_id)
    
    def test_different_calls_generate_different_ids(self):
        """Test that multiple calls generate different IDs"""
        trace_id1 = get_trace_id()
        trace_id2 = get_trace_id()
        assert trace_id1 != trace_id2

