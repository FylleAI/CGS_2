#!/bin/bash

# Benchmark Cards API - Measure p95 latency
# Usage: ./scripts/benchmark_cards_api.sh

set -e  # Exit on error

echo "📊 Benchmarking Cards API..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CARDS_API_URL="${CARDS_API_URL:-http://localhost:8002}"
TENANT_ID="123e4567-e89b-12d3-a456-426614174000"
NUM_REQUESTS=1000
CONCURRENCY=10
RESULTS_DIR="benchmark_results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create results directory
mkdir -p $RESULTS_DIR

echo -e "${YELLOW}📋 Configuration:${NC}"
echo "  - API URL: $CARDS_API_URL"
echo "  - Tenant ID: $TENANT_ID"
echo "  - Requests: $NUM_REQUESTS"
echo "  - Concurrency: $CONCURRENCY"
echo ""

# Check if API is healthy
echo -e "${YELLOW}📋 Checking API health...${NC}"
if ! curl -f -s "$CARDS_API_URL/health" > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: API is not healthy${NC}"
    exit 1
fi
echo -e "${GREEN}✅ API is healthy${NC}"
echo ""

# Function to run benchmark with Apache Bench
run_ab_benchmark() {
    local endpoint=$1
    local method=$2
    local payload_file=$3
    local description=$4
    local output_file="$RESULTS_DIR/${endpoint}_${TIMESTAMP}.txt"
    
    echo -e "${BLUE}📊 Benchmarking: $description${NC}"
    echo "  - Endpoint: $endpoint"
    echo "  - Method: $method"
    echo "  - Requests: $NUM_REQUESTS"
    echo "  - Concurrency: $CONCURRENCY"
    echo ""
    
    if [ "$method" = "POST" ]; then
        ab -n $NUM_REQUESTS -c $CONCURRENCY \
           -T "application/json" \
           -H "X-Tenant-ID: $TENANT_ID" \
           -H "Idempotency-Key: benchmark-$(uuidgen)" \
           -p "$payload_file" \
           "$CARDS_API_URL$endpoint" > "$output_file" 2>&1
    else
        ab -n $NUM_REQUESTS -c $CONCURRENCY \
           -H "X-Tenant-ID: $TENANT_ID" \
           "$CARDS_API_URL$endpoint" > "$output_file" 2>&1
    fi
    
    # Parse results
    local mean_time=$(grep "Time per request:" "$output_file" | head -1 | awk '{print $4}')
    local p50=$(grep "50%" "$output_file" | awk '{print $2}')
    local p95=$(grep "95%" "$output_file" | awk '{print $2}')
    local p99=$(grep "99%" "$output_file" | awk '{print $2}')
    local requests_per_sec=$(grep "Requests per second:" "$output_file" | awk '{print $4}')
    
    echo -e "${GREEN}✅ Results:${NC}"
    echo "  - Mean time: ${mean_time} ms"
    echo "  - p50: ${p50} ms"
    echo "  - p95: ${p95} ms"
    echo "  - p99: ${p99} ms"
    echo "  - Requests/sec: ${requests_per_sec}"
    echo ""
    
    # Check if p95 meets target
    local target_p95=$5
    if [ -n "$target_p95" ]; then
        if (( $(echo "$p95 <= $target_p95" | bc -l) )); then
            echo -e "${GREEN}✅ p95 ($p95 ms) meets target (≤ $target_p95 ms)${NC}"
        else
            echo -e "${RED}❌ p95 ($p95 ms) exceeds target (≤ $target_p95 ms)${NC}"
        fi
        echo ""
    fi
    
    # Save summary
    echo "$description,$mean_time,$p50,$p95,$p99,$requests_per_sec" >> "$RESULTS_DIR/summary_${TIMESTAMP}.csv"
}

# Function to run benchmark with Python (more accurate for POST requests)
run_python_benchmark() {
    local endpoint=$1
    local method=$2
    local payload=$3
    local description=$4
    local target_p95=$5
    
    echo -e "${BLUE}📊 Benchmarking: $description${NC}"
    echo "  - Endpoint: $endpoint"
    echo "  - Method: $method"
    echo "  - Requests: $NUM_REQUESTS"
    echo "  - Concurrency: $CONCURRENCY"
    echo ""
    
    python3 - <<EOF
import asyncio
import aiohttp
import time
import statistics
import json
from uuid import uuid4

async def make_request(session, url, headers, payload):
    start = time.time()
    try:
        async with session.post(url, headers=headers, json=payload) as response:
            await response.text()
            return (time.time() - start) * 1000  # Convert to ms
    except Exception as e:
        print(f"Error: {e}")
        return None

async def benchmark():
    url = "$CARDS_API_URL$endpoint"
    headers = {
        "X-Tenant-ID": "$TENANT_ID",
        "Idempotency-Key": f"benchmark-{uuid4()}",
        "Content-Type": "application/json"
    }
    payload = $payload
    
    latencies = []
    
    async with aiohttp.ClientSession() as session:
        # Warmup
        for _ in range(10):
            await make_request(session, url, headers, payload)
        
        # Actual benchmark
        tasks = []
        for i in range($NUM_REQUESTS):
            # Update idempotency key for each request
            headers["Idempotency-Key"] = f"benchmark-{uuid4()}"
            tasks.append(make_request(session, url, headers, payload))
            
            # Run in batches to control concurrency
            if len(tasks) >= $CONCURRENCY:
                results = await asyncio.gather(*tasks)
                latencies.extend([r for r in results if r is not None])
                tasks = []
        
        # Run remaining tasks
        if tasks:
            results = await asyncio.gather(*tasks)
            latencies.extend([r for r in results if r is not None])
    
    # Calculate statistics
    latencies.sort()
    mean = statistics.mean(latencies)
    median = statistics.median(latencies)
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[int(len(latencies) * 0.99)]
    min_lat = min(latencies)
    max_lat = max(latencies)
    
    print(f"✅ Results:")
    print(f"  - Mean: {mean:.2f} ms")
    print(f"  - Median (p50): {median:.2f} ms")
    print(f"  - p95: {p95:.2f} ms")
    print(f"  - p99: {p99:.2f} ms")
    print(f"  - Min: {min_lat:.2f} ms")
    print(f"  - Max: {max_lat:.2f} ms")
    print(f"  - Total requests: {len(latencies)}")
    print()
    
    # Check target
    target = $target_p95
    if target > 0:
        if p95 <= target:
            print(f"✅ p95 ({p95:.2f} ms) meets target (≤ {target} ms)")
        else:
            print(f"❌ p95 ({p95:.2f} ms) exceeds target (≤ {target} ms)")
        print()
    
    # Save to CSV
    with open("$RESULTS_DIR/summary_${TIMESTAMP}.csv", "a") as f:
        f.write(f"$description,{mean:.2f},{median:.2f},{p95:.2f},{p99:.2f},{len(latencies)/sum(latencies)*1000:.2f}\n")

asyncio.run(benchmark())
EOF
}

# Initialize summary CSV
echo "Endpoint,Mean (ms),p50 (ms),p95 (ms),p99 (ms),Requests/sec" > "$RESULTS_DIR/summary_${TIMESTAMP}.csv"

# Benchmark 1: Health endpoint (baseline)
echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}BENCHMARK 1: Health Check (GET /health)${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
echo ""

if command -v ab &> /dev/null; then
    ab -n $NUM_REQUESTS -c $CONCURRENCY "$CARDS_API_URL/health" > "$RESULTS_DIR/health_${TIMESTAMP}.txt" 2>&1
    
    mean_time=$(grep "Time per request:" "$RESULTS_DIR/health_${TIMESTAMP}.txt" | head -1 | awk '{print $4}')
    p95=$(grep "95%" "$RESULTS_DIR/health_${TIMESTAMP}.txt" | awk '{print $2}')
    
    echo -e "${GREEN}✅ Health Check Results:${NC}"
    echo "  - Mean: ${mean_time} ms"
    echo "  - p95: ${p95} ms"
    echo ""
else
    echo -e "${YELLOW}⚠️  Apache Bench (ab) not installed, skipping${NC}"
    echo ""
fi

# Benchmark 2: Batch Create (POST /api/v1/cards/batch)
echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}BENCHMARK 2: Batch Create (POST /api/v1/cards/batch)${NC}"
echo -e "${YELLOW}Target: p95 ≤ 100 ms${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
echo ""

