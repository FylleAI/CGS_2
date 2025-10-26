#!/bin/bash
#
# Lint check for manual HTTP calls to Fylle APIs
#
# Policy: Zero Manual Clients
# Direct use of httpx/requests to call Fylle APIs is prohibited when SDK exists.
#
# Usage: ./scripts/lint-no-manual-clients.sh
#

set -e

echo "🔍 Checking for manual HTTP calls to Fylle APIs..."
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Patterns to search for
PATTERNS=(
    "httpx\.(post|get|put|patch|delete)\("
    "requests\.(post|get|put|patch|delete)\("
)

violations=0
files_checked=0

# Find all Python files (excluding specific directories)
while IFS= read -r file; do
    # Skip excluded directories
    if [[ "$file" =~ clients/ ]] || \
       [[ "$file" =~ \.git/ ]] || \
       [[ "$file" =~ venv/ ]] || \
       [[ "$file" =~ __pycache__/ ]] || \
       [[ "$file" =~ \.pytest_cache/ ]] || \
       [[ "$file" =~ node_modules/ ]]; then
        continue
    fi

    files_checked=$((files_checked + 1))

    # Check if file has lint:allow-manual-http comment
    if grep -q "# lint:allow-manual-http" "$file" 2>/dev/null; then
        continue
    fi

    # Check for prohibited patterns
    for pattern in "${PATTERNS[@]}"; do
        if grep -E "$pattern" "$file" >/dev/null 2>&1; then
            # Check if it's calling a Fylle API
            if grep -E "(localhost:800[0-9]|cards-api\.fylle\.ai|workflow-api\.fylle\.ai|onboarding-api\.fylle\.ai)" "$file" >/dev/null 2>&1; then
                echo -e "${RED}❌ Manual HTTP call found in: $file${NC}"
                grep -n -E "$pattern" "$file" | head -3
                echo ""
                violations=$((violations + 1))
            fi
        fi
    done
done < <(find . -name "*.py" -type f)

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Files checked: $files_checked"

if [ $violations -eq 0 ]; then
    echo -e "${GREEN}✅ No manual HTTP calls found!${NC}"
    echo ""
    echo "Policy: Zero Manual Clients ✓"
    exit 0
else
    echo -e "${RED}❌ Found $violations file(s) with manual HTTP calls${NC}"
    echo ""
    echo "Policy: Zero Manual Clients"
    echo ""
    echo "Direct use of httpx/requests to call Fylle APIs is prohibited."
    echo "Use the appropriate SDK instead:"
    echo "  - fylle-cards-client for Cards API"
    echo "  - fylle-workflow-client for Workflow API"
    echo ""
    echo "Exceptions:"
    echo "  1. Add '# lint:allow-manual-http' comment to file"
    echo "  2. Get explicit approval from engineering lead"
    echo ""
    exit 1
fi

