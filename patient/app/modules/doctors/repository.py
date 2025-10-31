"""
Doctors Repository - Data Access Layer (Model)
Handles all database operations for doctors module
"""

from app.core.database import db


class DoctorsRepository:
    """Data access layer for doctors operations"""
    
    def __init__(self, db_instance):
        self.db = db_instance
        # Check if doctor_v2_collection exists
        if hasattr(db_instance, 'doctor_v2_collection'):
            self.collection = db_instance.doctor_v2_collection
        else:
            self.collection = None
    
    def find_doctor_by_id(self, doctor_id):
        """Find doctor by doctor_id"""
        if not self.collection:
            return None
        
        # Try different field names
        doctor = self.collection.find_one({"doctor_id": doctor_id})
        if not doctor:
            doctor = self.collection.find_one({"_id": doctor_id})
        if not doctor:
            doctor = self.collection.find_one({"id": doctor_id})
        return doctor
    
    def get_all_doctors(self, query=None, skip=0, limit=50):
        """Get all doctors with optional filtering"""
        if not self.collection:
            return []
        
        if query is None:
            query = {}
        
        return list(self.collection.find(query).skip(skip).limit(limit))
    
    def save_doctor(self, doctor_data):
        """Save doctor profile"""
        if not self.collection:
            return None
        
        result = self.collection.insert_one(doctor_data)
        return result.inserted_id

