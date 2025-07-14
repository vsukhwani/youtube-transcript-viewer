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
echo Backend starting... waiting 5 seconds...
timeout /t 5 /nobreak >nul
echo.
echo Testing backend connectivity...
curl -s http://localhost:3002/api/test >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend is responding!
) else (
    echo ❌ Backend might not be ready yet. Try again in a moment.
)
echo.
echo Opening static frontend in browser...
cd /d "%~dp0frontend"
start "" "index.html"
echo.
echo ==========================================
echo  Application is ready!
echo  - Backend API: http://localhost:3002
echo  - Frontend: Static website (opened in browser)
echo  - Test backend: http://localhost:3002/api/test
echo  - Close backend window to stop server
echo ==========================================
echo.
echo TROUBLESHOOTING:
echo - If you see CORS errors, make sure backend is running
echo - Check browser console (F12) for detailed error messages
echo - The frontend will auto-detect and use localhost backend
echo.
echo The frontend is a static website that runs
echo without any server. You can also open
echo index.html directly by double-clicking it!
echo.
pause
