"""
Symptoms Repository - Data Access Layer (Model)
Handles all database operations for symptoms module
"""

from app.core.database import db


class SymptomsRepository:
    """Data access layer for symptoms operations"""
    
    def __init__(self, db_instance):
        self.db = db_instance
        self.collection = db_instance.patients_collection
    
    def find_patient_by_id(self, patient_id):
        """Find patient by patient_id"""
        return self.collection.find_one({"patient_id": patient_id})
    
    def save_symptom_log(self, patient_id, symptom_log):
        """Save symptom log to patient"""
        result = self.collection.update_one(
            {"patient_id": patient_id},
            {"$push": {"symptom_logs": symptom_log}}
        )
        return result.modified_count > 0
    
    def save_analysis_report(self, patient_id, report):
        """Save analysis report to patient"""
        result = self.collection.update_one(
            {"patient_id": patient_id},
            {"$push": {"analysis_reports": report}}
        )
        return result.modified_count > 0
    
    def get_symptom_history(self, patient_id):
        """Get symptom history for patient"""
        patient = self.collection.find_one({"patient_id": patient_id})
        if patient:
            return patient.get('symptom_logs', [])
        return []
    
    def get_analysis_reports(self, patient_id):
        """Get analysis reports for patient"""
        patient = self.collection.find_one({"patient_id": patient_id})
        if patient:
            return patient.get('analysis_reports', [])
        return []

