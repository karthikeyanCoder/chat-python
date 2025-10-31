"""
Mental Health Module Routes
Handles mental health tracking, assessments, AI chat, story generation
EXTRACTED FROM app_simple.py lines 5989-8398
"""

from flask import Blueprint, request
from app.core.auth import token_required
from .services import (
    submit_mood_checkin_service,
    get_mental_health_history_service,
    submit_mental_health_assessment_service,
    generate_mental_health_story_service,
    assess_mental_health_service,
    generate_mental_health_audio_service,
    get_mental_health_story_types_service,
    mental_health_service_health_service,
    mental_health_chat_service,
    get_mental_health_chat_history_service,
    start_mental_health_chat_session_service,
    end_mental_health_chat_session_service,
    get_mental_health_assessments_service,
    debug_mental_health_database_service
)

mental_health_bp = Blueprint('mental_health', __name__)


@mental_health_bp.route('/mental-health/mood-checkin', methods=['POST'])
def submit_mood_checkin():
    """Submit a mood check-in for a patient"""
    data = request.get_json()
    return submit_mood_checkin_service(data)


@mental_health_bp.route('/mental-health/history/<patient_id>', methods=['GET'])
def get_mental_health_history(patient_id):
    """Get mental health history for a patient"""
    return get_mental_health_history_service(patient_id)


@mental_health_bp.route('/mental-health/assessment', methods=['POST'])
def submit_mental_health_assessment():
    """Submit a mental health assessment for a patient"""
    data = request.get_json()
    return submit_mental_health_assessment_service(data)


@mental_health_bp.route('/api/mental-health/generate-story', methods=['POST'])
@token_required
def generate_mental_health_story():
    """Generate a mental health assessment story"""
    data = request.get_json()
    return generate_mental_health_story_service(data)


@mental_health_bp.route('/api/mental-health/assess', methods=['POST'])
@token_required
def assess_mental_health():
    """Assess mental health based on story responses"""
    data = request.get_json()
    patient_id = request.user_data['patient_id']
    return assess_mental_health_service(data, patient_id)


@mental_health_bp.route('/api/mental-health/generate-audio', methods=['POST'])
@token_required
def generate_mental_health_audio():
    """Generate Tamil audio for mental health story"""
    data = request.get_json()
    return generate_mental_health_audio_service(data)


@mental_health_bp.route('/api/mental-health/story-types', methods=['GET'])
def get_mental_health_story_types():
    """Get available mental health story types"""
    return get_mental_health_story_types_service()


@mental_health_bp.route('/api/mental-health/health', methods=['GET'])
def mental_health_service_health():
    """Check mental health service health"""
    return mental_health_service_health_service()


@mental_health_bp.route('/api/mental-health/chat', methods=['POST'])
@token_required
def mental_health_chat():
    """Send a message to the mental health AI chat"""
    data = request.get_json()
    patient_id = request.user_data['patient_id']
    return mental_health_chat_service(data, patient_id)


@mental_health_bp.route('/api/mental-health/chat/history', methods=['GET'])
@token_required
def get_mental_health_chat_history():
    """Get mental health chat history for a patient"""
    patient_id = request.user_data['patient_id']
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    return get_mental_health_chat_history_service(patient_id, limit, offset)


@mental_health_bp.route('/api/mental-health/chat/session', methods=['POST'])
@token_required
def start_mental_health_chat_session():
    """Start a new mental health chat session"""
    data = request.get_json() or {}
    patient_id = request.user_data['patient_id']
    return start_mental_health_chat_session_service(data, patient_id)


@mental_health_bp.route('/api/mental-health/chat/session/<session_id>', methods=['DELETE'])
@token_required
def end_mental_health_chat_session(session_id):
    """End a mental health chat session"""
    data = request.get_json() or {}
    patient_id = request.user_data['patient_id']
    return end_mental_health_chat_session_service(session_id, data, patient_id)


@mental_health_bp.route('/api/mental-health/assessments', methods=['GET'])
@token_required
def get_mental_health_assessments():
    """Get mental health assessments for a patient"""
    patient_id = request.user_data['patient_id']
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    return get_mental_health_assessments_service(patient_id, limit, offset)


@mental_health_bp.route('/api/mental-health/debug', methods=['GET'])
@token_required
def debug_mental_health_database():
    """Debug endpoint to check mental health database status"""
    patient_id = request.user_data['patient_id']
    return debug_mental_health_database_service(patient_id)
