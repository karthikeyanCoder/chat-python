"""
Voice Repository - Data Access Layer (Model)
Handles all database operations for voice module
NOTE: Voice module primarily uses external voice_interaction_service
This repository is a thin wrapper for consistency
"""

from app.core.database import db


class VoiceRepository:
    """Data access layer for voice operations"""
    
    def __init__(self, db_instance):
        self.db = db_instance
        self.collection = db_instance.patients_collection
    
    def find_patient_by_id(self, patient_id):
        """Find patient by patient_id"""
        return self.collection.find_one({"patient_id": patient_id})
    
    def save_voice_interaction(self, patient_id, interaction_data):
        """Save voice interaction record (if storing)"""
        result = self.collection.update_one(
            {"patient_id": patient_id},
            {"$push": {"voice_interactions": interaction_data}}
        )
        return result.modified_count > 0
    
    def get_voice_history(self, patient_id):
        """Get voice interaction history"""
        patient = self.collection.find_one({"patient_id": patient_id})
        if patient:
            return patient.get('voice_interactions', [])
        return []

