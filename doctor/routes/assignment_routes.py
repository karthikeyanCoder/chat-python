"""
Assignment Routes - Flask blueprint for managing nurse-patient assignments
"""

from flask import Blueprint, request, jsonify
from controllers.assignment_controller import AssignmentController
from utils.jwt_utils import require_auth, require_roles

# Create blueprint
assignment_bp = Blueprint('assignments', __name__, url_prefix='/api/assignments')

# Initialize controller
assignment_controller = AssignmentController()


@assignment_bp.route('', methods=['GET'])
@require_auth
@require_roles('admin', 'doctor', 'nurse')
def list_assignments(current_user):
    """List nurse-patient assignments
    Admin: Can see all assignments
    Doctor: Can see all assignments
    Nurse: Can only see their own assignments
    """
    return assignment_controller.list_assignments(request, current_user)


@assignment_bp.route('', methods=['POST'])
@require_auth
@require_roles('admin', 'doctor')
def create_assignment(current_user):
    """Create a new nurse-patient assignment
    Admin: Can assign any nurse to any patient
    Doctor: Can assign nurses to patients
    """
    return assignment_controller.create_assignment(request, current_user)


@assignment_bp.route('/<assignment_id>', methods=['DELETE'])
@require_auth
@require_roles('admin', 'doctor')
def end_assignment(assignment_id, current_user):
    """End an active nurse-patient assignment
    Admin: Can end any assignment
    Doctor: Can end any assignment
    """
    return assignment_controller.end_assignment(request, assignment_id, current_user)


@assignment_bp.route('/nurse/<nurse_id>/patients', methods=['GET'])
@require_auth
@require_roles('admin', 'doctor', 'nurse')
def get_nurse_patients(nurse_id, current_user):
    """Get all patients assigned to a nurse
    Admin: Can view any nurse's patients
    Doctor: Can view any nurse's patients
    Nurse: Can only view their own patients
    """
    return assignment_controller.get_nurse_patients(request, nurse_id, current_user)


@assignment_bp.route('/patient/<patient_id>/nurse', methods=['GET'])
@require_auth
@require_roles('admin', 'doctor', 'nurse', 'patient')
def get_patient_nurse(patient_id, current_user):
    """Get nurse assigned to a patient
    Admin: Can view any patient's nurse
    Doctor: Can view any patient's nurse
    Nurse: Can only view if patient is assigned to them
    Patient: Can only view their own assigned nurse
    """
    return assignment_controller.get_patient_nurse(request, patient_id, current_user)