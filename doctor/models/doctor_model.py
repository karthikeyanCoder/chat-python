"""
Doctor Model - Handles doctor database operations
"""

import bcrypt
from datetime import datetime
from typing import Dict, Any, List, Optional
import sys
import os

# Add the parent directory to the path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.objectid_converter import convert_objectid_to_string

class DoctorModel:
    """Doctor model for database operations"""
    
    def __init__(self, db):
        self.db = db
        self.collection = None
        self._update_collection()
    
    def _update_collection(self):
        """Update collection reference"""
        try:
            print(f"🔍 Updating doctor collection - db: {self.db}, hasattr: {hasattr(self.db, 'doctors_collection') if self.db else 'No db'}")
            if self.db and hasattr(self.db, 'doctors_collection'):
                self.collection = self.db.doctors_collection
                print(f"✅ Doctor collection updated: {self.collection}")
            else:
                print(f"❌ Doctor collection not available - db: {self.db}, hasattr: {hasattr(self.db, 'doctors_collection') if self.db else 'No db'}")
                self.collection = None
        except Exception as e:
            print(f"❌ Error updating doctor collection: {e}")
            self.collection = None
    
    def create_doctor(self, doctor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new doctor"""
        try:
            self._update_collection()
            
            if self.collection is None:
                return {
                    'success': False,
                    'error': 'Database not connected'
                }
            
            # Generate unique doctor ID
            import time
            import random
            doctor_id = f"D{int(time.time() * 1000)}{random.randint(1000, 9999)}"
            
            # Hash password
            password = doctor_data.get('password', '')
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
            
            # Create doctor document
            doctor_doc = {
                'doctor_id': doctor_id,
                'username': doctor_data.get('username'),
                'email': doctor_data.get('email'),
                'mobile': doctor_data.get('mobile'),
                'password_hash': password_hash,
                'role': doctor_data.get('role', 'doctor'),
                'status': 'active',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'is_profile_complete': False
            }
            
            # Insert doctor
            result = self.collection.insert_one(doctor_doc)
            
            if result.inserted_id:
                return {
                    'success': True,
                    'doctor_id': doctor_id,
                    'message': 'Doctor created successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to create doctor'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
    
    def get_doctor_by_id(self, doctor_id: str) -> Optional[Dict[str, Any]]:
        """Get doctor by ID"""
        try:
            self._update_collection()
            
            if self.collection is None:
                return None
            
            doctor = self.collection.find_one({'doctor_id': doctor_id})
            if doctor:
                # Convert ObjectId to string
                doctor = convert_objectid_to_string(doctor)
                # Remove sensitive data
                if 'password_hash' in doctor:
                    del doctor['password_hash']
                return doctor
            return None
            
        except Exception as e:
            print(f"❌ Error getting doctor by ID: {e}")
            return None
    
    def get_doctor_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get doctor by email"""
        try:
            self._update_collection()
            
            if self.collection is None:
                return None
            
            doctor = self.collection.find_one({'email': email})
            if doctor:
                return convert_objectid_to_string(doctor)
            return None
            
        except Exception as e:
            print(f"❌ Error getting doctor by email: {e}")
            return None
    
    def check_email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        try:
            self._update_collection()
            
            if self.collection is None:
                return False
            
            count = self.collection.count_documents({'email': email})
            return count > 0
            
        except Exception as e:
            print(f"❌ Error checking email existence: {e}")
            return False
    
    def check_username_exists(self, username: str) -> bool:
        """Check if username already exists"""
        try:
            self._update_collection()
            
            if self.collection is None:
                return False
            
            count = self.collection.count_documents({'username': username})
            return count > 0
            
        except Exception as e:
            print(f"❌ Error checking username existence: {e}")
            return False
    
    def check_mobile_exists(self, mobile: str) -> bool:
        """Check if mobile already exists"""
        try:
            self._update_collection()
            
            if self.collection is None:
                return False
            
            count = self.collection.count_documents({'mobile': mobile})
            return count > 0
            
        except Exception as e:
            print(f"❌ Error checking mobile existence: {e}")
            return False
    
    def verify_password(self, identifier: str, password: str) -> bool:
        """Verify doctor password"""
        try:
            self._update_collection()
            
            if self.collection is None:
                return False
            
            # Find doctor by email or doctor_id
            doctor = self.collection.find_one({
                "$or": [
                    {"email": identifier},
                    {"doctor_id": identifier}
                ]
            })
            
            if not doctor:
                print(f"❌ Doctor not found for identifier: {identifier}")
                return False
            
            password_hash = doctor.get('password_hash')
            if not password_hash:
                print(f"❌ No password hash found for doctor: {identifier}")
                return False
            
            print(f"🔍 Password verification debug:")
            print(f"   Identifier: {identifier}")
            print(f"   Password hash type: {type(password_hash)}")
            print(f"   Password hash length: {len(password_hash) if password_hash else 0}")
            print(f"   Input password: {password}")
            
            # Convert password_hash to bytes if it's a string
            if isinstance(password_hash, str):
                password_hash = password_hash.encode('utf-8')
            elif isinstance(password_hash, bytes):
                # Already bytes, no conversion needed
                pass
            else:
                print(f"❌ Unexpected password_hash type: {type(password_hash)}")
                return False
            
            # Verify password
            is_valid = bcrypt.checkpw(password.encode('utf-8'), password_hash)
            print(f"   Password verification result: {is_valid}")
            
            return is_valid
            
        except Exception as e:
            print(f"❌ Error verifying password: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def reset_password(self, email: str, new_password: str) -> Dict[str, Any]:
        """Reset doctor password"""
        try:
            # Update collection reference
            self._update_collection()
            
            if self.collection is None:
                return {
                    'success': False,
                    'error': 'Database not connected'
                }
            
            # Hash the new password using bcrypt (same as signup)
            import bcrypt
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt)
            
            # Update password
            result = self.collection.update_one(
                {'email': email},
                {'$set': {
                    'password_hash': hashed_password,
                    'updated_at': datetime.utcnow()
                }}
            )
            
            if result.modified_count > 0:
                return {
                    'success': True,
                    'message': 'Password reset successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Doctor not found or no changes made'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
    
    def get_all_doctors(self, query_filter: Dict[str, Any] = None, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """Get all doctors with pagination and patient count"""
        try:
            self._update_collection()
            
            if self.collection is None:
                return {
                    'success': False,
                    'error': 'Database not connected'
                }
            
            # Default query filter
            if query_filter is None:
                query_filter = {"status": {"$ne": "deleted"}}
            
            # Calculate skip for pagination
            skip = (page - 1) * limit
            
            # Get doctors with pagination
            doctors_cursor = self.collection.find(
                query_filter,
                {
                    'password_hash': 0,  # Exclude sensitive data
                    '_id': 0
                }
            ).skip(skip).limit(limit).sort('created_at', -1)
            
            doctors = list(doctors_cursor)
            
            # Count total doctors
            total_count = self.collection.count_documents(query_filter)
            
            # Calculate total pages
            total_pages = (total_count + limit - 1) // limit
            
            # Add patient count for each doctor
            for doctor in doctors:
                patient_count = self._count_patients_for_doctor(doctor.get('doctor_id'))
                doctor['patient_count'] = patient_count
            
            # Convert ObjectIds to strings
            doctors = [convert_objectid_to_string(doctor) for doctor in doctors]
            
            return {
                'success': True,
                'doctors': doctors,
                'total_count': total_count,
                'page': page,
                'limit': limit,
                'total_pages': total_pages
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
    
    def _count_patients_for_doctor(self, doctor_id: str) -> int:
        """Count patients for a specific doctor"""
        try:
            if not self.db or not hasattr(self.db, 'patients_collection'):
                return 0
            
            patients_collection = self.db.patients_collection
            if patients_collection is None:
                return 0
            
            # Count patients assigned to this doctor
            count = patients_collection.count_documents({
                'assigned_doctor_id': doctor_id,
                'status': {'$ne': 'deleted'}
            })
            
            return count
            
        except Exception as e:
            print(f"❌ Error counting patients for doctor {doctor_id}: {e}")
            return 0
    
    def update_doctor_profile(self, doctor_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update doctor profile"""
        try:
            self._update_collection()
            
            if self.collection is None:
                return {
                    'success': False,
                    'error': 'Database not connected'
                }
            
            # Update profile
            result = self.collection.update_one(
                {'doctor_id': doctor_id},
                {
                    '$set': {
                        **profile_data,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                return {
                    'success': True,
                    'message': 'Profile updated successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Doctor not found or no changes made'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
    
    def complete_doctor_profile(self, doctor_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Complete doctor profile"""
        try:
            self._update_collection()
            
            if self.collection is None:
                return {
                    'success': False,
                    'error': 'Database not connected'
                }
            
            # Add profile completion timestamp
            profile_data['is_profile_complete'] = True
            profile_data['profile_completed_at'] = datetime.utcnow()
            
            # Update profile
            result = self.collection.update_one(
                {'doctor_id': doctor_id},
                {
                    '$set': {
                        **profile_data,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                return {
                    'success': True,
                    'message': 'Profile completed successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Doctor not found or no changes made'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
    
    def verify_doctor_email(self, doctor_id: str) -> Dict[str, Any]:
        """Verify doctor email by setting email_verified to True"""
        try:
            self._update_collection()
            
            if self.collection is None:
                return {
                    'success': False,
                    'error': 'Database not connected'
                }
            
            # Update doctor to mark email as verified
            result = self.collection.update_one(
                {'doctor_id': doctor_id},
                {
                    '$set': {
                        'email_verified': True,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                return {
                    'success': True,
                    'message': 'Email verified successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Doctor not found or email already verified'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }