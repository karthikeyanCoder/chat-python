"""
Medical Lab Module Routes
Handles medical lab report OCR processing
EXTRACTED FROM app_simple.py lines 8404-8529
"""

from flask import Blueprint, jsonify, request
from app.core.auth import token_required
from .services import (
    medical_lab_upload_service,
    medical_lab_base64_service,
    get_medical_lab_formats_service,
    get_medical_lab_languages_service,
    medical_lab_service_health_service
)

medical_lab_bp = Blueprint('medical_lab', __name__, url_prefix='/api/medical-lab')


@medical_lab_bp.route('/upload', methods=['POST'])
@token_required
def medical_lab_upload():
    """Upload and process medical documents (PDF, images, text files)"""
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No file provided'
        }), 400
    
    file = request.files['file']
    patient_id = request.user_data['patient_id']
    return medical_lab_upload_service(file, patient_id)


@medical_lab_bp.route('/base64', methods=['POST'])
@token_required
def medical_lab_base64():
    """Process base64 encoded image"""
    data = request.get_json()
    patient_id = request.user_data['patient_id']
    return medical_lab_base64_service(data, patient_id)


@medical_lab_bp.route('/formats', methods=['GET'])
def get_medical_lab_formats():
    """Get supported file formats"""
    return get_medical_lab_formats_service()


@medical_lab_bp.route('/languages', methods=['GET'])
def get_medical_lab_languages():
    """Get supported languages"""
    return get_medical_lab_languages_service()


@medical_lab_bp.route('/health', methods=['GET'])
def medical_lab_service_health():
    """Check medical lab service health"""
    return medical_lab_service_health_service()
