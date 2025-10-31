"""
Symptoms Routes - EXTRACTED FROM app_simple.py
Thin routing layer that delegates to services containing EXACT original logic
"""
from flask import Blueprint, request
from .services import (
    symptoms_health_check_service,
    get_symptom_assistance_service,
    save_symptom_log_service,
    save_symptom_analysis_report_service,
    get_symptom_history_service,
    get_analysis_reports_service,
    add_symptom_knowledge_service,
    add_symptom_knowledge_bulk_service,
    ingest_symptom_knowledge_service
)

symptoms_bp = Blueprint('symptoms', __name__)


@symptoms_bp.route('/health', methods=['GET'])
def symptoms_health_check():
    """EXTRACTED FROM app_simple.py line 2933"""
    return symptoms_health_check_service()


@symptoms_bp.route('/assist', methods=['POST'])
def get_symptom_assistance():
    """EXTRACTED FROM app_simple.py line 2942"""
    data = request.get_json()
    return get_symptom_assistance_service(data)


@symptoms_bp.route('/save-symptom-log', methods=['POST'])
def save_symptom_log():
    """EXTRACTED FROM app_simple.py line 3150"""
    data = request.get_json()
    return save_symptom_log_service(data)


@symptoms_bp.route('/save-analysis-report', methods=['POST'])
def save_symptom_analysis_report():
    """EXTRACTED FROM app_simple.py line 3243"""
    data = request.get_json()
    return save_symptom_analysis_report_service(data)


@symptoms_bp.route('/get-symptom-history/<patient_id>', methods=['GET'])
def get_symptom_history(patient_id):
    """EXTRACTED FROM app_simple.py line 3358"""
    return get_symptom_history_service(patient_id)


@symptoms_bp.route('/get-analysis-reports/<patient_id>', methods=['GET'])
def get_analysis_reports(patient_id):
    """EXTRACTED FROM app_simple.py line 3393"""
    return get_analysis_reports_service(patient_id)


@symptoms_bp.route('/knowledge/add', methods=['POST'])
def add_symptom_knowledge():
    """EXTRACTED FROM app_simple.py line 3446"""
    data = request.get_json()
    return add_symptom_knowledge_service(data)


@symptoms_bp.route('/knowledge/bulk', methods=['POST'])
def add_symptom_knowledge_bulk():
    """EXTRACTED FROM app_simple.py line 3481"""
    data = request.get_json()
    return add_symptom_knowledge_bulk_service(data)


@symptoms_bp.route('/ingest', methods=['POST'])
def ingest_symptom_knowledge():
    """EXTRACTED FROM app_simple.py line 3527"""
    return ingest_symptom_knowledge_service()
