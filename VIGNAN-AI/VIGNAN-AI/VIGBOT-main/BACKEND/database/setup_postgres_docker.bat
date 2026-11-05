@echo off
echo ==============================================================================
echo   VIGNAN FOUNDATION FOR SCIENCE, TECHNOLOGY AND RESEARCH (VFSTR)
echo   VIGBOT - PostgreSQL Docker Setup
echo ==============================================================================
echo.

echo [1/3] Starting PostgreSQL 16 container...
docker run -d --name vigbot_db -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=vigbot postgres:16

echo.
echo [2/3] Waiting for PostgreSQL service to be ready...
timeout /t 5 /nobreak >nul

echo.
echo [3/3] Deploying institutional schemas (01 to 13) and Section 7 seeds...
python init_db.py

echo.
echo ==============================================================================
echo   PostgreSQL database setup complete!
echo   Connection URL: postgresql://postgres:postgres@localhost:5432/vigbot
echo ==============================================================================
pause
