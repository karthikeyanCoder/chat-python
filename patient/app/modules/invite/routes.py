"""
Invite Module Routes
Handles doctor-patient invites and connections
EXTRACTED FROM patient_service/views/ - ZERO BACKEND LOGIC CHANGES
"""
import re
from flask import Blueprint, request, jsonify
from app.core.auth import token_required
from .services import (
    accept_invite_service,
    request_connection_service,
    remove_connection_service,
    get_connected_doctors_service,
    search_doctors_service,
    cancel_request_service,
    get_pending_invites_service,
    get_invite_details_service,
    verify_invite_code_service
)

invite_bp = Blueprint('invite', __name__, url_prefix='/api/invite')


@invite_bp.route('/accept', methods=['POST'])
@token_required
def accept_invite():
    """Patient accepts doctor's invite code"""
    data = request.get_json()
    patient_id = request.user_data['patient_id']
    email = request.user_data['email']
    
    if not data.get('invite_code'):
        return jsonify({"success": False, "error": "invite_code is required"}), 400
    
    return accept_invite_service(patient_id, email, data['invite_code'])


@invite_bp.route('/verify/<invite_code>', methods=['GET'])
def verify_invite_code(invite_code):
    """Verify invite code - Public endpoint (no auth required)"""
    return verify_invite_code_service(invite_code)


@invite_bp.route('/request-connection', methods=['POST'])
@token_required
def request_connection():
    """Patient requests connection with doctor using either doctor_id or doctor_email"""
    try:
        data = request.get_json()
        
        # Validate input using schema
        from .schemas import RequestConnectionSchema
        schema = RequestConnectionSchema()
        errors = schema.validate(data)
        if errors:
            return jsonify({"success": False, "error": "Validation failed", "details": errors}), 400
        
        patient_id = request.user_data['patient_id']
        message = data['message']
        connection_type = data.get('connection_type', 'primary')
        send_invite_code = data.get('send_invite_code', True)
        expires_in_days = data.get('expires_in_days', 7)
        
        # Extract doctor identifier
        doctor_id = data.get('doctor_id')
        doctor_email = data.get('doctor_email')
        
        return request_connection_service(
            patient_id=patient_id,
            message=message,
            connection_type=connection_type,
            doctor_id=doctor_id,
            doctor_email=doctor_email,
            send_invite_code=send_invite_code,
            expires_in_days=expires_in_days
        )
        
    except Exception as e:
        print(f"[ERROR] Request connection route failed: {e}")
        return jsonify({"success": False, "error": f"Request failed: {str(e)}"}), 500


@invite_bp.route('/remove-connection', methods=['POST'])
@token_required
def remove_connection():
    """Remove doctor-patient connection"""
    data = request.get_json()
    patient_id = request.user_data['patient_id']
    
    if not data.get('connection_id'):
        return jsonify({"success": False, "error": "connection_id is required"}), 400
    
    return remove_connection_service(
        data['connection_id'], 
        patient_id, 
        data.get('reason')
    )


@invite_bp.route('/my-doctors', methods=['GET'])
@token_required
def get_connected_doctors():
    """Get all connected doctors for authenticated patient"""
    patient_id = request.user_data['patient_id']
    return get_connected_doctors_service(patient_id)


@invite_bp.route('/search-doctors', methods=['GET'])
@token_required
def search_doctors():
    """Search for doctors with connection status"""
    patient_id = request.user_data['patient_id']
    query = request.args.get('query')
    specialty = request.args.get('specialty')
    city = request.args.get('city')
    limit = int(request.args.get('limit', 20))
    
    return search_doctors_service(patient_id, query, specialty, city, limit)


@invite_bp.route('/cancel-request', methods=['POST'])
@token_required
def cancel_request():
    """Cancel pending connection request"""
    try:
        data = request.get_json()
        
        # Validate input using schema
        from .schemas import CancelRequestSchema
        schema = CancelRequestSchema()
        errors = schema.validate(data)
        if errors:
            return jsonify({"success": False, "error": "Validation failed", "details": errors}), 400
        
        patient_id = request.user_data['patient_id']
        connection_id = data['connection_id']
        reason = data.get('reason')
        
        return cancel_request_service(connection_id, patient_id, reason)
        
    except Exception as e:
        print(f"[ERROR] Cancel request route failed: {e}")
        return jsonify({"success": False, "error": f"Request failed: {str(e)}"}), 500


@invite_bp.route('/pending-invites', methods=['GET'])
@token_required
def get_pending_invites():
    """Get pending connection requests from doctors"""
    patient_id = request.user_data['patient_id']
    return get_pending_invites_service(patient_id)


@invite_bp.route('/invite-details/<invite_id>', methods=['GET'])
@token_required
def get_invite_details(invite_id):
    """Get details of a specific doctor invite"""
    patient_id = request.user_data['patient_id']
    return get_invite_details_service(invite_id, patient_id)








