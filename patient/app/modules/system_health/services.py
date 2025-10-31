"""
System Health Module Services - FUNCTION-BASED MVC
EXTRACTED FROM app_simple.py lines 5915-5985
Business logic for database health and system status

NO CHANGES TO LOGIC - Exact extraction, converted to function-based
"""

from flask import jsonify
from datetime import datetime
from app.core.database import db


def check_database_health_service():
    """Check database connection status - EXACT from line 5915"""
    try:
        if db.is_connected():
            return jsonify({
                'success': True,
                'message': 'Database is connected and healthy',
                'status': 'connected',
                'collections': {
                    'patients': db.patients_collection is not None,
                    'mental_health': db.mental_health_collection is not None
                }
            }), 200
        else:
            # Try to reconnect
            print("[*] Database health check failed, attempting reconnection...")
            if db.reconnect():
                return jsonify({
                    'success': True,
                    'message': 'Database reconnected successfully',
                    'status': 'reconnected',
                    'collections': {
                        'patients': db.patients_collection is not None,
                        'mental_health': db.mental_health_collection is not None
                    }
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': 'Database is not connected and reconnection failed',
                    'status': 'disconnected',
                    'error': 'Database connection failed'
                }), 503
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Database health check failed',
            'status': 'error',
            'error': str(e)
        }), 500


def force_database_reconnect_service():
    """Force database reconnection - EXACT from line 5957"""
    try:
        print("[*] Force reconnecting to database...")
        if db.reconnect():
            return jsonify({
                'success': True,
                'message': 'Database reconnected successfully',
                'status': 'reconnected',
                'collections': {
                    'patients': db.patients_collection is not None,
                    'mental_health': db.mental_health_collection is not None
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Database reconnection failed',
                'status': 'failed',
                'error': 'Unable to reconnect to database'
            }), 503
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Database reconnection failed',
            'status': 'error',
            'error': str(e)
        }), 500
