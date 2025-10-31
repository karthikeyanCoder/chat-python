"""
Validation utilities for email, mobile, password, and profile validation
"""
import re
import bcrypt


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    try:
        # Ensure password is string and encode it
        if isinstance(password, bytes):
            password = password.decode('utf-8')
        password_bytes = password.encode('utf-8')
        
        # Ensure hashed is string and encode it
        if isinstance(hashed, bytes):
            hashed = hashed.decode('utf-8')
        hashed_bytes = hashed.encode('utf-8')
        
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception as e:
        print(f"Password verification error: {e}")
        return False


def validate_email(email: str) -> bool:
    """Validate email format"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None


def validate_mobile(mobile: str) -> bool:
    """Validate mobile number"""
    return mobile.isdigit() and len(mobile) >= 10


def is_profile_complete(patient_doc: dict) -> bool:
    """Check if patient profile is complete"""
    required_fields = [
        'first_name', 'last_name', 'date_of_birth', 'blood_type', 'gender',
        'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
        'address', 'height', 'weight', 'is_pregnant', 'last_period_date'
    ]
    return all(field in patient_doc for field in required_fields)

