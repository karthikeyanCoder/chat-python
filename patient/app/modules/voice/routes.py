"""
Voice Module Routes
Handles voice transcription, AI response, text-to-speech
EXTRACTED FROM app_simple.py lines 8535-8721
"""

from flask import Blueprint, jsonify, request
from app.core.auth import token_required
from .services import (
    voice_transcribe_service,
    voice_transcribe_base64_service,
    voice_ai_response_service,
    voice_text_to_speech_service,
    voice_process_service,
    voice_service_info_service,
    voice_service_health_service
)

voice_bp = Blueprint('voice', __name__, url_prefix='/api/voice')


@voice_bp.route('/transcribe', methods=['POST'])
@token_required
def voice_transcribe():
    """Transcribe audio to text"""
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No audio file provided'
        }), 400
    
    file = request.files['file']
    patient_id = request.user_data['patient_id']
    return voice_transcribe_service(file, patient_id)


@voice_bp.route('/transcribe-base64', methods=['POST'])
@token_required
def voice_transcribe_base64():
    """Transcribe base64 encoded audio"""
    data = request.get_json()
    patient_id = request.user_data['patient_id']
    return voice_transcribe_base64_service(data, patient_id)


@voice_bp.route('/ai-response', methods=['POST'])
@token_required
def voice_ai_response():
    """Generate AI response for text input"""
    data = request.get_json()
    patient_id = request.user_data['patient_id']
    return voice_ai_response_service(data, patient_id)


@voice_bp.route('/text-to-speech', methods=['POST'])
@token_required
def voice_text_to_speech():
    """Convert text to speech"""
    data = request.get_json()
    patient_id = request.user_data['patient_id']
    return voice_text_to_speech_service(data, patient_id)


@voice_bp.route('/process', methods=['POST'])
@token_required
def voice_process():
    """Complete voice interaction pipeline: STT -> AI -> TTS"""
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No audio file provided'
        }), 400
    
    file = request.files['file']
    enable_tts = request.form.get('enable_tts', 'true').lower() == 'true'
    patient_id = request.user_data['patient_id']
    return voice_process_service(file, enable_tts, patient_id)


@voice_bp.route('/service-info', methods=['GET'])
def voice_service_info():
    """Get voice interaction service information"""
    return voice_service_info_service()


@voice_bp.route('/health', methods=['GET'])
def voice_service_health():
    """Check voice interaction service health"""
    return voice_service_health_service()
