#!/bin/bash

# CHECK_SERVICES_STATUS.sh - Verifica lo stato di tutti i servizi

echo "🔍 Checking CGS Services Status..."
echo ""

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funzione per verificare servizio
check_service() {
    local url=$1
    local name=$2
    local port=$3
    
    if curl -s "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $name${NC} (port $port) - ${GREEN}RUNNING${NC}"
        return 0
    else
        echo -e "${RED}❌ $name${NC} (port $port) - ${RED}NOT RUNNING${NC}"
        return 1
    fi
}

# Funzione per verificare frontend
check_frontend() {
    local url=$1
    local name=$2
    local port=$3
    
    if curl -s "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $name${NC} (port $port) - ${GREEN}RUNNING${NC}"
        return 0
    else
        echo -e "${RED}❌ $name${NC} (port $port) - ${RED}NOT RUNNING${NC}"
        return 1
    fi
}

echo -e "${BLUE}Backend Services:${NC}"
echo "================================"
check_service "http://127.0.0.1:8000/docs" "Main API" "8000"
check_service "http://127.0.0.1:8001/docs" "Card Service" "8001"
check_service "http://127.0.0.1:8002/docs" "Onboarding Service" "8002"

echo ""
echo -e "${BLUE}Frontend Applications:${NC}"
echo "================================"
check_frontend "http://127.0.0.1:5173" "Card Manager" "5173"
check_frontend "http://127.0.0.1:5174" "Onboarding Frontend" "5174"

echo ""
echo -e "${BLUE}Database:${NC}"
echo "================================"
if [ ! -z "$SUPABASE_URL" ]; then
    echo -e "${GREEN}✅ Supabase URL configured${NC}"
else
    echo -e "${YELLOW}⚠️  Supabase URL not configured${NC}"
fi

echo ""
echo -e "${BLUE}Environment:${NC}"
echo "================================"
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ .env file found${NC}"
else
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
fi

if [ -f ".env.local" ]; then
    echo -e "${GREEN}✅ .env.local file found${NC}"
else
    echo -e "${YELLOW}⚠️  .env.local file not found${NC}"
fi

echo ""
echo -e "${BLUE}Logs:${NC}"
echo "================================"
if [ -d "logs" ]; then
    echo -e "${GREEN}✅ logs directory exists${NC}"
    ls -lh logs/ 2>/dev/null | tail -5
else
    echo -e "${YELLOW}⚠️  logs directory not found${NC}"
fi

echo ""
echo -e "${BLUE}Quick Links:${NC}"
echo "================================"
echo "  📌 Main API:              http://127.0.0.1:8000"
echo "  📌 Main API Docs:         http://127.0.0.1:8000/docs"
echo "  📌 Card Service Docs:     http://127.0.0.1:8001/docs"
echo "  📌 Onboarding Docs:       http://127.0.0.1:8002/docs"
echo "  📌 Card Manager:          http://127.0.0.1:5173"
echo "  📌 Onboarding Frontend:   http://127.0.0.1:5174"
echo ""

