#!/bin/bash

# STOP_ALL_SERVICES.sh - Ferma tutti i servizi CGS

echo "🛑 Stopping all CGS services..."
echo ""

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Load PIDs from file
if [ -f ".services_pids" ]; then
    source .services_pids
    
    # Kill each service
    if [ ! -z "$CARD_SERVICE_PID" ]; then
        kill $CARD_SERVICE_PID 2>/dev/null && print_success "Card Service stopped" || print_warning "Card Service already stopped"
    fi
    
    if [ ! -z "$ONBOARDING_PID" ]; then
        kill $ONBOARDING_PID 2>/dev/null && print_success "Onboarding Service stopped" || print_warning "Onboarding Service already stopped"
    fi
    
    if [ ! -z "$MAIN_API_PID" ]; then
        kill $MAIN_API_PID 2>/dev/null && print_success "Main API stopped" || print_warning "Main API already stopped"
    fi
    
    if [ ! -z "$CARD_MANAGER_PID" ]; then
        kill $CARD_MANAGER_PID 2>/dev/null && print_success "Card Manager Frontend stopped" || print_warning "Card Manager Frontend already stopped"
    fi
    
    if [ ! -z "$ONBOARDING_FRONTEND_PID" ]; then
        kill $ONBOARDING_FRONTEND_PID 2>/dev/null && print_success "Onboarding Frontend stopped" || print_warning "Onboarding Frontend already stopped"
    fi
    
    # Remove PID file
    rm .services_pids
    print_success "PID file removed"
else
    print_warning "No .services_pids file found. Trying to kill processes by port..."
    
    # Kill by port (Linux/Mac)
    if command -v lsof &> /dev/null; then
        for port in 8000 8001 8002 5173 5174; do
            lsof -ti:$port | xargs kill -9 2>/dev/null && print_success "Process on port $port killed" || print_warning "No process on port $port"
        done
    else
        print_error "lsof not found. Please manually kill the processes."
    fi
fi

echo ""
print_success "All services stopped!"

