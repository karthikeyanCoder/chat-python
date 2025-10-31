"""
Hydration Module Routes
Handles hydration tracking, goals, reminders, analytics
EXTRACTED FROM app_simple.py lines 7272-7940
"""

from flask import Blueprint, request
from app.core.auth import token_required
from .services import (
    save_hydration_intake_service,
    get_hydration_history_service,
    get_daily_hydration_stats_service,
    set_hydration_goal_service,
    get_hydration_goal_service,
    create_hydration_reminder_service,
    get_hydration_reminders_service,
    get_hydration_analysis_service,
    get_weekly_hydration_report_service,
    get_hydration_tips_service
)

hydration_bp = Blueprint('hydration', __name__, url_prefix='/api/hydration')


@hydration_bp.route('/intake', methods=['POST'])
@token_required
def save_hydration_intake():
    """Save hydration intake record"""
    data = request.get_json()
    authenticated_patient_id = request.user_data['patient_id']
    return save_hydration_intake_service(data, authenticated_patient_id)


@hydration_bp.route('/history', methods=['GET'])
@token_required
def get_hydration_history():
    """Get hydration intake history"""
    patient_id = request.user_data['patient_id']
    days = request.args.get('days', 7, type=int)
    return get_hydration_history_service(patient_id, days)


@hydration_bp.route('/stats', methods=['GET'])
@token_required
def get_daily_hydration_stats():
    """Get daily hydration statistics"""
    patient_id = request.user_data['patient_id']
    target_date = request.args.get('date')
    return get_daily_hydration_stats_service(patient_id, target_date)


@hydration_bp.route('/goal', methods=['POST'])
@token_required
def set_hydration_goal():
    """Set or update hydration goal"""
    data = request.get_json()
    patient_id = request.user_data['patient_id']
    return set_hydration_goal_service(data, patient_id)


@hydration_bp.route('/goal', methods=['GET'])
@token_required
def get_hydration_goal():
    """Get current hydration goal"""
    patient_id = request.user_data['patient_id']
    return get_hydration_goal_service(patient_id)


@hydration_bp.route('/reminder', methods=['POST'])
@token_required
def create_hydration_reminder():
    """Create hydration reminder"""
    data = request.get_json()
    patient_id = request.user_data['patient_id']
    return create_hydration_reminder_service(data, patient_id)


@hydration_bp.route('/reminders', methods=['GET'])
@token_required
def get_hydration_reminders():
    """Get all hydration reminders"""
    patient_id = request.user_data['patient_id']
    return get_hydration_reminders_service(patient_id)


@hydration_bp.route('/analysis', methods=['GET'])
@token_required
def get_hydration_analysis():
    """Get hydration analysis and insights"""
    patient_id = request.user_data['patient_id']
    days = request.args.get('days', 7, type=int)
    return get_hydration_analysis_service(patient_id, days)


@hydration_bp.route('/report', methods=['GET'])
@token_required
def get_weekly_hydration_report():
    """Get weekly hydration report"""
    patient_id = request.user_data['patient_id']
    return get_weekly_hydration_report_service(patient_id)


@hydration_bp.route('/tips', methods=['GET'])
@token_required
def get_hydration_tips():
    """Get personalized hydration tips"""
    patient_id = request.user_data['patient_id']
    return get_hydration_tips_service(patient_id)
