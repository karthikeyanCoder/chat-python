"""
User Controller - Handles user operations with role-based access control
"""

from flask import request, jsonify
from typing import Dict, Any, Tuple
from models.user_model import UserModel
from utils.jwt_utils import JWTUtils
from utils.validators import Validators


class UserController:
    """User controller with role-based access control"""
    
    def __init__(self, user_model: UserModel = None, jwt_utils: JWTUtils = None, validators: Validators = None):
        self.user_model = user_model or UserModel()
        self.jwt_utils = jwt_utils or JWTUtils()
        self.validators = validators or Validators()
    
    def login(self, request) -> Tuple[Dict[str, Any], int]:
        """User login endpoint with role-based response handling"""
        try:
            data = request.get_json()
            
            # Validate required fields
            email = data.get('email', '').strip()
            password = data.get('password', '')
            
            if not email or not password:
                return jsonify({'error': 'Email and password are required'}), 400
            
            # Validate email format
            if not self.validators.validate_email(email):
                return jsonify({'error': 'Invalid email format'}), 400
            
            # Get user details first to check if account exists
            user = self.user_model.find_by_email(email)
            if not user:
                return jsonify({'error': 'Account not found'}), 401
                
            # Check if account is active
            if not user.get('is_active', True):
                return jsonify({'error': 'Account is inactive. Please contact support.'}), 401
            
            # Verify credentials
            if not self.user_model.verify_password(email, password):
                return jsonify({'error': 'Invalid password'}), 401
            
            # Role-specific data preparation
            role_data = {}
            user_role = user.get('role')
            
            if user_role == 'doctor':
                # Get assigned nurses count
                role_data['assigned_nurses_count'] = 0  # TODO: Add nurse count logic
            elif user_role == 'nurse':
                # Get assigned patients count
                role_data['assigned_patients_count'] = 0  # TODO: Add patient count logic
            elif user_role == 'patient':
                # Get assigned nurse if any
                role_data['assigned_nurse'] = None  # TODO: Add assigned nurse logic
            
            # Generate JWT token with appropriate expiration
            token_expiration = {
                'admin': 24,  # 24 hours
                'doctor': 12,  # 12 hours
                'nurse': 8,    # 8 hours
                'patient': 4   # 4 hours
            }.get(user_role, 4)  # Default to 4 hours
            
            token_data = {
                'user_id': user['user_id'],
                'email': user['email'],
                'role': user['role'],
                'name': user['name']
            }
            
            token = self.jwt_utils.generate_token(token_data, expiration_hours=token_expiration)
            
            return jsonify({
                'success': True,
                'message': f'Welcome back, {user["name"]}!',
                'token': token,
                'user': {
                    'user_id': user['user_id'],
                    'name': user['name'],
                    'email': user['email'],
                    'role': user['role'],
                    'avatar': user.get('avatar', ''),
                    'last_login': user.get('last_login', ''),
                    **role_data  # Include role-specific data
                },
                'token_expires_in': f'{token_expiration} hours'
            }), 200
            
        except Exception as e:
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    def create_user(self, request, current_user: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """Create new user with role-based access control"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['name', 'email', 'password', 'role']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            # Role-based access control
            current_role = current_user.get('role')
            requested_role = data.get('role')
            
            # Role creation permissions
            role_permissions = {
                'admin': ['admin', 'doctor', 'nurse', 'patient'],
                'doctor': ['nurse', 'patient']
            }
            
            if current_role not in role_permissions:
                return jsonify({'error': 'Insufficient permissions to create users'}), 403
                
            allowed_roles = role_permissions[current_role]
            if requested_role not in allowed_roles:
                return jsonify({
                    'error': f'{current_role.capitalize()} can only create the following roles: {", ".join(allowed_roles)}'
                }), 403
            
            # Validate email format
            if not self.validators.validate_email(data['email']):
                return jsonify({'error': 'Invalid email format'}), 400
            
            # Validate role
            valid_roles = ['admin', 'doctor', 'nurse', 'patient']
            if requested_role not in valid_roles:
                return jsonify({'error': f'Invalid role. Must be one of: {valid_roles}'}), 400
            
            # Create user
            result = self.user_model.create_user(data)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': 'User created successfully',
                    'user': result['user']
                }), 201
            else:
                return jsonify({'error': result['error']}), 400
                
        except Exception as e:
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    def get_users(self, request, current_user: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """Get users list with role-based filtering"""
        try:
            # Get query parameters
            search_query = request.args.get('search', '').strip()
            
            # Role-based access control
            current_role = current_user.get('role')
            
            # Define role-based view permissions
            role_filters = {
                'admin': None,  # Can see all users
                'doctor': ['nurse', 'patient'],  # Can see nurses and patients
                'nurse': ['patient']  # Can only see patients
            }
            
            if current_role not in role_filters:
                return jsonify({'error': 'Insufficient permissions to view users'}), 403
                
            role_filter = role_filters[current_role]
            
            # For nurses, also filter by assigned patients
            if current_role == 'nurse':
                # TODO: Add assignment checking logic here
                # This would check a separate collection for nurse-patient assignments
                pass
            
            # Get users
            result = self.user_model.list_users(search_query, role_filter)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'users': result['users'],
                    'total_count': result['total_count'],
                    'search_query': search_query,
                    'role_filter': role_filter
                }), 200
            else:
                return jsonify({'error': result['error']}), 500
                
        except Exception as e:
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    def update_user(self, request, user_id: str, current_user: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """Update user with role-based access control"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Check if user exists
            target_user = self.user_model.find_by_id(user_id)
            if not target_user:
                return jsonify({'error': 'User not found'}), 404
            
            # Role-based access control
            current_role = current_user.get('role')
            target_role = target_user.get('role')
            current_user_id = current_user.get('user_id')
            
            # Define update permissions
            role_permissions = {
                'admin': ['admin', 'doctor', 'nurse', 'patient'],
                'doctor': ['nurse', 'patient'],
                'nurse': ['patient'],
                'patient': []  # Patients can only edit themselves
            }
            
            if current_role not in role_permissions:
                return jsonify({'error': 'Insufficient permissions to update users'}), 403
            
            # Allow users to update their own profile
            if current_user_id == user_id:
                allowed_fields = ['name', 'email', 'password', 'avatar']
                data = {k: v for k, v in data.items() if k in allowed_fields}
            else:
                # Check if user can update target role
                if target_role not in role_permissions[current_role]:
                    return jsonify({
                        'error': f'{current_role.capitalize()} cannot update {target_role} accounts'
                    }), 403
                
                # For nurses, check if patient is assigned to them
                if current_role == 'nurse' and target_role == 'patient':
                    # TODO: Add assignment checking logic here
                    pass
            
            # Validate email format if provided
            if 'email' in data and data['email']:
                if not self.validators.validate_email(data['email']):
                    return jsonify({'error': 'Invalid email format'}), 400
            
            # Update user
            result = self.user_model.update_user(user_id, data)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': 'User updated successfully',
                    'user': result['user']
                }), 200
            else:
                return jsonify({'error': result['error']}), 400
                
        except Exception as e:
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    def delete_user(self, request, user_id: str, current_user: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """Delete user with role-based access control"""
        try:
            # Check if user exists
            target_user = self.user_model.find_by_id(user_id)
            if not target_user:
                return jsonify({'error': 'User not found'}), 404
            
            # Role-based access control
            current_role = current_user.get('role')
            target_role = target_user.get('role')
            current_user_id = current_user.get('user_id')
            
            # Define delete permissions
            role_permissions = {
                'admin': ['admin', 'doctor', 'nurse', 'patient'],
                'doctor': ['nurse', 'patient']
            }
            
            if current_role not in role_permissions:
                return jsonify({'error': 'Insufficient permissions to delete users'}), 403
            
            # Prevent self-deletion
            if current_user_id == user_id:
                return jsonify({'error': 'Cannot delete your own account'}), 403
            
            # Check if user can delete target role
            if target_role not in role_permissions[current_role]:
                return jsonify({
                    'error': f'{current_role.capitalize()} cannot delete {target_role} accounts'
                }), 403
            
            # Prevent self-deletion
            if current_user.get('user_id') == user_id:
                return jsonify({'error': 'Cannot delete your own account'}), 400
            
            # Delete user
            result = self.user_model.delete_user(user_id)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': 'User deleted successfully'
                }), 200
            else:
                return jsonify({'error': result['error']}), 400
                
        except Exception as e:
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    def reset_password(self, request, user_id: str, current_user: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """Reset user password with role-based access control"""
        try:
            # Check if user exists
            target_user = self.user_model.find_by_id(user_id)
            if not target_user:
                return jsonify({'error': 'User not found'}), 404
            
            # Role-based access control
            current_role = current_user.get('role')
            target_role = target_user.get('role')
            current_user_id = current_user.get('user_id')
            
            # Define password reset permissions
            role_permissions = {
                'admin': ['admin', 'doctor', 'nurse', 'patient'],
                'doctor': ['nurse', 'patient'],
                'nurse': ['patient']
            }
            
            if current_role not in role_permissions:
                return jsonify({'error': 'Insufficient permissions to reset passwords'}), 403
            
            # Prevent self-password reset (use profile update instead)
            if current_user_id == user_id:
                return jsonify({'error': 'Use profile update to change your own password'}), 403
            
            # Check if user can reset password for target role
            if target_role not in role_permissions[current_role]:
                return jsonify({
                    'error': f'{current_role.capitalize()} cannot reset passwords for {target_role} accounts'
                }), 403
                
            # For nurses, check if patient is assigned to them
            if current_role == 'nurse' and target_role == 'patient':
                # TODO: Add assignment checking logic here
                pass
            
            # Get new password from request (optional)
            data = request.get_json() or {}
            new_password = data.get('new_password')
            
            # Reset password
            result = self.user_model.reset_password(user_id, new_password)
            
            if result['success']:
                response_data = {
                    'success': True,
                    'message': 'Password reset successfully'
                }
                
                # Include new password in response if it was generated
                if 'new_password' in result:
                    response_data['new_password'] = result['new_password']
                
                return jsonify(response_data), 200
            else:
                return jsonify({'error': result['error']}), 400
                
        except Exception as e:
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    def get_user_profile(self, request, user_id: str, current_user: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """Get user profile with role-based access control"""
        try:
            # Check if user exists
            target_user = self.user_model.find_by_id(user_id)
            if not target_user:
                return jsonify({'error': 'User not found'}), 404
            
            # Role-based access control
            current_role = current_user.get('role')
            target_role = target_user.get('role')
            
            if current_role == 'admin':
                # Admin can view any user profile
                pass
            elif current_role == 'doctor':
                # Doctor can only view nurse profiles
                if target_role != 'nurse':
                    return jsonify({'error': 'Doctors can only view nurse profiles'}), 403
            elif current_user.get('user_id') == user_id:
                # Users can view their own profile
                pass
            else:
                return jsonify({'error': 'Insufficient permissions to view user profile'}), 403
            
            return jsonify({
                'success': True,
                'user': target_user
            }), 200
                
        except Exception as e:
            return jsonify({'error': f'Server error: {str(e)}'}), 500
