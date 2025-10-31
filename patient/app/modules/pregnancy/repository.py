"""
Pregnancy Repository - Data Access Layer (Model)
Handles all database operations for pregnancy module
"""

from app.core.database import db


class PregnancyRepository:
    """Data access layer for pregnancy operations"""
    
    def __init__(self, db_instance):
        self.db = db_instance
        self.collection = db_instance.patients_collection
    
    def find_patient_by_id(self, patient_id):
        """Find patient by patient_id"""
        return self.collection.find_one({"patient_id": patient_id})
    
    def update_pregnancy_week(self, patient_id, pregnancy_data):
        """Update pregnancy week data for patient"""
        result = self.collection.update_one(
            {"patient_id": patient_id},
            {"$set": pregnancy_data}
        )
        return result.modified_count > 0
    
    def add_kick_count(self, patient_id, kick_count_entry):
        """Add kick count entry to patient's kick_count_logs"""
        result = self.collection.update_one(
            {"patient_id": patient_id},
            {"$push": {"kick_count_logs": kick_count_entry}}
        )
        return result.modified_count > 0
    
    def get_kick_count_history(self, patient_id):
        """Get kick count history for patient"""
        patient = self.collection.find_one({"patient_id": patient_id})
        if patient:
            return patient.get('kick_count_logs', [])
        return []
    
    def add_milestone(self, patient_id, milestone):
        """Add pregnancy milestone"""
        result = self.collection.update_one(
            {"patient_id": patient_id},
            {"$push": {"pregnancy_milestones": milestone}}
        )
        return result.modified_count > 0

