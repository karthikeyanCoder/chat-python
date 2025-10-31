"""
JWT Utilities - Handles JWT token generation and verification
"""

import jwt
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from functools import wraps
from flask import request, jsonify, current_app
from models.assignment_model import AssignmentModel


class JWTUtils:
    """JWT token utilities"""
    
    def __init__(self):
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this')
        self.algorithm = 'HS256'
        self.expiration_hours = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))
    
    def generate_token(self, data: Dict[str, Any]) -> str:
        """Generate JWT token"""
        try:
            # Add expiration time
            expiration = datetime.utcnow() + timedelta(hours=self.expiration_hours)
            
            payload = {
                'data': data,
                'exp': expiration,
                'iat': datetime.utcnow()
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            return token
            
        except Exception as e:
            print(f"Error generating token: {e}")
            raise Exception(f"Failed to generate token: {str(e)}")
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload.get('data')
            
        except jwt.ExpiredSignatureError:
            print("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            print(f"Invalid token: {e}")
            return None
        except Exception as e:
            print(f"Error verifying token: {e}")
            return None
    
    def get_token_from_header(self, request) -> Optional[str]:
        """Extract token from Authorization header"""
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return None
            
            # Check if it's Bearer token
            if auth_header.startswith('Bearer '):
                return auth_header.split(' ')[1]
            
            return None
            
        except Exception as e:
            print(f"Error extracting token: {e}")
            return None


def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Get token from header
            jwt_utils = JWTUtils()
            token = jwt_utils.get_token_from_header(request)
            
            if not token:
                return jsonify({'error': 'Authorization token required'}), 401
            
            # Verify token
            user_data = jwt_utils.verify_token(token)
            if not user_data:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            # Add user data to kwargs
            kwargs['current_user'] = user_data
            
            return f(*args, **kwargs)
            
        except Exception as e:
            return jsonify({'error': f'Authentication error: {str(e)}'}), 401
    
    return decorated_function


def require_roles(*allowed_roles):
    """Decorator to require specific roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Get current user from kwargs (should be set by require_auth)
                current_user = kwargs.get('current_user')
                if not current_user:
                    return jsonify({'error': 'Authentication required'}), 401
                
                # Check if user has required role
                user_role = current_user.get('role')
                if user_role not in allowed_roles:
                    return jsonify({'error': f'Insufficient permissions. Required roles: {allowed_roles}'}), 403
                
                return f(*args, **kwargs)
                
            except Exception as e:
                return jsonify({'error': f'Authorization error: {str(e)}'}), 403
        
        return decorated_function
    return decorator


def require_admin(f):
    """Decorator to require admin role"""
    return require_roles('admin')(f)


def require_doctor_or_admin(f):
    """Decorator to require doctor or admin role"""
    return require_roles('doctor', 'admin')(f)


def require_nurse_or_above(f):
    """Decorator to require nurse, doctor, or admin role"""
    return require_roles('nurse', 'doctor', 'admin')


def require_patient_or_above(f):
    """Decorator to require any valid role"""
    return require_roles('patient', 'nurse', 'doctor', 'admin')


def require_nurse_assignment(assignment_model=None):
    """Decorator to require nurse assignment to patient
    Must be used after require_auth and require_roles
    """
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Get current user and patient ID
                current_user = kwargs.get('current_user')
                patient_id = kwargs.get('patient_id')
                
                if not current_user or not patient_id:
                    return jsonify({'error': 'Missing required context'}), 401
                
                # Skip check for admin and doctors
                if current_user.get('role') in ['admin', 'doctor']:
                    return f(*args, **kwargs)
                
                # For nurses, verify assignment
                if current_user.get('role') == 'nurse':
                    model = assignment_model or AssignmentModel()
                    is_assigned = model.is_patient_assigned_to_nurse(
                        current_user.get('user_id'),
                        patient_id
                    )
                    
                    if not is_assigned:
                        return jsonify({'error': 'Patient not assigned to you'}), 403
                
                return f(*args, **kwargs)
                
            except Exception as e:
                return jsonify({'error': f'Authorization error: {str(e)}'}), 403
        
        return decorated_function
    return wrapper("f")
