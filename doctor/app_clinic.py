"""
Clinic User Management System - Main Flask Application
"""

from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import routes
from routes.user_routes import user_bp

# Import configuration
from config_clinic import Config

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Enable CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Register blueprints
    app.register_blueprint(user_bp)
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'Clinic User Management System',
            'version': '1.0.0'
        }), 200
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        """Root endpoint"""
        return jsonify({
            'message': 'Clinic User Management System API',
            'version': '1.0.0',
            'endpoints': {
                'health': '/api/health',
                'users': '/api/users',
                'login': '/api/users/login'
            }
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found',
            'status_code': 404
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An internal server error occurred',
            'status_code': 500
        }), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 errors"""
        return jsonify({
            'error': 'Bad Request',
            'message': 'The request was invalid',
            'status_code': 400
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 errors"""
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required',
            'status_code': 401
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 errors"""
        return jsonify({
            'error': 'Forbidden',
            'message': 'Insufficient permissions',
            'status_code': 403
        }), 403
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    # Get configuration
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"Starting Clinic User Management System...")
    print(f"Environment: {os.getenv('FLASK_ENV', 'production')}")
    print(f"Debug mode: {debug}")
    print(f"Port: {port}")
    
    # Run the application
    app.run(host='0.0.0.0', port=port, debug=debug)
