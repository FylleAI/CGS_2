#!/bin/bash
#
# Stop All Services for Sprint 4 Day 1 Testing
#

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo "=========================================================================="
echo "  SPRINT 4 DAY 1: STOP ALL SERVICES"
echo "=========================================================================="
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# ============================================================================
# STEP 1: Stop Workflow API
# ============================================================================
echo -e "${YELLOW}STEP 1: Stopping Workflow API...${NC}"

pkill -f "rest.main:app" || echo "No Workflow API process found"
echo -e "${GREEN}✅ Workflow API stopped${NC}"

echo ""

# ============================================================================
# STEP 2: Stop Onboarding API
# ============================================================================
echo -e "${YELLOW}STEP 2: Stopping Onboarding API...${NC}"

pkill -f "onboarding.api.main" || echo "No Onboarding API process found"
echo -e "${GREEN}✅ Onboarding API stopped${NC}"

echo ""

# ============================================================================
# STEP 3: Stop Cards API (Docker Compose)
# ============================================================================
echo -e "${YELLOW}STEP 3: Stopping Cards API (Docker Compose)...${NC}"

if [ -d "cards-api" ]; then
    cd cards-api
    
    if [ -f "docker-compose.yml" ]; then
        docker-compose down
        echo -e "${GREEN}✅ Cards API stopped${NC}"
    else
        echo -e "${YELLOW}⚠️  docker-compose.yml not found${NC}"
    fi
    
    cd "$PROJECT_ROOT"
else
    echo -e "${YELLOW}⚠️  cards-api directory not found${NC}"
fi

echo ""

# ============================================================================
# SUMMARY
# ============================================================================
echo "=========================================================================="
echo -e "${GREEN}✅ ALL SERVICES STOPPED${NC}"
echo "=========================================================================="
echo ""

