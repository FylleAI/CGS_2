# Cards API - Policies and Configuration

This document describes the operational policies, configuration, and best practices for the Cards API.

---

## Table of Contents

1. [Idempotency Policy](#idempotency-policy)
2. [TTL Configuration](#ttl-configuration)
3. [Rate Limiting](#rate-limiting)
4. [Security Policies](#security-policies)
5. [Monitoring and Alerts](#monitoring-and-alerts)
6. [Performance SLOs](#performance-slos)
7. [Data Retention](#data-retention)

---

## Idempotency Policy

### Overview

The Cards API implements **idempotency** to ensure that duplicate requests (e.g., due to network retries) do not create duplicate resources.

### How It Works

1. **Client sends request** with `Idempotency-Key` header
2. **API checks cache** in `idempotency_store` table
3. **Cache HIT**: Return cached response (no DB write)
4. **Cache MISS**: Process request, store response in cache

### Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| **TTL** | 24 hours | How long idempotency keys are cached |
| **Storage** | PostgreSQL | Persistent storage (survives restarts) |
| **Scope** | Per-tenant | Isolated by `tenant_id` |
| **Pattern** | UPSERT | `INSERT ... ON CONFLICT DO UPDATE` |

### Database Schema

```sql
CREATE TABLE idempotency_store (
    idempotency_key VARCHAR(255) NOT NULL,
    tenant_id UUID NOT NULL,
    response_payload JSONB NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (idempotency_key, tenant_id)
);
```

### Usage Example

```bash
# First request (cache MISS)
curl -X POST http://localhost:8002/api/v1/cards/batch \
  -H "X-Tenant-ID: 123e4567-e89b-12d3-a456-426614174000" \
  -H "Idempotency-Key: onboarding-session-abc123" \
  -d '{"cards": [...]}'

# Response: 201 Created
# Cards created in database

# Retry (cache HIT)
curl -X POST http://localhost:8002/api/v1/cards/batch \
  -H "X-Tenant-ID: 123e4567-e89b-12d3-a456-426614174000" \
  -H "Idempotency-Key: onboarding-session-abc123" \
  -d '{"cards": [...]}'

# Response: 201 Created (same response)
# No new cards created (cached response returned)
```

### Cleanup

Expired idempotency entries are automatically cleaned up:

```sql
-- Manual cleanup (if needed)
DELETE FROM idempotency_store WHERE expires_at < NOW();

-- Automated cleanup function
SELECT cleanup_expired_idempotency();
```

### Best Practices

1. **Use unique keys**: Generate UUIDs or session-based keys
2. **Include tenant context**: Keys are scoped per tenant
3. **Retry with same key**: Use the same key for retries
4. **Don't reuse keys**: Each logical operation should have a unique key

---

## TTL Configuration

### Idempotency TTL

| Environment | TTL | Rationale |
|-------------|-----|-----------|
| **Production** | 24 hours | Covers typical retry windows |
| **Staging** | 24 hours | Same as production |
| **Development** | 24 hours | Consistent behavior |

**Configuration**:
```bash
# Environment variable
IDEMPOTENCY_TTL_HOURS=24

# Database calculation
expires_at = NOW() + INTERVAL '24 hours'
```

### Card TTL (Soft Delete)

Cards are **never hard-deleted**. Instead, they are soft-deleted using the `is_active` flag.

| Field | Value | Description |
|-------|-------|-------------|
| `is_active` | `true` | Card is active |
| `is_active` | `false` | Card is soft-deleted |

**Soft delete**:
```sql
UPDATE cards
SET is_active = false, updated_at = NOW()
WHERE card_id = $1 AND tenant_id = $2;
```

### Usage Event Retention

Usage events in `card_usage` table are retained **indefinitely** for analytics.

**Future**: Implement archival policy (e.g., move events older than 90 days to cold storage).

---

## Rate Limiting

### Current Status

⚠️ **Not implemented yet** (planned for Sprint 4)

### Planned Configuration

| Endpoint | Rate Limit | Window | Scope |
|----------|------------|--------|-------|
| `/api/v1/cards/batch` | 100 req/min | 1 minute | Per tenant |
| `/api/v1/cards/retrieve` | 1000 req/min | 1 minute | Per tenant |
| `/api/v1/cards/{id}/usage` | 500 req/min | 1 minute | Per tenant |

### Implementation Plan

1. Use **Redis** for rate limiting counters
2. Implement **token bucket** algorithm
3. Return `429 Too Many Requests` when limit exceeded
4. Include `Retry-After` header in response

---

## Security Policies

### Required Headers

| Header | Required | Description |
|--------|----------|-------------|
| `X-Tenant-ID` | ✅ Yes | Tenant identifier (UUID) |
| `X-Trace-ID` | ⚠️ Recommended | Request tracing (UUID) |
| `Idempotency-Key` | ⚠️ Recommended | Idempotency key (batch endpoint) |
| `Content-Type` | ✅ Yes | Must be `application/json` |

### CORS Configuration

⚠️ **Not configured yet** (planned for Sprint 4)

**Planned**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.fylle.ai"],  # Production domain
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["X-Tenant-ID", "X-Trace-ID", "Idempotency-Key"],
)
```

### Authentication

⚠️ **Not implemented yet** (planned for Sprint 4)

**Planned**:
- JWT-based authentication
- API key authentication (for service-to-service)
- OAuth 2.0 (for user-facing apps)

### Row-Level Security (RLS)

✅ **Implemented** in database

**Policy**:
```sql
CREATE POLICY cards_tenant_isolation ON cards
    USING (tenant_id::text = current_setting('app.current_tenant_id', TRUE));
```

**Enforcement**:
```python
# Set tenant context before queries
await conn.execute("SET LOCAL app.current_tenant_id = $1", tenant_id)
```

---

## Monitoring and Alerts

### Prometheus Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `cards_api_requests_total` | Counter | Total requests (labels: method, endpoint, status) |
| `cards_api_request_duration_seconds` | Histogram | Request duration (labels: method, endpoint) |
| `cards_api_operations_total` | Counter | Card operations (labels: operation, status) |
| `card_usage_events_total` | Counter | Usage events (labels: card_type, workflow_type) |
| `cards_usage_write_duration_ms` | Histogram | Usage write duration |

### Alert Rules

See `prometheus_alerts.yml` for complete alert configuration.

**Critical Alerts**:
- `CardsAPIDown`: API is down for >1 minute
- `CardsAPIHighErrorRate`: Error rate >5% for >5 minutes
- `CardsAPIDatabasePoolExhausted`: High DB operation failure rate

**Warning Alerts**:
- `CardsAPIBatchHighLatency`: p95 >100ms for batch endpoint
- `CardsAPIRetrieveHighLatency`: p95 >50ms for retrieve endpoint
- `CardsAPIUsageTrackingHighLatency`: p95 >25ms for usage endpoint

**Info Alerts**:
- `CardsAPILowIdempotencyCacheHitRate`: Cache hit rate <50%
- `CardsAPIHighDeduplicationRate`: Deduplication rate >20%

### Alert Channels

⚠️ **Not configured yet** (planned for Sprint 4)

**Planned**:
- Slack notifications (critical alerts)
- PagerDuty (critical alerts, on-call rotation)
- Email (warning alerts)

---

## Performance SLOs

### Service Level Objectives (SLOs)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Availability** | 99.9% | Uptime over 30 days |
| **Batch p95 latency** | ≤ 100ms | 95th percentile response time |
| **Retrieve p95 latency** | ≤ 50ms | 95th percentile response time |
| **Usage p95 latency** | ≤ 25ms | 95th percentile response time |
| **Error rate** | < 1% | 5xx errors / total requests |

### Performance Targets

| Endpoint | p50 | p95 | p99 |
|----------|-----|-----|-----|
| `/api/v1/cards/batch` | ≤ 50ms | ≤ 100ms | ≤ 200ms |
| `/api/v1/cards/retrieve` | ≤ 20ms | ≤ 50ms | ≤ 100ms |
| `/api/v1/cards/{id}/usage` | ≤ 10ms | ≤ 25ms | ≤ 50ms |

### Benchmarking

Run benchmarks with:
```bash
./scripts/benchmark_cards_api.sh
```

Results are saved to `benchmark_results/summary_<timestamp>.csv`.

---

## Data Retention

### Cards Table

| Data | Retention | Policy |
|------|-----------|--------|
| Active cards | Indefinite | Soft delete only |
| Inactive cards | Indefinite | Archived, not deleted |

### Idempotency Store

| Data | Retention | Policy |
|------|-----------|--------|
| Idempotency keys | 24 hours | Auto-deleted after expiry |

**Cleanup**:
```sql
-- Automated cleanup (runs daily)
SELECT cleanup_expired_idempotency();

-- Manual cleanup
DELETE FROM idempotency_store WHERE expires_at < NOW();
```

### Card Usage Events

| Data | Retention | Policy |
|------|-----------|--------|
| Usage events | Indefinite | Retained for analytics |

**Future**: Implement archival policy (e.g., move to cold storage after 90 days).

---

## Configuration Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SUPABASE_DATABASE_URL` | - | PostgreSQL connection string |
| `PORT` | 8002 | API port |
| `HOST` | 0.0.0.0 | API host |
| `LOG_LEVEL` | info | Logging level (debug, info, warning, error) |
| `DB_MIN_POOL_SIZE` | 5 | Min database connections |
| `DB_MAX_POOL_SIZE` | 20 | Max database connections |
| `IDEMPOTENCY_TTL_HOURS` | 24 | Idempotency TTL in hours |

### Database Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| `max_connections` | 100 | Max PostgreSQL connections |
| `shared_buffers` | 256MB | Shared memory for caching |
| `effective_cache_size` | 1GB | Estimated cache size |
| `work_mem` | 16MB | Memory per query operation |

---

## Best Practices

### For Clients

1. **Always include `X-Tenant-ID`**: Required for multi-tenant isolation
2. **Use `Idempotency-Key` for batch operations**: Prevents duplicate cards
3. **Include `X-Trace-ID` for debugging**: Helps trace requests across services
4. **Handle 429 responses**: Implement exponential backoff for rate limits
5. **Validate card content**: Ensure content matches card type schema

### For Operations

1. **Monitor alert channels**: Respond to critical alerts within 5 minutes
2. **Review metrics daily**: Check for anomalies in request rate, latency, errors
3. **Run benchmarks weekly**: Ensure performance SLOs are met
4. **Clean up test data**: Remove test cards from production database
5. **Backup database daily**: Ensure data can be restored in case of failure

### For Developers

1. **Test with real database**: Use Docker Compose for local development
2. **Run integration tests**: Ensure changes don't break existing functionality
3. **Update documentation**: Keep this file in sync with code changes
4. **Follow semantic versioning**: Increment version on breaking changes
5. **Review Prometheus metrics**: Add metrics for new features

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2025-10-27 | 1.0.0 | Initial release (Sprint 3) |

---

## References

- [Cards API Documentation](../README.md)
- [Docker Compose Guide](../docker/README.md)
- [E2E Testing Guide](../tests/e2e/README.md)
- [SQL Test Suite](../scripts/README_SUPABASE_TESTS.md)
- [Prometheus Alerts](../prometheus_alerts.yml)

---

**Last Updated**: 2025-10-27  
**Maintained By**: Cards API Team

