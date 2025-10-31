"""
Profile Utilities Repository - Data Access Layer (Model)
Handles all database operations for profile utilities module
"""

from app.core.database import db


class ProfileUtilsRepository:
    """Data access layer for profile utilities operations"""
    
    def __init__(self, db_instance):
        self.db = db_instance
        self.collection = db_instance.patients_collection
    
    def find_patient_by_email(self, email):
        """Find patient by email"""
        return self.collection.find_one({"email": email})
    
    def find_patient_by_id(self, patient_id):
        """Find patient by patient_id"""
        return self.collection.find_one({"patient_id": patient_id})

