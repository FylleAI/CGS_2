# Docker Compose - Cards API Local Development

Complete local development environment for Cards API with PostgreSQL, Prometheus, and Grafana.

## Overview

This Docker Compose setup provides:
- **PostgreSQL 17**: Database with Cards API schema
- **Cards API**: FastAPI application on port 8002
- **Prometheus**: Metrics collection on port 9090
- **Grafana**: Metrics visualization on port 3000

## Architecture

```
┌─────────────┐
│  Cards API  │ :8002
│  (FastAPI)  │
└──────┬──────┘
       │
       ├─────────► PostgreSQL :5432
       │           (Database)
       │
       └─────────► Prometheus :9090
                   (Metrics)
                        │
                        ▼
                   Grafana :3000
                   (Dashboards)
```

## Quick Start

### 1. Start All Services

```bash
docker-compose -f docker-compose.cards.yml up -d
```

### 2. Verify Services

```bash
# Check all services are running
docker-compose -f docker-compose.cards.yml ps

# Check Cards API health
curl http://localhost:8002/health

# Check Prometheus
curl http://localhost:9090/-/healthy

# Check Grafana
curl http://localhost:3000/api/health
```

### 3. Access Services

- **Cards API**: http://localhost:8002
- **API Docs**: http://localhost:8002/docs
- **Metrics**: http://localhost:8002/metrics
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

### 4. Stop Services

```bash
docker-compose -f docker-compose.cards.yml down
```

### 5. Clean Up (Remove Volumes)

```bash
docker-compose -f docker-compose.cards.yml down -v
```

## Services

### PostgreSQL

**Image**: `postgres:17-alpine`  
**Port**: 5432  
**Database**: `cards_db`  
**User**: `cards_user`  
**Password**: `cards_password`

**Connection String**:
```
postgresql://cards_user:cards_password@localhost:5432/cards_db
```

**Schema**: Automatically initialized from `scripts/init_db.sql`

**Tables**:
- `cards` - Card storage
- `idempotency_store` - Idempotency cache
- `card_usage` - Usage tracking

### Cards API

**Image**: Built from `Dockerfile.cards`  
**Port**: 8002  
**Health Check**: `/health`

**Environment Variables**:
- `SUPABASE_DATABASE_URL`: PostgreSQL connection string
- `PORT`: API port (default: 8002)
- `HOST`: API host (default: 0.0.0.0)
- `LOG_LEVEL`: Logging level (default: info)
- `DB_MIN_POOL_SIZE`: Min DB connections (default: 5)
- `DB_MAX_POOL_SIZE`: Max DB connections (default: 20)
- `IDEMPOTENCY_TTL_HOURS`: Idempotency TTL (default: 24)

**Endpoints**:
- `GET /health` - Health check
- `GET /ready` - Readiness check
- `GET /metrics` - Prometheus metrics
- `POST /api/v1/cards/batch` - Batch create cards
- `POST /api/v1/cards/retrieve` - Retrieve cards
- `POST /api/v1/cards/{id}/usage` - Track usage

### Prometheus

**Image**: `prom/prometheus:latest`  
**Port**: 9090  
**Config**: `prometheus.yml`

**Scrape Targets**:
- Cards API: `cards-api:8002/metrics` (10s interval)
- Prometheus: `localhost:9090` (15s interval)

**Metrics Collected**:
- `cards_api_requests_total`
- `cards_api_request_duration_seconds`
- `card_usage_events_total`
- `cards_usage_write_duration_ms`

### Grafana

**Image**: `grafana/grafana:latest`  
**Port**: 3000  
**User**: admin  
**Password**: admin

**Datasources**: Prometheus (auto-configured)

**Dashboards**: (to be added in `grafana/dashboards/`)

## Usage Examples

### Create Cards

```bash
curl -X POST http://localhost:8002/api/v1/cards/batch \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: 123e4567-e89b-12d3-a456-426614174000" \
  -H "Idempotency-Key: test-$(uuidgen)" \
  -d '{
    "cards": [
      {
        "card_type": "company",
        "content": {
          "name": "Test Company",
          "domain": "test.com",
          "industry": "Technology"
        }
      }
    ]
  }'
```

### Retrieve Cards

