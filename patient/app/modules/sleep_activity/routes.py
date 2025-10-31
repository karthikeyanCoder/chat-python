"""
Sleep & Activity Module Routes
Handles sleep tracking and user activity management
EXTRACTED FROM app_simple.py lines 2378-2730
"""

from flask import Blueprint, request
from .services import (
    save_sleep_log_service,
    get_sleep_logs_service,
    get_sleep_logs_by_email_service,
    get_patient_complete_profile_service,
    get_user_activities_service,
    get_session_activities_service,
    get_activity_summary_service,
    track_activity_service,
    get_active_sessions_service
)

sleep_activity_bp = Blueprint('sleep_activity', __name__)


@sleep_activity_bp.route('/save-sleep-log', methods=['POST'])
def save_sleep_log():
    """Save sleep log data to MongoDB"""
    data = request.get_json()
    return save_sleep_log_service(data)


@sleep_activity_bp.route('/get-sleep-logs/<username>', methods=['GET'])
def get_sleep_logs(username):
    """Get sleep logs for a specific user"""
    return get_sleep_logs_service(username)


@sleep_activity_bp.route('/get-sleep-logs-by-email/<email>', methods=['GET'])
def get_sleep_logs_by_email(email):
    """Get sleep logs for a specific user by email"""
    return get_sleep_logs_by_email_service(email)


@sleep_activity_bp.route('/patient-complete-profile/<email>', methods=['GET'])
def get_patient_complete_profile(email):
    """Get complete patient profile including all health data"""
    return get_patient_complete_profile_service(email)


@sleep_activity_bp.route('/user-activities/<email>', methods=['GET'])
def get_user_activities(email):
    """Get all activities for a specific user"""
    return get_user_activities_service(email)


@sleep_activity_bp.route('/session-activities/<session_id>', methods=['GET'])
def get_session_activities(session_id):
    """Get all activities for a specific session"""
    return get_session_activities_service(session_id)


@sleep_activity_bp.route('/activity-summary/<email>', methods=['GET'])
def get_activity_summary(email):
    """Get summary of user activities"""
    return get_activity_summary_service(email)


@sleep_activity_bp.route('/track-activity', methods=['POST'])
def track_activity():
    """Manually track a user activity"""
    data = request.get_json()
    return track_activity_service(data)


@sleep_activity_bp.route('/active-sessions/<email>', methods=['GET'])
def get_active_sessions(email):
    """Get all active sessions for a user"""
    return get_active_sessions_service(email)
