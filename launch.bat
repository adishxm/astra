@echo off
cd /d "%~dp0"
title HEXARK - ASTRA Enterprise Cryptographic Discovery Launcher
cls

:: --- Display Banner ---
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    python scripts\banner.py
)

:: --- Pre-flight System Checks ---
echo  ===================================================================
echo   Checking Environment and Dependencies...
echo  ===================================================================

:: Check Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  [*] ERROR: Python is not found in your system PATH!
    echo      Please install Python 3.10+ from https://python.org/
    echo      and check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: Check Backend Dependencies (uvicorn, fastapi)
python -c "import uvicorn, fastapi" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  [*] First-time setup: Installing backend dependencies via pip...
    echo      This may take a moment, please wait...
    python -m pip install --upgrade pip >nul 2>&1
    python -m pip install -r requirements.txt
    python -m pip install -e .
    if %ERRORLEVEL% NEQ 0 (
        echo  [*] WARNING: Some Python dependencies may have failed to install.
    )
    echo  [OK] Backend dependencies installed.
) else (
    echo  [OK] Backend dependencies verified.
)

:: Check Frontend Dependencies (node_modules) — only if frontend exists
if exist "frontend\package.json" (
    where npm >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo  [*] NOTICE: Node.js / npm not found. Frontend dev server will not start.
        echo      The embedded dashboard at http://localhost:8000 will still work.
        echo.
    ) else (
        if not exist "frontend\node_modules\" (
            echo.
            echo  ===================================================================
            echo   First-time setup: 'frontend\node_modules' not found!
            echo   Installing frontend packages via 'npm install'...
            echo   This may take 1-2 minutes on first run, please wait...
            echo  ===================================================================
            cd /d "%~dp0frontend"
            call npm install
            cd /d "%~dp0"
            if not exist "frontend\node_modules\" (
                echo.
                echo  [*] WARNING: 'npm install' failed. Continuing with embedded dashboard only.
                echo.
            ) else (
                echo  [OK] Frontend dependencies installed successfully!
            )
        ) else (
            echo  [OK] Frontend dependencies verified.
        )
    )
)

echo  [OK] All pre-flight checks passed.
echo.

:: --- Pre-flight Cleanup: Release lingering ports from prior sessions ---
echo  [*] Releasing any lingering development server ports...
python scripts\launcher_utils.py --free-ports 8000 8001 5173 >nul 2>&1

:: --- Determine Available Backend Port ---
set BACKEND_PORT=8000
python scripts\launcher_utils.py --check-port 8000 >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo  [*] Notice: Port 8000 is occupied. Routing backend to fallback port 8001...
    set BACKEND_PORT=8001
)

:: --- Start Backend Server ---
echo  ===================================================================
echo   Starting ASTRA Backend [port %BACKEND_PORT%]...
echo  ===================================================================
start "HEXARK-Backend" cmd /k "title HEXARK-Backend && cd /d "%~dp0backend" && python -m uvicorn app.main:app --host 127.0.0.1 --port %BACKEND_PORT% --reload"

echo  [*] Waiting for backend to be ready at http://127.0.0.1:%BACKEND_PORT%/health ...
python scripts\launcher_utils.py --wait-url "http://127.0.0.1:%BACKEND_PORT%/health" 30 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo  [OK] Backend is online and responding!
) else (
    echo  [*] Notice: Backend is still warming up. Proceeding...
)

:: --- Start Frontend Dev Server (if available) ---
set HAS_FRONTEND=0
if exist "frontend\package.json" (
    if exist "frontend\node_modules\" (
        echo.
        echo  ===================================================================
        echo   Starting ASTRA Dashboard Frontend [port 5173]...
        echo  ===================================================================
        start "HEXARK-Frontend" cmd /k "title HEXARK-Frontend && cd /d "%~dp0frontend" && set VITE_API_BASE_URL=http://127.0.0.1:%BACKEND_PORT%&& call npm run dev"

        echo  [*] Waiting for frontend to be ready at http://127.0.0.1:5173 ...
        python scripts\launcher_utils.py --wait-url "http://127.0.0.1:5173" 30 >nul 2>&1
        if %ERRORLEVEL% EQU 0 (
            echo  [OK] Frontend is online and responding!
            set HAS_FRONTEND=1
        ) else (
            echo  [*] Notice: Frontend is still warming up. Proceeding...
        )
    )
)

:: --- Open Dashboard in Browser ---
echo.
echo  ===================================================================
echo   Opening ASTRA Dashboard in your browser...
echo  ===================================================================
if %HAS_FRONTEND% EQU 1 (
    start "" "http://127.0.0.1:5173"
) else (
    start "" "http://127.0.0.1:%BACKEND_PORT%"
)

echo.
echo  +-----------------------------------------------------------------+
echo  ^|                                                                 ^|
echo  ^|   HEXARK - ASTRA ECDAT is now running!                            ^|
echo  ^|   Backend:   http://127.0.0.1:%BACKEND_PORT%                            ^|
echo  ^|   API Docs:  http://127.0.0.1:%BACKEND_PORT%/docs                       ^|
if %HAS_FRONTEND% EQU 1 (
echo  ^|   Frontend:  http://127.0.0.1:5173                              ^|
) else (
echo  ^|   Dashboard: http://127.0.0.1:%BACKEND_PORT%                            ^|
)
echo  ^|   Health:    http://127.0.0.1:%BACKEND_PORT%/health                     ^|
echo  ^|                                                                 ^|
echo  ^|   Press any key in this window to stop all servers...           ^|
echo  ^|                                                                 ^|
echo  +-----------------------------------------------------------------+
echo.
pause >nul

:: --- Shutdown Servers ---
echo.
echo  [*] Shutting down servers...
python scripts\launcher_utils.py --free-ports 8000 8001 5173 >nul 2>&1
echo  [OK] All servers closed.
echo.
