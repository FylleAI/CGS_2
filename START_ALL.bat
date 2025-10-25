@echo off
REM Card Service V1 - Complete System Startup Script for Windows

setlocal enabledelayedexpansion

echo.
echo 🚀 Card Service V1 - Complete System Startup
echo =============================================
echo.

REM Configuration
set BACKEND_PORT=8000
set CARD_FRONTEND_PORT=3001
set ONBOARDING_FRONTEND_PORT=3000

REM Check prerequisites
echo 📋 Checking prerequisites...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed
    exit /b 1
)
echo ✅ Python found

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed
    exit /b 1
)
echo ✅ Node.js found

REM Check npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm is not installed
    exit /b 1
)
echo ✅ npm found

echo.

REM Check .env file
if not exist ".env" (
    echo ⚠️  .env file not found, creating from .env.example
    if exist ".env.example" (
        copy .env.example .env >nul
        echo ✅ Created .env from .env.example
    ) else (
        echo ❌ .env.example not found
        exit /b 1
    )
)

echo.
echo 🔧 Starting Backend (FastAPI)...
echo.

REM Create virtual environment if needed
if not exist "venv" (
    echo 📦 Creating Python virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -q -r requirements.txt
    echo ✅ Virtual environment created
) else (
    call venv\Scripts\activate.bat
)

REM Start backend in background
echo Starting FastAPI server on port %BACKEND_PORT%...
start "Backend - Card Service V1" cmd /k "uvicorn api.rest.main:app --host 0.0.0.0 --port %BACKEND_PORT% --reload"
echo ✅ Backend started

REM Wait for backend to be ready
echo.
echo ⏳ Waiting for Backend to be ready...
timeout /t 5 /nobreak

REM Start Card Frontend
echo.
echo 🎨 Starting Card Frontend (React)...
echo.

if exist "card-frontend" (
    cd card-frontend
    
    REM Install dependencies if needed
    if not exist "node_modules" (
        echo 📦 Installing Card Frontend dependencies...
        call npm install -q
        echo ✅ Dependencies installed
    )
    
    REM Create .env if needed
    if not exist ".env" (
        echo Creating .env for card-frontend...
        (
            echo VITE_API_BASE_URL=http://localhost:%BACKEND_PORT%
            echo VITE_APP_NAME=Card Service
        ) > .env
        echo ✅ Created .env
    )
    
    REM Start frontend in background
    echo Starting React dev server on port %CARD_FRONTEND_PORT%...
    start "Card Frontend - Card Service V1" cmd /k "npm run dev"
    echo ✅ Card Frontend started
    
    cd ..
) else (
    echo ⚠️  card-frontend directory not found
)

echo.
echo ════════════════════════════════════════════════════════════
echo ✅ ALL SERVICES STARTED SUCCESSFULLY!
echo ════════════════════════════════════════════════════════════
echo.

echo 📍 Service URLs:
echo   Backend API:        http://localhost:%BACKEND_PORT%
echo   API Docs:           http://localhost:%BACKEND_PORT%/docs
echo   Card Frontend:      http://localhost:%CARD_FRONTEND_PORT%
echo.

echo 📋 Test the flow:
echo   1. Open http://localhost:3000 (Onboarding Frontend)
echo   2. Complete onboarding
echo   3. Cards will be created automatically
echo   4. Open http://localhost:%CARD_FRONTEND_PORT% (Card Frontend)
echo   5. View your cards
echo   6. Go to CGS and generate content
echo.

echo 📊 Logs:
echo   Backend:       Check "Backend - Card Service V1" window
echo   Card Frontend: Check "Card Frontend - Card Service V1" window
echo.

echo 🧪 To run tests:
echo   pytest tests/ -v
echo   run_tests.bat all
echo.

echo ✅ Services are running in separate windows
echo Press Ctrl+C in each window to stop services
echo.

pause

