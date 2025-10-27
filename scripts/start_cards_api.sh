#!/bin/bash
# Start Cards API server

set -e

echo "🚀 Starting Cards API..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if SUPABASE_DATABASE_URL is set
if [ -z "$SUPABASE_DATABASE_URL" ]; then
    echo "❌ ERROR: SUPABASE_DATABASE_URL not set"
    exit 1
fi

echo "✅ Environment loaded"
echo "📍 Database: $(echo $SUPABASE_DATABASE_URL | cut -d'@' -f2)"

# Start server
python3 -m uvicorn cards.api.main:app \
    --host 0.0.0.0 \
    --port 8002 \
    --reload \
    --log-level info

