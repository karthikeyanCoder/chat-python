"""
Invite Helpers - Utility functions for invite codes
Based on doctor/utils/helpers.py
"""
import secrets
import string
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


class InviteHelpers:
    """Helper utility functions for invite codes"""
    
    @staticmethod
    def generate_invite_code() -> str:
        """Generate invite code format: ABC-XYZ-123"""
        chars = string.ascii_uppercase + string.digits
        parts = []
        for _ in range(3):
            part = ''.join(secrets.choice(chars) for _ in range(3))
            parts.append(part)
        return '-'.join(parts)
    
    @staticmethod
    def hash_invite_code(code: str) -> str:
        """Hash invite code for security"""
        import hashlib
        return hashlib.sha256(code.encode()).hexdigest()
    
    @staticmethod
    def generate_connection_id() -> str:
        """Generate unique connection ID"""
        timestamp = int(datetime.utcnow().timestamp() * 1000)
        random_suffix = ''.join(secrets.choice(string.digits) for _ in range(3))
        return f"CONN{timestamp}{random_suffix}"
    
    @staticmethod
    def get_expiry_time(days: int = 7) -> datetime:
        """Get expiry time from now"""
        return datetime.utcnow() + timedelta(days=days)
    
    @staticmethod
    def is_expired(expiry_time: datetime) -> bool:
        """Check if a datetime is expired"""
        return datetime.utcnow() > expiry_time
    
    @staticmethod
    def format_datetime(dt: datetime) -> str:
        """Format datetime to ISO string"""
        return dt.isoformat()
    
    @staticmethod
    def validate_invite_code_format(code: str) -> bool:
        """Validate invite code format: ABC-XYZ-123"""
        import re
        pattern = r'^[A-Z0-9]{3}-[A-Z0-9]{3}-[A-Z0-9]{3}$'
        return bool(re.match(pattern, code))
    
    @staticmethod
    def create_invite_data(doctor_id: str, patient_email: str, 
                          expires_in_days: int = 7, 
                          message: str = "") -> Dict[str, Any]:
        """Create invite data structure"""
        invite_code = InviteHelpers.generate_invite_code()
        expires_at = InviteHelpers.get_expiry_time(expires_in_days)
        
        return {
            "invite_code": invite_code,
            "invite_code_hash": InviteHelpers.hash_invite_code(invite_code),
            "doctor_id": doctor_id,
            "patient_email": patient_email,
            "status": "active",
            "expires_at": expires_at,
            "created_at": datetime.utcnow(),
            "usage_limit": 1,
            "used_count": 0,
            "message": message
        }
