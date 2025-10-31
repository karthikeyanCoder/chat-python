#!/usr/bin/env python3
"""
Simple launcher script for the PaddleOCR FastAPI service
This script starts the server from the app directory structure
"""

import uvicorn
import sys
import os

if __name__ == "__main__":
    # Add the current directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    print("🚀 Starting PaddleOCR FastAPI Service...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("📖 Root Info: http://localhost:8000/")
    print("\n⏹️  Press Ctrl+C to stop the server\n")
    
    try:
        # Start the server using the app.main:app module path
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("💡 Make sure you have installed all dependencies:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
