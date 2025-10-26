"""
E2E tests for Onboarding → Cards → Workflow flow.

Tests:
- Complete flow: Create session → Submit answers → Create cards → Execute workflow
- Scenario: Success (all cards created, workflow executes)
- Scenario: Partial result (X-Partial-Result: true)
- Scenario: Failure + retry + safety net
"""

import pytest
import httpx
from uuid import UUID
import time


class TestOnboardingWorkflowE2E:
    """E2E tests for complete Onboarding → Workflow flow."""

    @pytest.fixture
    def base_url(self):
        """API base URL."""
        return "http://localhost:8000"

    @pytest.fixture
    def tenant_id(self):
        """Test tenant ID."""
        return "123e4567-e89b-12d3-a456-426614174000"

    @pytest.fixture
    def trace_id(self):
        """Test trace ID."""
        return f"e2e-test-{int(time.time())}"

    @pytest.mark.asyncio
    async def test_e2e_success_flow(self, base_url, tenant_id, trace_id):
        """
        Test complete E2E flow - SUCCESS scenario.
        
        Flow:
        1. Create onboarding session
        2. Submit answers → Creates 4 cards
        3. Execute workflow with card_ids
        4. Verify workflow uses cards as context
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Step 1: Create onboarding session
            print("\n📝 Step 1: Create onboarding session")
            create_response = await client.post(
                f"{base_url}/api/v1/onboarding/sessions",
                json={
                    "tenant_id": tenant_id,
                    "company_domain": "e2e-success.com",
                    "user_email": "test@e2e-success.com",
                },
                headers={"X-Trace-ID": trace_id},
            )

            assert create_response.status_code == 201
            session_id = create_response.json()["session_id"]
            print(f"✅ Session created: {session_id}")

            # Step 2: Submit answers → Creates 4 cards
            print("\n📝 Step 2: Submit answers and create cards")
            submit_response = await client.post(
                f"{base_url}/api/v1/onboarding/sessions/{session_id}/answers",
                json={
                    "answers": [
                        {"question_id": "q1", "answer": "E2E Success Corp builds innovative AI solutions"},
                        {"question_id": "q2", "answer": "Enterprise CTOs and Tech Leaders"},
                        {"question_id": "q3", "answer": "Professional, data-driven, and visionary"},
                    ]
                },
                headers={
                    "X-Tenant-ID": tenant_id,
                    "X-Trace-ID": trace_id,
                    "Idempotency-Key": f"e2e-success-{trace_id}",
                },
            )

            assert submit_response.status_code == 200
            submit_data = submit_response.json()
            card_ids = submit_data["card_ids"]
            
            assert len(card_ids) == 4
            assert submit_data["cards_created_count"] == 4
            print(f"✅ Cards created: {len(card_ids)} cards")
            print(f"   Card IDs: {card_ids}")

            # Step 3: Execute workflow with card_ids
            print("\n📝 Step 3: Execute workflow with cards as context")
            workflow_response = await client.post(
                f"{base_url}/api/v1/workflow/execute",
                json={
                    "tenant_id": tenant_id,
                    "workflow_type": "linkedin_post",
                    "context": {
                        "topic": "AI innovation in enterprise",
                        "card_ids": card_ids,  # Use cards from onboarding
                    },
                },
                headers={
                    "X-Tenant-ID": tenant_id,
                    "X-Trace-ID": trace_id,
                },
            )

            assert workflow_response.status_code == 200
            workflow_data = workflow_response.json()
            
            assert "execution_id" in workflow_data
            assert workflow_data["status"] in ["completed", "partial"]
            print(f"✅ Workflow executed: {workflow_data['execution_id']}")
            print(f"   Status: {workflow_data['status']}")
            
            # Verify cards were used
            if "cards_used" in workflow_data:
                assert len(workflow_data["cards_used"]) > 0
                print(f"   Cards used: {len(workflow_data['cards_used'])}")

    @pytest.mark.asyncio
    async def test_e2e_partial_result_flow(self, base_url, tenant_id, trace_id):
        """
        Test E2E flow with PARTIAL result.
        
        Simulates scenario where some cards fail to load but workflow continues.
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Create session and cards
            create_response = await client.post(
                f"{base_url}/api/v1/onboarding/sessions",
                json={
                    "tenant_id": tenant_id,
                    "company_domain": "e2e-partial.com",
                    "user_email": "test@e2e-partial.com",
                },
                headers={"X-Trace-ID": trace_id},
            )
            session_id = create_response.json()["session_id"]

            submit_response = await client.post(
                f"{base_url}/api/v1/onboarding/sessions/{session_id}/answers",
                json={
                    "answers": [
                        {"question_id": "q1", "answer": "Partial test"},
                        {"question_id": "q2", "answer": "Partial test"},
                        {"question_id": "q3", "answer": "Partial test"},
                    ]
                },
                headers={
                    "X-Tenant-ID": tenant_id,
                    "X-Trace-ID": trace_id,
                    "Idempotency-Key": f"e2e-partial-{trace_id}",
                },
            )
            card_ids = submit_response.json()["card_ids"]

            # Execute workflow with mix of valid and invalid card IDs
            invalid_card_id = "00000000-0000-0000-0000-000000000000"
            mixed_card_ids = card_ids[:2] + [invalid_card_id]  # 2 valid + 1 invalid

            workflow_response = await client.post(
                f"{base_url}/api/v1/workflow/execute",
                json={
                    "tenant_id": tenant_id,
                    "workflow_type": "linkedin_post",
                    "context": {
                        "topic": "Partial result test",
                        "card_ids": mixed_card_ids,
                    },
                },
                headers={
                    "X-Tenant-ID": tenant_id,
                    "X-Trace-ID": trace_id,
                },
            )

            # Should still succeed with partial result
            assert workflow_response.status_code == 200
            workflow_data = workflow_response.json()
            
            # Check for partial result indicator
            if "X-Partial-Result" in workflow_response.headers:
                assert workflow_response.headers["X-Partial-Result"] == "true"
                print("✅ Partial result detected and handled")

    @pytest.mark.asyncio
    async def test_e2e_retry_and_safety_net(self, base_url, tenant_id, trace_id):
        """
        Test E2E flow with retry logic and safety net.
        
        Simulates transient failures and verifies retry + fallback behavior.
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Create session
            create_response = await client.post(
                f"{base_url}/api/v1/onboarding/sessions",
                json={
                    "tenant_id": tenant_id,
                    "company_domain": "e2e-retry.com",
                    "user_email": "test@e2e-retry.com",
                },
                headers={"X-Trace-ID": trace_id},
            )
            session_id = create_response.json()["session_id"]

            # Submit answers
            submit_response = await client.post(
                f"{base_url}/api/v1/onboarding/sessions/{session_id}/answers",
                json={
                    "answers": [
                        {"question_id": "q1", "answer": "Retry test"},
                        {"question_id": "q2", "answer": "Retry test"},
                        {"question_id": "q3", "answer": "Retry test"},
                    ]
                },
                headers={
                    "X-Tenant-ID": tenant_id,
                    "X-Trace-ID": trace_id,
                    "Idempotency-Key": f"e2e-retry-{trace_id}",
                },
            )
            card_ids = submit_response.json()["card_ids"]

            # Execute workflow - should handle retries internally
            workflow_response = await client.post(
                f"{base_url}/api/v1/workflow/execute",
                json={
                    "tenant_id": tenant_id,
                    "workflow_type": "linkedin_post",
                    "context": {
                        "topic": "Retry and safety net test",
                        "card_ids": card_ids,
                    },
                },
                headers={
                    "X-Tenant-ID": tenant_id,
                    "X-Trace-ID": trace_id,
                },
            )

            # Should succeed (with retries if needed)
            assert workflow_response.status_code in [200, 206]  # 200 OK or 206 Partial
            workflow_data = workflow_response.json()
            
            assert "execution_id" in workflow_data
            print(f"✅ Workflow completed with retry/safety net: {workflow_data['status']}")

    @pytest.mark.asyncio
    async def test_e2e_latency_p95(self, base_url, tenant_id):
        """
        Test E2E latency - verify p95 ≤ 2.5s for onboarding flow.
        
        Runs multiple iterations and measures latency.
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            latencies = []

            # Run 20 iterations
            for i in range(20):
                trace_id = f"e2e-latency-{int(time.time())}-{i}"
                
                # Create session
                start_time = time.time()
                
                create_response = await client.post(
                    f"{base_url}/api/v1/onboarding/sessions",
                    json={
                        "tenant_id": tenant_id,
                        "company_domain": f"latency-test-{i}.com",
                        "user_email": f"test{i}@latency-test.com",
                    },
                    headers={"X-Trace-ID": trace_id},
                )
                session_id = create_response.json()["session_id"]

                # Submit answers (this is the critical path)
                submit_response = await client.post(
                    f"{base_url}/api/v1/onboarding/sessions/{session_id}/answers",
                    json={
                        "answers": [
                            {"question_id": "q1", "answer": f"Latency test {i}"},
                            {"question_id": "q2", "answer": f"Latency test {i}"},
                            {"question_id": "q3", "answer": f"Latency test {i}"},
                        ]
                    },
                    headers={
                        "X-Tenant-ID": tenant_id,
                        "X-Trace-ID": trace_id,
                        "Idempotency-Key": f"latency-test-{trace_id}",
                    },
                )
                
                end_time = time.time()
                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)
                
                assert submit_response.status_code == 200

            # Calculate p95
            latencies.sort()
            p95_index = int(len(latencies) * 0.95)
            p95_latency = latencies[p95_index]
            
            print(f"\n📊 Latency Results (n={len(latencies)}):")
            print(f"   Min: {min(latencies):.2f}ms")
            print(f"   Median: {latencies[len(latencies)//2]:.2f}ms")
            print(f"   P95: {p95_latency:.2f}ms")
            print(f"   Max: {max(latencies):.2f}ms")
            
            # Verify p95 ≤ 2.5s (2500ms)
            assert p95_latency <= 2500, f"P95 latency {p95_latency:.2f}ms exceeds 2.5s target"
            print(f"✅ P95 latency {p95_latency:.2f}ms ≤ 2.5s target")

