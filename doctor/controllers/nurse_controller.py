"""
Nurse Controller - Handles nurse operations with role-based access control
"""

from flask import jsonify
from typing import Dict, Any, Tuple
from models.nurse_model import NurseModel
from utils.validators import Validators


class NurseController:
    """Controller for nurse operations with role-based access"""
    
    def __init__(self, nurse_model: NurseModel = None, validators: Validators = None):
        self.nurse_model = nurse_model or NurseModel()
        self.validators = validators or Validators()
    
    def create_nurse(self, request, current_user: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """Create new nurse (Doctor only)"""
        try:
            # Check if user is authenticated
            if not current_user:
                return jsonify({
                    'error': 'Authentication required',
                    'details': 'You must be logged in with a valid token'
                }), 401
            
            # Log debug info
            print(f"Create nurse request from user: {current_user}")
            
            data = request.get_json()
            if not data:
                return jsonify({
                    'error': 'Invalid request',
                    'details': 'Request body is missing or invalid JSON'
                }), 400
                
            # Validate role-based access
            if current_user.get('role') != 'doctor':
                return jsonify({
                    'error': 'Permission denied',
                    'details': f"Only doctors can create nurse accounts. Your role is: {current_user.get('role', 'unknown')}"
                }), 403
            
            # Validate required fields
            required_fields = ['name', 'email', 'phone']
            missing_fields = [field for field in required_fields if not data.get(field)]
            
            if missing_fields:
                return jsonify({
                    'error': 'Missing required fields',
                    'details': f"The following fields are required: {', '.join(missing_fields)}",
                    'required_fields': required_fields
                }), 400
            
            # Validate email format
            if not self.validators.validate_email(data['email']):
                return jsonify({
                    'error': 'Invalid email format',
                    'details': f"The provided email '{data['email']}' is not valid",
                    'email': data['email']
                }), 400
            
            # Create nurse with doctor's ID 
            doctor_id = current_user.get('doctor_id') or current_user.get('user_id')
            if not doctor_id:
                return jsonify({'error': 'Missing doctor ID in token'}), 400

            result = self.nurse_model.create_nurse(data, doctor_id)
            
            if result['success']:
                response_data = {
                    'success': True,
                    'message': 'Nurse created successfully',
                    'nurse': result['nurse']
                }
                
                # Include temporary password if generated
                if 'temporary_password' in result:
                    response_data['temporary_password'] = result['temporary_password']
                    response_data['details'] = 'A temporary password has been generated'
                
                print(f"Successfully created nurse: {result['nurse'].get('email')}")
                return jsonify(response_data), 201
            else:
                return jsonify({
                    'error': result['error'],
                    'details': 'Failed to create nurse account',
                    'request_data': {
                        'name': data.get('name'),
                        'email': data.get('email'),
                        'phone': data.get('phone')
                    }
                }), 400
                
        except Exception as e:
            print(f"Error creating nurse: {e}")
            return jsonify({
                'error': 'Server error',
                'details': str(e),
                'message': 'An unexpected error occurred while creating the nurse account'
            }), 500
    
    def get_nurses(self, request, current_user: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """Get list of nurses assigned to doctor"""
        try:
            # Validate role-based access
            if current_user.get('role') != 'doctor':
                return jsonify({'error': 'Only doctors can view nurse lists'}), 403
            
            # Get nurses assigned to the doctor
            result = self.nurse_model.list_nurses_by_doctor(current_user.get('user_id'))
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'nurses': result['nurses'],
                    'total_count': result['total_count']
                }), 200
            else:
                return jsonify({'error': result['error']}), 400
                
        except Exception as e:
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    def delete_nurse(self, request, current_user: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """Delete nurse by email (Doctor only)"""
        try:
            # Check if user is authenticated and is a doctor
            if not current_user or current_user.get('role') != 'doctor':
                return jsonify({
                    'error': 'Permission denied',
                    'details': 'Only doctors can delete nurses'
                }), 403

            data = request.get_json()
            if not data or not data.get('email'):
                return jsonify({
                    'error': 'Invalid request',
                    'details': 'Email is required'
                }), 400

            # Delete the nurse
            result = self.nurse_model.delete_by_email(
                data['email'], 
                current_user.get('doctor_id') or current_user.get('user_id')
            )

            if result['success']:
                return jsonify({
                    'success': True,
                    'message': result['message']
                }), 200
            else:
                return jsonify({
                    'error': result['error']
                }), 404

        except Exception as e:
            return jsonify({
                'error': 'Server error',
                'details': str(e)
            }), 500

    def reset_nurse_password(self, request, nurse_id: str, current_user: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """Reset nurse password (Doctor only)"""
        try:
            print(f"\n🔄 Starting password reset for nurse ID: {nurse_id}")
            
            # Validate role-based access
            if current_user.get('role') != 'doctor':
                return jsonify({
                    'error': 'Only doctors can reset nurse passwords',
                    'details': 'You must be logged in as a doctor to perform this action'
                }), 403
            
            # Get nurse details to verify existence
            nurse_details = self.nurse_model.get_nurse_by_id(nurse_id)
            if not nurse_details['success']:
                return jsonify({
                    'error': 'Nurse not found',
                    'details': 'Could not find a nurse with the provided ID'
                }), 404
            
            # Get new password from request (optional)
            new_password = None
            try:
                if request.is_json and request.get_json():
                    data = request.get_json()
                    new_password = data.get('new_password')
                    print("✅ New password provided in request")
            except Exception as e:
                print(f"ℹ️ No JSON data in request: {str(e)}")
                # Continue with auto-generated password
                pass
            
            # Reset password
            print("🔐 Resetting password...")
            result = self.nurse_model.reset_password(nurse_id, new_password)
            
            if result['success']:
                response = {
                    'success': True,
                    'message': 'Password reset successfully'
                }
                # Only include the new password if it was auto-generated
                if not new_password and 'new_password' in result:
                    response['new_password'] = result['new_password']
                    response['details'] = 'A new password has been generated'
                
                print("✅ Password reset successful")
                return jsonify(response), 200
            else:
                print(f"❌ Password reset failed: {result.get('error')}")
                return jsonify({'error': result['error']}), 400
                
        except Exception as e:
            return jsonify({'error': f'Server error: {str(e)}'}), 500