"""
Nurse Routes - Flask blueprint for nurse management endpoints
"""

from flask import Blueprint, request
from controllers.nurse_controller import NurseController
from utils.jwt_utils import require_auth, require_roles

# Create blueprint
nurse_bp = Blueprint('nurses', __name__, url_prefix='/api/nurses')

# Initialize controller
nurse_controller = NurseController()


@nurse_bp.route('', methods=['POST'])
@require_auth
@require_roles('doctor')
def create_nurse(current_user):
    """Create new nurse - Doctor only"""
    return nurse_controller.create_nurse(request, current_user)


@nurse_bp.route('', methods=['GET'])
@require_auth
@require_roles('doctor')
def get_nurses(current_user):
    """Get list of nurses assigned to doctor"""
    return nurse_controller.get_nurses(request, current_user)


@nurse_bp.route('/<nurse_id>/reset-password', methods=['POST'])
@require_auth
@require_roles('doctor')
def reset_nurse_password(nurse_id, current_user):
    """Reset nurse password - Doctor only"""
    return nurse_controller.reset_nurse_password(request, nurse_id, current_user)