BATCH_PAYLOAD='{
  "cards": [
    {
      "card_type": "company",
      "content": {
        "name": "Benchmark Company",
        "domain": "benchmark.com",
        "industry": "Technology"
      }
    }
  ]
}'

run_python_benchmark "/api/v1/cards/batch" "POST" "$BATCH_PAYLOAD" "Batch Create" 100

# Benchmark 3: Retrieve Cards (POST /api/v1/cards/retrieve)
echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}BENCHMARK 3: Retrieve Cards (POST /api/v1/cards/retrieve)${NC}"
echo -e "${YELLOW}Target: p95 ≤ 50 ms${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
echo ""

# First, create a card to retrieve
CARD_ID=$(curl -s -X POST "$CARDS_API_URL/api/v1/cards/batch" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: $TENANT_ID" \
  -H "Idempotency-Key: setup-$(uuidgen)" \
  -d "$BATCH_PAYLOAD" | python3 -c "import sys, json; print(json.load(sys.stdin)['cards'][0]['card_id'])")

echo "Created test card: $CARD_ID"
echo ""

RETRIEVE_PAYLOAD="{\"card_ids\": [\"$CARD_ID\"]}"

run_python_benchmark "/api/v1/cards/retrieve" "POST" "$RETRIEVE_PAYLOAD" "Retrieve Cards" 50

# Benchmark 4: Track Usage (POST /api/v1/cards/{id}/usage)
echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}BENCHMARK 4: Track Usage (POST /api/v1/cards/{id}/usage)${NC}"
echo -e "${YELLOW}Target: p95 ≤ 25 ms${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
echo ""

USAGE_PAYLOAD='{
  "workflow_id": "benchmark-workflow",
  "workflow_type": "premium_newsletter",
  "session_id": "benchmark-session"
}'

run_python_benchmark "/api/v1/cards/$CARD_ID/usage" "POST" "$USAGE_PAYLOAD" "Track Usage" 25

# Summary
echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}BENCHMARK SUMMARY${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${BLUE}📊 Results saved to: $RESULTS_DIR/summary_${TIMESTAMP}.csv${NC}"
echo ""

cat "$RESULTS_DIR/summary_${TIMESTAMP}.csv"

echo ""
echo -e "${GREEN}🎉 Benchmark complete!${NC}"
echo ""
echo "📋 Next steps:"
echo "  1. Review results: cat $RESULTS_DIR/summary_${TIMESTAMP}.csv"
echo "  2. View detailed logs: ls -la $RESULTS_DIR/"
echo "  3. Compare with targets:"
echo "     - Batch Create: p95 ≤ 100 ms"
echo "     - Retrieve Cards: p95 ≤ 50 ms"
echo "     - Track Usage: p95 ≤ 25 ms"
echo ""

