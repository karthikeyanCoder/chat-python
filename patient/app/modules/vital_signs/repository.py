"""
Vital Signs Repository - Data Access Layer (Model)
Handles all database operations for vital signs module
"""

from app.core.database import db


class VitalSignsRepository:
    """Data access layer for vital signs operations"""
    
    def __init__(self, db_instance):
        self.db = db_instance
        self.collection = db_instance.patients_collection
    
    def find_patient_by_id(self, patient_id):
        """Find patient by patient_id"""
        return self.collection.find_one({"patient_id": patient_id})
    
    def save_vital_signs(self, patient_id, vital_signs_data):
        """Save vital signs to patient record"""
        result = self.collection.update_one(
            {"patient_id": patient_id},
            {"$push": {"vital_signs_history": vital_signs_data}}
        )
        return result.modified_count > 0
    
    def get_vital_signs_history(self, patient_id):
        """Get vital signs history for patient"""
        patient = self.collection.find_one({"patient_id": patient_id})
        if patient:
            return patient.get('vital_signs_history', [])
        return []
    
    def get_latest_vital_signs(self, patient_id):
        """Get latest vital signs for patient"""
        patient = self.collection.find_one({"patient_id": patient_id})
        if patient:
            history = patient.get('vital_signs_history', [])
            return history[-1] if history else None
        return None
    
    def delete_vital_sign(self, patient_id, vital_id):
        """Delete specific vital sign entry"""
        result = self.collection.update_one(
            {"patient_id": patient_id},
            {"$pull": {"vital_signs_history": {"vital_id": vital_id}}}
        )
        return result.modified_count > 0

