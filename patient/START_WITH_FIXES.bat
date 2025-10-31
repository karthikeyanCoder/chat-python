@echo off
echo ==================================================
echo Starting Patient API with Payment Fixes Applied
echo ==================================================
echo.

REM Add ALLOW_TEST_MODE to .env if not exists
findstr /C:"ALLOW_TEST_MODE" .env >nul
if %errorlevel% neq 0 (
    echo ALLOW_TEST_MODE=true >> .env
    echo Added ALLOW_TEST_MODE=true to .env
)

echo.
echo Starting server on port 5002...
echo.

python run_app.py

pause

