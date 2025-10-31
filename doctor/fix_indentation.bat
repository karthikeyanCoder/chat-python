@echo off
echo 🔧 Python Indentation Fixer
echo ================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "app_simple.py" (
    echo ❌ app_simple.py not found in current directory
    echo Please run this script from the doctor directory
    pause
    exit /b 1
)

echo 📁 Current directory: %CD%
echo.

REM Run the indentation fixer
echo 🔧 Running indentation fixer...
python fix_indentation.py

echo.
echo ✅ Indentation fixer completed!
echo.
echo 🚀 You can now run your Python applications:
echo    python app_simple.py
echo    python app_mvc.py
echo.
pause
