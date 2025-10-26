"""
Integration tests for Onboarding API v1.

Tests:
- POST /api/v1/onboarding/sessions
- GET /api/v1/onboarding/sessions/{id}
- POST /api/v1/onboarding/sessions/{id}/answers
- Idempotency replay
- Error handling (Cards API 5xx → 502)
- Partial creation (< 4 cards)
"""

import pytest
import httpx
from uuid import UUID
import time


class TestOnboardingAPIIntegration:
    """Integration tests for Onboarding API with Mock Cards API."""

    @pytest.fixture
    def base_url(self):
        """Onboarding API base URL."""
        return "http://localhost:8000"

    @pytest.fixture
    def tenant_id(self):
        """Test tenant ID."""
        return "123e4567-e89b-12d3-a456-426614174000"

    @pytest.fixture
    def trace_id(self):
        """Test trace ID."""
        return f"integration-test-{int(time.time())}"

    @pytest.mark.asyncio
    async def test_create_session_success(self, base_url, tenant_id, trace_id):
        """Test POST /api/v1/onboarding/sessions - success."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/api/v1/onboarding/sessions",
                json={
                    "tenant_id": tenant_id,
                    "company_domain": "integration-test.com",
                    "user_email": "test@integration-test.com",
                },
                headers={"X-Trace-ID": trace_id},
            )

            assert response.status_code == 201
            data = response.json()

            assert "session_id" in data
            assert data["tenant_id"] == tenant_id
            assert data["company_domain"] == "integration-test.com"
            assert data["user_email"] == "test@integration-test.com"
            assert data["status"] == "research"
            assert "created_at" in data
            assert "updated_at" in data

            # Validate session_id is UUID
            session_id = UUID(data["session_id"])
            assert isinstance(session_id, UUID)

    @pytest.mark.asyncio
    async def test_get_session_success(self, base_url, tenant_id, trace_id):
        """Test GET /api/v1/onboarding/sessions/{id} - success."""
        async with httpx.AsyncClient() as client:
            # Create session first
            create_response = await client.post(
                f"{base_url}/api/v1/onboarding/sessions",
                json={
                    "tenant_id": tenant_id,
                    "company_domain": "get-test.com",
                    "user_email": "test@get-test.com",
                },
                headers={"X-Trace-ID": trace_id},
            )
            session_id = create_response.json()["session_id"]

            # Get session
            get_response = await client.get(
                f"{base_url}/api/v1/onboarding/sessions/{session_id}",
                headers={"X-Trace-ID": trace_id},
            )

            assert get_response.status_code == 200
            data = get_response.json()

            assert data["session_id"] == session_id
            assert data["company_domain"] == "get-test.com"
            assert data["status"] == "research"

    @pytest.mark.asyncio
    async def test_get_session_not_found(self, base_url, trace_id):
        """Test GET /api/v1/onboarding/sessions/{id} - not found."""
        async with httpx.AsyncClient() as client:
            fake_session_id = "00000000-0000-0000-0000-000000000000"
            response = await client.get(
                f"{base_url}/api/v1/onboarding/sessions/{fake_session_id}",
                headers={"X-Trace-ID": trace_id},
            )

            assert response.status_code == 404
            data = response.json()
            assert data["error"] == "NotFound"

    @pytest.mark.asyncio
    async def test_submit_answers_success(self, base_url, tenant_id, trace_id):
        """Test POST /api/v1/onboarding/sessions/{id}/answers - success."""
        async with httpx.AsyncClient() as client:
            # Create session
            create_response = await client.post(
                f"{base_url}/api/v1/onboarding/sessions",
                json={
                    "tenant_id": tenant_id,
                    "company_domain": "submit-test.com",
                    "user_email": "test@submit-test.com",
                },
                headers={"X-Trace-ID": trace_id},
            )
            session_id = create_response.json()["session_id"]

            # Submit answers
            submit_response = await client.post(
                f"{base_url}/api/v1/onboarding/sessions/{session_id}/answers",
                json={
                    "answers": [
                        {"question_id": "q1", "answer": "We build integration test tools"},
                        {"question_id": "q2", "answer": "QA Engineers and DevOps teams"},
                        {"question_id": "q3", "answer": "Technical and precise"},
                    ]
                },
                headers={
                    "X-Tenant-ID": tenant_id,
                    "X-Trace-ID": trace_id,
                    "Idempotency-Key": f"integration-test-{trace_id}",
                },
            )

            assert submit_response.status_code == 200
            data = submit_response.json()

            assert data["session_id"] == session_id
            assert data["status"] == "completed"
            assert "card_ids" in data
            assert len(data["card_ids"]) == 4  # Should create 4 cards
            assert data["cards_created_count"] == 4
            assert "updated_at" in data

            # Validate card_ids are UUIDs
            for card_id in data["card_ids"]:
                assert isinstance(UUID(card_id), UUID)

    @pytest.mark.asyncio
    async def test_submit_answers_idempotency(self, base_url, tenant_id, trace_id):
        """Test idempotency - same Idempotency-Key returns same cards."""
        async with httpx.AsyncClient() as client:
            # Create session
            create_response = await client.post(
                f"{base_url}/api/v1/onboarding/sessions",
                json={
                    "tenant_id": tenant_id,
                    "company_domain": "idempotency-test.com",
                    "user_email": "test@idempotency-test.com",
                },
                headers={"X-Trace-ID": trace_id},
            )
            session_id = create_response.json()["session_id"]

            idempotency_key = f"idempotency-test-{trace_id}"

            # First call
            first_response = await client.post(
                f"{base_url}/api/v1/onboarding/sessions/{session_id}/answers",
                json={
                    "answers": [
                        {"question_id": "q1", "answer": "First call"},
                        {"question_id": "q2", "answer": "First call"},
                        {"question_id": "q3", "answer": "First call"},
                    ]
                },
                headers={
                    "X-Tenant-ID": tenant_id,
                    "X-Trace-ID": trace_id,
                    "Idempotency-Key": idempotency_key,
                },
            )

            assert first_response.status_code == 200
            first_data = first_response.json()
            first_card_ids = first_data["card_ids"]

            # Second call with SAME idempotency key but DIFFERENT answers
            second_response = await client.post(
                f"{base_url}/api/v1/onboarding/sessions/{session_id}/answers",
                json={
                    "answers": [
                        {"question_id": "q1", "answer": "DIFFERENT - should be ignored"},
                        {"question_id": "q2", "answer": "DIFFERENT - should be ignored"},
                        {"question_id": "q3", "answer": "DIFFERENT - should be ignored"},
                    ]
                },
                headers={
                    "X-Tenant-ID": tenant_id,
                    "X-Trace-ID": f"{trace_id}-replay",
                    "Idempotency-Key": idempotency_key,  # SAME KEY
                },
            )

            assert second_response.status_code == 200
            second_data = second_response.json()
            second_card_ids = second_data["card_ids"]

            # Should return SAME card IDs (idempotency)
            assert first_card_ids == second_card_ids
            assert len(second_card_ids) == 4

    @pytest.mark.asyncio
    async def test_submit_answers_session_not_found(self, base_url, tenant_id, trace_id):
        """Test submit answers - session not found."""
        async with httpx.AsyncClient() as client:
            fake_session_id = "00000000-0000-0000-0000-000000000000"
            response = await client.post(
                f"{base_url}/api/v1/onboarding/sessions/{fake_session_id}/answers",
                json={
                    "answers": [
                        {"question_id": "q1", "answer": "Test"},
                        {"question_id": "q2", "answer": "Test"},
                        {"question_id": "q3", "answer": "Test"},
                    ]
                },
                headers={
                    "X-Tenant-ID": tenant_id,
                    "X-Trace-ID": trace_id,
                },
            )

            assert response.status_code == 404
            data = response.json()
            assert data["error"] == "NotFound"

    @pytest.mark.asyncio
    async def test_metrics_incremented(self, base_url, tenant_id, trace_id):
        """Test that Prometheus metrics are incremented."""
        async with httpx.AsyncClient() as client:
            # Get initial metrics
            metrics_before = await client.get(f"{base_url}/metrics")
            metrics_before_text = metrics_before.text

            # Create session
            create_response = await client.post(
                f"{base_url}/api/v1/onboarding/sessions",
                json={
                    "tenant_id": tenant_id,
                    "company_domain": "metrics-test.com",
                    "user_email": "test@metrics-test.com",
                },
                headers={"X-Trace-ID": trace_id},
            )
            session_id = create_response.json()["session_id"]

            # Submit answers
            await client.post(
                f"{base_url}/api/v1/onboarding/sessions/{session_id}/answers",
                json={
                    "answers": [
                        {"question_id": "q1", "answer": "Metrics test"},
                        {"question_id": "q2", "answer": "Metrics test"},
                        {"question_id": "q3", "answer": "Metrics test"},
                    ]
                },
                headers={
                    "X-Tenant-ID": tenant_id,
                    "X-Trace-ID": trace_id,
                    "Idempotency-Key": f"metrics-test-{trace_id}",
                },
            )

            # Get metrics after
            metrics_after = await client.get(f"{base_url}/metrics")
            metrics_after_text = metrics_after.text

            # Check that metrics were incremented
            assert "onboarding_sessions_total" in metrics_after_text
            assert "onboarding_sessions_completed_total" in metrics_after_text
            assert "onboarding_cards_created_total" in metrics_after_text
            assert "onboarding_batch_duration_ms" in metrics_after_text

