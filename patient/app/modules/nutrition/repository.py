"""
Nutrition Repository - Data Access Layer (Model)
Handles all database operations for nutrition module
"""

from app.core.database import db


class NutritionRepository:
    """Data access layer for nutrition operations"""
    
    def __init__(self, db_instance):
        self.db = db_instance
        self.collection = db_instance.patients_collection
    
    def find_patient_by_id(self, patient_id):
        """Find patient by patient_id"""
        return self.collection.find_one({"patient_id": patient_id})
    
    def save_food_entry(self, patient_id, food_entry):
        """Save food entry to patient's food_data"""
        # Get patient first to maintain array properly
        patient = self.collection.find_one({"patient_id": patient_id})
        if not patient:
            return False
        
        if 'food_data' not in patient:
            patient['food_data'] = []
        
        patient['food_data'].append(food_entry)
        
        result = self.collection.update_one(
            {"patient_id": patient_id},
            {"$set": {"food_data": patient['food_data']}}
        )
        return result.modified_count > 0
    
    def get_food_entries(self, patient_id):
        """Get food entries for patient"""
        patient = self.collection.find_one({"patient_id": patient_id})
        if patient:
            return patient.get('food_data', [])
        return []

