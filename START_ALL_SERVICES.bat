@echo off
REM START_ALL_SERVICES.bat - Avvia tutti i servizi CGS

setlocal enabledelayedexpansion

echo.
echo ========================================
echo 🚀 Starting all CGS services...
echo ========================================
echo.

REM Check if venv exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate venv
call venv\Scripts\activate.bat

REM Install dependencies
echo Checking dependencies...
pip install -q -r requirements.txt

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

echo.
echo ========================================
echo Starting Services...
echo ========================================
echo.

REM 1. Card Service (port 8001)
echo Starting Card Service on port 8001...
start "Card Service" cmd /k "cd services\card_service 2>nul || cd core\card_service && python -m uvicorn api.card_routes:app --host 127.0.0.1 --port 8001 --reload"
timeout /t 2 /nobreak

REM 2. Onboarding Service (port 8002)
echo Starting Onboarding Service on port 8002...
start "Onboarding Service" cmd /k "cd services\onboarding 2>nul || cd onboarding && python -m uvicorn api.main:app --host 127.0.0.1 --port 8002 --reload"
timeout /t 2 /nobreak

REM 3. Main API (port 8000)
echo Starting Main API on port 8000...
start "Main API" cmd /k "cd api\rest && python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"
timeout /t 2 /nobreak

REM 4. Card Manager Frontend (port 5173)
echo Starting Card Manager Frontend on port 5173...
start "Card Manager" cmd /k "cd frontends\card-explorer 2>nul || cd card-frontend && npm run dev"
timeout /t 2 /nobreak

REM 5. Onboarding Frontend (port 5174)
echo Starting Onboarding Frontend on port 5174...
start "Onboarding Frontend" cmd /k "cd onboarding-frontend && npm run dev -- --port 5174"
timeout /t 3 /nobreak

echo.
echo ========================================
echo ✅ Services Started Successfully!
echo ========================================
echo.
echo Services running:
echo   📌 Main API:              http://127.0.0.1:8000
echo   📌 Main API Docs:         http://127.0.0.1:8000/docs
echo   📌 Card Service:          http://127.0.0.1:8001
echo   📌 Card Service Docs:     http://127.0.0.1:8001/docs
echo   📌 Onboarding Service:    http://127.0.0.1:8002
echo   📌 Onboarding Docs:       http://127.0.0.1:8002/docs
echo   📌 Card Manager:          http://127.0.0.1:5173
echo   📌 Onboarding Frontend:   http://127.0.0.1:5174
echo.
echo To stop all services, close the terminal windows or run:
echo   STOP_ALL_SERVICES.bat
echo.

pause

