"""
Startup script for Modular MVC Application
Run this from the project root directory
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now import and run the app
from app.main import create_app

if __name__ == '__main__':
    app, socketio = create_app()
    print(f"[*] Starting server on port 5002...")
    socketio.run(app, host='0.0.0.0', port=5002, debug=True)

