"""
Assignment Controller - Handles nurse-patient assignment operations
"""

from flask import jsonify
from typing import Dict, Any, Tuple
from models.assignment_model import AssignmentModel
from models.user_model import UserModel
from utils.validators import Validators


class AssignmentController:
    """Controller for nurse-patient assignments with role-based access"""
    
    def __init__(self, assignment_model: AssignmentModel = None, 
                 user_model: UserModel = None, validators: Validators = None):
        self.assignment_model = assignment_model or AssignmentModel()
        self.user_model = user_model or UserModel()
        self.validators = validators or Validators()
    
    def list_assignments(self, request, current_user: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """List assignments with role-based filtering"""
        try:
            current_role = current_user.get('role')
            nurse_id = None
            
            # Role-based filtering
            if current_role == 'nurse':
                nurse_id = current_user.get('user_id')
            
            # Get assignments
            result = self.assignment_model.list_assignments(nurse_id, active_only=True)
            
            if result['success']:
                # Enhance assignment data with user details
                assignments = result['assignments']
                for assignment in assignments:
                    # Add nurse details
                    nurse = self.user_model.find_by_id(assignment['nurse_id'])
                    if nurse:
                        assignment['nurse'] = {
                            'name': nurse['name'],
                            'email': nurse['email']
                        }
                    
                    # Add patient details
                    patient = self.user_model.find_by_id(assignment['patient_id'])
                    if patient:
                        assignment['patient'] = {
                            'name': patient['name'],
                            'email': patient['email']
                        }
                
                return jsonify({
                    'success': True,
                    'assignments': assignments,
                    'total_count': result['total_count']
                }), 200
            else:
                return jsonify({'error': result['error']}), 500
                
        except Exception as e:
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    def create_assignment(self, request, current_user: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """Create a new nurse-patient assignment"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['nurse_id', 'patient_id']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            # Validate user existence and roles
            nurse = self.user_model.find_by_id(data['nurse_id'])
            if not nurse or nurse['role'] != 'nurse':
                return jsonify({'error': 'Invalid nurse ID'}), 400
            
            patient = self.user_model.find_by_id(data['patient_id'])
            if not patient or patient['role'] != 'patient':
                return jsonify({'error': 'Invalid patient ID'}), 400
            
            # Create assignment
            result = self.assignment_model.create_assignment(
                data['nurse_id'],
                data['patient_id'],
                current_user.get('user_id')
            )
            
            if result['success']:
                # Add user details to response
                assignment = result['assignment']
                assignment['nurse'] = {
                    'name': nurse['name'],
                    'email': nurse['email']
                }
                assignment['patient'] = {
                    'name': patient['name'],
                    'email': patient['email']
                }
                
                return jsonify({
                    'success': True,
                    'message': 'Assignment created successfully',
                    'assignment': assignment
                }), 201
            else:
                return jsonify({'error': result['error']}), 400
                
        except Exception as e:
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    def end_assignment(self, request, assignment_id: str, current_user: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """End an active nurse-patient assignment"""
        try:
            # End assignment
            result = self.assignment_model.end_assignment(assignment_id)
            
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify({'error': result['error']}), 400
                
        except Exception as e:
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    def get_nurse_patients(self, request, nurse_id: str, current_user: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """Get patients assigned to a nurse"""
        try:
            current_role = current_user.get('role')
            
            # Role-based access control
            if current_role == 'nurse' and nurse_id != current_user.get('user_id'):
                return jsonify({'error': 'Cannot view other nurses\' patients'}), 403
            
            # Validate nurse
            nurse = self.user_model.find_by_id(nurse_id)
            if not nurse or nurse['role'] != 'nurse':
                return jsonify({'error': 'Invalid nurse ID'}), 400
            
            # Get patient IDs
            patient_ids = self.assignment_model.get_nurse_patients(nurse_id)
            
            # Get patient details
            patients = []
            for patient_id in patient_ids:
                patient = self.user_model.find_by_id(patient_id)
                if patient:
                    patients.append({
                        'user_id': patient['user_id'],
                        'name': patient['name'],
                        'email': patient['email']
                    })
            
            return jsonify({
                'success': True,
                'nurse': {
                    'user_id': nurse['user_id'],
                    'name': nurse['name'],
                    'email': nurse['email']
                },
                'patients': patients,
                'total_count': len(patients)
            }), 200
                
        except Exception as e:
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    def get_patient_nurse(self, request, patient_id: str, current_user: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """Get nurse assigned to a patient"""
        try:
            current_role = current_user.get('role')
            current_user_id = current_user.get('user_id')
            
            # Role-based access control
            if current_role == 'patient' and patient_id != current_user_id:
                return jsonify({'error': 'Cannot view other patients\' nurse'}), 403
            elif current_role == 'nurse':
                # Verify assignment
                is_assigned = self.assignment_model.is_patient_assigned_to_nurse(
                    current_user_id, patient_id
                )
                if not is_assigned:
                    return jsonify({'error': 'Patient not assigned to you'}), 403
            
            # Get assigned nurse ID
            nurse_id = self.assignment_model.get_patient_nurse(patient_id)
            if not nurse_id:
                return jsonify({
                    'success': True,
                    'message': 'No nurse currently assigned',
                    'nurse': None
                }), 200
            
            # Get nurse details
            nurse = self.user_model.find_by_id(nurse_id)
            if nurse:
                return jsonify({
                    'success': True,
                    'nurse': {
                        'user_id': nurse['user_id'],
                        'name': nurse['name'],
                        'email': nurse['email']
                    }
                }), 200
            else:
                return jsonify({'error': 'Assigned nurse not found'}), 500
                
        except Exception as e:
            return jsonify({'error': f'Server error: {str(e)}'}), 500