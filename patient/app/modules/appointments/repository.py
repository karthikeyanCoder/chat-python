"""
Appointments Repository - Data Access Layer (Model)
Handles all database operations for appointments module
"""

from app.core.database import db
from datetime import datetime


class AppointmentsRepository:
    """Data access layer for appointments operations"""
    
    def __init__(self, db_instance):
        self.db = db_instance
        self.collection = db_instance.patients_collection
    
    def find_patient_by_id(self, patient_id):
        """Find patient by patient_id"""
        return self.collection.find_one({"patient_id": patient_id})
    
    def find_patient_with_appointment(self, appointment_id):
        """Find patient with specific appointment"""
        return self.collection.find_one({
            "appointments.appointment_id": appointment_id
        })
    
    def get_patient_appointments(self, patient_id):
        """Get all appointments for patient"""
        patient = self.collection.find_one({"patient_id": patient_id})
        if patient:
            return patient.get('appointments', [])
        return []
    
    def create_appointment(self, patient_id, appointment):
        """Create new appointment for patient"""
        result = self.collection.update_one(
            {"patient_id": patient_id},
            {"$push": {"appointments": appointment}}
        )
        return result.modified_count > 0
    
    def update_appointment_by_index(self, patient_id, appointment_index, update_fields):
        """Update appointment at specific index"""
        result = self.collection.update_one(
            {"patient_id": patient_id},
            {"$set": update_fields}
        )
        return result.modified_count > 0
    
    def update_appointment_by_id(self, appointment_id, update_fields):
        """Update appointment by appointment_id using positional operator"""
        result = self.collection.update_one(
            {"appointments.appointment_id": appointment_id},
            {"$set": update_fields}
        )
        return result.modified_count > 0
    
    def delete_appointment(self, patient_id, appointment_id):
        """Delete appointment from patient"""
        result = self.collection.update_one(
            {"patient_id": patient_id},
            {"$pull": {"appointments": {"appointment_id": appointment_id}}}
        )
        return result.modified_count > 0
    
    def get_all_appointments(self, query_filter=None):
        """Get all appointments across all patients"""
        if query_filter is None:
            query_filter = {}
        
        patients = self.collection.find(query_filter)
        all_appointments = []
        
        for patient in patients:
            appointments = patient.get('appointments', [])
            for appointment in appointments:
                appointment['patient_id'] = patient.get('patient_id')
                appointment['patient_name'] = f"{patient.get('first_name', '')} {patient.get('last_name', '')}".strip() or patient.get('username', 'Unknown')
                appointment['patient_email'] = patient.get('email', '')
                appointment['patient_mobile'] = patient.get('mobile', '')
                all_appointments.append(appointment)
        
        return all_appointments
    
    def get_pending_appointments(self):
        """Get all pending appointments"""
        patients = self.collection.find({
            "appointments.appointment_status": "pending"
        })
        
        pending = []
        for patient in patients:
            for appointment in patient.get('appointments', []):
                if appointment.get('appointment_status') == 'pending':
                    appointment['patient_id'] = patient.get('patient_id')
                    appointment['patient_name'] = f"{patient.get('first_name', '')} {patient.get('last_name', '')}".strip()
                    appointment['patient_email'] = patient.get('email', '')
                    appointment['patient_mobile'] = patient.get('mobile', '')
                    pending.append(appointment)
        
        return pending

