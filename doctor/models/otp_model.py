"""
OTP Model - Handles OTP-related database operations
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import secrets
import string

class OTPModel:
    """OTP data model and operations"""
    
    def __init__(self, database):
        self.db = database
        self._update_collection()
    
    def _update_collection(self):
        """Update collection reference"""
        print(f"🔍 Updating OTP collection - db: {self.db}, hasattr: {hasattr(self.db, 'temp_otp_collection') if self.db else 'No db'}")
        if self.db and hasattr(self.db, 'temp_otp_collection') and self.db.temp_otp_collection is not None:
            self.temp_collection = self.db.temp_otp_collection
            print(f"✅ OTP collection updated: {self.temp_collection}")
        else:
            print(f"❌ OTP collection not available - db: {self.db}, hasattr: {hasattr(self.db, 'temp_otp_collection') if self.db else 'No db'}")
            self.temp_collection = None
    
    def store_temp_signup_data(self, email: str, signup_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store temporary signup data for OTP verification"""
        try:
            # Update collection reference
            self._update_collection()
            
            if self.temp_collection is None:
                return {
                    'success': False,
                    'error': 'Database not connected'
                }
            
            # Prepare temp data
            temp_data = {
                'email': email,
                'signup_data': signup_data,
                'created_at': datetime.utcnow(),
                'expires_at': datetime.utcnow() + timedelta(hours=1)  # Expire in 1 hour
            }
            
            # Remove any existing temp data for this email
            self.temp_collection.delete_many({'email': email})
            
            # Insert new temp data
            result = self.temp_collection.insert_one(temp_data)
            
            if result.inserted_id:
                return {
                    'success': True,
                    'message': 'Temporary signup data stored successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to store temporary data'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
    
    def get_temp_signup_data(self, email: str) -> Optional[Dict[str, Any]]:
        """Get temporary signup data"""
        try:
            # Update collection reference
            self._update_collection()
            
            if self.temp_collection is None:
                return None
            
            temp_data = self.temp_collection.find_one({'email': email})
            if temp_data:
                # Check if expired
                if temp_data.get('expires_at', datetime.utcnow()) < datetime.utcnow():
                    # Remove expired data
                    self.temp_collection.delete_one({'email': email})
                    return None
                return temp_data
            return None
        except Exception as e:
            print(f"❌ Error getting temp signup data: {e}")
            return None
    
    def cleanup_temp_data(self, email: str) -> Dict[str, Any]:
        """Clean up temporary signup data"""
        try:
            result = self.temp_collection.delete_many({'email': email})
            return {
                'success': True,
                'deleted_count': result.deleted_count,
                'message': 'Temporary data cleaned up successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
    
    def cleanup_expired_data(self) -> Dict[str, Any]:
        """Clean up expired temporary data"""
        try:
            current_time = datetime.utcnow()
            result = self.temp_collection.delete_many({'expires_at': {'$lt': current_time}})
            return {
                'success': True,
                'deleted_count': result.deleted_count,
                'message': f'Cleaned up {result.deleted_count} expired records'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
    
    def generate_otp(self, length: int = 6) -> str:
        """Generate random OTP"""
        return ''.join(secrets.choice(string.digits) for _ in range(length))
    
    def is_otp_valid(self, otp: str, min_length: int = 6) -> bool:
        """Validate OTP format"""
        if not otp or len(otp) != min_length:
            return False
        return otp.isdigit()
