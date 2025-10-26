#!/bin/bash
#
# Validate all OpenAPI contracts
#
# Usage: ./contracts/validate.sh
#

set -e

echo "🔍 Validating OpenAPI Contracts..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if openapi-spec-validator is installed
if ! python3 -c "import openapi_spec_validator" 2>/dev/null; then
    echo "❌ openapi-spec-validator not installed"
    echo "Install with: pip install openapi-spec-validator"
    exit 1
fi

# Validate each contract
contracts=(
    "contracts/cards-api-v1.yaml"
    "contracts/workflow-api-v1.yaml"
    "contracts/onboarding-api-v1.yaml"
)

failed=0

for contract in "${contracts[@]}"; do
    echo "Validating $contract..."
    if python3 -m openapi_spec_validator "$contract"; then
        echo -e "${GREEN}✅ $contract: OK${NC}"
    else
        echo -e "${RED}❌ $contract: FAILED${NC}"
        failed=$((failed + 1))
    fi
    echo ""
done

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $failed -eq 0 ]; then
    echo -e "${GREEN}✅ All contracts valid!${NC}"
    exit 0
else
    echo -e "${RED}❌ $failed contract(s) failed validation${NC}"
    exit 1
fi

