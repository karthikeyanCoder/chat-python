"""
Authentication Routes - EXTRACTED FROM app_simple.py
Thin routing layer that delegates to services containing EXACT original logic
"""
from flask import Blueprint, request, jsonify
from .services import (
    signup_service,
    send_otp_service,
    resend_otp_service,
    verify_otp_service,
    login_service,
    logout_service,
    forgot_password_service,
    reset_password_service,
    complete_profile_service,
    edit_profile_service,
    verify_token_service,
    get_profile_service
)
from app.core.auth import token_required

# Create blueprint
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Register a new patient - EXTRACTED FROM app_simple.py line 1462"""
    data = request.get_json()
    return signup_service(data)


@auth_bp.route('/send-otp', methods=['POST'])
def send_otp():
    """Send OTP to email - EXTRACTED FROM app_simple.py line 1539"""
    data = request.get_json()
    return send_otp_service(data)


@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    """Resend OTP - EXTRACTED FROM app_simple.py line 1584"""
    data = request.get_json()
    return resend_otp_service(data)


@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP - EXTRACTED FROM app_simple.py line 1637"""
    data = request.get_json()
    return verify_otp_service(data)


@auth_bp.route('/login', methods=['POST'])
def login():
    """User login - EXTRACTED FROM app_simple.py line 1745"""
    try:
        data = request.get_json()
        if data is None:
            print("[ERROR] Login request - No JSON data received")
            print(f"[DEBUG] Content-Type: {request.content_type}")
            print(f"[DEBUG] Request data: {request.get_data(as_text=True)[:200]}")
            return jsonify({"error": "Invalid JSON data"}), 400
        print(f"[DEBUG] Login route - Received data keys: {list(data.keys()) if data else 'None'}")
        return login_service(data)
    except Exception as e:
        print(f"[ERROR] Login route exception: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": f"Login request failed: {str(e)}"}), 500


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """User logout - EXTRACTED FROM app_simple.py line 1830"""
    return logout_service(request.user_data)


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Forgot password - EXTRACTED FROM app_simple.py line 1864"""
    data = request.get_json()
    return forgot_password_service(data)


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password - EXTRACTED FROM app_simple.py line 1914"""
    data = request.get_json()
    return reset_password_service(data)


@auth_bp.route('/complete-profile', methods=['POST'])
@token_required
def complete_profile():
    """Complete profile - EXTRACTED FROM app_simple.py line 1973"""
    data = request.get_json()
    patient_id = request.user_data.get('patient_id')
    return complete_profile_service(patient_id, data)


@auth_bp.route('/edit-profile', methods=['PUT'])
def edit_profile():
    """Edit profile - EXTRACTED FROM app_simple.py line 2075"""
    data = request.get_json()
    return edit_profile_service(data)


@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    """Verify token - EXTRACTED FROM app_simple.py line 2169"""
    data = request.get_json()
    token = data.get('token')
    return verify_token_service(token)


@auth_bp.route('/profile/<patient_id>', methods=['GET'])
@token_required
def get_profile(patient_id):
    """Get profile - EXTRACTED FROM app_simple.py line 2241"""
    return get_profile_service(patient_id)
