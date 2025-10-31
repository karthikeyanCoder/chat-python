"""
WSGI entry point for Gunicorn
Run with: gunicorn wsgi:app
"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app
from app.main import create_app

# Create app instance
app = create_app()

if __name__ == "__main__":
    app.run()


