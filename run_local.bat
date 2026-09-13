@echo off
title MT5 Super Bot V2 - Local Runner
cd /d "%~dp0"

echo =======================================================
echo   MT5 SUPER BOT V2 - PROD GRACE - ACTION ENGINE
echo =======================================================
echo.

if not exist "backend\.env" (
    echo [.env] Not found. Creating from backend\.env.demo...
    copy "backend\.env.demo" "backend\.env" >nul
)

echo [1/2] Starting FastAPI Backend on http://localhost:8000...
start "MT5 Super Bot V2 Backend" cmd /k "cd /d %~dp0backend && python main_v2.py"

echo [2/2] Opening Dashboard in default browser...
timeout /t 2 /nobreak >nul
start http://localhost:8000/dashboard

echo.
echo =======================================================
echo   Application is running locally!
echo   - Web UI:  http://localhost:8000/dashboard
echo   - API Doc: http://localhost:8000/docs
echo   - Status:  http://localhost:8000/api/status
echo =======================================================
echo Press any key to exit this launcher window...
pause >nul
