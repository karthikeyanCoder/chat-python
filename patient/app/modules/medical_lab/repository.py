"""
Medical Lab Repository - Data Access Layer (Model)
Handles all database operations for medical lab module
NOTE: Medical Lab primarily uses external medical_lab_service for OCR
This repository is a thin wrapper for consistency
"""

from app.core.database import db


class MedicalLabRepository:
    """Data access layer for medical lab operations"""
    
    def __init__(self, db_instance):
        self.db = db_instance
        self.collection = db_instance.patients_collection
    
    def find_patient_by_id(self, patient_id):
        """Find patient by patient_id"""
        return self.collection.find_one({"patient_id": patient_id})
    
    def save_lab_report(self, patient_id, report_data):
        """Save lab report to patient record"""
        result = self.collection.update_one(
            {"patient_id": patient_id},
            {"$push": {"lab_reports": report_data}}
        )
        return result.modified_count > 0
    
    def get_lab_reports(self, patient_id):
        """Get lab reports for patient"""
        patient = self.collection.find_one({"patient_id": patient_id})
        if patient:
            return patient.get('lab_reports', [])
        return []

