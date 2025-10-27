#!/bin/bash
#
# Start All Services for Sprint 4 Day 1 Testing
#
# Services:
# - Cards API (port 8002)
# - Onboarding API (port 8001)
# - Workflow API (port 8000)
#

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo "=========================================================================="
echo "  SPRINT 4 DAY 1: START ALL SERVICES"
echo "=========================================================================="
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# ============================================================================
# STEP 1: Start Cards API (Docker Compose)
# ============================================================================
echo -e "${YELLOW}STEP 1: Starting Cards API (Docker Compose)...${NC}"

if [ -d "cards-api" ]; then
    cd cards-api
    
    # Check if docker-compose.yml exists
    if [ -f "docker-compose.yml" ]; then
        echo "Starting Cards API services..."
        docker-compose up -d
        
        # Wait for health check
        echo "Waiting for Cards API to be ready..."
        for i in {1..30}; do
            if curl -s http://localhost:8002/health > /dev/null 2>&1; then
                echo -e "${GREEN}✅ Cards API is ready (http://localhost:8002)${NC}"
                break
            fi
            
            if [ $i -eq 30 ]; then
                echo -e "${RED}❌ Cards API failed to start after 30 seconds${NC}"
                exit 1
            fi
            
            sleep 1
        done
    else
        echo -e "${RED}❌ docker-compose.yml not found in cards-api/${NC}"
        exit 1
    fi
    
    cd "$PROJECT_ROOT"
else
    echo -e "${RED}❌ cards-api directory not found${NC}"
    exit 1
fi

echo ""

# ============================================================================
# STEP 2: Start Onboarding API (Python)
# ============================================================================
echo -e "${YELLOW}STEP 2: Starting Onboarding API...${NC}"

if [ -d "onboarding" ]; then
    cd onboarding
    
    # Check if main.py exists
    if [ -f "api/main.py" ]; then
        echo "Starting Onboarding API in background..."
        
        # Kill existing process if running
        pkill -f "onboarding.api.main" || true
        
        # Start in background
        nohup python3 -m onboarding.api.main > ../logs/onboarding.log 2>&1 &
        ONBOARDING_PID=$!
        
        echo "Onboarding API PID: $ONBOARDING_PID"
        
        # Wait for health check
        echo "Waiting for Onboarding API to be ready..."
        for i in {1..30}; do
            if curl -s http://localhost:8001/health > /dev/null 2>&1; then
                echo -e "${GREEN}✅ Onboarding API is ready (http://localhost:8001)${NC}"
                break
            fi
            
            if [ $i -eq 30 ]; then
                echo -e "${RED}❌ Onboarding API failed to start after 30 seconds${NC}"
                echo "Check logs: tail -f logs/onboarding.log"
                exit 1
            fi
            
            sleep 1
        done
    else
        echo -e "${RED}❌ api/main.py not found in onboarding/${NC}"
        exit 1
    fi
    
    cd "$PROJECT_ROOT"
else
    echo -e "${RED}❌ onboarding directory not found${NC}"
    exit 1
fi

echo ""

# ============================================================================
# STEP 3: Start Workflow API (Python/FastAPI)
# ============================================================================
echo -e "${YELLOW}STEP 3: Starting Workflow API...${NC}"

if [ -d "api" ]; then
    cd api
    
    # Check if main.py exists
    if [ -f "rest/main.py" ]; then
        echo "Starting Workflow API in background..."
        
        # Kill existing process if running
        pkill -f "rest.main:app" || true
        
        # Start in background
        nohup uvicorn rest.main:app --host 0.0.0.0 --port 8000 > ../logs/workflow.log 2>&1 &
        WORKFLOW_PID=$!
        
        echo "Workflow API PID: $WORKFLOW_PID"
        
        # Wait for health check
        echo "Waiting for Workflow API to be ready..."
        for i in {1..30}; do
            if curl -s http://localhost:8000/health > /dev/null 2>&1; then
                echo -e "${GREEN}✅ Workflow API is ready (http://localhost:8000)${NC}"
                break
            fi
            
            if [ $i -eq 30 ]; then
                echo -e "${RED}❌ Workflow API failed to start after 30 seconds${NC}"
                echo "Check logs: tail -f logs/workflow.log"
                exit 1
            fi
            
            sleep 1
        done
    else
        echo -e "${RED}❌ rest/main.py not found in api/${NC}"
        exit 1
    fi
    
    cd "$PROJECT_ROOT"
else
    echo -e "${RED}❌ api directory not found${NC}"
    exit 1
fi

echo ""

# ============================================================================
# SUMMARY
# ============================================================================
echo "=========================================================================="
echo -e "${GREEN}✅ ALL SERVICES STARTED SUCCESSFULLY${NC}"
echo "=========================================================================="
echo ""
echo "Services:"
echo "  - Cards API:      http://localhost:8002"
echo "  - Onboarding API: http://localhost:8001"
echo "  - Workflow API:   http://localhost:8000"
echo ""
echo "Logs:"
echo "  - Onboarding: tail -f logs/onboarding.log"
echo "  - Workflow:   tail -f logs/workflow.log"
echo "  - Cards:      docker-compose -f cards-api/docker-compose.yml logs -f"
echo ""
echo "To run end-to-end test:"
echo "  python3 scripts/test_e2e_onboarding_cards.py"
echo ""
echo "To stop services:"
echo "  ./scripts/stop_all_services.sh"
echo ""

