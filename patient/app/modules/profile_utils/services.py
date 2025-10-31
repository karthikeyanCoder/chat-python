"""
Profile Utilities Module Services - FUNCTION-BASED MVC
EXTRACTED FROM app_simple.py lines 5708-5827
Business logic for patient profile retrieval

NO CHANGES TO LOGIC - Exact extraction, converted to function-based
"""

from flask import jsonify
from app.core.database import db


def get_patient_profile_by_email_service(email):
    """Get patient profile by email - EXACT from line 5708"""
    try:
        patient = db.patients_collection.find_one({"email": email})
        if not patient:
            return jsonify({'success': False, 'message': 'Patient not found'}), 404
        
        profile_data = {
            'patient_id': patient.get('patient_id'),
            'username': patient.get('username'),
            'email': patient.get('email'),
            'pregnancy_week': patient.get('pregnancy_week'),
            # Add other fields as needed
        }
        
        return jsonify({
            'success': True,
            'profile': profile_data
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


def get_patient_profile_service(patient_id):
    """Get patient profile by patient ID - EXACT from line 5732"""
    try:
        print(f"[*] Getting patient profile for patient ID: {patient_id}")
        
        # Find patient by Patient ID (same as kick count storage)
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({
                'success': False,
                'message': f'Patient not found with ID: {patient_id}'
            }), 404
        
        # Check if patient is connected to a doctor
        is_connected_to_doctor = False
        try:
            from app.modules.invite.repository import InviteRepository
            repo = InviteRepository(db)
            patient_connections = repo.get_patient_connections(patient_id, "active")
            is_connected_to_doctor = len(patient_connections) > 0
        except Exception as e:
            print(f"[WARN] Could not check doctor connection status: {str(e)}")
            is_connected_to_doctor = False
        
        # Prepare profile data (complete structure with all fields)
        profile_data = {
            'patient_id': patient.get('patient_id'),
            'username': patient.get('username'),
            'email': patient.get('email'),
            'mobile': patient.get('mobile'),
            'first_name': patient.get('first_name'),
            'last_name': patient.get('last_name'),
            'age': patient.get('age'),
            'gender': patient.get('gender'),
            'blood_type': patient.get('blood_type'),
            'date_of_birth': patient.get('date_of_birth'),
            'height': patient.get('height'),
            'weight': patient.get('weight'),
            'is_pregnant': patient.get('is_pregnant'),
            'pregnancy_status': patient.get('pregnancy_status'),
            'pregnancy_week': patient.get('pregnancy_week'),
            'last_period_date': patient.get('last_period_date'),
            'expected_delivery_date': patient.get('expected_delivery_date'),
            'emergency_contact': patient.get('emergency_contact'),
            'emergency_contact_name': patient.get('emergency_contact_name'),
            'emergency_contact_phone': patient.get('emergency_contact_phone'),
            'emergency_contact_relationship': patient.get('emergency_contact_relationship'),
            'address': patient.get('address'),
            'city': patient.get('city'),
            'state': patient.get('state'),
            'zip_code': patient.get('zip_code'),
            'phone': patient.get('phone'),
            'medical_conditions': patient.get('medical_conditions', []),
            'allergies': patient.get('allergies', []),
            'medications': patient.get('medications', []),
            'status': patient.get('status'),
            'created_at': patient.get('created_at'),
            'last_updated': patient.get('last_updated'),
            'profile_completed_at': patient.get('profile_completed_at'),
            'email_verified': patient.get('email_verified'),
            'verified_at': patient.get('verified_at'),
            'password_updated_at': patient.get('password_updated_at'),
            'is_connected_to_doctor': is_connected_to_doctor,
        }
        
        print(f"[OK] Patient profile retrieved successfully for patient ID: {patient_id}")
        print(f"[*] Patient ID: {profile_data['patient_id']}")
        print(f"[*] Username: {profile_data['username']}")
        print(f"[*] Email: {profile_data['email']}")
        print(f"[*] First Name: {profile_data['first_name']}")
        print(f"[*] Last Name: {profile_data['last_name']}")
        print(f"[*] Blood Type: {profile_data['blood_type']}")
        print(f"[*] Height: {profile_data['height']}")
        print(f"[*] Weight: {profile_data['weight']}")
        print(f"[*] Pregnancy Status: {profile_data['pregnancy_status']}")
        print(f"[*] Pregnancy Week: {profile_data['pregnancy_week']}")
        print(f"[*] Expected Delivery: {profile_data['expected_delivery_date']}")
        print(f"[*] Emergency Contact: {profile_data['emergency_contact_name']}")
        print(f"[*] Is Connected to Doctor: {profile_data['is_connected_to_doctor']}")
        
        return jsonify({
            'success': True,
            'profile': profile_data
        }), 200
        
    except Exception as e:
        print(f"Error retrieving patient profile: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
