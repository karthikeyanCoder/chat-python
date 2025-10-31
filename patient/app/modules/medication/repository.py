"""
Medication Repository - Data Access Layer (Model)
Handles all database operations for medication module
"""

from app.core.database import db
from datetime import datetime


class MedicationRepository:
    """Data access layer for medication operations"""
    
    def __init__(self, db_instance):
        self.db = db_instance
        self.collection = db_instance.patients_collection
    
    def find_patient_by_id(self, patient_id):
        """Find patient by patient_id"""
        return self.collection.find_one({"patient_id": patient_id})
    
    def save_medication_log(self, patient_id, medication_log_entry):
        """Save medication log to patient"""
        result = self.collection.update_one(
            {"patient_id": patient_id},
            {
                "$push": {"medication_logs": medication_log_entry},
                "$set": {"last_updated": datetime.now()}
            }
        )
        return result.modified_count > 0
    
    def get_medication_logs(self, patient_id):
        """Get medication logs for patient"""
        patient = self.collection.find_one({"patient_id": patient_id})
        if patient:
            return patient.get('medication_logs', [])
        return []
    
    def save_tablet_tracking(self, patient_id, tablet_entry):
        """Save tablet tracking entry"""
        patient = self.collection.find_one({"patient_id": patient_id})
        if not patient:
            return False
        
        if 'tablet_tracking' not in patient:
            patient['tablet_tracking'] = []
        
        patient['tablet_tracking'].append(tablet_entry)
        
        result = self.collection.update_one(
            {"patient_id": patient_id},
            {"$set": {"tablet_tracking": patient['tablet_tracking']}}
        )
        return result.modified_count > 0
    
    def get_tablet_tracking(self, patient_id):
        """Get tablet tracking history"""
        patient = self.collection.find_one({"patient_id": patient_id})
        if patient:
            return patient.get('tablet_tracking', [])
        return []
    
    def save_prescription(self, patient_id, prescription_entry):
        """Save prescription to patient"""
        patient = self.collection.find_one({"patient_id": patient_id})
        if not patient:
            return False
        
        if 'prescriptions' not in patient:
            patient['prescriptions'] = []
        
        patient['prescriptions'].append(prescription_entry)
        
        result = self.collection.update_one(
            {"patient_id": patient_id},
            {"$set": {"prescriptions": patient['prescriptions']}}
        )
        return result.modified_count > 0
    
    def get_prescriptions(self, patient_id):
        """Get prescriptions for patient"""
        patient = self.collection.find_one({"patient_id": patient_id})
        if patient:
            return patient.get('prescriptions', [])
        return []
    
    def update_prescription_status(self, patient_id, prescription_id, new_status):
        """Update prescription status"""
        result = self.collection.update_one(
            {
                "patient_id": patient_id,
                "prescriptions._id": prescription_id
            },
            {
                "$set": {
                    "prescriptions.$.status": new_status,
                    "prescriptions.$.last_updated": datetime.now().isoformat()
                }
            }
        )
        return result.modified_count > 0
    
    def save_prescription_document(self, patient_id, prescription_data):
        """Save processed prescription document"""
        result = self.collection.update_one(
            {"patient_id": patient_id},
            {"$push": {"prescription_documents": prescription_data}},
            upsert=True
        )
        return result.modified_count > 0
    
    def save_tablet_daily_tracking(self, patient_id, tablet_entry):
        """Save daily tablet tracking entry"""
        patient = self.collection.find_one({"patient_id": patient_id})
        if not patient:
            return False
        
        if 'medication_daily_tracking' not in patient:
            patient['medication_daily_tracking'] = []
        
        patient['medication_daily_tracking'].append(tablet_entry)
        
        result = self.collection.update_one(
            {"patient_id": patient_id},
            {"$set": {"medication_daily_tracking": patient['medication_daily_tracking']}}
        )
        return result.modified_count > 0
    
    def get_tablet_daily_tracking(self, patient_id):
        """Get daily tablet tracking history"""
        patient = self.collection.find_one({"patient_id": patient_id})
        if patient:
            return patient.get('medication_daily_tracking', [])
        return []

