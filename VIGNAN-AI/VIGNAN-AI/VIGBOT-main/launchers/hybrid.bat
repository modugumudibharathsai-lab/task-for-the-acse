@echo off
setlocal enabledelayedexpansion
title VIGBOT - Laptop Hybrid Ollama Tunnel (Permanent Domain)
color 0A

echo =====================================================================
echo                     VIGBOT: LAPTOP HYBRID OLLAMA TUNNEL LAUNCHER
echo =====================================================================
echo.

:: 1. Ensure Ollama Environment allows cross-origin requests
set "OLLAMA_ORIGINS=*"
set "OLLAMA_HOST=127.0.0.1:11434"

:: 2. Check if Ollama daemon is running
echo [*] Checking local Ollama AI daemon (port 11434)...
curl.exe -s http://localhost:11434/api/tags >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo     [OK] Ollama daemon is active and responsive on port 11434.
) else (
    echo     [..] Starting Ollama daemon in background...
    start /B ollama serve >nul 2>&1
    timeout /t 3 /nobreak >nul
    curl.exe -s http://localhost:11434/api/tags >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo     [OK] Ollama daemon successfully started.
    ) else (
        echo     [*] Notice: Ollama starting up. Ensure Ollama app is running.
    )
)

:: 3. Detect Available Tunnels
set "NGROK_BIN="
if exist "%~dp0..\bin\ngrok.exe" set "NGROK_BIN=%~dp0bin\ngrok.exe"
if not defined NGROK_BIN if exist "%~dp0..\ngrok.exe" set "NGROK_BIN=%~dp0ngrok.exe"
if not defined NGROK_BIN (
    where ngrok >nul 2>&1
    if not errorlevel 1 set "NGROK_BIN=ngrok"
)

set "CF_BIN="
if exist "%~dp0..\bin\cloudflared.exe" set "CF_BIN=%~dp0bin\cloudflared.exe"
if not defined CF_BIN if exist "%~dp0..\cloudflared.exe" set "CF_BIN=%~dp0cloudflared.exe"
if not defined CF_BIN (
    where cloudflared >nul 2>&1
    if not errorlevel 1 set "CF_BIN=cloudflared"
)

:: 4. Direct CLI Arguments
if /i "%~1"=="test" goto test_tunnel
if /i "%~1"=="3" goto test_tunnel
if /i "%~1"=="cf" goto run_cloudflare
if /i "%~1"=="cloudflare" goto run_cloudflare
if /i "%~1"=="2" goto run_cloudflare
if /i "%~1"=="ngrok" goto run_ngrok
if /i "%~1"=="1" goto run_ngrok

echo.
echo =====================================================================
echo                 SELECT HYBRID TUNNEL METHOD
echo =====================================================================
if defined NGROK_BIN (
    echo [1] Permanent Static Domain [ngrok - Recommended]
    echo     Domain : https://resonate-trimester-glade.ngrok-free.dev
    echo     Notice : Never changes. Configured on Render cloud backend.
)
if not defined NGROK_BIN (
    echo [1] [-] ngrok.exe not detected
)

if defined CF_BIN (
    echo [2] Cloudflare Quick Tunnel [cloudflared - Free Fallback]
    echo     Notice : Generates random *.trycloudflare.com URL
)
if not defined CF_BIN (
    echo [2] [-] cloudflared.exe not detected
)

echo [3] Test Tunnel Connection to Ollama
echo =====================================================================
set "choice=1"
set /p "choice=Select option (1, 2, or 3) [Default=1]: "

if "%choice%"=="2" goto run_cloudflare
if "%choice%"=="3" goto test_tunnel
goto run_ngrok

:run_ngrok
if not defined NGROK_BIN (
    echo.
    echo [*] ngrok executable not found in project or system PATH.
    echo [*] Switching to Cloudflare fallback...
    goto run_cloudflare
)

echo.
echo =====================================================================
echo   STARTING PERMANENT NGROK TUNNEL FOR OLLAMA (PORT 11434)
echo =====================================================================
echo   STATIC URL: https://resonate-trimester-glade.ngrok-free.dev
echo.
echo   Configured on Render Backend as LOCAL_MODEL_URL:
echo   https://resonate-trimester-glade.ngrok-free.dev
echo.
echo   Press Ctrl+C anytime to stop tunnel.
echo =====================================================================
echo.

"%NGROK_BIN%" http 11434 --url=resonate-trimester-glade.ngrok-free.dev --host-header=rewrite
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [*] ngrok exited with code %ERRORLEVEL%.
    echo [*] Possible causes:
    echo     1. Another ngrok session is active on your free account.
    echo     2. Network connectivity issue.
    echo.
    set "retry_cf=Y"
    set /p "retry_cf=Would you like to switch to Cloudflare Tunnel instead? (Y/N) [Default=Y]: "
    if /i not "!retry_cf!"=="N" goto run_cloudflare
)
goto done

:run_cloudflare
if not defined CF_BIN (
    echo.
    echo [*] Neither ngrok nor cloudflared were found.
    echo [*] Please ensure ngrok.exe or cloudflared.exe is in "%~dp0"
    pause
    exit /b 1
)

echo.
echo =====================================================================
echo   STARTING CLOUDFLARE QUICK TUNNEL (FALLBACK)
echo =====================================================================
echo Look for the URL ending in .trycloudflare.com below:
echo Copy that URL into your Render environment variable: LOCAL_MODEL_URL
echo =====================================================================
echo.
"%CF_BIN%" tunnel --url http://localhost:11434 --http-host-header localhost:11434
goto done

:test_tunnel
echo.
echo =====================================================================
echo   TESTING OLLAMA TUNNEL CONNECTIVITY
echo =====================================================================
echo [*] Pinging local Ollama:
curl.exe -s http://localhost:11434/api/tags >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo     [OK] Local Ollama is responding on port 11434.
) else (
    echo     [-] Local Ollama is NOT responding.
)

echo [*] Testing permanent domain (https://resonate-trimester-glade.ngrok-free.dev):
curl.exe -s -i -H "ngrok-skip-browser-warning: true" https://resonate-trimester-glade.ngrok-free.dev/api/tags
echo.
echo =====================================================================
goto done

:done
if "%~1"=="" pause

