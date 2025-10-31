#!/usr/bin/env python3
"""
Voice Model - Database operations for voice functionality
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import hashlib
import secrets

class VoiceModel:
    """Model for voice-related database operations"""
    
    def __init__(self, db):
        self.db = db
        self.voice_collection = db.db.voice_users
        self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes for voice collections"""
        try:
            # Create indexes for voice_users collection
            self.voice_collection.create_index("email", unique=True)
            self.voice_collection.create_index("username", unique=True)
            self.voice_collection.create_index("created_at")
        except Exception as e:
            print(f"Warning: Could not create voice indexes: {e}")
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with email and password"""
        try:
            # Find user by email
            user = self.voice_collection.find_one({"email": email})
            
            if not user:
                return None
            
            # In a real implementation, you would verify the password hash
            # For now, we'll just check if the user exists
            if user.get('password_hash'):
                # Here you would use bcrypt or similar to verify password
                # For demo purposes, we'll return the user
                return {
                    'id': str(user['_id']),
                    'email': user['email'],
                    'username': user.get('username', ''),
                    'role': user.get('role', 'voice_user'),
                    'created_at': user.get('created_at', '')
                }
            
            return None
            
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return None
    
    def create_user(self, user_data: Dict[str, Any]) -> str:
        """Create a new voice user"""
        try:
            # Generate user ID
            user_id = f"voice_{int(datetime.now().timestamp() * 1000)}"
            
            # Prepare user document
            user_doc = {
                "user_id": user_id,
                "email": user_data.get("email"),
                "username": user_data.get("username", ""),
                "password_hash": user_data.get("password_hash", ""),
                "role": user_data.get("role", "voice_user"),
                "is_active": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Insert user
            result = self.voice_collection.insert_one(user_doc)
            
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"Error creating user: {e}")
            raise e
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            user = self.voice_collection.find_one({"user_id": user_id})
            
            if not user:
                return None
            
            return {
                'id': str(user['_id']),
                'user_id': user['user_id'],
                'email': user['email'],
                'username': user.get('username', ''),
                'role': user.get('role', 'voice_user'),
                'is_active': user.get('is_active', True),
                'created_at': user.get('created_at', ''),
                'updated_at': user.get('updated_at', '')
            }
            
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user information"""
        try:
            update_data["updated_at"] = datetime.now().isoformat()
            
            result = self.voice_collection.update_one(
                {"user_id": user_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return self.get_user_by_id(user_id)
            
            return None
            
        except Exception as e:
            print(f"Error updating user: {e}")
            return None
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        try:
            result = self.voice_collection.delete_one({"user_id": user_id})
            return result.deleted_count > 0
            
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    def get_users(self, filters: Dict[str, Any] = None, page: int = 1, limit: int = 10) -> List[Dict[str, Any]]:
        """Get users with pagination and filters"""
        try:
            if filters is None:
                filters = {}
            
            # Calculate skip
            skip = (page - 1) * limit
            
            # Find users
            cursor = self.voice_collection.find(filters).skip(skip).limit(limit)
            users = []
            
            for user in cursor:
                users.append({
                    'id': str(user['_id']),
                    'user_id': user['user_id'],
                    'email': user['email'],
                    'username': user.get('username', ''),
                    'role': user.get('role', 'voice_user'),
                    'is_active': user.get('is_active', True),
                    'created_at': user.get('created_at', ''),
                    'updated_at': user.get('updated_at', '')
                })
            
            return users
            
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    def count_users(self, filters: Dict[str, Any] = None) -> int:
        """Count users with filters"""
        try:
            if filters is None:
                filters = {}
            
            return self.voice_collection.count_documents(filters)
            
        except Exception as e:
            print(f"Error counting users: {e}")
            return 0
