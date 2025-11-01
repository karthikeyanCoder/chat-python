"""
User Model - Handles user operations with MongoDB
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import hashlib
import secrets
import string
from bson import ObjectId
from models.database import Database


class UserModel:
    """User model for MongoDB operations"""
    
    def __init__(self, db: Database = None):
        if db is None:
            self.db = Database()
            self.db.connect()
        else:
            self.db = db
        
        # Check if database connection is valid
        is_connected = getattr(self.db, 'is_connected', False)
        if self.db is not None and self.db.db is not None and is_connected:
            self.users_collection = self.db.db.users
        else:
            self.users_collection = None
            print("⚠️ Warning: Database not connected. UserModel operating in fallback mode.")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _generate_random_password(self, length: int = 12) -> str:
        """Generate a random password"""
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(characters) for _ in range(length))
    
    def _convert_to_dict(self, user_doc) -> Dict[str, Any]:
        """Convert MongoDB document to dictionary"""
        if not user_doc:
            return None
        
        user_dict = {
            'user_id': str(user_doc['_id']),
            'name': user_doc.get('name', ''),
            'email': user_doc.get('email', ''),
            'role': user_doc.get('role', ''),
            'avatar': user_doc.get('avatar', ''),
            'created_at': user_doc.get('created_at', ''),
            'is_active': user_doc.get('is_active', True)
        }
        return user_dict
    
    def create_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
        try:
            # Validate required fields
            required_fields = ['name', 'email', 'password', 'role']
            for field in required_fields:
                if not data.get(field):
                    return {'success': False, 'error': f'Missing required field: {field}'}
            
            # Validate role
            valid_roles = ['admin', 'doctor', 'nurse', 'patient']
            if data['role'] not in valid_roles:
                return {'success': False, 'error': f'Invalid role. Must be one of: {valid_roles}'}
            
            # Check if email already exists
            if self.find_by_email(data['email']):
                return {'success': False, 'error': 'Email already exists'}
            
            # Hash password
            hashed_password = self._hash_password(data['password'])
            
            # Create user document
            user_doc = {
                'name': data['name'].strip(),
                'email': data['email'].strip().lower(),
                'password': hashed_password,
                'role': data['role'],
                'avatar': data.get('avatar', ''),
                'created_at': datetime.now().isoformat(),
                'is_active': True
            }
            
            # Insert into database
            result = self.users_collection.insert_one(user_doc)
            
            if result.inserted_id:
                # Get the created user
                created_user = self.users_collection.find_one({'_id': result.inserted_id})
                return {
                    'success': True,
                    'user': self._convert_to_dict(created_user),
                    'message': 'User created successfully'
                }
            else:
                return {'success': False, 'error': 'Failed to create user'}
                
        except Exception as e:
            return {'success': False, 'error': f'Database error: {str(e)}'}
    
    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find user by email"""
        try:
            user_doc = self.users_collection.find_one({'email': email.strip().lower()})
            return self._convert_to_dict(user_doc) if user_doc else None
        except Exception as e:
            print(f"Error finding user by email: {e}")
            return None
    
    def find_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Find user by ID"""
        try:
            if not ObjectId.is_valid(user_id):
                return None
            
            user_doc = self.users_collection.find_one({'_id': ObjectId(user_id)})
            return self._convert_to_dict(user_doc) if user_doc else None
        except Exception as e:
            print(f"Error finding user by ID: {e}")
            return None
    
    def update_user(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user information"""
        try:
            if not ObjectId.is_valid(user_id):
                return {'success': False, 'error': 'Invalid user ID'}
            
            # Check if user exists
            existing_user = self.find_by_id(user_id)
            if not existing_user:
                return {'success': False, 'error': 'User not found'}
            
            # Prepare update data
            update_data = {}
            allowed_fields = ['name', 'email', 'avatar']
            
            for field in allowed_fields:
                if field in data and data[field] is not None:
                    if field == 'email':
                        # Check if email is already taken by another user
                        existing_email_user = self.find_by_email(data[field])
                        if existing_email_user and existing_email_user['user_id'] != user_id:
                            return {'success': False, 'error': 'Email already exists'}
                        update_data[field] = data[field].strip().lower()
                    else:
                        update_data[field] = data[field].strip() if isinstance(data[field], str) else data[field]
            
            # Update password if provided
            if 'password' in data and data['password']:
                update_data['password'] = self._hash_password(data['password'])
            
            if not update_data:
                return {'success': False, 'error': 'No valid fields to update'}
            
            # Update in database
            result = self.users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                # Get updated user
                updated_user = self.find_by_id(user_id)
                return {
                    'success': True,
                    'user': updated_user,
                    'message': 'User updated successfully'
                }
            else:
                return {'success': False, 'error': 'No changes made'}
                
        except Exception as e:
            return {'success': False, 'error': f'Database error: {str(e)}'}
    
    def delete_user(self, user_id: str) -> Dict[str, Any]:
        """Delete user (soft delete by setting is_active to False)"""
        try:
            if not ObjectId.is_valid(user_id):
                return {'success': False, 'error': 'Invalid user ID'}
            
            # Check if user exists
            existing_user = self.find_by_id(user_id)
            if not existing_user:
                return {'success': False, 'error': 'User not found'}
            
            # Soft delete by setting is_active to False
            result = self.users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'is_active': False}}
            )
            
            if result.modified_count > 0:
                return {
                    'success': True,
                    'message': 'User deleted successfully'
                }
            else:
                return {'success': False, 'error': 'Failed to delete user'}
                
        except Exception as e:
            return {'success': False, 'error': f'Database error: {str(e)}'}
    
    def list_users(self, search_query: str = None, role_filter: str = None) -> Dict[str, Any]:
        """List users with optional search and role filtering"""
        try:
            # Build query filter
            query_filter = {'is_active': True}
            
            if role_filter:
                query_filter['role'] = role_filter
            
            if search_query:
                query_filter['$or'] = [
                    {'name': {'$regex': search_query, '$options': 'i'}},
                    {'email': {'$regex': search_query, '$options': 'i'}}
                ]
            
            # Find users
            users_cursor = self.users_collection.find(query_filter)
            users = []
            
            for user_doc in users_cursor:
                users.append(self._convert_to_dict(user_doc))
            
            return {
                'success': True,
                'users': users,
                'total_count': len(users)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Database error: {str(e)}'}
    
    def reset_password(self, user_id: str, new_password: str = None) -> Dict[str, Any]:
        """Reset user password"""
        try:
            if not ObjectId.is_valid(user_id):
                return {'success': False, 'error': 'Invalid user ID'}
            
            # Check if user exists
            existing_user = self.find_by_id(user_id)
            if not existing_user:
                return {'success': False, 'error': 'User not found'}
            
            # Generate new password if not provided
            if not new_password:
                new_password = self._generate_random_password()
            
            # Hash new password
            hashed_password = self._hash_password(new_password)
            
            # Update password in database
            result = self.users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'password': hashed_password}}
            )
            
            if result.modified_count > 0:
                return {
                    'success': True,
                    'new_password': new_password,
                    'message': 'Password reset successfully'
                }
            else:
                return {'success': False, 'error': 'Failed to reset password'}
                
        except Exception as e:
            return {'success': False, 'error': f'Database error: {str(e)}'}
    
    def verify_password(self, email: str, password: str) -> bool:
        """Verify user password"""
        try:
            user = self.find_by_email(email)
            if not user:
                return False
            
            # Get user document with password
            user_doc = self.users_collection.find_one({'email': email.strip().lower()})
            if not user_doc:
                return False
            
            hashed_input = self._hash_password(password)
            return hashed_input == user_doc.get('password')
            
        except Exception as e:
            print(f"Error verifying password: {e}")
            return False
