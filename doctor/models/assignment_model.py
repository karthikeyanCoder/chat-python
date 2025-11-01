"""
Assignment Model - Manages nurse-patient assignments
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from bson import ObjectId
from models.database import Database


class AssignmentModel:
    """Manages nurse-patient assignments in MongoDB"""
    
    def __init__(self, db: Database = None):
        if db is None:
            self.db = Database()
            self.db.connect()
        else:
            self.db = db
        
        # Check if database connection is valid
        is_connected = getattr(self.db, 'is_connected', False)
        if self.db is not None and self.db.db is not None and is_connected:
            self.assignments_collection = self.db.db.nurse_patient_assignments
        else:
            self.assignments_collection = None
            print("⚠️ Warning: Database not connected. AssignmentModel operating in fallback mode.")
    
    def _convert_to_dict(self, assignment_doc) -> Dict[str, Any]:
        """Convert MongoDB document to dictionary"""
        if not assignment_doc:
            return None
        
        assignment_dict = {
            'assignment_id': str(assignment_doc['_id']),
            'nurse_id': str(assignment_doc['nurse_id']),
            'patient_id': str(assignment_doc['patient_id']),
            'assigned_at': assignment_doc.get('assigned_at', ''),
            'assigned_by': str(assignment_doc.get('assigned_by', '')),
            'is_active': assignment_doc.get('is_active', True)
        }
        return assignment_dict
    
    def create_assignment(self, nurse_id: str, patient_id: str, assigned_by: str) -> Dict[str, Any]:
        """Create a new nurse-patient assignment"""
        try:
            # Validate IDs
            if not all(ObjectId.is_valid(id_) for id_ in [nurse_id, patient_id, assigned_by]):
                return {'success': False, 'error': 'Invalid ID format'}
            
            # Check for existing active assignment
            existing = self.assignments_collection.find_one({
                'patient_id': ObjectId(patient_id),
                'is_active': True
            })
            
            if existing:
                return {'success': False, 'error': 'Patient already has an active nurse assignment'}
            
            # Create assignment
            assignment_doc = {
                'nurse_id': ObjectId(nurse_id),
                'patient_id': ObjectId(patient_id),
                'assigned_by': ObjectId(assigned_by),
                'assigned_at': datetime.now().isoformat(),
                'is_active': True
            }
            
            result = self.assignments_collection.insert_one(assignment_doc)
            
            if result.inserted_id:
                return {
                    'success': True,
                    'assignment': self._convert_to_dict(
                        self.assignments_collection.find_one({'_id': result.inserted_id})
                    ),
                    'message': 'Assignment created successfully'
                }
            else:
                return {'success': False, 'error': 'Failed to create assignment'}
                
        except Exception as e:
            return {'success': False, 'error': f'Database error: {str(e)}'}
    
    def end_assignment(self, assignment_id: str) -> Dict[str, Any]:
        """End an active assignment"""
        try:
            if not ObjectId.is_valid(assignment_id):
                return {'success': False, 'error': 'Invalid assignment ID'}
            
            result = self.assignments_collection.update_one(
                {'_id': ObjectId(assignment_id), 'is_active': True},
                {'$set': {'is_active': False}}
            )
            
            if result.modified_count > 0:
                return {
                    'success': True,
                    'message': 'Assignment ended successfully'
                }
            else:
                return {'success': False, 'error': 'No active assignment found'}
                
        except Exception as e:
            return {'success': False, 'error': f'Database error: {str(e)}'}
    
    def is_patient_assigned_to_nurse(self, nurse_id: str, patient_id: str) -> bool:
        """Check if a patient is assigned to a nurse"""
        try:
            if not all(ObjectId.is_valid(id_) for id_ in [nurse_id, patient_id]):
                return False
            
            assignment = self.assignments_collection.find_one({
                'nurse_id': ObjectId(nurse_id),
                'patient_id': ObjectId(patient_id),
                'is_active': True
            })
            
            return assignment is not None
            
        except Exception:
            return False
    
    def get_nurse_patients(self, nurse_id: str) -> List[str]:
        """Get list of patient IDs assigned to a nurse"""
        try:
            if not ObjectId.is_valid(nurse_id):
                return []
            
            assignments = self.assignments_collection.find({
                'nurse_id': ObjectId(nurse_id),
                'is_active': True
            })
            
            return [str(a['patient_id']) for a in assignments]
            
        except Exception:
            return []
    
    def get_patient_nurse(self, patient_id: str) -> Optional[str]:
        """Get nurse ID assigned to a patient"""
        try:
            if not ObjectId.is_valid(patient_id):
                return None
            
            assignment = self.assignments_collection.find_one({
                'patient_id': ObjectId(patient_id),
                'is_active': True
            })
            
            return str(assignment['nurse_id']) if assignment else None
            
        except Exception:
            return None
    
    def list_assignments(self, nurse_id: str = None, active_only: bool = True) -> Dict[str, Any]:
        """List assignments with optional filtering"""
        try:
            # Build query filter
            query_filter = {}
            
            if active_only:
                query_filter['is_active'] = True
            
            if nurse_id:
                if not ObjectId.is_valid(nurse_id):
                    return {'success': False, 'error': 'Invalid nurse ID'}
                query_filter['nurse_id'] = ObjectId(nurse_id)
            
            # Get assignments
            assignments = []
            cursor = self.assignments_collection.find(query_filter)
            
            for doc in cursor:
                assignments.append(self._convert_to_dict(doc))
            
            return {
                'success': True,
                'assignments': assignments,
                'total_count': len(assignments)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Database error: {str(e)}'}