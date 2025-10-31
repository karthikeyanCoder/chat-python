"""
Sleep & Activity Repository - Data Access Layer (Model)
Handles all database operations for sleep and activity module
"""

from app.core.database import db
from datetime import datetime


class SleepActivityRepository:
    """Data access layer for sleep and activity operations"""
    
    def __init__(self, db_instance):
        self.db = db_instance
        self.patients_collection = db_instance.patients_collection
        self.doctors_collection = db_instance.doctors_collection
    
    def find_patient_by_id(self, patient_id):
        """Find patient by patient_id"""
        return self.patients_collection.find_one({"patient_id": patient_id})
    
    def find_patient_by_email(self, email):
        """Find patient by email"""
        return self.patients_collection.find_one({"email": email})
    
    def find_patient_by_username(self, username):
        """Find patient by username"""
        return self.patients_collection.find_one({"username": username})
    
    def find_doctor_by_username(self, username):
        """Find doctor by username"""
        return self.doctors_collection.find_one({"username": username})
    
    def find_doctor_by_email(self, email):
        """Find doctor by email"""
        return self.doctors_collection.find_one({"email": email})
    
    def save_sleep_log_to_patient(self, patient_id, sleep_log_entry):
        """Save sleep log to patient's sleep_logs array"""
        result = self.patients_collection.update_one(
            {"patient_id": patient_id},
            {
                "$push": {"sleep_logs": sleep_log_entry},
                "$set": {"last_updated": datetime.now()}
            }
        )
        return result.modified_count > 0
    
    def save_sleep_log_to_doctor(self, sleep_log):
        """Save sleep log to doctors collection"""
        result = self.doctors_collection.insert_one(sleep_log)
        return result.inserted_id
    
    def get_sleep_logs_by_username(self, username, collection):
        """Get sleep logs by username"""
        return list(collection.find(
            {"username": username, "startTime": {"$exists": True}},
            {"_id": 0}
        ))
    
    def get_sleep_logs_from_patient(self, patient):
        """Get sleep logs from patient document"""
        return patient.get('sleep_logs', [])

