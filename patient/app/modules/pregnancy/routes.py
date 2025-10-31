"""
Pregnancy Routes - EXTRACTED FROM app_simple.py
Thin routing layer - delegates to services with EXACT original logic
"""
from flask import Blueprint, request
from app.core.auth import token_required
from .services import (
    get_pregnancy_week_service,
    get_all_pregnancy_weeks_service,
    get_trimester_weeks_service,
    get_baby_size_image_service,
    get_ai_baby_size_service,
    get_early_symptoms_service,
    get_prenatal_screening_service,
    get_wellness_tips_service,
    get_nutrition_tips_service,
    get_openai_status_service,
    save_pregnancy_tracking_service,
    get_pregnancy_tracking_history_service,
    calculate_pregnancy_progress_service,
    update_patient_pregnancy_week_service,
    save_kick_session_service,
    get_kick_history_service,
    get_current_pregnancy_week_service
)
from app.shared.activity_tracker import activity_tracker

pregnancy_bp = Blueprint('pregnancy', __name__)


@pregnancy_bp.route('/week/<int:week>', methods=['GET'])
@token_required
def get_pregnancy_week(week):
    """EXTRACTED FROM app_simple.py line 7075"""
    return get_pregnancy_week_service(week)


@pregnancy_bp.route('/weeks', methods=['GET'])
@token_required
def get_all_pregnancy_weeks():
    """EXTRACTED FROM app_simple.py line 7088"""
    return get_all_pregnancy_weeks_service()


@pregnancy_bp.route('/trimester/<int:trimester>', methods=['GET'])
@token_required
def get_trimester_weeks(trimester):
    """EXTRACTED FROM app_simple.py line 7105"""
    return get_trimester_weeks_service(trimester)


@pregnancy_bp.route('/week/<int:week>/baby-image', methods=['GET'])
@token_required
def get_baby_size_image(week):
    """EXTRACTED FROM app_simple.py line 7129"""
    style = request.args.get('style', 'matplotlib')
    return get_baby_size_image_service(week, style)


@pregnancy_bp.route('/week/<int:week>/baby-size', methods=['GET'])
@token_required
def get_ai_baby_size(week):
    """EXTRACTED FROM app_simple.py line 7143"""
    import asyncio
    return asyncio.run(get_ai_baby_size_service(week))


@pregnancy_bp.route('/week/<int:week>/symptoms', methods=['GET'])
@token_required
def get_early_symptoms(week):
    """EXTRACTED FROM app_simple.py line 7156"""
    import asyncio
    return asyncio.run(get_early_symptoms_service(week))


@pregnancy_bp.route('/week/<int:week>/screening', methods=['GET'])
@token_required
def get_prenatal_screening(week):
    """EXTRACTED FROM app_simple.py line 7169"""
    import asyncio
    return asyncio.run(get_prenatal_screening_service(week))


@pregnancy_bp.route('/week/<int:week>/wellness', methods=['GET'])
@token_required
def get_wellness_tips(week):
    """EXTRACTED FROM app_simple.py line 7182"""
    import asyncio
    return asyncio.run(get_wellness_tips_service(week))


@pregnancy_bp.route('/week/<int:week>/nutrition', methods=['GET'])
@token_required
def get_nutrition_tips(week):
    """EXTRACTED FROM app_simple.py line 7195"""
    import asyncio
    return asyncio.run(get_nutrition_tips_service(week))


@pregnancy_bp.route('/openai/status', methods=['GET'])
def get_openai_status():
    """EXTRACTED FROM app_simple.py line 7208"""
    return get_openai_status_service()


@pregnancy_bp.route('/tracking', methods=['POST'])
@token_required
def save_pregnancy_tracking():
    """EXTRACTED FROM app_simple.py line 7221"""
    data = request.get_json()
    patient_id = request.user_data['patient_id']
    return save_pregnancy_tracking_service(patient_id, data)


@pregnancy_bp.route('/tracking/history', methods=['GET'])
@token_required
def get_pregnancy_tracking_history():
    """EXTRACTED FROM app_simple.py line 7237"""
    patient_id = request.user_data['patient_id']
    return get_pregnancy_tracking_history_service(patient_id)


@pregnancy_bp.route('/progress', methods=['GET'])
@token_required
def calculate_pregnancy_progress():
    """EXTRACTED FROM app_simple.py line 7251"""
    patient_id = request.user_data['patient_id']
    return calculate_pregnancy_progress_service(patient_id)


@pregnancy_bp.route('/update-week/<patient_id>', methods=['POST'])
@token_required
def update_patient_pregnancy_week(patient_id):
    """EXTRACTED FROM app_simple.py line 2318"""
    data = request.get_json()
    return update_patient_pregnancy_week_service(patient_id, data)


# ==================== KICK COUNT ENDPOINTS ====================
# EXTRACTED FROM app_simple.py lines 2732-2840

@pregnancy_bp.route('/save-kick-session', methods=['POST'])
def save_kick_session():
    """Save kick session data"""
    data = request.get_json()
    return save_kick_session_service(data, activity_tracker)


@pregnancy_bp.route('/get-kick-history/<patient_id>', methods=['GET'])
def get_kick_history(patient_id):
    """Get kick history for a patient"""
    return get_kick_history_service(patient_id)


@pregnancy_bp.route('/get-current-pregnancy-week/<patient_id>', methods=['GET'])
def get_current_pregnancy_week(patient_id):
    """Get current pregnancy week for a patient"""
    return get_current_pregnancy_week_service(patient_id)


# ==================== ALL PREGNANCY ENDPOINTS COMPLETE ====================
# Total: 17 pregnancy endpoints (14 basic + 2 kick count + 1 current week)
