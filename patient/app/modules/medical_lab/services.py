"""
Medical Lab Module Services - FUNCTION-BASED MVC
EXTRACTED FROM app_simple.py lines 8404-8529
Business logic for medical lab report OCR processing

NO CHANGES TO LOGIC - Exact extraction, converted to function-based
"""

from flask import jsonify
from datetime import datetime
import asyncio
from app.shared.external_services.medical_lab_service import medical_lab_service


def medical_lab_upload_service(file, patient_id):
    """Upload and process medical documents - EXACT from line 8404"""
    try:
        if not file or file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Read file content
        file_content = file.read()
        filename = file.filename
        
        # Validate file type
        if not medical_lab_service.validate_file_type(file.content_type, filename):
            return jsonify({
                'success': False,
                'error': f'Unsupported file type: {file.content_type}',
                'supported_types': list(medical_lab_service.supported_formats.keys())
            }), 400
        
        # Process file
        result = asyncio.run(medical_lab_service.process_file(file_content, filename))
        
        # Add patient ID to result
        result['patient_id'] = patient_id
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error processing file: {str(e)}'
        }), 500


def medical_lab_base64_service(data, patient_id):
    """Process base64 encoded image - EXACT from line 8448"""
    try:
        base64_image = data.get('image', '')
        filename = data.get('filename', 'base64_image')
        
        if not base64_image:
            return jsonify({
                'success': False,
                'error': 'Base64 image data is required'
            }), 400
        
        # Process base64 image
        result = asyncio.run(medical_lab_service.process_base64_image(base64_image, filename))
        
        # Add patient ID to result
        result['patient_id'] = patient_id
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error processing base64 image: {str(e)}'
        }), 500


def get_medical_lab_formats_service():
    """Get supported file formats - EXACT from line 8477"""
    try:
        formats = medical_lab_service.get_supported_formats()
        return jsonify({
            'success': True,
            'supported_formats': formats,
            'description': 'File formats supported by medical lab service'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error getting supported formats: {str(e)}'
        }), 500


def get_medical_lab_languages_service():
    """Get supported languages - EXACT from line 8493"""
    try:
        languages = {
            "supported_languages": ["en", "ch", "chinese_cht", "ko", "ja", "latin", "arabic", "cyrillic"],
            "current_language": "en",
            "supported_file_formats": ["PDF", "TXT", "DOC", "DOCX", "Images (JPEG, PNG, GIF, BMP, TIFF)"]
        }
        
        return jsonify({
            'success': True,
            **languages
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error getting supported languages: {str(e)}'
        }), 500


def medical_lab_service_health_service():
    """Check medical lab service health - EXACT from line 8513"""
    try:
        service_info = medical_lab_service.get_service_info()
        return jsonify({
            'success': True,
            'status': 'healthy',
            'service': 'Medical Lab OCR Service',
            'timestamp': datetime.now().isoformat(),
            **service_info
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error checking service health: {str(e)}'
        }), 500
