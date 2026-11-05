<#
.SYNOPSIS
    VIGBOT: One-Click Launcher for FastAPI Backend + Live Public Tunnel
.DESCRIPTION
    Launches your local FastAPI backend, verifies local Ollama status,
    and opens a public HTTPS tunnel (Cloudflare Tunnel or LocalTunnel)
    so your live Vercel frontend can call your local VIGBOT model!
#>

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "                     VIGBOT - LIVE TUNNEL LAUNCHER                    " -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

$launcherDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Split-Path -Parent $launcherDir
$pythonPath = Join-Path $rootDir "BACKEND\.venv\Scripts\python.exe"

# 1. Check Python Venv
if (-not (Test-Path $pythonPath)) {
    Write-Host "[!] Virtual environment not found at $pythonPath" -ForegroundColor Red
    Write-Host "[*] Please initialize venv: python -m venv BACKEND\.venv; .\BACKEND\.venv\Scripts\pip install -r .\BACKEND\requirements.txt"
    exit 1
}

# 2. Check Ollama
Write-Host "[*] Checking local Ollama AI daemon..." -ForegroundColor Yellow
try {
    $tags = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 2
    $models = $tags.models.name -join ", "
    Write-Host "    [OK] Ollama is active with models: $models" -ForegroundColor Green
} catch {
    Write-Host "    [!] Local Ollama daemon not reachable on localhost:11434." -ForegroundColor Yellow
    Write-Host "        Make sure to start Ollama or VIGBOT will automatically use Groq/Gemini cloud cascade." -ForegroundColor DarkGray
}

# 3. Launch Backend in new window
Write-Host ""
Write-Host "[*] Starting FastAPI Backend on http://localhost:8000..." -ForegroundColor Yellow
Start-Process cmd -ArgumentList "/k", "cd /d `"$rootDir\BACKEND`" && `"$pythonPath`" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

Start-Sleep -Seconds 3

# 4. Check Health
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 3
    Write-Host "    [OK] Backend is healthy: $($health.status) (LLM Provider: $($health.llm_provider))" -ForegroundColor Green
} catch {
    Write-Host "    [!] Backend still initializing..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "Starting Cloudflare Tunnel on http://localhost:8000..." -ForegroundColor Cyan
Write-Host "Copy the generated *.trycloudflare.com URL for Vercel NEXT_PUBLIC_BACKEND_URL" -ForegroundColor Yellow
Write-Host "=====================================================================" -ForegroundColor Cyan

$cfLocal = Join-Path $rootDir "bin\cloudflared.exe"
if (-not (Test-Path $cfLocal)) {
    $cfLocal = Join-Path $rootDir "cloudflared.exe"
}
if (Test-Path $cfLocal) {
    & $cfLocal tunnel --url http://localhost:8000
} elseif (Get-Command cloudflared -ErrorAction SilentlyContinue) {
    cloudflared tunnel --url http://localhost:8000
} else {
    Write-Host "[*] cloudflared not found in PATH, running via npx localtunnel..." -ForegroundColor Yellow
    npx localtunnel --port 8000
}
