@echo off
REM YouTube Transcript Viewer - Static Frontend + Backend API
echo.
echo ==========================================
echo  YouTube Transcript Viewer - Launcher
echo ==========================================
echo.
echo Starting backend API server...
cd /d "%~dp0backend"
call venv\Scripts\activate.bat
start "Backend API Server" python server.py
echo.
echo Backend starting... waiting 3 seconds...
timeout /t 3 /nobreak >nul
echo.
echo Opening static frontend in browser...
cd /d "%~dp0frontend"
start "" "index.html"
echo.
echo ==========================================
echo  Application is ready!
echo  - Backend API: http://localhost:3002
echo  - Frontend: Static website (opened in browser)
echo  - Close backend window to stop server
echo ==========================================
echo.
echo The frontend is a static website that runs
echo without any server. You can also open
echo index.html directly by double-clicking it!
echo.
pause
