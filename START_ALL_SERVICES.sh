#!/bin/bash

# START_ALL_SERVICES.sh - Avvia tutti i servizi CGS

set -e

echo "🚀 Starting all CGS services..."
echo ""

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funzione per stampare header
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# Funzione per stampare success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Funzione per stampare warning
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Funzione per stampare error
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check Python venv
print_header "Checking Python Virtual Environment"
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found. Creating..."
    python -m venv venv
fi

# Activate venv
source venv/Scripts/activate 2>/dev/null || source venv/bin/activate
print_success "Virtual environment activated"

# Check dependencies
print_header "Checking Dependencies"
pip install -q -r requirements.txt 2>/dev/null || print_warning "Some dependencies may not have installed"
print_success "Dependencies checked"

# Start services in background
print_header "Starting Services"

# 1. Card Service (port 8001)
print_warning "Starting Card Service on port 8001..."
cd services/card_service || cd core/card_service
python -m uvicorn api.card_routes:app --host 127.0.0.1 --port 8001 --reload > ../../logs/card_service.log 2>&1 &
CARD_SERVICE_PID=$!
cd ../..
print_success "Card Service started (PID: $CARD_SERVICE_PID)"

# 2. Onboarding Service (port 8002)
print_warning "Starting Onboarding Service on port 8002..."
cd services/onboarding || cd onboarding
python -m uvicorn api.main:app --host 127.0.0.1 --port 8002 --reload > ../logs/onboarding_service.log 2>&1 &
ONBOARDING_PID=$!
cd ..
print_success "Onboarding Service started (PID: $ONBOARDING_PID)"

# 3. Main API (port 8000)
print_warning "Starting Main API on port 8000..."
cd api/rest
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload > ../../logs/main_api.log 2>&1 &
MAIN_API_PID=$!
cd ../..
print_success "Main API started (PID: $MAIN_API_PID)"

# 4. Card Manager Frontend (port 5173)
print_warning "Starting Card Manager Frontend on port 5173..."
cd frontends/card-explorer || cd card-frontend
npm run dev > ../../logs/card_manager.log 2>&1 &
CARD_MANAGER_PID=$!
cd ../..
print_success "Card Manager Frontend started (PID: $CARD_MANAGER_PID)"

# 5. Onboarding Frontend (port 5174)
print_warning "Starting Onboarding Frontend on port 5174..."
cd onboarding-frontend
npm run dev -- --port 5174 > ../logs/onboarding_frontend.log 2>&1 &
ONBOARDING_FRONTEND_PID=$!
cd ..
print_success "Onboarding Frontend started (PID: $ONBOARDING_FRONTEND_PID)"

# Save PIDs to file
print_header "Saving Process IDs"
cat > .services_pids << EOF
CARD_SERVICE_PID=$CARD_SERVICE_PID
ONBOARDING_PID=$ONBOARDING_PID
MAIN_API_PID=$MAIN_API_PID
CARD_MANAGER_PID=$CARD_MANAGER_PID
ONBOARDING_FRONTEND_PID=$ONBOARDING_FRONTEND_PID
EOF
print_success "Process IDs saved to .services_pids"

# Wait a bit for services to start
sleep 3

# Check services
print_header "Checking Services Status"

check_service() {
    local url=$1
    local name=$2
    if curl -s "$url" > /dev/null 2>&1; then
        print_success "$name is running"
    else
        print_warning "$name may not be ready yet (check logs)"
    fi
}

check_service "http://127.0.0.1:8000/docs" "Main API"
check_service "http://127.0.0.1:8001/docs" "Card Service"
check_service "http://127.0.0.1:8002/docs" "Onboarding Service"

# Print summary
print_header "Services Started Successfully!"
echo ""
echo -e "${GREEN}Services running:${NC}"
echo "  📌 Main API:              http://127.0.0.1:8000"
echo "  📌 Main API Docs:         http://127.0.0.1:8000/docs"
echo "  📌 Card Service:          http://127.0.0.1:8001"
echo "  📌 Card Service Docs:     http://127.0.0.1:8001/docs"
echo "  📌 Onboarding Service:    http://127.0.0.1:8002"
echo "  📌 Onboarding Docs:       http://127.0.0.1:8002/docs"
echo "  📌 Card Manager:          http://127.0.0.1:5173"
echo "  📌 Onboarding Frontend:   http://127.0.0.1:5174"
echo ""
echo -e "${YELLOW}Logs:${NC}"
echo "  📄 logs/main_api.log"
echo "  📄 logs/card_service.log"
echo "  📄 logs/onboarding_service.log"
echo "  📄 logs/card_manager.log"
echo "  📄 logs/onboarding_frontend.log"
echo ""
echo -e "${YELLOW}To stop all services, run:${NC}"
echo "  bash STOP_ALL_SERVICES.sh"
echo ""

