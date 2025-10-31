"""
Validators - Input validation utilities
"""

import re
from typing import Any

class Validators:
    """Input validation utilities"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_mobile(mobile: str) -> bool:
        """Validate mobile number format"""
        if not mobile:
            return False
        
        # Remove any non-digit characters
        mobile_digits = re.sub(r'\D', '', mobile)
        
        # Check if it's a valid mobile number (10 digits)
        return len(mobile_digits) == 10 and mobile_digits.isdigit()
    
    @staticmethod
    def validate_password(password: str) -> bool:
        """Validate password strength"""
        if not password:
            return False
        
        # At least 8 characters, 1 uppercase, 1 lowercase, 1 digit
        if len(password) < 8:
            return False
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        return has_upper and has_lower and has_digit
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate username format"""
        if not username:
            return False
        
        # Username should be 3-20 characters, alphanumeric and underscores only
        pattern = r'^[a-zA-Z0-9_]{3,20}$'
        return bool(re.match(pattern, username))
    
    @staticmethod
    def validate_required_fields(data: dict, required_fields: list) -> tuple[bool, str]:
        """Validate required fields in data"""
        missing_fields = []
        
        for field in required_fields:
            if field not in data or not data[field]:
                missing_fields.append(field)
        
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        return True, ""
    
    @staticmethod
    def sanitize_string(value: str) -> str:
        """Sanitize string input"""
        if not value:
            return ""
        
        # Remove leading/trailing whitespace
        value = value.strip()
        
        # Remove any potentially dangerous characters
        value = re.sub(r'[<>"\']', '', value)
        
        return value
    
    @staticmethod
    def validate_otp(otp: str) -> bool:
        """Validate OTP format"""
        if not otp:
            return False
        
        # OTP should be 6 digits
        return len(otp) == 6 and otp.isdigit()
    
    @staticmethod
    def validate_doctor_id(doctor_id: str) -> bool:
        """Validate doctor ID format"""
        if not doctor_id:
            return False
        
        # Doctor ID should start with 'D' followed by digits
        pattern = r'^D\d+$'
        return bool(re.match(pattern, doctor_id))
    
    @staticmethod
    def validate_patient_id(patient_id: str) -> bool:
        """Validate patient ID format"""
        if not patient_id:
            return False
        
        # Patient ID should start with 'P' followed by digits
        pattern = r'^P\d+$'
        return bool(re.match(pattern, patient_id))
