"""
User Activity Tracking System
Tracks all user activities from login to logout
"""
import os
import uuid
from datetime import datetime
from flask import request
# Import shared database instance and create global tracker
from app.core.database import db

class UserActivityTracker:
    """Track all user activities from login to logout"""
    
    def __init__(self, db):
        self.db = db
        # Handle case where database is not connected
        if db.client:
            db_name = os.getenv("DB_NAME", "patients_db")
            self.activities_collection = db.client[db_name]["user_activities"]
            
            # Create indexes for efficient querying
            try:
                self.activities_collection.create_index("user_email")
                self.activities_collection.create_index("session_id")
                self.activities_collection.create_index("timestamp")
                self.activities_collection.create_index("activity_type")
                print("[OK] User Activity Tracker initialized")
            except Exception as e:
                print(f"[WARN] Activity tracker index creation: {e}")
        else:
            self.activities_collection = None
            print("[WARN] User Activity Tracker: Database not connected, using fallback mode")
    
    def start_user_session(self, user_email, user_role, username, user_id):
        """Start tracking a new user session"""
        if self.activities_collection is None:
            return None
            
        session_id = str(uuid.uuid4())
        session_start = datetime.now()
        
        session_data = {
            "session_id": session_id,
            "user_email": user_email,
            "user_role": user_role,
            "username": username,
            "user_id": user_id,
            "session_start": session_start,
            "session_end": None,
            "is_active": True,
            "activities": [],
            "created_at": session_start
        }
        
        result = self.activities_collection.insert_one(session_data)
        print(f"[*] Started tracking session {session_id} for user {user_email}")
        return session_id
    
    def end_user_session(self, user_email, session_id=None):
        """End a user session"""
        if self.activities_collection is None:
            return 0
            
        if session_id:
            # End specific session
            result = self.activities_collection.update_one(
                {"session_id": session_id, "is_active": True},
                {
                    "$set": {
                        "session_end": datetime.now(),
                        "is_active": False
                    }
                }
            )
        else:
            # End all active sessions for user
            result = self.activities_collection.update_many(
                {"user_email": user_email, "is_active": True},
                {
                    "$set": {
                        "session_end": datetime.now(),
                        "is_active": False
                    }
                }
            )
        
        print(f"[*] Ended session(s) for user {user_email}")
        return result.modified_count
    
    def log_activity(self, user_email, activity_type, activity_data, session_id=None):
        """Log a user activity"""
        if self.activities_collection is None:
            return None
            
        if not session_id:
            # Find active session for user
            active_session = self.activities_collection.find_one(
                {"user_email": user_email, "is_active": True}
            )
            if active_session:
                session_id = active_session["session_id"]
            else:
                print(f"[WARN] No active session found for user {user_email}")
                return None
        
        activity_entry = {
            "activity_id": str(uuid.uuid4()),
            "timestamp": datetime.now(),
            "activity_type": activity_type,
            "activity_data": activity_data,
            "ip_address": request.remote_addr if request else "unknown"
        }
        
        # Add activity to session
        result = self.activities_collection.update_one(
            {"session_id": session_id},
            {"$push": {"activities": activity_entry}}
        )
        
        print(f"[*] Logged activity: {activity_type} for user {user_email}")
        return activity_entry["activity_id"]
    
    def get_user_activities(self, user_email, limit=100):
        """Get all activities for a user"""
        if self.activities_collection is None:
            return []
        sessions = list(self.activities_collection.find(
            {"user_email": user_email},
            {"_id": 0}
        ).sort("created_at", -1).limit(limit))
        
        return sessions
    
    def get_session_activities(self, session_id):
        """Get all activities for a specific session"""
        if self.activities_collection is None:
            return None
        session = self.activities_collection.find_one(
            {"session_id": session_id},
            {"_id": 0}
        )
        return session
    
    def get_activity_summary(self, user_email):
        """Get summary of user activities"""
        if self.activities_collection is None:
            return []
        pipeline = [
            {"$match": {"user_email": user_email}},
            {"$unwind": "$activities"},
            {"$group": {
                "_id": "$activities.activity_type",
                "count": {"$sum": 1},
                "last_activity": {"$max": "$activities.timestamp"}
            }},
            {"$sort": {"count": -1}}
        ]
        
        summary = list(self.activities_collection.aggregate(pipeline))
        return summary


# Global activity tracker instance - import this for use across the app
activity_tracker = UserActivityTracker(db)

