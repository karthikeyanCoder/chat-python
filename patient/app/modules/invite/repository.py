"""
Invite Repository - Data Access Layer
Handles doctor-patient invites and connections
EXTRACTED FROM patient_service/ - ZERO BACKEND LOGIC CHANGES
"""
from datetime import datetime, timedelta
from app.core.database import db
import secrets
import string
import hashlib
import os


class InviteRepository:
    """Data access layer for invite and connection operations"""
    
    def __init__(self, db_instance):
        self.db = db_instance
        self.patients_collection = db_instance.patients_collection
        self.doctors_collection = db_instance.doctor_v2_collection
        
        # Get or create collections
        db_name = os.getenv("DB_NAME", "patients_db")
        self.invite_codes_collection = self.db.client[db_name]["invite_codes"]
        self.connections_collection = self.db.client[db_name]["connections"]
    
    # ========== INVITE CODE METHODS ==========
    
    def create_invite_code(self, doctor_id, patient_email, doctor_info, expires_in_days=7):
        """Create specific invite code for a patient"""
        invite_code = self._generate_invite_code()
        invite_hash = self._hash_code(invite_code)
        
        invite_data = {
            "invite_code": invite_code,
            "invite_code_hash": invite_hash,
            "doctor_id": doctor_id,
            "doctor_info": doctor_info,
            "patient_email": patient_email,
            "usage_limit": 1,
            "usage_count": 0,
            "status": "active",
            "expires_at": datetime.utcnow() + timedelta(days=expires_in_days),
            "security": {
                "max_attempts": 5,
                "attempts_count": 0,
                "last_attempt_at": None
            },
            "metadata": {
                "sent_via": "email",
                "sent_at": None
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = self.invite_codes_collection.insert_one(invite_data)
        invite_data['_id'] = str(result.inserted_id)
        return invite_data
    
    def find_invite_by_code(self, invite_code):
        """Find invite by code"""
        return self.invite_codes_collection.find_one({"invite_code": invite_code})
    
    def validate_invite_code(self, invite_code, patient_email):
        """Validate invite code - returns (is_valid, message, invite_data)"""
        invite = self.find_invite_by_code(invite_code)
        
        if not invite:
            self._increment_invite_attempts(invite_code)
            return False, "Invalid invite code", None
        
        if invite['status'] != 'active':
            return False, "Invite code is not active", None
        
        if datetime.utcnow() > invite['expires_at']:
            self.invite_codes_collection.update_one(
                {"invite_code": invite_code},
                {"$set": {"status": "expired", "updated_at": datetime.utcnow()}}
            )
            return False, "Invite code has expired", None
        
        if invite['usage_count'] >= invite['usage_limit']:
            return False, "Invite code has been used", None
        
        if patient_email and invite['patient_email'] != patient_email:
            return False, "This invite is for a different email address", None
        
        if invite['security']['attempts_count'] >= invite['security']['max_attempts']:
            self.invite_codes_collection.update_one(
                {"invite_code": invite_code},
                {"$set": {"status": "locked", "updated_at": datetime.utcnow()}}
            )
            return False, "Invite code locked due to too many attempts", None
        
        return True, "Valid invite code", invite
    
    def mark_invite_as_used(self, invite_code):
        """Mark invite code as used"""
        result = self.invite_codes_collection.update_one(
            {"invite_code": invite_code},
            {
                "$inc": {"usage_count": 1},
                "$set": {"status": "used", "updated_at": datetime.utcnow()}
            }
        )
        return result.modified_count > 0
    
    def validate_invite_code_format(self, invite_code):
        """Validate invite code format: ABC-XYZ-123"""
        import re
        return re.match(r'^[A-Z0-9]{3}-[A-Z0-9]{3}-[A-Z0-9]{3}$', invite_code) is not None
    
    def _increment_invite_attempts(self, invite_code):
        """Increment failed attempts counter"""
        self.invite_codes_collection.update_one(
            {"invite_code": invite_code},
            {
                "$inc": {"security.attempts_count": 1},
                "$set": {"security.last_attempt_at": datetime.utcnow()}
            }
        )
    
    @staticmethod
    def _generate_invite_code():
        """Generate invite code format: ABC-XYZ-123"""
        chars = string.ascii_uppercase + string.digits
        parts = []
        for _ in range(3):
            part = ''.join(secrets.choice(chars) for _ in range(3))
            parts.append(part)
        return '-'.join(parts)
    
    @staticmethod
    def _hash_code(code):
        """Hash invite code for security"""
        return hashlib.sha256(code.encode()).hexdigest()
    
    # ========== CONNECTION METHODS ==========
    
    def create_connection(self, doctor_id, patient_id, invited_by, 
                         invite_code=None, request_message=None, connection_type="primary"):
        """Create a new connection"""
        connection_id = self._generate_connection_id()
        status = "active" if invited_by == "doctor" else "pending"
        
        connection_data = {
            "connection_id": connection_id,
            "doctor_id": doctor_id,
            "patient_id": patient_id,
            "status": status,
            "invited_by": invited_by,
            "invite_code": invite_code,
            "connection_type": connection_type,
            "request_message": request_message,
            "response_message": None,
            "dates": {
                "invite_sent_at": datetime.utcnow() if invited_by == "doctor" else None,
                "request_sent_at": datetime.utcnow() if invited_by == "patient" else None,
                "connected_at": datetime.utcnow() if invited_by == "doctor" else None,
                "rejected_at": None,
                "removed_at": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            "removal_info": None,
            "statistics": {
                "total_appointments": 0,
                "completed_appointments": 0,
                "cancelled_appointments": 0,
                "last_appointment_date": None,
                "next_appointment_date": None
            },
            "permissions": {
                "can_view_medical_records": True,
                "can_book_appointments": True,
                "can_send_messages": True,
                "can_view_prescriptions": True
            },
            "audit_log": [
                {
                    "action": "connection_created",
                    "actor_id": doctor_id if invited_by == "doctor" else patient_id,
                    "actor_type": invited_by,
                    "timestamp": datetime.utcnow(),
                    "details": {}
                }
            ]
        }
        
        result = self.connections_collection.insert_one(connection_data)
        connection_data['_id'] = str(result.inserted_id)
        return connection_data
    
    def find_connection(self, doctor_id, patient_id):
        """Find connection between doctor and patient"""
        return self.connections_collection.find_one({
            "doctor_id": doctor_id,
            "patient_id": patient_id,
            "status": {"$in": ["active", "pending"]}
        })
    
    def find_connection_by_id(self, connection_id):
        """Find connection by connection_id"""
        return self.connections_collection.find_one({"connection_id": connection_id})
    
    def get_patient_connections(self, patient_id, status="active"):
        """Get all connections for a patient"""
        query = {"patient_id": patient_id}
        if status != "all":
            query["status"] = status
        return list(self.connections_collection.find(query).limit(100))
    
    def connection_exists(self, doctor_id, patient_id):
        """Check if active or pending connection exists"""
        return self.connections_collection.count_documents({
            "doctor_id": doctor_id,
            "patient_id": patient_id,
            "status": {"$in": ["active", "pending"]}
        }, limit=1) > 0
    
    def remove_connection(self, connection_id, removed_by, removed_by_type, reason=None):
        """Remove/disconnect a connection"""
        result = self.connections_collection.update_one(
            {"connection_id": connection_id},
            {
                "$set": {
                    "status": "removed",
                    "dates.removed_at": datetime.utcnow(),
                    "dates.updated_at": datetime.utcnow(),
                    "removal_info": {
                        "removed_by": removed_by,
                        "removed_by_type": removed_by_type,
                        "reason": reason,
                        "removed_at": datetime.utcnow()
                    }
                },
                "$push": {
                    "audit_log": {
                        "action": "connection_removed",
                        "actor_id": removed_by,
                        "actor_type": removed_by_type,
                        "timestamp": datetime.utcnow(),
                        "details": {"reason": reason}
                    }
                }
            }
        )
        return result.modified_count > 0
    
    def cancel_request(self, connection_id, cancelled_by, cancelled_by_type, reason=None):
        """Cancel a pending connection request"""
        result = self.connections_collection.update_one(
            {"connection_id": connection_id, "status": "pending"},
            {
                "$set": {
                    "status": "cancelled",
                    "dates.cancelled_at": datetime.utcnow(),
                    "dates.updated_at": datetime.utcnow(),
                    "cancellation_info": {
                        "cancelled_by": cancelled_by,
                        "cancelled_by_type": cancelled_by_type,
                        "reason": reason,
                        "cancelled_at": datetime.utcnow()
                    }
                },
                "$push": {
                    "audit_log": {
                        "action": "request_cancelled",
                        "actor_id": cancelled_by,
                        "actor_type": cancelled_by_type,
                        "timestamp": datetime.utcnow(),
                        "details": {"reason": reason}
                    }
                }
            }
        )
        return result.modified_count > 0
    
    @staticmethod
    def _generate_connection_id():
        """Generate unique connection ID"""
        timestamp = int(datetime.utcnow().timestamp() * 1000)
        random_suffix = ''.join(secrets.choice(string.digits) for _ in range(3))
        return f"CONN{timestamp}{random_suffix}"
    
    # ========== DOCTOR METHODS ==========
    
    def find_doctor_by_id(self, doctor_id):
        """Find doctor by doctor_id from doctor_v2 collection"""
        if self.doctors_collection is None:
            return None
        return self.doctors_collection.find_one({"doctor_id": doctor_id})
    
    def find_doctor_by_email(self, email):
        """Find doctor by email address"""
        if self.doctors_collection is None:
            return None
        
        # Search in both flat and nested email fields
        doctor = self.doctors_collection.find_one({
            "$or": [
                {"email": email},
                {"personal_info.email": email}
            ]
        })
        return doctor
    
    def search_doctors(self, query=None, specialty=None, city=None, limit=20):
        """Search doctors by various criteria"""
        if self.doctors_collection is None:
            return []
        
        search_query = {}
        
        # Support both flat and nested structures
        if specialty:
            search_query["$or"] = [
                {"specialty": specialty},
                {"professional_info.specialty": specialty}
            ]
        
        if city:
            # Try both flat location and nested workplace_info
            city_query = {"$or": [
                {"location": {"$regex": city, "$options": "i"}},
                {"workplace_info.hospital_address.city": city}
            ]}
            if search_query:
                search_query = {"$and": [search_query, city_query]}
            else:
                search_query = city_query
        
        if query:
            query_search = {"$or": [
                {"name": {"$regex": query, "$options": "i"}},
                {"personal_info.full_name": {"$regex": query, "$options": "i"}},
                {"location": {"$regex": query, "$options": "i"}},
                {"workplace_info.hospital_name": {"$regex": query, "$options": "i"}},
                {"specialty": {"$regex": query, "$options": "i"}},
                {"professional_info.specialty": {"$regex": query, "$options": "i"}}
            ]}
            if search_query:
                search_query = {"$and": [search_query, query_search]}
            else:
                search_query = query_search
        
        return list(self.doctors_collection.find(search_query).limit(limit))
    
    def increment_doctor_patient_count(self, doctor_id):
        """Increment doctor's patient count"""
        if self.doctors_collection is None:
            return False
        # Support both flat and nested statistics structures
        result = self.doctors_collection.update_one(
            {"doctor_id": doctor_id},
            {
                "$inc": {
                    "statistics.total_patients": 1,
                    "statistics.active_patients": 1,
                    "total_patients": 1,  # Flat structure support
                    "active_patients": 1   # Flat structure support
                }
            }
        )
        return result.modified_count > 0
    
    def decrement_doctor_patient_count(self, doctor_id):
        """Decrement doctor's active patient count"""
        if self.doctors_collection is None:
            return False
        # Support both flat and nested statistics structures
        result = self.doctors_collection.update_one(
            {"doctor_id": doctor_id},
            {
                "$inc": {
                    "statistics.active_patients": -1,
                    "active_patients": -1  # Flat structure support
                }
            }
        )
        return result.modified_count > 0
    
    def get_patient_pending_invites(self, patient_id):
        """Get pending invites for patient from doctors"""
        return list(self.connections_collection.find({
            "patient_id": patient_id,
            "invited_by": "doctor",
            "status": "pending"
        }))
    
    def get_patient_invite_details(self, invite_id, patient_id):
        """Get details of a specific doctor invite for patient"""
        return self.connections_collection.find_one({
            "connection_id": invite_id,
            "patient_id": patient_id,
            "invited_by": "doctor"
        })




    

    def get_patient_connections(self, patient_id, status="active"):

        """Get all connections for a patient"""

        query = {"patient_id": patient_id}

        if status != "all":

            query["status"] = status

        return list(self.connections_collection.find(query).limit(100))

    

    def connection_exists(self, doctor_id, patient_id):

        """Check if active or pending connection exists"""

        return self.connections_collection.count_documents({

            "doctor_id": doctor_id,

            "patient_id": patient_id,

            "status": {"$in": ["active", "pending"]}

        }, limit=1) > 0

    

    def remove_connection(self, connection_id, removed_by, removed_by_type, reason=None):

        """Remove/disconnect a connection"""

        result = self.connections_collection.update_one(

            {"connection_id": connection_id},

            {

                "$set": {

                    "status": "removed",

                    "dates.removed_at": datetime.utcnow(),

                    "dates.updated_at": datetime.utcnow(),

                    "removal_info": {

                        "removed_by": removed_by,

                        "removed_by_type": removed_by_type,

                        "reason": reason,

                        "removed_at": datetime.utcnow()

                    }

                },

                "$push": {

                    "audit_log": {

                        "action": "connection_removed",

                        "actor_id": removed_by,

                        "actor_type": removed_by_type,

                        "timestamp": datetime.utcnow(),

                        "details": {"reason": reason}

                    }

                }

            }

        )

        return result.modified_count > 0

    

    def cancel_request(self, connection_id, cancelled_by, cancelled_by_type, reason=None):
        """Cancel a pending connection request"""
        result = self.connections_collection.update_one(
            {"connection_id": connection_id, "status": "pending"},
            {
                "$set": {
                    "status": "cancelled",
                    "dates.cancelled_at": datetime.utcnow(),
                    "dates.updated_at": datetime.utcnow(),
                    "cancellation_info": {
                        "cancelled_by": cancelled_by,
                        "cancelled_by_type": cancelled_by_type,
                        "reason": reason,
                        "cancelled_at": datetime.utcnow()
                    }
                },
                "$push": {
                    "audit_log": {
                        "action": "request_cancelled",
                        "actor_id": cancelled_by,
                        "actor_type": cancelled_by_type,
                        "timestamp": datetime.utcnow(),
                        "details": {"reason": reason}
                    }
                }
            }
        )
        return result.modified_count > 0
    
    @staticmethod

    def _generate_connection_id():

        """Generate unique connection ID"""

        timestamp = int(datetime.utcnow().timestamp() * 1000)

        random_suffix = ''.join(secrets.choice(string.digits) for _ in range(3))

        return f"CONN{timestamp}{random_suffix}"

    

    # ========== DOCTOR METHODS ==========

    

    def find_doctor_by_id(self, doctor_id):

        """Find doctor by doctor_id from doctor_v2 collection"""

        if self.doctors_collection is None:
            return None

        return self.doctors_collection.find_one({"doctor_id": doctor_id})

    

    def find_doctor_by_email(self, email):
        """Find doctor by email address"""
        if self.doctors_collection is None:
            return None
        
        # Search in both flat and nested email fields
        doctor = self.doctors_collection.find_one({
            "$or": [
                {"email": email},
                {"personal_info.email": email}
            ]
        })
        return doctor
    
    def search_doctors(self, query=None, specialty=None, city=None, limit=20):

        """Search doctors by various criteria"""

        if self.doctors_collection is None:
            return []

        

        search_query = {}

        

        # Support both flat and nested structures
        if specialty:

            search_query["$or"] = [
                {"specialty": specialty},
                {"professional_info.specialty": specialty}
            ]
        

        if city:

            # Try both flat location and nested workplace_info
            city_query = {"$or": [
                {"location": {"$regex": city, "$options": "i"}},
                {"workplace_info.hospital_address.city": city}
            ]}
            if search_query:
                search_query = {"$and": [search_query, city_query]}
            else:
                search_query = city_query
        

        if query:

            query_search = {"$or": [
                {"name": {"$regex": query, "$options": "i"}},
                {"personal_info.full_name": {"$regex": query, "$options": "i"}},

                {"location": {"$regex": query, "$options": "i"}},
                {"workplace_info.hospital_name": {"$regex": query, "$options": "i"}},

                {"specialty": {"$regex": query, "$options": "i"}},
                {"professional_info.specialty": {"$regex": query, "$options": "i"}}

            ]}
            if search_query:
                search_query = {"$and": [search_query, query_search]}
            else:
                search_query = query_search
        

        return list(self.doctors_collection.find(search_query).limit(limit))

    

    def increment_doctor_patient_count(self, doctor_id):

        """Increment doctor's patient count"""

        if self.doctors_collection is None:
            return False

        # Support both flat and nested statistics structures
        result = self.doctors_collection.update_one(

            {"doctor_id": doctor_id},

            {
                "$inc": {
                    "statistics.total_patients": 1,
                    "statistics.active_patients": 1,
                    "total_patients": 1,  # Flat structure support
                    "active_patients": 1   # Flat structure support
                }
            }
        )

        return result.modified_count > 0

    

    def decrement_doctor_patient_count(self, doctor_id):

        """Decrement doctor's active patient count"""

        if self.doctors_collection is None:
            return False

        # Support both flat and nested statistics structures
        result = self.doctors_collection.update_one(

            {"doctor_id": doctor_id},

            {
                "$inc": {
                    "statistics.active_patients": -1,
                    "active_patients": -1  # Flat structure support
                }
            }
        )

        return result.modified_count > 0

    
    def get_patient_pending_invites(self, patient_id):
        """Get pending invites for patient from doctors"""
        return list(self.connections_collection.find({
            "patient_id": patient_id,
            "invited_by": "doctor",
            "status": "pending"
        }))
    
    def get_patient_invite_details(self, invite_id, patient_id):
        """Get details of a specific doctor invite for patient"""
        return self.connections_collection.find_one({
            "connection_id": invite_id,
            "patient_id": patient_id,
            "invited_by": "doctor"
        })





