"""
Authentication Repository - Data Access Layer (Model)
Handles all database operations for authentication
"""
from datetime import datetime, timedelta
from app.core.database import db


class AuthRepository:
    """Data access layer for authentication operations"""
    
    def __init__(self):
        self.db = db
        self.collection = self.db.patients_collection
    
    def find_by_email(self, email: str):
        """Find user by email"""
        return self.collection.find_one({"email": email})
    
    def find_by_username(self, username: str):
        """Find user by username"""
        return self.collection.find_one({"username": username})
    
    def find_by_mobile(self, mobile: str):
        """Find user by mobile number"""
        return self.collection.find_one({"mobile": mobile})
    
    def find_by_patient_id(self, patient_id: str):
        """Find user by patient ID"""
        return self.collection.find_one({"patient_id": patient_id})
    
    def find_by_email_or_patient_id(self, identifier: str):
        """Find user by email or patient_id"""
        user = self.collection.find_one({"patient_id": identifier})
        if not user:
            user = self.collection.find_one({"email": identifier})
        return user
    
    def create_user(self, user_data: dict):
        """Create new user in database"""
        user_data['created_at'] = datetime.utcnow()
        user_data['updated_at'] = datetime.utcnow()
        result = self.collection.insert_one(user_data)
        return {**user_data, '_id': result.inserted_id}
    
    def update_user(self, patient_id: str, updates: dict):
        """Update user data"""
        updates['updated_at'] = datetime.utcnow()
        result = self.collection.update_one(
            {"patient_id": patient_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    def store_otp(self, email: str, otp: str, expiration_minutes: int = 10):
        """Store OTP for email verification"""
        expiration_time = datetime.utcnow() + timedelta(minutes=expiration_minutes)
        result = self.collection.update_one(
            {"email": email},
            {
                "$set": {
                    "otp": otp,
                    "otp_expiration": expiration_time,
                    "otp_created_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0
    
    def get_otp(self, email: str):
        """Get stored OTP for email"""
        user = self.collection.find_one({"email": email})
        if user and 'otp' in user:
            # Check if OTP is expired
            if 'otp_expiration' in user:
                if datetime.utcnow() < user['otp_expiration']:
                    return user['otp']
            return None
        return None
    
    def clear_otp(self, email: str):
        """Clear OTP after verification"""
        result = self.collection.update_one(
            {"email": email},
            {
                "$unset": {
                    "otp": "",
                    "otp_expiration": "",
                    "otp_created_at": ""
                }
            }
        )
        return result.modified_count > 0
    
    def activate_user(self, email: str):
        """Activate user account after OTP verification"""
        result = self.collection.update_one(
            {"email": email},
            {"$set": {"status": "active", "verified": True}}
        )
        return result.modified_count > 0
    
    def update_password(self, email: str, hashed_password: str):
        """Update user password"""
        result = self.collection.update_one(
            {"email": email},
            {"$set": {"password": hashed_password, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0
    
    def complete_profile(self, patient_id: str, profile_data: dict):
        """Complete user profile with additional information"""
        profile_data['profile_completed'] = True
        profile_data['updated_at'] = datetime.utcnow()
        
        result = self.collection.update_one(
            {"patient_id": patient_id},
            {"$set": profile_data}
        )
        return result.modified_count > 0
    
    def get_profile(self, patient_id: str):
        """Get user profile"""
        return self.collection.find_one({"patient_id": patient_id}, {"password": 0, "otp": 0})

