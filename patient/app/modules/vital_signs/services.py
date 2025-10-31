"""
Vital Signs Service - EXTRACTED FROM app_simple.py
Contains EXACT business logic from lines 3548-3844
NO CHANGES to functionality - just reorganized
"""
from flask import jsonify
from datetime import datetime, timedelta
from app.core.database import db
from app.shared.external_services.vital_signs_service import VitalSignsService
from app.shared.ocr_service import OCRService

# Initialize
vital_signs_service = VitalSignsService(db)
ocr_service = OCRService()


def record_vital_sign_service(data):
    """
    EXTRACTED FROM app_simple.py lines 3548-3576
    Record a new vital sign for a patient
    EXACT SAME LOGIC - NO CHANGES
    """
    try:
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        patient_id = data.get('patient_id')
        if not patient_id:
            return jsonify({'success': False, 'message': 'Patient ID is required'}), 400
        
        # Validate required fields
        required_fields = ['type', 'value']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        
        # Record vital sign using service
        result = vital_signs_service.record_vital_sign(patient_id, data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        print(f"Error recording vital sign: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


def get_vital_signs_history_service(patient_id, days=30):
    """
    EXTRACTED FROM app_simple.py lines 3578-3593
    Get vital signs history for a patient
    EXACT SAME LOGIC - NO CHANGES
    """
    try:
        result = vital_signs_service.get_vital_signs_history(patient_id, days)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        print(f"Error getting vital signs history: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


def analyze_vital_signs_service(data):
    """
    EXTRACTED FROM app_simple.py lines 3595-3618
    AI analysis of patient's vital signs
    EXACT SAME LOGIC - NO CHANGES
    """
    try:
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        patient_id = data.get('patient_id')
        if not patient_id:
            return jsonify({'success': False, 'message': 'Patient ID is required'}), 400
        
        days = data.get('days', 7)
        
        result = vital_signs_service.analyze_vital_signs(patient_id, days)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        print(f"Error analyzing vital signs: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


def get_vital_signs_stats_service(patient_id, days=30):
    """
    EXTRACTED FROM app_simple.py lines 3620-3676
    Get vital signs statistics for a patient
    EXACT SAME LOGIC - NO CHANGES
    """
    try:
        # Get vital signs history
        history_result = vital_signs_service.get_vital_signs_history(patient_id, days)
        if not history_result['success']:
            return jsonify(history_result), 500
        
        vital_signs = history_result['vital_signs']
        
        # Calculate statistics
        stats = {}
        for vs in vital_signs:
            vs_type = vs.get('type')
            value = vs.get('value', 0)
            
            if vs_type not in stats:
                stats[vs_type] = {
                    'count': 0,
                    'values': [],
                    'latest_value': value,
                    'latest_timestamp': vs.get('timestamp')
                }
            
            stats[vs_type]['count'] += 1
            stats[vs_type]['values'].append(value)
        
        # Calculate averages
        for vs_type in stats:
            values = stats[vs_type]['values']
            if values:
                stats[vs_type]['average'] = sum(values) / len(values)
                stats[vs_type]['min'] = min(values)
                stats[vs_type]['max'] = max(values)
        
        return jsonify({
            'success': True,
            'patient_id': patient_id,
            'days': days,
            'statistics': stats
        }), 200
            
    except Exception as e:
        print(f"Error getting vital signs stats: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


def get_health_summary_service(patient_id):
    """EXTRACTED FROM app_simple.py lines 3678-3691"""
    try:
        result = vital_signs_service.get_health_summary(patient_id)
        return jsonify(result), 200 if result.get('success') else 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


def create_vital_alert_service(data):
    """EXTRACTED FROM app_simple.py lines 3693-3736"""
    try:
        patient_id = data.get('patient_id')
        if not patient_id:
            return jsonify({'error': 'Patient ID is required'}), 400
        
        result = vital_signs_service.create_alert(patient_id, data)
        return jsonify(result), 200 if result.get('success') else 500
    except Exception as e:
        return jsonify({'error': f'Failed: {str(e)}'}), 500


def get_vital_alerts_service(patient_id):
    """EXTRACTED FROM app_simple.py lines 3738-3776"""
    try:
        result = vital_signs_service.get_alerts(patient_id)
        return jsonify(result), 200 if result.get('success') else 500
    except Exception as e:
        return jsonify({'error': f'Failed: {str(e)}'}), 500


def process_vital_signs_ocr_service(file, patient_id):
    """EXTRACTED FROM app_simple.py lines 3778-3814"""
    try:
        file_content = file.read()
        result = ocr_service.process_file(file_content, file.filename)
        
        return jsonify(result), 200 if result.get('success') else 400
    except Exception as e:
        return jsonify({'error': f'OCR failed: {str(e)}'}), 500


# ==================== VITAL OCR ENDPOINTS ====================
# EXTRACTED FROM app_simple.py lines 3844-3933

def vital_ocr_upload_service(file, vital_ocr_service):
    """Upload document for enhanced OCR - EXACT from line 3844"""
    try:
        if not file or file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        # Validate file type
        if not vital_ocr_service.validate_file_type(file.content_type, file.filename):
            return jsonify({
                'success': False, 
                'message': f'Unsupported file type: {file.content_type}. Allowed types: {vital_ocr_service.allowed_types}'
            }), 400
        
        # Read file content
        file_content = file.read()
        
        # Process file using vital OCR service
        result = vital_ocr_service.process_file(file_content, file.filename)
        
        return jsonify(result), 200 if result.get('success') else 400
        
    except Exception as e:
        print(f"Error processing vital OCR upload: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


def vital_ocr_base64_service(data, vital_ocr_service):
    """Process base64 encoded image - EXACT from line 3874"""
    try:
        print("[*] Vital OCR base64 endpoint called")
        print(f"[*] Received data keys: {list(data.keys()) if data else 'None'}")
        
        if not data or 'image' not in data:
            print("[ERROR] No image data provided")
            return jsonify({'success': False, 'message': 'No image data provided'}), 400
        
        image_data = data['image']
        print(f"[*] Image data length: {len(image_data) if image_data else 0}")
        
        if not image_data or not image_data.strip():
            print("[ERROR] Image data is empty")
            return jsonify({'success': False, 'message': 'Image data cannot be empty'}), 400
        
        print("[*] Processing base64 image with vital OCR service...")
        # Process base64 image using vital OCR service
        result = vital_ocr_service.process_base64_image(image_data, "base64_image")
        print(f"[*] Vital OCR result: {result}")
        
        return jsonify(result), 200 if result.get('success') else 400
        
    except Exception as e:
        print(f"[ERROR] Error processing vital OCR base64: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


def get_vital_ocr_formats_service(vital_ocr_service):
    """Get supported file formats - EXACT from line 3906"""
    try:
        formats = vital_ocr_service.get_supported_formats()
        return jsonify({
            'success': True,
            'supported_formats': formats,
            'description': 'File formats supported by vital OCR service'
        }), 200
        
    except Exception as e:
        print(f"Error getting vital OCR formats: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


def get_vital_ocr_status_service(vital_ocr_service):
    """Get vital OCR service status - EXACT from line 3921"""
    try:
        status = vital_ocr_service.get_webhook_status()
        return jsonify({
            'success': True,
            'status': status
        }), 200
        
    except Exception as e:
        print(f"Error getting vital OCR status: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


def process_vital_signs_text_service(data):
    """EXTRACTED FROM app_simple.py lines 3816-3842"""
    try:
        patient_id = data.get('patient_id')
        text = data.get('text')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        result = vital_signs_service.process_text(patient_id, text)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': f'Failed: {str(e)}'}), 500

