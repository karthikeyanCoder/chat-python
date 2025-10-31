@echo off
echo 🚀 Starting PaddleOCR FastAPI Service...
echo.
echo 📍 Server will be available at: http://localhost:8000
echo 📚 API Documentation: http://localhost:8000/docs
echo 🔍 Health Check: http://localhost:8000/health
echo 📖 Root Info: http://localhost:8000/
echo.
echo ⏹️  Press Ctrl+C to stop the server
echo.

python main.py

pause
