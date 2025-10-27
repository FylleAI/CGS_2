#!/bin/bash

# Deploy Cards API to Staging Environment
# Usage: ./scripts/deploy_staging.sh

set -e  # Exit on error

echo "🚀 Deploying Cards API to Staging..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.cards.yml"
STAGING_ENV=".env.staging"
HEALTH_CHECK_URL="http://localhost:8002/health"
READY_CHECK_URL="http://localhost:8002/ready"
METRICS_URL="http://localhost:8002/metrics"
MAX_RETRIES=30
RETRY_INTERVAL=2

# Step 1: Check prerequisites
echo -e "${YELLOW}📋 Step 1: Checking prerequisites...${NC}"

if [ ! -f "$COMPOSE_FILE" ]; then
    echo -e "${RED}❌ Error: $COMPOSE_FILE not found${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Error: Docker not installed${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Error: docker-compose not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites OK${NC}"

# Step 2: Load staging environment variables
echo -e "${YELLOW}📋 Step 2: Loading staging environment...${NC}"

if [ -f "$STAGING_ENV" ]; then
    export $(cat $STAGING_ENV | grep -v '^#' | xargs)
    echo -e "${GREEN}✅ Staging environment loaded${NC}"
else
    echo -e "${YELLOW}⚠️  Warning: $STAGING_ENV not found, using defaults${NC}"
fi

# Step 3: Stop existing containers
echo -e "${YELLOW}📋 Step 3: Stopping existing containers...${NC}"

docker-compose -f $COMPOSE_FILE down || true

echo -e "${GREEN}✅ Containers stopped${NC}"

# Step 4: Pull latest images
echo -e "${YELLOW}📋 Step 4: Pulling latest images...${NC}"

docker-compose -f $COMPOSE_FILE pull || true

echo -e "${GREEN}✅ Images pulled${NC}"

# Step 5: Build Cards API image
echo -e "${YELLOW}📋 Step 5: Building Cards API image...${NC}"

docker-compose -f $COMPOSE_FILE build cards-api

echo -e "${GREEN}✅ Cards API image built${NC}"

# Step 6: Start services
echo -e "${YELLOW}📋 Step 6: Starting services...${NC}"

docker-compose -f $COMPOSE_FILE up -d

echo -e "${GREEN}✅ Services started${NC}"

# Step 7: Wait for health check
echo -e "${YELLOW}📋 Step 7: Waiting for health check...${NC}"

RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f -s $HEALTH_CHECK_URL > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Health check passed${NC}"
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo -e "${YELLOW}⏳ Waiting for health check... ($RETRY_COUNT/$MAX_RETRIES)${NC}"
    sleep $RETRY_INTERVAL
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}❌ Error: Health check failed after $MAX_RETRIES retries${NC}"
    echo -e "${YELLOW}📋 Showing logs:${NC}"
    docker-compose -f $COMPOSE_FILE logs --tail=50 cards-api
    exit 1
fi

# Step 8: Verify readiness
echo -e "${YELLOW}📋 Step 8: Verifying readiness...${NC}"

if curl -f -s $READY_CHECK_URL > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Readiness check passed${NC}"
else
    echo -e "${RED}❌ Error: Readiness check failed${NC}"
    exit 1
fi

# Step 9: Verify metrics endpoint
echo -e "${YELLOW}📋 Step 9: Verifying metrics endpoint...${NC}"

if curl -f -s $METRICS_URL > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Metrics endpoint OK${NC}"
else
    echo -e "${RED}❌ Error: Metrics endpoint failed${NC}"
    exit 1
fi

# Step 10: Show service status
echo -e "${YELLOW}📋 Step 10: Service status...${NC}"

docker-compose -f $COMPOSE_FILE ps

echo ""
echo -e "${GREEN}🎉 Deployment successful!${NC}"
echo ""
echo "📊 Service URLs:"
echo "  - Cards API:  http://localhost:8002"
echo "  - API Docs:   http://localhost:8002/docs"
echo "  - Health:     $HEALTH_CHECK_URL"
echo "  - Ready:      $READY_CHECK_URL"
echo "  - Metrics:    $METRICS_URL"
echo "  - Prometheus: http://localhost:9090"
echo "  - Grafana:    http://localhost:3000"
echo ""
echo "📋 Next steps:"
echo "  1. Run health checks: curl $HEALTH_CHECK_URL"
echo "  2. View API docs: open http://localhost:8002/docs"
echo "  3. View logs: docker-compose -f $COMPOSE_FILE logs -f cards-api"
echo "  4. Run benchmarks: ./scripts/benchmark_cards_api.sh"
echo ""

