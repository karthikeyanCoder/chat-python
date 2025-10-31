"""
Authentication utilities: JWT token generation, verification, and decorators
"""
import jwt
import uuid
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from .config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_HOURS


def generate_jwt_token(user_data):
    """Generate JWT token for user"""
    payload = {
        "user_id": str(user_data.get("_id")) if user_data.get("_id") else str(user_data.get("patient_id", "")),
        "patient_id": user_data.get("patient_id"),
        "email": user_data.get("email"),
        "username": user_data.get("username"),
        "object_id": str(user_data.get("_id")) if user_data.get("_id") else str(user_data.get("patient_id", "")),  # Add object_id for compatibility
        "type": "access_token",  # Add type field for doctor module compatibility
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_jwt_token(token):
    """Verify JWT token and return user data"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    """Decorator to require JWT token for protected routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({"error": "Invalid token format"}), 401
        
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        
        # Verify token
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        # Add user data to request
        request.user_data = payload
        return f(*args, **kwargs)
    
    return decorated


def generate_patient_id():
    """Generate unique patient ID with timestamp and random component"""
    import time
    timestamp = int(time.time())
    random_component = uuid.uuid4().hex[:6].upper()
    return f"PAT{timestamp}{random_component}"


def generate_unique_patient_id():
    """Generate a unique patient ID that doesn't exist in database"""
    from .database import db
    
    while True:
        patient_id = generate_patient_id()
        # Check if patient_id already exists in database
        existing_patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not existing_patient:
            return patient_id

