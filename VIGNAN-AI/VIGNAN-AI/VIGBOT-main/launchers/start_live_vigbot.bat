@echo off
setlocal enabledelayedexpansion
title VIGBOT - Live Server ^& Public Tunnel Launcher
color 0A

echo =====================================================================
echo                     VIGBOT - LIVE TUNNEL LAUNCHER
echo =====================================================================
echo.

:: 1. Verify Virtual Environment
if not exist "%~dp0..\BACKEND\.venv\Scripts\python.exe" (
    echo [!] Virtual environment not found at BACKEND\.venv
    echo [*] Please run: python -m venv BACKEND\.venv ^&^& BACKEND\.venv\Scripts\pip install -r BACKEND\requirements.txt
    pause
    exit /b 1
)

:: 2. Check Ollama Status
echo [*] Checking local Ollama AI daemon...
"%~dp0..\BACKEND\.venv\Scripts\python.exe" -c "import sys; sys.path.insert(0, r'%~dp0BACKEND'); from app.agent.local_llm import LocalLLMClient; print('    [OK] Ollama is active with model:', LocalLLMClient.get_active_model()) if LocalLLMClient.is_available() else print('    [!] Notice: Ollama not running, falling back to cloud cascade.')"

:: 3. Launch FastAPI Backend in a separate window
echo.
echo [*] Starting FastAPI Backend on http://localhost:8000...
start "VIGBOT Backend (FastAPI)" cmd /k "cd /d "%~dp0..\BACKEND" && "%~dp0..\BACKEND\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

:: Wait 3 seconds for backend to initialize
ping 127.0.0.1 -n 4 >nul

:: 4. Verify Backend Health
echo [*] Verifying backend health...
"%~dp0..\BACKEND\.venv\Scripts\python.exe" -c "import requests; r = requests.get('http://localhost:8000/health', timeout=3); print('    [OK] Backend is healthy:', r.json().get('status'))" 2>nul || echo     [!] Backend initializing...

echo.
echo =====================================================================
echo                CHOOSE YOUR PUBLIC TUNNEL METHOD
echo =====================================================================
echo [1] Cloudflare Tunnel (Recommended: cloudflared - fast, stable HTTPS)
echo [2] LocalTunnel (Instant: requires zero installation via npx)
echo =====================================================================
set /p tunnel_choice="Enter your choice (1 or 2) [Default=1]: "

if "%tunnel_choice%"=="2" (
    goto run_localtunnel
)

:run_cloudflare
set "CF_BIN="
if exist "%~dp0..\bin\cloudflared.exe" set "CF_BIN=%~dp0bin\cloudflared.exe"
if not defined CF_BIN if exist "%~dp0..\cloudflared.exe" set "CF_BIN=%~dp0cloudflared.exe"
if not defined CF_BIN (
    where cloudflared >nul 2>nul
    if not errorlevel 1 set "CF_BIN=cloudflared"
)

if not defined CF_BIN (
    echo [!] cloudflared.exe was not found. Switching to LocalTunnel fallback...
    goto run_localtunnel
)

echo.
echo [*] Launching Cloudflare Tunnel on http://localhost:8000...
echo [*] Look for the URL ending in .trycloudflare.com below:
echo =====================================================================
"%CF_BIN%" tunnel --url http://localhost:8000
goto done

:run_localtunnel
echo.
echo [*] Launching LocalTunnel on port 8000...
echo [*] Copy the generated URL into your Vercel NEXT_PUBLIC_BACKEND_URL
echo =====================================================================
call npx localtunnel --port 8000

:done
pause
