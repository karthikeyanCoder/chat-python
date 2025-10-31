"""
Mental Health Repository - Data Access Layer (Model)
Handles all database operations for mental health module
"""

from app.core.database import db


class MentalHealthRepository:
    """Data access layer for mental health operations"""
    
    def __init__(self, db_instance):
        self.db = db_instance
        self.patients_collection = db_instance.patients_collection
        self.mental_health_collection = db_instance.mental_health_collection
    
    def find_patient_by_id(self, patient_id):
        """Find patient by patient_id"""
        return self.patients_collection.find_one({"patient_id": patient_id})
    
    def save_mood_checkin(self, mood_entry):
        """Save mood check-in to mental health collection"""
        result = self.mental_health_collection.insert_one(mood_entry)
        return result.inserted_id
    
    def update_patient_mental_health_logs(self, patient_id, mood_entry):
        """Update patient's mental health logs"""
        result = self.patients_collection.update_one(
            {"patient_id": patient_id},
            {
                "$push": {"mental_health_logs": mood_entry},
                "$inc": {"mental_health_logs_count": 1}
            }
        )
        return result.modified_count > 0
    
    def find_existing_mood_checkin(self, patient_id, date):
        """Check if mood check-in exists for date"""
        return self.mental_health_collection.find_one({
            "patient_id": patient_id,
            "date": date,
            "type": "mood_checkin"
        })
    
    def get_mood_entries(self, patient_id, limit=30):
        """Get mood check-ins for patient"""
        return list(self.mental_health_collection.find(
            {"patient_id": patient_id, "type": "mood_checkin"},
            {"_id": 0}
        ).sort("date", -1).limit(limit))
    
    def get_assessment_entries(self, patient_id, limit=30):
        """Get assessment entries for patient"""
        return list(self.mental_health_collection.find(
            {"patient_id": patient_id, "type": "mental_health_assessment"},
            {"_id": 0}
        ).sort("date", -1).limit(limit))
    
    def save_assessment(self, assessment_entry):
        """Save mental health assessment"""
        result = self.mental_health_collection.insert_one(assessment_entry)
        return result.inserted_id
    
    def save_chat_session(self, session_data):
        """Save chat session"""
        result = self.mental_health_collection.insert_one(session_data)
        return result.inserted_id
    
    def update_chat_session(self, session_id, patient_id, update_data):
        """Update chat session"""
        result = self.mental_health_collection.update_one(
            {"session_id": session_id, "patient_id": patient_id, "type": "chat_session"},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    def get_chat_sessions(self, patient_id, limit=50, offset=0):
        """Get chat sessions for patient"""
        return list(self.mental_health_collection.find(
            {"patient_id": patient_id, "type": "chat_session"}
        ).sort("created_at", -1).skip(offset).limit(limit))
    
    def get_assessments(self, patient_id, limit=10, offset=0):
        """Get assessments for patient"""
        return list(self.mental_health_collection.find(
            {"patient_id": patient_id, "type": "mental_health_assessment"}
        ).sort("created_at", -1).skip(offset).limit(limit))

