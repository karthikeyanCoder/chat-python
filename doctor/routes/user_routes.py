"""
User Routes - Flask blueprint for user management endpoints with role-based access control
"""

from flask import Blueprint, request, jsonify
from controllers.user_controller import UserController
from utils.jwt_utils import require_auth, require_roles, require_nurse_assignment

# Create blueprint
user_bp = Blueprint('users', __name__, url_prefix='/api/users')

# Initialize controller
user_controller = UserController()


@user_bp.route('/login', methods=['POST'])
def login():
    """Login endpoint - public access
    Returns:
        JWT token on successful authentication
    """
    return user_controller.login(request)


@user_bp.route('', methods=['GET'])
@require_auth
@require_roles('admin', 'doctor', 'nurse')
def get_users(current_user):
    """Get users list with role-based filtering
    Admin: Can see all users
    Doctor: Can see nurses and patients
    Nurse: Can only see assigned patients
    """
    return user_controller.get_users(request, current_user)


@user_bp.route('', methods=['POST'])
@require_auth
@require_roles('admin', 'doctor')
def create_user(current_user):
    """Create new user with role-based access control
    Admin: Can create any role
    Doctor: Can create only nurses and patients
    """
    return user_controller.create_user(request, current_user)


@user_bp.route('/<user_id>', methods=['GET'])
@require_auth
def get_user_profile(user_id, current_user):
    """Get user profile with access control
    Admin: Can view any user
    Doctor: Can view nurses and patients
    Nurse: Can view assigned patients and own profile
    Patient: Can only view own profile
    """
    return user_controller.get_user_profile(request, user_id, current_user)


@user_bp.route('/<user_id>', methods=['PUT'])
@require_auth
@require_roles('admin', 'doctor', 'nurse', 'patient')
def update_user(user_id, current_user):
    """Update user with role-based access control
    Admin: Can update any user
    Doctor: Can update nurses and patients
    Nurse: Can update only assigned patients and own profile
    Patient: Can update only own profile
    Fields editable: name, email, password, avatar
    """
    return user_controller.update_user(request, user_id, current_user)


@user_bp.route('/<user_id>', methods=['DELETE'])
@require_auth
@require_roles('admin', 'doctor')
def delete_user(user_id, current_user):
    """Delete user with role-based access control
    Admin: Can delete any user except self
    Doctor: Can delete only nurses and patients
    """
    return user_controller.delete_user(request, user_id, current_user)


@user_bp.route('/<user_id>/reset-password', methods=['PATCH'])
@require_auth
@require_roles('admin', 'doctor', 'nurse')
def reset_password(user_id, current_user):
    """Reset user password with role-based access control
    Admin: Can reset password for any user except self
    Doctor: Can reset password for nurses and patients
    Nurse: Can reset password for assigned patients
    """
    return user_controller.reset_password(request, user_id, current_user)
