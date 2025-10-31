"""
Voice Module Services - FUNCTION-BASED MVC
EXTRACTED FROM app_simple.py lines 8535-8721
Business logic for voice transcription, AI response, text-to-speech

NO CHANGES TO LOGIC - Exact extraction, converted to function-based
"""

from flask import jsonify
import asyncio
from app.shared.external_services.voice_interaction_service import voice_interaction_service


def voice_transcribe_service(file, patient_id):
    """Transcribe audio to text - EXACT from line 8535"""
    try:
        if not file or file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No audio file selected'
            }), 400
        
        # Read audio data
        audio_data = file.read()
        
        # Transcribe audio
        result = asyncio.run(voice_interaction_service.transcribe_audio(audio_data))
        
        # Add patient ID to result
        result['patient_id'] = patient_id
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error transcribing audio: {str(e)}'
        }), 500


def voice_transcribe_base64_service(data, patient_id):
    """Transcribe base64 encoded audio - EXACT from line 8570"""
    try:
        base64_audio = data.get('audio', '')
        
        if not base64_audio:
            return jsonify({
                'success': False,
                'error': 'Base64 audio data is required'
            }), 400
        
        # Transcribe base64 audio
        result = asyncio.run(voice_interaction_service.transcribe_base64_audio(base64_audio))
        
        # Add patient ID to result
        result['patient_id'] = patient_id
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error transcribing base64 audio: {str(e)}'
        }), 500


def voice_ai_response_service(data, patient_id):
    """Generate AI response for text input - EXACT from line 8598"""
    try:
        text = data.get('text', '').strip()
        conversation_history = data.get('conversation_history', [])
        
        if not text:
            return jsonify({
                'success': False,
                'error': 'Text input is required'
            }), 400
        
        # Generate AI response
        result = asyncio.run(voice_interaction_service.generate_ai_response(text, conversation_history))
        
        # Add patient ID to result
        result['patient_id'] = patient_id
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error generating AI response: {str(e)}'
        }), 500


def voice_text_to_speech_service(data, patient_id):
    """Convert text to speech - EXACT from line 8627"""
    try:
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({
                'success': False,
                'error': 'Text input is required'
            }), 400
        
        # Convert text to speech
        result = asyncio.run(voice_interaction_service.text_to_speech(text))
        
        # Add patient ID to result
        result['patient_id'] = patient_id
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error converting text to speech: {str(e)}'
        }), 500


def voice_process_service(file, enable_tts, patient_id):
    """Complete voice interaction pipeline: STT -> AI -> TTS - EXACT from line 8655"""
    try:
        if not file or file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No audio file selected'
            }), 400
        
        # Read audio data
        audio_data = file.read()
        
        # Process voice interaction
        result = asyncio.run(voice_interaction_service.process_voice_interaction(audio_data, enable_tts))
        
        # Add patient ID to result
        result['patient_id'] = patient_id
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error processing voice interaction: {str(e)}'
        }), 500


def voice_service_info_service():
    """Get voice interaction service information - EXACT from line 8693"""
    try:
        service_info = voice_interaction_service.get_service_info()
        return jsonify({
            'success': True,
            **service_info
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error getting service info: {str(e)}'
        }), 500


def voice_service_health_service():
    """Check voice interaction service health - EXACT from line 8708"""
    try:
        health_status = voice_interaction_service.get_health_status()
        return jsonify({
            'success': True,
            **health_status
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error checking service health: {str(e)}'
        }), 500
