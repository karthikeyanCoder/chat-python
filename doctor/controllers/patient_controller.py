"""
Patient controller for handling patient-related operations
"""

from flask import request
from typing import Dict, Any, Tuple
import logging
from models.patient_model import PatientModel

logger = logging.getLogger(__name__)


class PatientController:
    """Controller for patient operations."""
    
    def __init__(self):
        from models.database import Database
        self.db = Database()
        self.db.connect()  # Ensure database connection
        self.patient_model = PatientModel(self.db)
    
    def create_patient(self, request) -> Tuple[Dict[str, Any], int]:
        """Create a new patient."""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['full_name', 'date_of_birth', 'contact_number', 'email']
            for field in required_fields:
                if not data.get(field):
                    return {'error': f'Missing required field: {field}'}, 400
            
            # Validate email format
            email = data.get('email', '')
            if '@' not in email or '.' not in email.split('@')[1]:
                return {'error': 'Invalid email format'}, 400
            
            # Validate contact number
            contact_number = data.get('contact_number', '')
            if len(contact_number) < 10:
                return {'error': 'Contact number must be at least 10 digits'}, 400
            
            # Check if patient already exists with same email
            existing_patients = self.patient_model.search_patients(email)
            if existing_patients:
                return {'error': 'Patient with this email already exists'}, 409
            
            # Prepare patient data
            patient_data = {
                'full_name': data.get('full_name', '').strip(),
                'date_of_birth': data.get('date_of_birth', '').strip(),
                'contact_number': data.get('contact_number', '').strip(),
                'email': data.get('email', '').strip().lower(),
                'gender': data.get('gender', '').strip(),
                'address': data.get('address', '').strip(),
                'city': data.get('city', '').strip(),
                'state': data.get('state', '').strip(),
                'pincode': data.get('pincode', '').strip(),
                'emergency_contact_name': data.get('emergency_contact_name', '').strip(),
                'emergency_contact_number': data.get('emergency_contact_number', '').strip(),
                'medical_notes': data.get('medical_notes', '').strip(),
                'allergies': data.get('allergies', '').strip(),
                'blood_type': data.get('blood_type', '').strip(),
                'assigned_doctor_id': data.get('assigned_doctor_id', ''),
                'is_active': True
            }
            
            # Create patient
            patient_id = self.patient_model.create_patient(patient_data)
            
            return {
                'message': 'Patient created successfully',
                'patient_id': patient_id,
                'status': 'success'
            }, 201
            
        except Exception as e:
            logger.error(f"Error creating patient: {str(e)}")
            return {'error': f'Failed to create patient: {str(e)}'}, 500
    
    def get_patient(self, request, patient_id: str) -> Tuple[Dict[str, Any], int]:
        """Get patient by ID."""
        try:
            patient = self.patient_model.get_patient(patient_id)
            
            if patient:
                return {'patient': patient}, 200
            else:
                return {'error': 'Patient not found'}, 404
                
        except Exception as e:
            logger.error(f"Error getting patient {patient_id}: {str(e)}")
            return {'error': f'Failed to get patient: {str(e)}'}, 500
    
    def get_all_patients(self, request) -> Tuple[Dict[str, Any], int]:
        """Get all patients with pagination."""
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 20))
            search = request.args.get('search', '')
            
            skip = (page - 1) * limit
            
            if search:
                patients = self.patient_model.search_patients(search)
            else:
                patients = self.patient_model.get_all_patients(limit=limit, skip=skip)
            
            return {
                'patients': patients,
                'total': len(patients),
                'page': page,
                'limit': limit
            }, 200
            
        except Exception as e:
            logger.error(f"Error getting all patients: {str(e)}")
            return {'error': f'Failed to get patients: {str(e)}'}, 500
    
    def update_patient(self, request, patient_id: str) -> Tuple[Dict[str, Any], int]:
        """Update patient."""
        try:
            data = request.get_json()
            
            if not data:
                return {'error': 'No data provided'}, 400
            
            # Validate email format if provided
            if 'email' in data and data['email']:
                email = data['email']
                if '@' not in email or '.' not in email.split('@')[1]:
                    return {'error': 'Invalid email format'}, 400
            
            # Validate contact number if provided
            if 'contact_number' in data and data['contact_number']:
                contact_number = data['contact_number']
                if len(contact_number) < 10:
                    return {'error': 'Contact number must be at least 10 digits'}, 400
            
            # Prepare update data
            update_data = {}
            allowed_fields = [
                'full_name', 'date_of_birth', 'contact_number', 'email', 'gender',
                'address', 'city', 'state', 'pincode', 'emergency_contact_name',
                'emergency_contact_number', 'medical_notes', 'allergies', 'blood_type',
                'assigned_doctor_id', 'is_active'
            ]
            
            for field in allowed_fields:
                if field in data:
                    update_data[field] = data[field].strip() if isinstance(data[field], str) else data[field]
            
            if not update_data:
                return {'error': 'No valid fields to update'}, 400
            
            # Update patient
            success = self.patient_model.update_patient(patient_id, update_data)
            
            if success:
                return {'message': 'Patient updated successfully'}, 200
            else:
                return {'error': 'Patient not found or no changes made'}, 404
                
        except Exception as e:
            logger.error(f"Error updating patient {patient_id}: {str(e)}")
            return {'error': f'Failed to update patient: {str(e)}'}, 500
    
    def delete_patient(self, request, patient_id: str) -> Tuple[Dict[str, Any], int]:
        """Delete patient."""
        try:
            success = self.patient_model.delete_patient(patient_id)
            
            if success:
                return {'message': 'Patient deleted successfully'}, 200
            else:
                return {'error': 'Patient not found'}, 404
                
        except Exception as e:
            logger.error(f"Error deleting patient {patient_id}: {str(e)}")
            return {'error': f'Failed to delete patient: {str(e)}'}, 500
    
    def get_patients_by_doctor(self, request, doctor_id: str) -> Tuple[Dict[str, Any], int]:
        """Get all patients assigned to a specific doctor."""
        try:
            patients = self.patient_model.get_patients_by_doctor(doctor_id)
            
            return {
                'patients': patients,
                'total': len(patients),
                'doctor_id': doctor_id
            }, 200
            
        except Exception as e:
            logger.error(f"Error getting patients by doctor {doctor_id}: {str(e)}")
            return {'error': f'Failed to get patients: {str(e)}'}, 500
    
    def get_patient(self, request, patient_id: str) -> Tuple[Dict[str, Any], int]:
        """Get patient by ID."""
        try:
            patient = self.patient_model.get_patient(patient_id)
            
            if patient:
                return {'patient': patient}, 200
            else:
                return {'error': 'Patient not found'}, 404
                
        except Exception as e:
            logger.error(f"Error getting patient {patient_id}: {str(e)}")
            return {'error': f'Failed to get patient: {str(e)}'}, 500
    
    def get_all_patients(self, request) -> Tuple[Dict[str, Any], int]:
        """Get all patients with pagination."""
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 20))
            search = request.args.get('search', '')
            
            skip = (page - 1) * limit
            
            if search:
                patients = self.patient_model.search_patients(search)
            else:
                patients = self.patient_model.get_all_patients(limit=limit, skip=skip)
            
            return {
                'patients': patients,
                'total': len(patients),
                'page': page,
                'limit': limit
            }, 200
            
        except Exception as e:
            logger.error(f"Error getting all patients: {str(e)}")
            return {'error': f'Failed to get patients: {str(e)}'}, 500
    
    def update_patient(self, request, patient_id: str) -> Tuple[Dict[str, Any], int]:
        """Update patient."""
        try:
            data = request.get_json()
            
            if not data:
                return {'error': 'No data provided'}, 400
            
            # Validate email format if provided
            if 'email' in data and data['email']:
                email = data['email']
                if '@' not in email or '.' not in email.split('@')[1]:
                    return {'error': 'Invalid email format'}, 400
            
            # Validate contact number if provided
            if 'contact_number' in data and data['contact_number']:
                contact_number = data['contact_number']
                if len(contact_number) < 10:
                    return {'error': 'Contact number must be at least 10 digits'}, 400
            
            # Prepare update data
            update_data = {}
            allowed_fields = [
                'full_name', 'date_of_birth', 'contact_number', 'email', 'gender',
                'address', 'city', 'state', 'pincode', 'emergency_contact_name',
                'emergency_contact_number', 'medical_notes', 'allergies', 'blood_type',
                'assigned_doctor_id', 'is_active'
            ]
            
            for field in allowed_fields:
                if field in data:
                    update_data[field] = data[field].strip() if isinstance(data[field], str) else data[field]
            
            if not update_data:
                return {'error': 'No valid fields to update'}, 400
            
            # Update patient
            success = self.patient_model.update_patient(patient_id, update_data)
            
            if success:
                return {'message': 'Patient updated successfully'}, 200
            else:
                return {'error': 'Patient not found or no changes made'}, 404
                
        except Exception as e:
            logger.error(f"Error updating patient {patient_id}: {str(e)}")
            return {'error': f'Failed to update patient: {str(e)}'}, 500
    
    def delete_patient(self, request, patient_id: str) -> Tuple[Dict[str, Any], int]:
        """Delete patient."""
        try:
            success = self.patient_model.delete_patient(patient_id)
            
            if success:
                return {'message': 'Patient deleted successfully'}, 200
            else:
                return {'error': 'Patient not found'}, 404
                
        except Exception as e:
            logger.error(f"Error deleting patient {patient_id}: {str(e)}")
            return {'error': f'Failed to delete patient: {str(e)}'}, 500
    
    def get_patients_by_doctor(self, request, doctor_id: str) -> Tuple[Dict[str, Any], int]:
        """Get all patients assigned to a specific doctor."""
        try:
            patients = self.patient_model.get_patients_by_doctor(doctor_id)
            
            return {
                'patients': patients,
                'total': len(patients),
                'doctor_id': doctor_id
            }, 200
            
        except Exception as e:
            logger.error(f"Error getting patients by doctor {doctor_id}: {str(e)}")
            return {'error': f'Failed to get patients: {str(e)}'}, 500
                
    
    def get_patient(self, request, patient_id: str) -> Tuple[Dict[str, Any], int]:
        """Get patient by ID."""
        try:
            patient = self.patient_model.get_patient(patient_id)
            
            if patient:
                return {'patient': patient}, 200
            else:
                return {'error': 'Patient not found'}, 404
                
        except Exception as e:
            logger.error(f"Error getting patient {patient_id}: {str(e)}")
            return {'error': f'Failed to get patient: {str(e)}'}, 500
    
    def get_all_patients(self, request) -> Tuple[Dict[str, Any], int]:
        """Get all patients with pagination."""
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 20))
            search = request.args.get('search', '')
            
            skip = (page - 1) * limit
            
            if search:
                patients = self.patient_model.search_patients(search)
            else:
                patients = self.patient_model.get_all_patients(limit=limit, skip=skip)
            
            return {
                'patients': patients,
                'total': len(patients),
                'page': page,
                'limit': limit
            }, 200
            
        except Exception as e:
            logger.error(f"Error getting all patients: {str(e)}")
            return {'error': f'Failed to get patients: {str(e)}'}, 500
    
    def update_patient(self, request, patient_id: str) -> Tuple[Dict[str, Any], int]:
        """Update patient."""
        try:
            data = request.get_json()
            
            if not data:
                return {'error': 'No data provided'}, 400
            
            # Validate email format if provided
            if 'email' in data and data['email']:
                email = data['email']
                if '@' not in email or '.' not in email.split('@')[1]:
                    return {'error': 'Invalid email format'}, 400
            
            # Validate contact number if provided
            if 'contact_number' in data and data['contact_number']:
                contact_number = data['contact_number']
                if len(contact_number) < 10:
                    return {'error': 'Contact number must be at least 10 digits'}, 400
            
            # Prepare update data
            update_data = {}
            allowed_fields = [
                'full_name', 'date_of_birth', 'contact_number', 'email', 'gender',
                'address', 'city', 'state', 'pincode', 'emergency_contact_name',
                'emergency_contact_number', 'medical_notes', 'allergies', 'blood_type',
                'assigned_doctor_id', 'is_active'
            ]
            
            for field in allowed_fields:
                if field in data:
                    update_data[field] = data[field].strip() if isinstance(data[field], str) else data[field]
            
            if not update_data:
                return {'error': 'No valid fields to update'}, 400
            
            # Update patient
            success = self.patient_model.update_patient(patient_id, update_data)
            
            if success:
                return {'message': 'Patient updated successfully'}, 200
            else:
                return {'error': 'Patient not found or no changes made'}, 404
                
        except Exception as e:
            logger.error(f"Error updating patient {patient_id}: {str(e)}")
            return {'error': f'Failed to update patient: {str(e)}'}, 500
    
    def delete_patient(self, request, patient_id: str) -> Tuple[Dict[str, Any], int]:
        """Delete patient."""
        try:
            success = self.patient_model.delete_patient(patient_id)
            
            if success:
                return {'message': 'Patient deleted successfully'}, 200
            else:
                return {'error': 'Patient not found'}, 404
                
        except Exception as e:
            logger.error(f"Error deleting patient {patient_id}: {str(e)}")
            return {'error': f'Failed to delete patient: {str(e)}'}, 500
    
    def get_patients_by_doctor(self, request, doctor_id: str) -> Tuple[Dict[str, Any], int]:
        """Get all patients assigned to a specific doctor."""
        try:
            patients = self.patient_model.get_patients_by_doctor(doctor_id)
            
            return {
                'patients': patients,
                'total': len(patients),
                'doctor_id': doctor_id
            }, 200
            
        except Exception as e:
            logger.error(f"Error getting patients by doctor {doctor_id}: {str(e)}")
            return {'error': f'Failed to get patients: {str(e)}'}, 500