```bash
curl -X POST http://localhost:8002/api/v1/cards/retrieve \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: 123e4567-e89b-12d3-a456-426614174000" \
  -d '{
    "card_ids": ["<card-id-1>", "<card-id-2>"]
  }'
```

### Track Usage

```bash
curl -X POST http://localhost:8002/api/v1/cards/<card-id>/usage \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: 123e4567-e89b-12d3-a456-426614174000" \
  -d '{
    "workflow_id": "workflow-123",
    "workflow_type": "premium_newsletter",
    "session_id": "session-456"
  }'
```

### View Metrics

```bash
curl http://localhost:8002/metrics
```

## Database Access

### Connect to PostgreSQL

```bash
# Using docker exec
docker exec -it cards-postgres psql -U cards_user -d cards_db

# Using psql client
psql postgresql://cards_user:cards_password@localhost:5432/cards_db
```

### Run SQL Queries

```sql
-- List all cards
SELECT card_id, card_type, content FROM cards;

-- Check usage count
SELECT card_id, card_type, usage_count, last_used_at FROM cards;

-- View usage events
SELECT * FROM card_usage ORDER BY used_at DESC LIMIT 10;

-- Check idempotency cache
SELECT idempotency_key, expires_at FROM idempotency_store;
```

## Logs

### View All Logs

```bash
docker-compose -f docker-compose.cards.yml logs -f
```

### View Specific Service Logs

```bash
# Cards API
docker-compose -f docker-compose.cards.yml logs -f cards-api

# PostgreSQL
docker-compose -f docker-compose.cards.yml logs -f postgres

# Prometheus
docker-compose -f docker-compose.cards.yml logs -f prometheus
```

## Troubleshooting

### Cards API Not Starting

**Check logs**:
```bash
docker-compose -f docker-compose.cards.yml logs cards-api
```

**Common issues**:
- Database not ready: Wait for PostgreSQL health check
- Port 8002 already in use: Change port in `docker-compose.cards.yml`

### Database Connection Error

**Check PostgreSQL health**:
```bash
docker-compose -f docker-compose.cards.yml ps postgres
```

**Verify connection**:
```bash
docker exec -it cards-postgres pg_isready -U cards_user -d cards_db
```

### Metrics Not Showing in Prometheus

**Check Prometheus targets**:
- Open http://localhost:9090/targets
- Verify `cards-api` target is UP

**Check Cards API metrics endpoint**:
```bash
curl http://localhost:8002/metrics
```

## Development Workflow

### 1. Start Services

```bash
docker-compose -f docker-compose.cards.yml up -d
```

### 2. Make Code Changes

Edit files in `cards/` directory

### 3. Rebuild and Restart

```bash
docker-compose -f docker-compose.cards.yml up -d --build cards-api
```

### 4. Run Tests

```bash
# E2E tests against local Docker environment
export CARDS_API_URL=http://localhost:8002
pytest tests/e2e/ -v -s -m e2e
```

### 5. View Logs

```bash
docker-compose -f docker-compose.cards.yml logs -f cards-api
```

## Performance Testing

### Load Test with Apache Bench

```bash
# Batch create (100 requests, 10 concurrent)
ab -n 100 -c 10 -T application/json \
  -H "X-Tenant-ID: 123e4567-e89b-12d3-a456-426614174000" \
  -H "Idempotency-Key: load-test-$(uuidgen)" \
  -p batch_payload.json \
  http://localhost:8002/api/v1/cards/batch
```

### Monitor Metrics in Prometheus

1. Open http://localhost:9090
2. Query: `rate(cards_api_requests_total[1m])`
3. Query: `histogram_quantile(0.95, rate(cards_api_request_duration_seconds_bucket[1m]))`

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Docker Build

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: docker build -f Dockerfile.cards -t cards-api:latest .
      
      - name: Start services
        run: docker-compose -f docker-compose.cards.yml up -d
      
      - name: Wait for health
        run: |
          timeout 60 bash -c 'until curl -f http://localhost:8002/health; do sleep 2; done'
      
      - name: Run tests
        run: pytest tests/e2e/ -v -m e2e
```

## Next Steps

1. Add Grafana dashboards for Cards API metrics
2. Add alerting rules in Prometheus
3. Add pg_exporter for PostgreSQL metrics
4. Add Redis for caching (optional)
5. Add Nginx for load balancing (optional)

