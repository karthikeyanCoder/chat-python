"""
Patient model for CRUD operations
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from bson import ObjectId
import logging
import sys
import os

# Add the parent directory to the path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.objectid_converter import convert_objectid_to_string

logger = logging.getLogger(__name__)


class PatientModel:
    """Model for patient CRUD operations."""
    
    def __init__(self, db):
        self.db = db
        self.collection_name = "Patient_test"
        self.collection = None
    
    def _ensure_collection(self):
        """Ensure the patients collection exists."""
        try:
            # Ensure database connection is established
            if self.db.db is None:
                self.db.connect()
            
            if self.db and hasattr(self.db, 'db') and self.db.db is not None:
                self.collection = self.db.db[self.collection_name]
                logger.info(f"✅ Patient collection '{self.collection_name}' initialized")
            else:
                logger.error("Database connection not available")
                self.collection = None
        except Exception as e:
            logger.error(f"Error ensuring collection: {str(e)}")
            self.collection = None
    
    def create_patient(self, patient_data: Dict[str, Any]) -> str:
        """Create a new patient."""
        try:
            self._ensure_collection()
            if self.collection is None:
                raise Exception("Database collection not available")
            
            # Add timestamps
            patient_data['created_at'] = datetime.now()
            patient_data['updated_at'] = datetime.now()
            
            # Generate patient ID
            patient_id = f"PAT{int(datetime.now().timestamp())}{hash(patient_data.get('email', '')) % 10000:04d}"
            patient_data['patient_id'] = patient_id
            
            # Insert patient
            result = self.collection.insert_one(patient_data)
            
            if result.inserted_id:
                logger.info(f"Created patient: {patient_id}")
                return str(result.inserted_id)
            else:
                raise Exception("Failed to create patient")
                
        except Exception as e:
            logger.error(f"Error creating patient: {str(e)}")
            raise
    
    def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Get patient by ID."""
        try:
            self._ensure_collection()
            if self.collection is None:
                raise Exception("Database collection not available")
            
            # Try to find by patient_id first, then by ObjectId
            patient = self.collection.find_one({"patient_id": patient_id})
            if not patient:
                try:
                    patient = self.collection.find_one({"_id": ObjectId(patient_id)})
                except:
                    pass
            
            if patient:
                # Convert all ObjectIds to strings recursively
                return convert_objectid_to_string(patient)
            return None
            
        except Exception as e:
            logger.error(f"Error getting patient {patient_id}: {str(e)}")
            return None
    
    def get_all_patients(self, limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        """Get all patients with pagination."""
        try:
            self._ensure_collection()
            if self.collection is None:
                raise Exception("Database collection not available")
            
            patients = list(self.collection.find().skip(skip).limit(limit).sort("created_at", -1))
            
            # Convert all ObjectIds to strings recursively for each patient
            return [convert_objectid_to_string(patient) for patient in patients]
                
        except Exception as e:
            logger.error(f"Error getting all patients: {str(e)}")
            return []
    
    def update_patient(self, patient_id: str, update_data: Dict[str, Any]) -> bool:
        """Update patient."""
        try:
            self._ensure_collection()
            if self.collection is None:
                raise Exception("Database collection not available")
            
            # Add update timestamp
            update_data['updated_at'] = datetime.now()
            
            # Try to find by patient_id first, then by ObjectId
            query = {"patient_id": patient_id}
            patient = self.collection.find_one(query)
            
            if not patient:
                try:
                    query = {"_id": ObjectId(patient_id)}
                    patient = self.collection.find_one(query)
                except:
                    pass
            
            if patient:
                result = self.collection.update_one(query, {"$set": update_data})
                if result.modified_count > 0:
                    logger.info(f"Updated patient: {patient_id}")
                    return True
                else:
                    logger.warning(f"No changes made to patient: {patient_id}")
                    return False
            else:
                logger.error(f"Patient not found: {patient_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating patient {patient_id}: {str(e)}")
            return False
    
    def delete_patient(self, patient_id: str) -> bool:
        """Delete patient."""
        try:
            self._ensure_collection()
            if self.collection is None:
                raise Exception("Database collection not available")
            
            # Try to find by patient_id first, then by ObjectId
            query = {"patient_id": patient_id}
            patient = self.collection.find_one(query)
            
            if not patient:
                try:
                    query = {"_id": ObjectId(patient_id)}
                    patient = self.collection.find_one(query)
                except:
                    pass
            
            if patient:
                result = self.collection.delete_one(query)
                if result.deleted_count > 0:
                    logger.info(f"Deleted patient: {patient_id}")
                    return True
                else:
                    logger.warning(f"Failed to delete patient: {patient_id}")
                    return False
            else:
                logger.error(f"Patient not found: {patient_id}")
            return False
    
        except Exception as e:
            logger.error(f"Error deleting patient {patient_id}: {str(e)}")
            return False
    
    def search_patients(self, search_term: str) -> List[Dict[str, Any]]:
        """Search patients by name, email, or patient_id."""
        try:
            self._ensure_collection()
            if self.collection is None:
                raise Exception("Database collection not available")
            
            # Create search query
            query = {
                "$or": [
                    {"full_name": {"$regex": search_term, "$options": "i"}},
                    {"email": {"$regex": search_term, "$options": "i"}},
                    {"patient_id": {"$regex": search_term, "$options": "i"}},
                    {"contact_number": {"$regex": search_term, "$options": "i"}}
                ]
            }
            
            patients = list(self.collection.find(query).sort("created_at", -1))
            
            # Convert all ObjectIds to strings recursively for each patient
            return [convert_objectid_to_string(patient) for patient in patients]
            
        except Exception as e:
            logger.error(f"Error searching patients: {str(e)}")
            return []
    
    def get_patients_by_doctor(self, doctor_id: str) -> List[Dict[str, Any]]:
        """Get all patients assigned to a specific doctor."""
        try:
            self._ensure_collection()
            if self.collection is None:
                raise Exception("Database collection not available")
            
            patients = list(self.collection.find({"assigned_doctor_id": doctor_id}).sort("created_at", -1))
            
            # Convert all ObjectIds to strings recursively for each patient
            return [convert_objectid_to_string(patient) for patient in patients]
            
        except Exception as e:
            logger.error(f"Error getting patients by doctor {doctor_id}: {str(e)}")
            return []