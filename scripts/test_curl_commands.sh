#!/usr/bin/env bash
set -euo pipefail

BASE_URL=${BASE_URL:-http://localhost:8000}

printf "\n==> Testing /api/v1/content/generate <==\n"
cat <<'JSON' > /tmp/payload.json
{
  "topic": "AI nel Fintech",
  "workflow_type": "enhanced_article",
  "client_profile": "default",
  "provider": "openai",
  "model": "gpt-4o",
  "temperature": 0.7,
  "target_word_count": 800,
  "target_audience": "investitori retail",
  "tone": "professionale",
  "include_statistics": true,
  "include_examples": true,
  "context": "focus su trend 2025 e impatto normativo"
}
JSON

curl -s -X POST "$BASE_URL/api/v1/content/generate" \
  -H "Content-Type: application/json" \
  -d @/tmp/payload.json | jq '.title, (.body | tostring)[0:300]'

printf "\n==> Testing /api/v1/workflows/execute <==\n"
cat <<'JSON' > /tmp/payload_exec.json
{
  "workflow_id": "enhanced_article",
  "parameters": {
    "topic": "AI nel Fintech",
    "target_audience": "investitori retail",
    "tone": "professionale",
    "context": "focus su trend 2025 e impatto normativo",
    "include_statistics": true,
    "include_examples": true,
    "client_profile": "default",
    "target_word_count": 800
  }
}
JSON

curl -s -X POST "$BASE_URL/api/v1/workflows/execute" \
  -H "Content-Type: application/json" \
  -d @/tmp/payload_exec.json | jq '.'

