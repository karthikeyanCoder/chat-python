"""
Doctors Module Routes
Handles doctor profile management
EXTRACTED FROM app_simple.py lines 9610-9850
"""

from flask import Blueprint, request, jsonify
from app.core.auth import token_required
from .services import (
    get_doctor_profile_service,
    get_doctor_profile_by_id_service,
    get_all_doctors_service,
    get_doctor_availability_service,
    get_available_slots_service
)
import os
import requests
from datetime import datetime, timedelta

doctors_bp = Blueprint('doctors', __name__)


@doctors_bp.route('/doctor/profile', methods=['GET'])
@token_required
def get_doctor_profile():
    """Get doctor profile details from doctor_v2 collection"""
    doctor_id = request.user_data['patient_id']
    return get_doctor_profile_service(doctor_id)


@doctors_bp.route('/doctor/profile/<doctor_id>', methods=['GET'])
@token_required
def get_doctor_profile_by_id(doctor_id):
    """Get specific doctor profile by doctor_id from doctor_v2 collection"""
    return get_doctor_profile_by_id_service(doctor_id)


@doctors_bp.route('/doctors', methods=['GET'])
@token_required
def get_all_doctors():
    """Get all doctors from doctor_v2 collection"""
    specialty = request.args.get('specialty')
    location = request.args.get('location')
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    return get_all_doctors_service(specialty, location, limit, offset)


@doctors_bp.route('/doctor/<doctor_id>/availability/<date>', methods=['GET'])
@token_required
def get_doctor_availability(doctor_id, date):
    """Get doctor availability for authenticated patients"""
    try:
        # Get patient token from request
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'success': False, 'error': 'Authorization header required'}), 401
        
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else auth_header
        
        # Call service function
        return get_doctor_availability_service(doctor_id, date, token)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get doctor availability: {str(e)}'}), 500


@doctors_bp.route('/doctor/<doctor_id>/availability/<date>/<appointment_type>', methods=['GET'])
@token_required
def get_available_slots(doctor_id, date, appointment_type):
    """Get available slots for specific appointment type"""
    try:
        # Get patient token from request
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'success': False, 'error': 'Authorization header required'}), 401
        
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else auth_header
        
        # Call service function
        return get_available_slots_service(doctor_id, date, appointment_type, token)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get available slots: {str(e)}'}), 500


# ==================== NEW: Overall availability with filters ====================
DOCTOR_BASE_URL = os.getenv('DOCTOR_MODULE_URL')


@doctors_bp.route('/doctor/<doctor_id>/availability', methods=['GET'])
@token_required
def get_doctor_availability_by_query_date(doctor_id):
    # Supports: date OR start_date&end_date (optional), consultation_type, appointment_type
    date = request.args.get('date')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    consultation_type = request.args.get('consultation_type')
    appointment_type = request.args.get('appointment_type')

    try:
        # Build doctor overall endpoint URL
        base = f"{DOCTOR_BASE_URL}/patient/doctor/{doctor_id}/availability"
        params = []
        if date:
            params.append(f"date={date}")
        if start_date:
            params.append(f"start_date={start_date}")
        if end_date:
            params.append(f"end_date={end_date}")
        if consultation_type:
            params.append(f"consultation_type={consultation_type}")
        if appointment_type:
            params.append(f"appointment_type={appointment_type}")
        url = base + (f"?{'&'.join(params)}" if params else "")

        headers = {}
        auth_header = request.headers.get('Authorization')
        if auth_header:
            headers['Authorization'] = auth_header

        resp = requests.get(url, headers=headers, timeout=15)
        data = resp.json()

        # Reshape to consultation_type-centric structure if request is overall (no single date)
        # or to always provide the requested shape
        try:
            avail_list = (data or {}).get('availability', [])
            by_cons = {}
            for doc in avail_list:
                ctype = (doc.get('consultation_type') or 'Unknown').strip()
                d = doc.get('date')
                for t in doc.get('types', []):
                    slots = t.get('slots', [])
                    by_cons.setdefault(ctype, {}).setdefault(d, []).extend(slots)

            types_out = []
            for ctype, date_map in by_cons.items():
                dates_out = []
                for d_key in sorted(date_map.keys()):
                    dates_out.append({
                        'date': d_key,
                        'slots': date_map[d_key]
                    })
                types_out.append({
                    'consultation_type': ctype,
                    'dates': dates_out
                })

            return jsonify({
                'success': bool(data.get('success', True)),
                'doctor_id': doctor_id,
                'types': types_out
            }), resp.status_code
        except Exception:
            # Fallback to raw if reshaping fails
            return jsonify(data), resp.status_code
    except Exception as e:
        return jsonify({'success': False, 'error': f'Upstream error: {str(e)}'}), 502
    """Patient-facing: require date; forward to doctor patient endpoint.
    Optional: consultation_type=Online|In-Person
    """
    date = request.args.get('date')
    consultation_type = request.args.get('consultation_type')
    if not date:
        return jsonify({'success': False, 'error': 'date is required (YYYY-MM-DD)'}), 400

    try:
        url = f"{DOCTOR_BASE_URL}/patient/doctor/{doctor_id}/availability/{date}"
        if consultation_type:
            url += f"?consultation_type={consultation_type}"

        headers = {}
        auth_header = request.headers.get('Authorization')
        if auth_header:
            headers['Authorization'] = auth_header

        resp = requests.get(url, headers=headers, timeout=15)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({'success': False, 'error': f'Upstream error: {str(e)}'}), 502
