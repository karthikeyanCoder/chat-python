"""
Appointments Module Routes
Handles patient and doctor appointment management
EXTRACTED FROM app_simple.py lines 8727-9604
"""

from flask import Blueprint, request
from app.core.auth import token_required
from .services import (
    get_patient_appointments_service,
    create_patient_appointment_service,
    get_patient_appointment_service,
    update_patient_appointment_service,
    cancel_patient_appointment_service,
    get_upcoming_appointments_service,
    get_appointment_history_service,
    get_doctor_appointments_service,
    create_doctor_appointment_service,
    get_doctor_appointment_service,
    update_doctor_appointment_service,
    delete_doctor_appointment_service,
    approve_appointment_service,
    reject_appointment_service,
    get_pending_appointments_service,
    get_appointment_statistics_service
)

appointments_bp = Blueprint('appointments', __name__)


# PATIENT APPOINTMENT ROUTES

@appointments_bp.route('/patient/appointments', methods=['GET'])
@token_required
def get_patient_appointments():
    """Get all appointments for the authenticated patient"""
    patient_id = request.user_data['patient_id']
    date = request.args.get('date')
    status = request.args.get('status')
    consultation_type = request.args.get('type')
    appointment_type = request.args.get('appointment_type')
    return get_patient_appointments_service(patient_id, date, status, consultation_type, appointment_type)


@appointments_bp.route('/patient/appointments', methods=['POST'])
@token_required
def create_patient_appointment():
    """Create a new appointment request - patient can request appointments"""
    data = request.get_json()
    patient_id = request.user_data['patient_id']
    return create_patient_appointment_service(data, patient_id)


@appointments_bp.route('/patient/appointments/<appointment_id>', methods=['GET'])
@token_required
def get_patient_appointment(appointment_id):
    """Get specific appointment details for the authenticated patient"""
    patient_id = request.user_data['patient_id']
    return get_patient_appointment_service(appointment_id, patient_id)


@appointments_bp.route('/patient/appointments/<appointment_id>', methods=['PUT'])
@token_required
def update_patient_appointment(appointment_id):
    """Update appointment details - ONLY for pending appointments"""
    data = request.get_json()
    patient_id = request.user_data['patient_id']
    # Get token from Authorization header
    auth_header = request.headers.get('Authorization', '')
    patient_token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else auth_header
    return update_patient_appointment_service(appointment_id, data, patient_id, patient_token)


@appointments_bp.route('/patient/appointments/<appointment_id>', methods=['DELETE'])
@token_required
def cancel_patient_appointment(appointment_id):
    """Cancel/delete appointment - works for both pending and approved"""
    patient_id = request.user_data['patient_id']
    # Get token from Authorization header
    auth_header = request.headers.get('Authorization', '')
    patient_token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else auth_header
    return cancel_patient_appointment_service(appointment_id, patient_id, patient_token)


@appointments_bp.route('/patient/appointments/upcoming', methods=['GET'])
@token_required
def get_upcoming_appointments():
    """Get upcoming appointments for the authenticated patient"""
    patient_id = request.user_data['patient_id']
    return get_upcoming_appointments_service(patient_id)


@appointments_bp.route('/patient/appointments/history', methods=['GET'])
@token_required
def get_appointment_history():
    """Get appointment history for the authenticated patient with filtering support"""
    patient_id = request.user_data['patient_id']
    status = request.args.get('status')
    consultation_type = request.args.get('type')
    appointment_type = request.args.get('appointment_type')
    date = request.args.get('date')
    return get_appointment_history_service(patient_id, status, consultation_type, appointment_type, date)


# DOCTOR APPOINTMENT ROUTES

@appointments_bp.route('/doctor/appointments', methods=['GET'])
@token_required
def get_doctor_appointments():
    """Get all appointments for doctor management"""
    date = request.args.get('date')
    status = request.args.get('status')
    appointment_type = request.args.get('appointment_type')
    patient_id = request.args.get('patient_id')
    return get_doctor_appointments_service(date, status, appointment_type, patient_id)


@appointments_bp.route('/doctor/appointments', methods=['POST'])
@token_required
def create_doctor_appointment():
    """Create a new appointment by doctor"""
    data = request.get_json()
    return create_doctor_appointment_service(data)


@appointments_bp.route('/doctor/appointments/<appointment_id>', methods=['GET'])
@token_required
def get_doctor_appointment(appointment_id):
    """Get specific appointment details for doctor"""
    return get_doctor_appointment_service(appointment_id)


@appointments_bp.route('/doctor/appointments/<appointment_id>', methods=['PUT'])
@token_required
def update_doctor_appointment(appointment_id):
    """Update an existing appointment - doctor can update all fields"""
    data = request.get_json()
    return update_doctor_appointment_service(appointment_id, data)


@appointments_bp.route('/doctor/appointments/<appointment_id>', methods=['DELETE'])
@token_required
def delete_doctor_appointment(appointment_id):
    """Delete an appointment - doctor can delete appointments"""
    return delete_doctor_appointment_service(appointment_id)


@appointments_bp.route('/doctor/appointments/<appointment_id>/approve', methods=['POST'])
@token_required
def approve_appointment(appointment_id):
    """Approve a pending appointment"""
    data = request.get_json() or {}
    return approve_appointment_service(appointment_id, data)


@appointments_bp.route('/doctor/appointments/<appointment_id>/reject', methods=['POST'])
@token_required
def reject_appointment(appointment_id):
    """Reject a pending appointment"""
    data = request.get_json() or {}
    return reject_appointment_service(appointment_id, data)


@appointments_bp.route('/doctor/appointments/pending', methods=['GET'])
@token_required
def get_pending_appointments():
    """Get all pending appointments for doctor approval"""
    return get_pending_appointments_service()


@appointments_bp.route('/doctor/appointments/statistics', methods=['GET'])
@token_required
def get_appointment_statistics():
    """Get appointment statistics for doctor dashboard"""
    return get_appointment_statistics_service()
