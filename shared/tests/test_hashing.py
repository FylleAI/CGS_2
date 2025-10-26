"""
Tests for Fylle Shared Hashing Utils
"""

import pytest

from fylle_shared.utils.hashing import generate_content_hash, generate_idempotency_key


class TestGenerateContentHash:
    """Tests for generate_content_hash"""
    
    def test_deterministic_hash(self):
        """Test that same content produces same hash"""
        payload = {"name": "Acme Corp", "industry": "SaaS"}
        hash1 = generate_content_hash(payload)
        hash2 = generate_content_hash(payload)
        assert hash1 == hash2
    
    def test_different_content_different_hash(self):
        """Test that different content produces different hash"""
        payload1 = {"name": "Acme Corp"}
        payload2 = {"name": "Beta Inc"}
        hash1 = generate_content_hash(payload1)
        hash2 = generate_content_hash(payload2)
        assert hash1 != hash2
    
    def test_key_order_invariant(self):
        """Test that key order doesn't affect hash"""
        payload1 = {"name": "Acme", "industry": "SaaS"}
        payload2 = {"industry": "SaaS", "name": "Acme"}
        hash1 = generate_content_hash(payload1)
        hash2 = generate_content_hash(payload2)
        assert hash1 == hash2
    
    def test_type_hint_affects_hash(self):
        """Test that type hint creates different hash"""
        payload = {"name": "Acme"}
        hash1 = generate_content_hash(payload, type_hint="company")
        hash2 = generate_content_hash(payload, type_hint="audience")
        assert hash1 != hash2
    
    def test_hash_length(self):
        """Test that hash is SHA-256 (64 hex chars)"""
        payload = {"test": "data"}
        hash_value = generate_content_hash(payload)
        assert len(hash_value) == 64
        assert all(c in "0123456789abcdef" for c in hash_value)


class TestGenerateIdempotencyKey:
    """Tests for generate_idempotency_key"""
    
    def test_idempotency_key_format(self):
        """Test idempotency key format"""
        key = generate_idempotency_key("123e4567", "batch")
        assert key == "batch-123e4567"
    
    def test_idempotency_key_different_operations(self):
        """Test different operations produce different keys"""
        entity_id = "123e4567"
        key1 = generate_idempotency_key(entity_id, "batch")
        key2 = generate_idempotency_key(entity_id, "create")
        assert key1 != key2
    
    def test_idempotency_key_different_entities(self):
        """Test different entities produce different keys"""
        operation = "batch"
        key1 = generate_idempotency_key("entity1", operation)
        key2 = generate_idempotency_key("entity2", operation)
        assert key1 != key2

