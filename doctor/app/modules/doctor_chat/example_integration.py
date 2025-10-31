"""
Doctor Chat Module - Integration Example
This file demonstrates how to integrate the doctor chat module into your Flask application
"""

from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from pymongo import MongoClient
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Enable CORS
CORS(app, resources={
    r"/doctor/chat/*": {"origins": "*"},
    r"/socket.io/*": {"origins": "*"}
})

# Initialize Socket.IO
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='eventlet',  # or 'threading', 'gevent'
    logger=True,
    engineio_logger=True
)

# Database connection
try:
    mongo_client = MongoClient('mongodb://localhost:27017/')
    db = mongo_client['pregnancy_ai']
    print("✅ MongoDB connected successfully")
except Exception as e:
    print(f"❌ MongoDB connection failed: {str(e)}")
    raise

# Initialize Doctor Chat Module
try:
    # Import and initialize repository
    from chat.repository import init_doctor_chat_repository
    chat_repo = init_doctor_chat_repository(db)
    print("✅ Doctor chat repository initialized")
    
    # Import and initialize service
    from chat.services import init_doctor_chat_service
    chat_service = init_doctor_chat_service(db)
    print("✅ Doctor chat service initialized")
    
    # Register REST API blueprints
    from chat.routes import doctor_chat_bp
    from chat.file_upload_routes import doctor_file_upload_bp
    
    app.register_blueprint(doctor_chat_bp, url_prefix='/doctor/chat')
    app.register_blueprint(doctor_file_upload_bp, url_prefix='/doctor/chat/files')
    print("✅ REST API routes registered")
    
    # Initialize Socket.IO handlers
    from chat.socket_handlers import init_doctor_chat_socket_handlers
    init_doctor_chat_socket_handlers(socketio, db)
    print("✅ Socket.IO handlers initialized")
    
    print("\n" + "="*50)
    print("🎉 Doctor Chat Module Initialized Successfully!")
    print("="*50)
    
except Exception as e:
    print(f"❌ Failed to initialize doctor chat module: {str(e)}")
    raise


# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return {
        "status": "healthy",
        "message": "Doctor Chat System is running",
        "modules": {
            "rest_api": "operational",
            "websocket": "operational",
            "database": "connected"
        }
    }, 200


# Root endpoint
@app.route('/', methods=['GET'])
def index():
    return {
        "name": "Doctor Chat System",
        "version": "2.0.0",
        "endpoints": {
            "rest_api": "/doctor/chat/*",
            "file_upload": "/doctor/chat/files/*",
            "websocket": "/socket.io",
            "health": "/health"
        },
        "documentation": "/doctor/chat/health"
    }, 200


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return {"success": False, "message": "Endpoint not found", "data": None}, 404


@app.errorhandler(500)
def internal_error(error):
    return {"success": False, "message": "Internal server error", "data": None}, 500


# Main entry point
if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Starting Doctor Chat System...")
    print("="*50)
    print(f"📍 REST API: http://localhost:5000/doctor/chat")
    print(f"🔌 WebSocket: http://localhost:5000/socket.io")
    print(f"💚 Health Check: http://localhost:5000/health")
    print("="*50 + "\n")
    
    # Run the application
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )


