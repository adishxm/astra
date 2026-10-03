@echo off
title ASTRA - Enterprise Cryptographic Discovery Engine
color 0B

echo.
echo  ============================================================
echo    ASTRA - Enterprise Cryptographic Discovery ^& Analysis Tool
echo    SIH26164 ECDAT  ^|  Post-Quantum Migration Engine
echo  ============================================================
echo.

:: Navigate to script directory
cd /d "%~dp0"

:: Check Python
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo  [ERROR] Python not found. Install Python 3.10+ and add to PATH.
    pause
    exit /b 1
)

:: Create venv if it doesn't exist
if not exist "venv\Scripts\activate.bat" (
    echo  [*] Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo  [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo  [+] Virtual environment created.
)

:: Activate venv
echo  [*] Activating virtual environment...
call venv\Scripts\activate.bat

:: Install dependencies if needed
pip show fastapi >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo  [*] Installing dependencies...
    pip install --upgrade pip >nul 2>&1
    pip install -r requirements.txt
    pip install -e .
    echo  [+] Dependencies installed.
) else (
    echo  [+] Dependencies already installed.
)

echo.
echo  [*] Starting ASTRA Server...
echo  [*] Dashboard:  http://localhost:8000
echo  [*] API Docs:   http://localhost:8000/docs
echo  [*] Health:     http://localhost:8000/health
echo.
echo  Press Ctrl+C to stop the server.
echo  ============================================================
echo.

:: Open browser after a short delay
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:8000"

:: Launch the server
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

pause
