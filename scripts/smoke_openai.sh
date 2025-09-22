#!/usr/bin/env bash
set -euo pipefail

JSON=$(cat <<'EOF'
{
  "topic": "Smoke test Milano skyline sunset",
  "content_type": "article",
  "content_format": "markdown",
  "client_profile": "reopla",
  "workflow_type": "enhanced_article_with_image",
  "provider": "openai",
  "model": "gpt-4o-mini",
  "temperature": 0.2,
  "max_tokens": 256,
  "target_word_count": 120,
  "tone": "professional",
  "include_statistics": false,
  "include_examples": false,
  "image_style": "professional",
  "image_provider": "openai",
  "custom_instructions": "Short smoke test"
}
EOF
)

curl -s -S -H 'Content-Type: application/json' -d "$JSON" http://localhost:8000/api/v1/content/generate |
  tee /tmp/smoke_out.json |
  jq -C '{success, tasks_completed, total_tasks, generated_image: ( .generated_image | {type, url, size, format} ), image_metadata: ( .image_metadata | {provider, size, style} ) }'

