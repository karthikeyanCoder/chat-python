"""
Profile Utilities Module Routes
Handles patient profile retrieval
EXTRACTED FROM app_simple.py lines 5708-5827
"""

from flask import Blueprint
from .services import (
    get_patient_profile_by_email_service,
    get_patient_profile_service
)

profile_utils_bp = Blueprint('profile_utils', __name__)


@profile_utils_bp.route('/get-patient-profile-by-email/<email>', methods=['GET'])
def get_patient_profile_by_email(email):
    """Get patient profile by email"""
    return get_patient_profile_by_email_service(email)


@profile_utils_bp.route('/get-patient-profile/<patient_id>', methods=['GET'])
def get_patient_profile(patient_id):
    """Get patient profile by patient ID"""
    return get_patient_profile_service(patient_id)
