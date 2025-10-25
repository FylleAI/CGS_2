@echo off
REM Card Service V1 - Test Runner Script for Windows

setlocal enabledelayedexpansion

echo.
echo 🧪 Card Service V1 - Test Suite
echo ================================
echo.

REM Parse arguments
set TEST_TYPE=%1
if "%TEST_TYPE%"=="" set TEST_TYPE=all

set COVERAGE=%2
if "%COVERAGE%"=="" set COVERAGE=false

REM Run tests based on type
if "%TEST_TYPE%"=="unit" (
    echo Running Unit Tests...
    if "%COVERAGE%"=="true" (
        pytest tests/unit -v --cov=core --cov=onboarding --cov-report=html
    ) else (
        pytest tests/unit -v
    )
) else if "%TEST_TYPE%"=="integration" (
    echo Running Integration Tests...
    if "%COVERAGE%"=="true" (
        pytest tests/integration -v --cov=core --cov=onboarding --cov-report=html
    ) else (
        pytest tests/integration -v
    )
) else if "%TEST_TYPE%"=="all" (
    echo Running All Tests...
    if "%COVERAGE%"=="true" (
        pytest tests/ -v --cov=core --cov=onboarding --cov-report=html
    ) else (
        pytest tests/ -v
    )
) else (
    echo Unknown test type: %TEST_TYPE%
    echo Usage: run_tests.bat [unit^|integration^|all] [coverage]
    exit /b 1
)

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ All tests passed!
    if "%COVERAGE%"=="true" (
        echo 📊 Coverage report generated: htmlcov\index.html
    )
) else (
    echo.
    echo ❌ Tests failed!
    exit /b 1
)

endlocal

