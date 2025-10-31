"""
Vital Signs Routes - EXTRACTED FROM app_simple.py
Thin routing layer that delegates to services containing EXACT original logic
"""
from flask import Blueprint, request, jsonify
from app.core.auth import token_required
from .services import (
    record_vital_sign_service,
    get_vital_signs_history_service,
    analyze_vital_signs_service,
    get_vital_signs_stats_service,
    get_health_summary_service,
    create_vital_alert_service,
    get_vital_alerts_service,
    process_vital_signs_ocr_service,
    process_vital_signs_text_service,
    vital_ocr_upload_service,
    vital_ocr_base64_service,
    get_vital_ocr_formats_service,
    get_vital_ocr_status_service
)
from app.shared.ocr_service import ocr_service as vital_ocr_service

vital_signs_bp = Blueprint('vital_signs', __name__)


@vital_signs_bp.route('/record', methods=['POST'])
def record_vital_sign():
    """EXTRACTED FROM app_simple.py line 3548"""
    data = request.get_json()
    return record_vital_sign_service(data)


@vital_signs_bp.route('/history/<patient_id>', methods=['GET'])
def get_vital_signs_history(patient_id):
    """EXTRACTED FROM app_simple.py line 3578"""
    days = request.args.get('days', 30, type=int)
    return get_vital_signs_history_service(patient_id, days)


@vital_signs_bp.route('/analyze', methods=['POST'])
def analyze_vital_signs():
    """EXTRACTED FROM app_simple.py line 3595"""
    data = request.get_json()
    return analyze_vital_signs_service(data)


@vital_signs_bp.route('/stats/<patient_id>', methods=['GET'])
def get_vital_signs_stats(patient_id):
    """EXTRACTED FROM app_simple.py line 3620"""
    days = request.args.get('days', 30, type=int)
    return get_vital_signs_stats_service(patient_id, days)


@vital_signs_bp.route('/health-summary/<patient_id>', methods=['GET'])
def get_health_summary(patient_id):
    """EXTRACTED FROM app_simple.py line 3678"""
    return get_health_summary_service(patient_id)


@vital_signs_bp.route('/alerts', methods=['POST'])
def create_vital_alert():
    """EXTRACTED FROM app_simple.py line 3693"""
    data = request.get_json()
    return create_vital_alert_service(data)


@vital_signs_bp.route('/alerts/<patient_id>', methods=['GET'])
def get_vital_alerts(patient_id):
    """EXTRACTED FROM app_simple.py line 3738"""
    return get_vital_alerts_service(patient_id)


@vital_signs_bp.route('/ocr', methods=['POST'])
def process_vital_signs_ocr():
    """EXTRACTED FROM app_simple.py line 3778"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    patient_id = request.form.get('patient_id')
    return process_vital_signs_ocr_service(file, patient_id)


@vital_signs_bp.route('/process-text', methods=['POST'])
def process_vital_signs_text():
    """EXTRACTED FROM app_simple.py line 3816"""
    data = request.get_json()
    return process_vital_signs_text_service(data)


# ==================== VITAL OCR ENDPOINTS ====================
# EXTRACTED FROM app_simple.py lines 3844-3933

@vital_signs_bp.route('/vital-ocr/upload', methods=['POST'])
def vital_ocr_upload():
    """Upload document for enhanced OCR processing"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'}), 400
    
    file = request.files['file']
    return vital_ocr_upload_service(file, vital_ocr_service)


@vital_signs_bp.route('/vital-ocr/base64', methods=['POST'])
def vital_ocr_base64():
    """Process base64 encoded image for OCR"""
    data = request.get_json()
    return vital_ocr_base64_service(data, vital_ocr_service)


@vital_signs_bp.route('/vital-ocr/formats', methods=['GET'])
def get_vital_ocr_formats():
    """Get supported file formats for vital OCR"""
    return get_vital_ocr_formats_service(vital_ocr_service)


@vital_signs_bp.route('/vital-ocr/status', methods=['GET'])
def get_vital_ocr_status():
    """Get vital OCR service status"""
    return get_vital_ocr_status_service(vital_ocr_service)


# ==================== ALL VITAL SIGNS ENDPOINTS COMPLETE ====================
# Total: 14 vital signs endpoints (10 basic + 4 OCR)
