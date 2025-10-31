@echo off
REM Start Patient Alert System with Gunicorn (Windows)

echo ================================================================================
echo                   PATIENT ALERT SYSTEM - GUNICORN SERVER
echo ================================================================================
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo [*] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [*] No virtual environment found, using global Python
)

REM Check if gunicorn is installed
python -c "import gunicorn" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Gunicorn not installed. Installing now...
    pip install gunicorn
)

echo.
echo [*] Starting Gunicorn server...
echo [*] Press Ctrl+C to stop the server
echo.

REM Start gunicorn with config file
gunicorn --config gunicorn_config.py wsgi:app

echo.
echo [*] Server stopped.
pause


