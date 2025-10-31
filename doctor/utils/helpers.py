"""
Helpers - Utility functions
"""

import secrets
import string
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class Helpers:
    """Helper utility functions"""
    
    @staticmethod
    def generate_random_string(length: int = 8) -> str:
        """Generate random string"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))
    
    @staticmethod
    def generate_otp(length: int = 6) -> str:
        """Generate random OTP"""
        return ''.join(secrets.choice(string.digits) for _ in range(length))
    
    @staticmethod
    def format_datetime(dt: datetime) -> str:
        """Format datetime to ISO string"""
        return dt.isoformat()
    
    @staticmethod
    def parse_datetime(dt_str: str) -> Optional[datetime]:
        """Parse ISO datetime string"""
        try:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except:
            return None
    
    @staticmethod
    def is_expired(expiry_time: datetime) -> bool:
        """Check if a datetime is expired"""
        return datetime.utcnow() > expiry_time
    
    @staticmethod
    def get_expiry_time(minutes: int = 30) -> datetime:
        """Get expiry time from now"""
        return datetime.utcnow() + timedelta(minutes=minutes)
    
    @staticmethod
    def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize dictionary data"""
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = value.strip()
            elif isinstance(value, dict):
                sanitized[key] = Helpers.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [Helpers.sanitize_dict(item) if isinstance(item, dict) else item for item in value]
            else:
                sanitized[key] = value
        
        return sanitized
    
    @staticmethod
    def remove_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from dictionary"""
        sensitive_keys = ['password', 'password_hash', 'token', 'secret', 'key']
        
        cleaned = data.copy()
        
        for key in sensitive_keys:
            if key in cleaned:
                del cleaned[key]
        
        return cleaned
    
    @staticmethod
    def mask_email(email: str) -> str:
        """Mask email address for privacy"""
        if not email or '@' not in email:
            return email
        
        local, domain = email.split('@', 1)
        
        if len(local) <= 2:
            masked_local = local[0] + '*' * (len(local) - 1)
        else:
            masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
        
        return f"{masked_local}@{domain}"
    
    @staticmethod
    def mask_phone(phone: str) -> str:
        """Mask phone number for privacy"""
        if not phone or len(phone) < 4:
            return phone
        
        return phone[:2] + '*' * (len(phone) - 4) + phone[-2:]
    
    @staticmethod
    def format_response(success: bool, message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Format API response"""
        response = {
            'success': success,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if data:
            response['data'] = data
        
        return response
    
    @staticmethod
    def log_operation(operation: str, user_id: str, details: str = "") -> None:
        """Log operation for debugging"""
        timestamp = datetime.utcnow().isoformat()
        print(f"[{timestamp}] {operation} - User: {user_id} - {details}")
    
    @staticmethod
    def validate_json_structure(data: Dict[str, Any], required_structure: Dict[str, type]) -> tuple[bool, str]:
        """Validate JSON structure against required schema"""
        for key, expected_type in required_structure.items():
            if key not in data:
                return False, f"Missing required field: {key}"
            
            if not isinstance(data[key], expected_type):
                return False, f"Field '{key}' should be of type {expected_type.__name__}"
        
        return True, ""
    
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