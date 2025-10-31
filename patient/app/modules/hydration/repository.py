"""
Hydration Repository - Data Access Layer (Model)
Handles all database operations for hydration module
"""

from app.core.database import db


class HydrationRepository:
    """Data access layer for hydration operations"""
    
    def __init__(self, db_instance):
        self.db = db_instance
        self.collection = db_instance.patients_collection
    
    def find_patient_by_id(self, patient_id):
        """Find patient by patient_id"""
        return self.collection.find_one({"patient_id": patient_id})
    
    def save_hydration_intake(self, patient_id, hydration_record):
        """Save hydration intake record"""
        result = self.collection.update_one(
            {"patient_id": patient_id},
            {"$push": {"hydration_records": hydration_record}}
        )
        return result.modified_count > 0
    
    def get_hydration_records(self, patient_id):
        """Get hydration records for patient"""
        patient = self.collection.find_one({"patient_id": patient_id})
        if patient:
            return patient.get('hydration_records', [])
        return []
    
    def set_hydration_goal(self, patient_id, goal_data):
        """Set hydration goal for patient"""
        result = self.collection.update_one(
            {"patient_id": patient_id},
            {"$set": {"hydration_goal": goal_data}}
        )
        return result.modified_count > 0
    
    def get_hydration_goal(self, patient_id):
        """Get hydration goal for patient"""
        patient = self.collection.find_one({"patient_id": patient_id})
        if patient:
            return patient.get('hydration_goal', {})
        return {}
    
    def add_hydration_reminder(self, patient_id, reminder_data):
        """Add hydration reminder"""
        result = self.collection.update_one(
            {"patient_id": patient_id},
            {"$push": {"hydration_reminders": reminder_data}}
        )
        return result.modified_count > 0
    
    def get_hydration_reminders(self, patient_id):
        """Get hydration reminders for patient"""
        patient = self.collection.find_one({"patient_id": patient_id})
        if patient:
            return patient.get('hydration_reminders', [])
        return []

