"""
Nutrition Module Routes
Handles food tracking, GPT-4 analysis, transcription via N8N
EXTRACTED FROM app_simple.py lines 6566-7070
"""

from flask import Blueprint, request
from .services import (
    health_check_service,
    transcribe_audio_service,
    analyze_food_with_gpt4_service,
    save_food_entry_service,
    get_food_entries_service,
    debug_food_data_service,
    get_food_history_service
)

nutrition_bp = Blueprint('nutrition', __name__, url_prefix='/nutrition')


@nutrition_bp.route('/health', methods=['GET'])
def health_check():
    """Nutrition service health check endpoint"""
    return health_check_service()


@nutrition_bp.route('/transcribe', methods=['POST'])
def transcribe_audio():
    """Transcribe audio using N8N webhook only (Whisper disabled)"""
    data = request.get_json()
    return transcribe_audio_service(data)


@nutrition_bp.route('/analyze-with-gpt4', methods=['POST'])
def analyze_food_with_gpt4():
    """Analyze food using GPT-4"""
    data = request.get_json()
    return analyze_food_with_gpt4_service(data)


@nutrition_bp.route('/save-food-entry', methods=['POST'])
def save_food_entry():
    """Save basic food entry to patient's food_data array"""
    data = request.get_json()
    return save_food_entry_service(data)


@nutrition_bp.route('/get-food-entries/<user_id>', methods=['GET'])
def get_food_entries(user_id):
    """Get food entries from patient's food_data array"""
    return get_food_entries_service(user_id)


@nutrition_bp.route('/debug-food-data/<user_id>', methods=['GET'])
def debug_food_data(user_id):
    """Debug endpoint to check food data structure"""
    return debug_food_data_service(user_id)


@nutrition_bp.route('/get-food-history/<patient_id>', methods=['GET'])
def get_food_history(patient_id):
    """Get food history for a patient"""
    return get_food_history_service(patient_id)


# ==================== ALL NUTRITION ENDPOINTS COMPLETE ====================
# Total: 7 nutrition endpoints
