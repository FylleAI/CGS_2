#!/bin/bash

# Card Service V1 - Complete System Startup Script
# This script starts all services needed for end-to-end testing

set -e

echo "🚀 Card Service V1 - Complete System Startup"
echo "=============================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_PORT=8000
CARD_FRONTEND_PORT=3001
ONBOARDING_FRONTEND_PORT=3000

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=0

    echo -e "${YELLOW}⏳ Waiting for $service_name to be ready...${NC}"
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $service_name is ready!${NC}"
            return 0
        fi
        attempt=$((attempt + 1))
        echo -n "."
        sleep 1
    done
    
    echo -e "${RED}❌ $service_name failed to start${NC}"
    return 1
}

# Check prerequisites
echo -e "${BLUE}📋 Checking prerequisites...${NC}"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 3 found${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Node.js found${NC}"

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ npm found${NC}"

echo ""

# Check if ports are available
echo -e "${BLUE}🔍 Checking ports...${NC}"
echo ""

if check_port $BACKEND_PORT; then
    echo -e "${YELLOW}⚠️  Port $BACKEND_PORT is already in use${NC}"
    read -p "Kill process on port $BACKEND_PORT? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null || true
        sleep 1
    else
        echo -e "${RED}Cannot proceed without port $BACKEND_PORT${NC}"
        exit 1
    fi
fi

if check_port $CARD_FRONTEND_PORT; then
    echo -e "${YELLOW}⚠️  Port $CARD_FRONTEND_PORT is already in use${NC}"
    read -p "Kill process on port $CARD_FRONTEND_PORT? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        lsof -ti:$CARD_FRONTEND_PORT | xargs kill -9 2>/dev/null || true
        sleep 1
    else
        echo -e "${YELLOW}⚠️  Skipping card-frontend${NC}"
    fi
fi

echo -e "${GREEN}✅ Ports are available${NC}"
echo ""

# Start Backend
echo -e "${BLUE}🔧 Starting Backend (FastAPI)...${NC}"
echo ""

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found, creating from .env.example${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✅ Created .env from .env.example${NC}"
    else
        echo -e "${RED}❌ .env.example not found${NC}"
        exit 1
    fi
fi

# Install Python dependencies if needed
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating Python virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -q -r requirements.txt
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    source venv/bin/activate
fi

# Start backend in background
echo -e "${YELLOW}Starting FastAPI server on port $BACKEND_PORT...${NC}"
uvicorn api.rest.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"

# Wait for backend to be ready
wait_for_service "http://localhost:$BACKEND_PORT/health" "Backend"
echo ""

# Start Card Frontend
echo -e "${BLUE}🎨 Starting Card Frontend (React)...${NC}"
echo ""

if [ -d "card-frontend" ]; then
    cd card-frontend
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}📦 Installing Card Frontend dependencies...${NC}"
        npm install -q
        echo -e "${GREEN}✅ Dependencies installed${NC}"
    fi
    
    # Create .env if needed
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}Creating .env for card-frontend...${NC}"
        cat > .env << EOF
VITE_API_BASE_URL=http://localhost:$BACKEND_PORT
VITE_APP_NAME=Card Service
EOF
        echo -e "${GREEN}✅ Created .env${NC}"
    fi
    
    # Start frontend in background
    echo -e "${YELLOW}Starting React dev server on port $CARD_FRONTEND_PORT...${NC}"
    npm run dev > /tmp/card-frontend.log 2>&1 &
    CARD_FRONTEND_PID=$!
    echo -e "${GREEN}✅ Card Frontend started (PID: $CARD_FRONTEND_PID)${NC}"
    
    # Wait for frontend to be ready
    wait_for_service "http://localhost:$CARD_FRONTEND_PORT" "Card Frontend"
    
    cd ..
else
    echo -e "${YELLOW}⚠️  card-frontend directory not found${NC}"
fi

echo ""

# Display startup summary
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ ALL SERVICES STARTED SUCCESSFULLY!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${BLUE}📍 Service URLs:${NC}"
echo -e "  Backend API:        ${YELLOW}http://localhost:$BACKEND_PORT${NC}"
echo -e "  API Docs:           ${YELLOW}http://localhost:$BACKEND_PORT/docs${NC}"
echo -e "  Card Frontend:      ${YELLOW}http://localhost:$CARD_FRONTEND_PORT${NC}"
echo ""

echo -e "${BLUE}📋 Test the flow:${NC}"
echo -e "  1. Open ${YELLOW}http://localhost:3000${NC} (Onboarding Frontend)"
echo -e "  2. Complete onboarding"
echo -e "  3. Cards will be created automatically"
echo -e "  4. Open ${YELLOW}http://localhost:$CARD_FRONTEND_PORT${NC} (Card Frontend)"
echo -e "  5. View your cards"
echo -e "  6. Go to CGS and generate content"
echo ""

echo -e "${BLUE}📊 Logs:${NC}"
echo -e "  Backend:       ${YELLOW}tail -f /tmp/backend.log${NC}"
echo -e "  Card Frontend: ${YELLOW}tail -f /tmp/card-frontend.log${NC}"
echo ""

echo -e "${BLUE}🛑 To stop all services:${NC}"
echo -e "  ${YELLOW}kill $BACKEND_PID $CARD_FRONTEND_PID${NC}"
echo ""

echo -e "${BLUE}🧪 To run tests:${NC}"
echo -e "  ${YELLOW}pytest tests/ -v${NC}"
echo -e "  ${YELLOW}./run_tests.sh all${NC}"
echo ""

# Keep script running
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Trap Ctrl+C to cleanup
trap cleanup INT

cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down services...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $CARD_FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}✅ All services stopped${NC}"
    exit 0
}

# Wait indefinitely
wait

