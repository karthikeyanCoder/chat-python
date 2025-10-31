"""
Profile Routes - API Endpoints (View Layer)
Note: Additional profile endpoints beyond auth module
"""
from flask import Blueprint, jsonify

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'available',
        'service': 'Profile Management',
        'note': 'Extended profile features - MVC migration pending'
    }), 200

