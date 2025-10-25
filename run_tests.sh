#!/bin/bash

# Card Service V1 - Test Runner Script

set -e

echo "🧪 Card Service V1 - Test Suite"
echo "================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
TEST_TYPE=${1:-all}
COVERAGE=${2:-false}

# Function to run tests
run_tests() {
    local test_type=$1
    local coverage=$2

    case $test_type in
        unit)
            echo -e "${YELLOW}Running Unit Tests...${NC}"
            if [ "$coverage" = "true" ]; then
                pytest tests/unit -v --cov=core --cov=onboarding --cov-report=html
            else
                pytest tests/unit -v
            fi
            ;;
        integration)
            echo -e "${YELLOW}Running Integration Tests...${NC}"
            if [ "$coverage" = "true" ]; then
                pytest tests/integration -v --cov=core --cov=onboarding --cov-report=html
            else
                pytest tests/integration -v
            fi
            ;;
        all)
            echo -e "${YELLOW}Running All Tests...${NC}"
            if [ "$coverage" = "true" ]; then
                pytest tests/ -v --cov=core --cov=onboarding --cov-report=html
            else
                pytest tests/ -v
            fi
            ;;
        *)
            echo -e "${RED}Unknown test type: $test_type${NC}"
            echo "Usage: ./run_tests.sh [unit|integration|all] [coverage]"
            exit 1
            ;;
    esac
}

# Run tests
if run_tests "$TEST_TYPE" "$COVERAGE"; then
    echo ""
    echo -e "${GREEN}✅ All tests passed!${NC}"
    
    if [ "$COVERAGE" = "true" ]; then
        echo -e "${GREEN}📊 Coverage report generated: htmlcov/index.html${NC}"
    fi
else
    echo ""
    echo -e "${RED}❌ Tests failed!${NC}"
    exit 1
fi

