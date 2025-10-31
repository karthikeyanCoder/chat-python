#!/bin/bash

# Start Patient Alert System with Gunicorn (Linux/Mac)

echo "================================================================================"
echo "                   PATIENT ALERT SYSTEM - GUNICORN SERVER"
echo "================================================================================"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "[*] Activating virtual environment..."
    source venv/bin/activate
else
    echo "[*] No virtual environment found, using global Python"
fi

# Check if gunicorn is installed
python -c "import gunicorn" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[ERROR] Gunicorn not installed. Installing now..."
    pip install gunicorn
fi

echo ""
echo "[*] Starting Gunicorn server..."
echo "[*] Press Ctrl+C to stop the server"
echo ""

# Start gunicorn with config file
gunicorn --config gunicorn_config.py wsgi:app

echo ""
echo "[*] Server stopped."


