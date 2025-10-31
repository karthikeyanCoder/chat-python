"""
Doctor Chat Services - Enhanced business logic for doctor chat operations
Service layer for processing doctor chat requests
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from app.modules.doctor_chat.models import Message, ChatRoom, MessageAttachment
from app.modules.doctor_chat.repository import get_doctor_chat_repository

logger = logging.getLogger(__name__)


class DoctorChatService:
    """Enhanced service for doctor chat business logic"""
    
    def __init__(self, db):
        """
        Initialize doctor chat service
        
        Args:
            db: Database instance
        """
        self.db = db
        self.repository = get_doctor_chat_repository()
        self._init_collections()
    
    # def _init_collections(self):
    #     """Initialize database collections"""
    #     try:
    #         if hasattr(self.db, 'doctors_collection'):
    #             self.doctors_collection = self.db.doctors_collection
    #         elif hasattr(self.db, 'db') and hasattr(self.db, 'client'):
    #             # Our custom Database class with db attribute
    #             self.doctors_collection = self.db.db['doctor_v2']
    #         elif hasattr(self.db, 'client'):
    #             db_client = self.db.client[self.db.client.get_database().name]
    #             self.doctors_collection = db_client['doctors']
    #         else:
    #             self.doctors_collection = self.db['doctors']
            
    #         if hasattr(self.db, 'patients_collection'):
    #             self.patients_collection = self.db.patients_collection
    #         elif hasattr(self.db, 'db') and hasattr(self.db, 'client'):
    #             # Our custom Database class with db attribute
    #             self.patients_collection = self.db.db['Patient']
    #         elif hasattr(self.db, 'client'):
    #             db_client = self.db.client[self.db.client.get_database().name]
    #             self.patients_collection = db_client['patient']
    #         else:
    #             self.patients_collection = self.db['patient']
                
    #         if hasattr(self.db, 'connections_collection'):
    #             self.connections_collection = self.db.connections_collection
    #         elif hasattr(self.db, 'db') and hasattr(self.db, 'client'):
    #             # Our custom Database class with db attribute
    #             try:
    #                 self.connections_collection = self.db.db['connections']
    #             except:
    #                 self.connections_collection = None
    #         elif hasattr(self.db, 'client'):
    #             try:
    #                 db_client = self.db.client[self.db.client.get_database().name]
    #                 self.connections_collection = db_client['connections']
    #             except:
    #                 self.connections_collection = None
    #         else:
    #             try:
    #                 self.connections_collection = self.db['connections']
    #             except:
    #                 self.connections_collection = None
                
    #     except Exception as e:
    #         logger.error(f"Failed to initialize collections: {str(e)}")
    
    # ...existing code...

class DoctorChatService:
    # Define collection name constants
    PATIENT_COLLECTION = 'patient'
    DOCTOR_COLLECTION = 'doctor_v2'
    CONNECTIONS_COLLECTION = 'connections'
    
    
    def __init__(self, db):
        """
        Initialize doctor chat service
        
        Args:
            db: Database instance
        """
        self.db = db
        self.repository = get_doctor_chat_repository()
        self._init_collections()
    
    def _init_collections(self):
        """Initialize database collections"""
        try:
            if hasattr(self.db, 'doctors_collection'):
                self.doctors_collection = self.db.doctors_collection
            elif hasattr(self.db, 'db') and hasattr(self.db, 'client'):
                # Our custom Database class with db attribute
                self.doctors_collection = self.db.db[self.DOCTOR_COLLECTION]
            elif hasattr(self.db, 'client'):
                db_client = self.db.client[self.db.client.get_database().name]
                self.doctors_collection = db_client['doctors']
            else:
                self.doctors_collection = self.db['doctors']
            
            if hasattr(self.db, 'patients_collection'):
                self.patients_collection = self.db.patients_collection
            elif hasattr(self.db, 'db') and hasattr(self.db, 'client'):
                # Our custom Database class with db attribute
                self.patients_collection = self.db.db[self.PATIENT_COLLECTION]
            elif hasattr(self.db, 'client'):
                db_client = self.db.client[self.db.client.get_database().name]
                self.patients_collection = db_client[self.PATIENT_COLLECTION]
            else:
                self.patients_collection = self.db[self.PATIENT_COLLECTION]
                
            if hasattr(self.db, 'connections_collection'):
                self.connections_collection = self.db.connections_collection
            elif hasattr(self.db, 'db') and hasattr(self.db, 'client'):
                # Our custom Database class with db attribute
                try:
                    self.connections_collection = self.db.db[self.CONNECTIONS_COLLECTION]
                except:
                    self.connections_collection = None
            elif hasattr(self.db, 'client'):
                try:
                    db_client = self.db.client[self.db.client.get_database().name]
                    self.connections_collection = db_client[self.CONNECTIONS_COLLECTION]
                except:
                    self.connections_collection = None
            else:
                try:
                    self.connections_collection = self.db[self.CONNECTIONS_COLLECTION]
                except:
                    self.connections_collection = None
                
        except Exception as e:
            logger.error(f"Failed to initialize collections: {str(e)}")

    def check_active_connection(self, patient_id: str, doctor_id: str) -> bool:
        """
        Check if patient and doctor have an active connection
        
        Args:
            patient_id: Patient ID
            doctor_id: Doctor ID
        
        Returns:
            bool: True if active connection exists, False otherwise
        """
        try:
            # If no connections collection, assume all doctor-patient pairs can chat
            if self.connections_collection is None:
                return True
                
            connection = self.connections_collection.find_one({
                "patient_id": patient_id,
                "doctor_id": doctor_id,
                "status": "active"
            })
            return connection is not None
        except Exception as e:
            logger.error(f"Error checking active connection: {str(e)}")
            # If there's an error, assume connection exists for basic functionality
            return True
    
    def get_doctor_chat_rooms(self, doctor_id: str, include_archived: bool = False) -> Dict[str, Any]:
        """
        Get all chat rooms for a doctor with enriched patient information
        
        Args:
            doctor_id: Doctor ID
            include_archived: Whether to include archived rooms
        
        Returns:
            dict: Response with chat rooms
        """
        try:
            # Verify doctor exists
            doctor = self.doctors_collection.find_one({"doctor_id": doctor_id})
            if not doctor:
                # Try alternate collection
                from pymongo import MongoClient
                if hasattr(self.db, 'client'):
                    db_client = self.db.client[self.db.client.get_database().name]
                    doctor_v2_collection = db_client.get('doctor_v2', db_client['doctors'])
                    doctor = doctor_v2_collection.find_one({"doctor_id": doctor_id})
            
            if not doctor:
                return {
                    "success": False,
                    "message": "Doctor not found",
                    "data": None
                }
            
            # Get active connections for this doctor
            if self.connections_collection is not None:
                active_connections = list(self.connections_collection.find({
                    "doctor_id": doctor_id,
                    "status": "active"
                }))
                connected_patient_ids = {conn["patient_id"] for conn in active_connections}
            else:
                # If no connections collection, get all patients (for basic functionality)
                all_patients = list(self.patients_collection.find({}, {"patient_id": 1}))
                connected_patient_ids = {patient["patient_id"] for patient in all_patients}
            
            # Get chat rooms
            chat_rooms = self.repository.get_doctor_chat_rooms(doctor_id, include_archived)
            
            # Filter chat rooms to only include those with active connections
            chat_rooms = [room for room in chat_rooms if room.get("patient_id") in connected_patient_ids]
            
            # Get patients with active connections but no chat rooms yet
            existing_chat_patient_ids = {room.get("patient_id") for room in chat_rooms}
            patients_without_rooms = connected_patient_ids - existing_chat_patient_ids
            
            # Create potential chat rooms for patients without existing rooms
            potential_rooms = []
            for patient_id in patients_without_rooms:
                patient = self.patients_collection.find_one({"patient_id": patient_id})
                if patient:
                    potential_room = {
                        "room_id": f"potential_{doctor_id}_{patient_id}",
                        "doctor_id": doctor_id,
                        "patient_id": patient_id,
                        "room_type": "potential",  # Mark as potential room
                        "status": "active",
                        "created_at": datetime.utcnow().isoformat(),
                        "last_message_at": None,
                        "last_message": None,
                        "unread_count": 0,
                        "is_archived": False,
                        "patient_info": {
                            "patient_id": patient_id,
                            "name": f"{patient.get('first_name', '')} {patient.get('last_name', '')}".strip() or patient.get('username', 'Unknown Patient'),
                            "age": patient.get('age'),
                            "blood_type": patient.get('blood_type'),
                            "is_pregnant": patient.get('is_pregnant', False),
                            "pregnancy_week": patient.get('pregnancy_week'),
                            "expected_delivery_date": patient.get('expected_delivery_date'),
                            "is_online": False
                        }
                    }
                    potential_rooms.append(potential_room)
            
            # Combine existing chat rooms and potential rooms
            all_rooms = chat_rooms + potential_rooms
            
            # Enrich with patient information
            enriched_rooms = []
            for room in all_rooms:
                patient_id = room.get("patient_id")
                
                # Get patient information
                patient = self.patients_collection.find_one({"patient_id": patient_id})
                
                if patient:
                    # Extract patient information
                    full_name = f"{patient.get('first_name', '')} {patient.get('last_name', '')}".strip()
                    patient_info = {
                        "patient_id": patient_id,
                        "name": full_name or patient.get('username', 'Unknown Patient'),
                        "age": patient.get('age'),
                        "gender": patient.get('gender'),
                        "profile_picture": patient.get('profile_picture'),
                        "is_online": False  # Can be updated with real-time status
                    }
                    
                    # Add pregnancy information if available
                    if patient.get('pregnancy_info'):
                        pregnancy_info = patient['pregnancy_info']
                        patient_info["is_pregnant"] = True
                        patient_info["pregnancy_week"] = pregnancy_info.get('current_week')
                        patient_info["due_date"] = pregnancy_info.get('expected_delivery_date')
                    
                    room["patient_info"] = patient_info
                else:
                    room["patient_info"] = {
                        "patient_id": patient_id,
                        "name": "Unknown Patient",
                        "is_online": False
                    }
                
                enriched_rooms.append(room)
            
            return {
                "success": True,
                "message": "Chat rooms retrieved successfully",
                "data": {
                    "chat_rooms": enriched_rooms,
                    "total_rooms": len(enriched_rooms)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting doctor chat rooms: {str(e)}")
            return {
                "success": False,
                "message": "Failed to retrieve chat rooms",
                "data": None
            }
    
    def start_chat_with_patient(self, doctor_id: str, patient_id: str) -> Dict[str, Any]:
        """
        Start a new chat conversation with a patient
        
        Args:
            doctor_id: Doctor ID
            patient_id: Patient ID
        
        Returns:
            dict: Response with chat room information
        """
        try:
            # Verify doctor exists
            doctor = self.doctors_collection.find_one({"doctor_id": doctor_id})
            if not doctor:
                return {
                    "success": False,
                    "message": "Doctor not found",
                    "data": None
                }
            
            # Verify patient exists
            patient = self.patients_collection.find_one({"patient_id": patient_id})
            if not patient:
                return {
                    "success": False,
                    "message": "Patient not found",
                    "data": None
                }
            
            # Check if active connection exists
            if not self.check_active_connection(patient_id, doctor_id):
                return {
                    "success": False,
                    "message": "No active connection found with this patient. Please connect with the patient first.",
                    "data": None
                }
            
            # Create or get existing chat room
            chat_room = self.repository.create_chat_room(doctor_id, patient_id)
            
            if not chat_room:
                return {
                    "success": False,
                    "message": "Failed to create chat room",
                    "data": None
                }
            
            # Add patient info to response
            full_name = f"{patient.get('first_name', '')} {patient.get('last_name', '')}".strip()
            patient_info = {
                "patient_id": patient_id,
                "name": full_name or patient.get('username', 'Unknown Patient'),
                "age": patient.get('age'),
                "gender": patient.get('gender'),
                "is_online": False
            }
            
            response_data = chat_room.to_dict()
            response_data["patient_info"] = patient_info
            
            return {
                "success": True,
                "message": "Chat room created successfully",
                "data": response_data
            }
            
        except Exception as e:
            logger.error(f"Error starting chat with patient: {str(e)}")
            return {
                "success": False,
                "message": "Failed to start chat",
                "data": None
            }
    
    def send_message_to_patient(self, doctor_id: str, patient_id: str, 
                              message_content: str, message_type: str = "text",
                              is_urgent: bool = False, priority: str = "normal",
                              reply_to_message_id: Optional[str] = None,
                              attachment: Optional[dict] = None) -> Dict[str, Any]:
        """
        Send a message from doctor to patient
        
        Args:
            doctor_id: Doctor ID
            patient_id: Patient ID
            message_content: Message content
            message_type: Message type
            is_urgent: Urgent flag
            priority: Message priority
            reply_to_message_id: Reply to message ID
            attachment: Attachment data (file_url, file_name, etc.)
        
        Returns:
            dict: Response with message information
        """
        try:
            logger.info(f"📨 Sending message - Type: {message_type}, Has Attachment: {attachment is not None}")
            if attachment:
                logger.info(f"   Attachment Type: {attachment.get('file_type')}, File: {attachment.get('file_name')}")
            
            # Verify doctor exists
            doctor = self.doctors_collection.find_one({"doctor_id": doctor_id})
            if not doctor:
                return {
                    "success": False,
                    "message": "Doctor not found",
                    "data": None
                }
            
            # Check if active connection exists
            if not self.check_active_connection(patient_id, doctor_id):
                return {
                    "success": False,
                    "message": "No active connection found with this patient. Please connect with the patient first.",
                    "data": None
                }
            
            # Get doctor name
            doctor_name = f"Dr. {doctor.get('first_name', 'Unknown')} {doctor.get('last_name', '')}".strip()
            
            # Get or create chat room
            chat_room = self.repository.create_chat_room(doctor_id, patient_id)
            if not chat_room:
                return {
                    "success": False,
                    "message": "Failed to create chat room",
                    "data": None
                }
            
            # Process attachment if provided
            attachments_list = None
            if attachment:
                logger.info(f"📎 Processing attachment: {attachment}")
                try:
                    attachment_obj = MessageAttachment(
                        file_name=attachment.get('file_name', ''),
                        file_type=attachment.get('file_type', ''),
                        file_url=attachment.get('file_url', ''),
                        file_size=attachment.get('file_size', 0),
                        uploaded_at=attachment.get('uploaded_at'),
                        thumbnail_url=attachment.get('thumbnail_url'),
                        duration=attachment.get('duration'),
                        mime_type=attachment.get('mime_type'),
                        s3_key=attachment.get('s3_key')
                    )
                    attachments_list = [attachment_obj]
                    logger.info(f"✅ Attachment object created successfully")
                except Exception as e:
                    logger.error(f"❌ Error creating attachment object: {str(e)}")
                    # Continue without attachment rather than failing
                    attachments_list = None
            
            # Create message
            message = Message(
                chat_room_id=chat_room.room_id,
                sender_id=doctor_id,
                sender_type="doctor",
                receiver_id=patient_id,
                receiver_type="patient",
                message_type=message_type,
                content=message_content,
                is_urgent=is_urgent,
                priority=priority,
                reply_to_message_id=reply_to_message_id,
                sender_name=doctor_name,
                attachments=attachments_list
            )
            
            # Save message
            created_message = self.repository.create_message(message)
            
            if not created_message:
                return {
                    "success": False,
                    "message": "Failed to send message",
                    "data": None
                }
            
            # Emit real-time event to patient if online
            # This will be handled by socket handlers
            
            return {
                "success": True,
                "message": "Message sent successfully",
                "data": created_message.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error sending message to patient: {str(e)}")
            return {
                "success": False,
                "message": "Failed to send message",
                "data": None
            }
    
    def get_chat_messages(self, doctor_id: str, room_id: str, 
                         page: int = 1, limit: int = 50) -> Dict[str, Any]:
        """
        Get messages from a chat room
        
        Args:
            doctor_id: Doctor ID
            room_id: Room ID
            page: Page number
            limit: Messages per page
        
        Returns:
            dict: Response with messages
        """
        try:
            # Verify doctor exists
            doctor = self.doctors_collection.find_one({"doctor_id": doctor_id})
            if not doctor:
                return {
                    "success": False,
                    "message": "Doctor not found",
                    "data": None
                }
            
            # Verify chat room and access
            chat_room = self.repository.get_chat_room(room_id)
            if not chat_room:
                return {
                    "success": False,
                    "message": "Chat room not found",
                    "data": None
                }
            
            if chat_room.doctor_id != doctor_id:
                return {
                    "success": False,
                    "message": "Access denied",
                    "data": None
                }
            
            # Check if active connection exists
            if not self.check_active_connection(chat_room.patient_id, doctor_id):
                return {
                    "success": False,
                    "message": "No active connection found with this patient. Please connect with the patient first.",
                    "data": None
                }
            
            # Get messages
            messages = self.repository.get_chat_messages(room_id, page, limit)
            
            # Calculate pagination info
            total_messages = len(messages)
            has_more = total_messages == limit
            
            # Mark messages as read for doctor
            self.repository.mark_room_messages_as_read(room_id, doctor_id, "doctor")
            
            return {
                "success": True,
                "message": "Messages retrieved successfully",
                "data": {
                    "messages": messages,
                    "total_messages": total_messages,
                    "page": page,
                    "limit": limit,
                    "has_more": has_more,
                    "room_info": chat_room.to_dict()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting chat messages: {str(e)}")
            return {
                "success": False,
                "message": "Failed to retrieve messages",
                "data": None
            }
    
    def mark_messages_as_read(self, doctor_id: str, room_id: str, 
                             message_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Mark messages as read
        
        Args:
            doctor_id: Doctor ID
            room_id: Room ID
            message_id: Specific message ID (optional)
        
        Returns:
            dict: Response with success status
        """
        try:
            # Verify doctor exists
            doctor = self.doctors_collection.find_one({"doctor_id": doctor_id})
            if not doctor:
                return {
                    "success": False,
                    "message": "Doctor not found",
                    "data": None
                }
            
            # Verify chat room access
            chat_room = self.repository.get_chat_room(room_id)
            if not chat_room or chat_room.doctor_id != doctor_id:
                return {
                    "success": False,
                    "message": "Chat room not found or access denied",
                    "data": None
                }
            
            if message_id:
                # Mark specific message as read
                success = self.repository.mark_message_as_read(message_id)
                count = 1 if success else 0
            else:
                # Mark all messages in room as read
                count = self.repository.mark_room_messages_as_read(
                    room_id, doctor_id, "doctor"
                )
            
            return {
                "success": True,
                "message": f"{count} message(s) marked as read",
                "data": {"count": count}
            }
            
        except Exception as e:
            logger.error(f"Error marking messages as read: {str(e)}")
            return {
                "success": False,
                "message": "Failed to mark messages as read",
                "data": None
            }
    
    def get_unread_count(self, doctor_id: str) -> Dict[str, Any]:
        """
        Get unread message count for a doctor
        
        Args:
            doctor_id: Doctor ID
        
        Returns:
            dict: Response with unread count
        """
        try:
            # Verify doctor exists
            doctor = self.doctors_collection.find_one({"doctor_id": doctor_id})
            if not doctor:
                return {
                    "success": False,
                    "message": "Doctor not found",
                    "data": None
                }
            
            # Get total unread count
            total_unread = self.repository.get_unread_message_count(doctor_id, "doctor")
            
            # Get unread count by room
            chat_rooms = self.repository.get_doctor_chat_rooms(doctor_id, False)
            unread_by_room = [
                {
                    "room_id": room["room_id"],
                    "patient_id": room["patient_id"],
                    "unread_count": room["unread_count_doctor"]
                }
                for room in chat_rooms if room.get("unread_count_doctor", 0) > 0
            ]
            
            return {
                "success": True,
                "message": "Unread count retrieved successfully",
                "data": {
                    "total_unread": total_unread,
                    "unread_by_room": unread_by_room
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting unread count: {str(e)}")
            return {
                "success": False,
                "message": "Failed to retrieve unread count",
                "data": None
            }
    
    def search_messages(self, doctor_id: str, search_query: str, 
                       room_id: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
        """
        Search messages for a doctor
        
        Args:
            doctor_id: Doctor ID
            search_query: Search query
            room_id: Optional room ID to limit search
            limit: Maximum results
        
        Returns:
            dict: Response with search results
        """
        try:
            # Verify doctor exists
            doctor = self.doctors_collection.find_one({"doctor_id": doctor_id})
            if not doctor:
                return {
                    "success": False,
                    "message": "Doctor not found",
                    "data": None
                }
            
            # Search messages
            messages = self.repository.search_messages(
                doctor_id, "doctor", search_query, room_id, limit
            )
            
            return {
                "success": True,
                "message": "Search completed successfully",
                "data": {
                    "messages": messages,
                    "total_results": len(messages),
                    "search_query": search_query
                }
            }
            
        except Exception as e:
            logger.error(f"Error searching messages: {str(e)}")
            return {
                "success": False,
                "message": "Failed to search messages",
                "data": None
            }
    
    def search_patients(self, doctor_id: str, search_query: str, 
                       page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """
        Search patients for starting new chats
        
        Args:
            doctor_id: Doctor ID
            search_query: Search query
            page: Page number
            limit: Maximum results
        
        Returns:
            dict: Response with patients
        """
        try:
            # Verify doctor exists
            doctor = self.doctors_collection.find_one({"doctor_id": doctor_id})
            if not doctor:
                return {
                    "success": False,
                    "message": "Doctor not found",
                    "data": None
                }
            
            # Search patients by name
            skip = (page - 1) * limit
            query = {
                "$or": [
                    {"name": {"$regex": search_query, "$options": "i"}},
                    {"patient_id": {"$regex": search_query, "$options": "i"}},
                    {"email": {"$regex": search_query, "$options": "i"}}
                ]
            }
            
            patients = list(
                self.patients_collection.find(query)
                .skip(skip)
                .limit(limit)
            )
            
            # Filter sensitive information
            filtered_patients = []
            for patient in patients:
                filtered_patient = {
                    "patient_id": patient.get("patient_id"),
                    "name": patient.get("name", "Unknown"),
                    "age": patient.get("age"),
                    "gender": patient.get("gender"),
                    "profile_picture": patient.get("profile_picture")
                }
                filtered_patients.append(filtered_patient)
            
            return {
                "success": True,
                "message": "Patients search completed successfully",
                "data": {
                    "patients": filtered_patients,
                    "total_results": len(filtered_patients),
                    "page": page,
                    "limit": limit
                }
            }
            
        except Exception as e:
            logger.error(f"Error searching patients: {str(e)}")
            return {
                "success": False,
                "message": "Failed to search patients",
                "data": None
            }
    
    def edit_message(self, doctor_id: str, message_id: str, 
                    new_content: str) -> Dict[str, Any]:
        """
        Edit a message
        
        Args:
            doctor_id: Doctor ID
            message_id: Message ID
            new_content: New message content
        
        Returns:
            dict: Response with success status
        """
        try:
            # Get message
            message = self.repository.get_message(message_id)
            if not message:
                return {
                    "success": False,
                    "message": "Message not found",
                    "data": None
                }
            
            # Verify sender
            if message.sender_id != doctor_id or message.sender_type != "doctor":
                return {
                    "success": False,
                    "message": "You can only edit your own messages",
                    "data": None
                }
            
            # Edit message
            success = self.repository.edit_message(message_id, new_content)
            
            if success:
                return {
                    "success": True,
                    "message": "Message edited successfully",
                    "data": {"message_id": message_id}
                }
            
            return {
                "success": False,
                "message": "Failed to edit message",
                "data": None
            }
            
        except Exception as e:
            logger.error(f"Error editing message: {str(e)}")
            return {
                "success": False,
                "message": "Failed to edit message",
                "data": None
            }
    
    def delete_message(self, doctor_id: str, message_id: str) -> Dict[str, Any]:
        """
        Delete a message
        
        Args:
            doctor_id: Doctor ID
            message_id: Message ID
        
        Returns:
            dict: Response with success status
        """
        try:
            # Get message
            message = self.repository.get_message(message_id)
            if not message:
                return {
                    "success": False,
                    "message": "Message not found",
                    "data": None
                }
            
            # Verify sender
            if message.sender_id != doctor_id or message.sender_type != "doctor":
                return {
                    "success": False,
                    "message": "You can only delete your own messages",
                    "data": None
                }
            
            # Delete message
            success = self.repository.delete_message(message_id)
            
            if success:
                return {
                    "success": True,
                    "message": "Message deleted successfully",
                    "data": {"message_id": message_id}
                }
            
            return {
                "success": False,
                "message": "Failed to delete message",
                "data": None
            }
            
        except Exception as e:
            logger.error(f"Error deleting message: {str(e)}")
            return {
                "success": False,
                "message": "Failed to delete message",
                "data": None
            }
    
    def add_reaction(self, doctor_id: str, message_id: str, reaction: str) -> Dict[str, Any]:
        """
        Add a reaction to a message
        
        Args:
            doctor_id: Doctor ID
            message_id: Message ID
            reaction: Reaction emoji or type
        
        Returns:
            dict: Response with success status
        """
        try:
            # Verify message exists
            message = self.repository.get_message(message_id)
            if not message:
                return {
                    "success": False,
                    "message": "Message not found",
                    "data": None
                }
            
            # Add reaction
            success = self.repository.add_reaction(message_id, doctor_id, "doctor", reaction)
            
            if success:
                return {
                    "success": True,
                    "message": "Reaction added successfully",
                    "data": {"message_id": message_id, "reaction": reaction}
                }
            
            return {
                "success": False,
                "message": "Failed to add reaction",
                "data": None
            }
            
        except Exception as e:
            logger.error(f"Error adding reaction: {str(e)}")
            return {
                "success": False,
                "message": "Failed to add reaction",
                "data": None
            }
    
    def update_room_settings(self, doctor_id: str, room_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update chat room settings
        
        Args:
            doctor_id: Doctor ID
            room_id: Room ID
            settings: Settings to update
        
        Returns:
            dict: Response with success status
        """
        try:
            # Verify chat room access
            chat_room = self.repository.get_chat_room(room_id)
            if not chat_room or chat_room.doctor_id != doctor_id:
                return {
                    "success": False,
                    "message": "Chat room not found or access denied",
                    "data": None
                }
            
            # Update settings
            success = self.repository.update_room_settings(room_id, doctor_id, settings)
            
            if success:
                return {
                    "success": True,
                    "message": "Room settings updated successfully",
                    "data": {"room_id": room_id}
                }
            
            return {
                "success": False,
                "message": "Failed to update room settings",
                "data": None
            }
            
        except Exception as e:
            logger.error(f"Error updating room settings: {str(e)}")
            return {
                "success": False,
                "message": "Failed to update room settings",
                "data": None
            }
    
    def get_patient_health_summary(self, doctor_id: str, patient_id: str) -> Dict[str, Any]:
        """
        Get patient health summary for the doctor
        
        Args:
            doctor_id: Doctor ID
            patient_id: Patient ID
        
        Returns:
            dict: Response with health summary
        """
        try:
            # Verify doctor exists
            doctor = self.doctors_collection.find_one({"doctor_id": doctor_id})
            if not doctor:
                return {
                    "success": False,
                    "message": "Doctor not found",
                    "data": None
                }
            
            # Get patient information
            patient = self.patients_collection.find_one({"patient_id": patient_id})
            if not patient:
                return {
                    "success": False,
                    "message": "Patient not found",
                    "data": None
                }
            
            # Helper function to clean MongoDB data for JSON serialization
            def clean_mongo_data(data):
                """Convert MongoDB ObjectId and other non-serializable objects to strings"""
                if isinstance(data, dict):
                    return {key: clean_mongo_data(value) for key, value in data.items()}
                elif isinstance(data, list):
                    return [clean_mongo_data(item) for item in data]
                elif hasattr(data, '__class__') and 'ObjectId' in str(data.__class__):
                    return str(data)
                elif hasattr(data, 'isoformat'):  # datetime objects
                    return data.isoformat()
                else:
                    return data
            
            # Prepare health summary
            health_summary = {
                "basic_info": {
                    "patient_id": patient.get("patient_id"),
                    "name": patient.get("name", "Unknown"),
                    "age": patient.get("age"),
                    "gender": patient.get("gender"),
                    "blood_type": patient.get("blood_type"),
                    "height": patient.get("height"),
                    "weight": patient.get("weight")
                },
                "pregnancy_info": clean_mongo_data(patient.get("pregnancy_info")),
                "health_data": {
                    "allergies": clean_mongo_data(patient.get("allergies", [])),
                    "medications": clean_mongo_data(patient.get("medications", [])),
                    "medical_conditions": clean_mongo_data(patient.get("medical_conditions", [])),
                    "family_history": clean_mongo_data(patient.get("family_history", []))
                },
                "emergency_contact": clean_mongo_data(patient.get("emergency_contact")),
                "recent_logs": {
                    "medication_logs": clean_mongo_data(patient.get("medication_logs", [])[-5:]),
                    "symptom_logs": clean_mongo_data(patient.get("symptom_logs", [])[-5:]),
                    "mental_health_logs": clean_mongo_data(patient.get("mental_health_logs", [])[-3:])
                }
            }
            
            return {
                "success": True,
                "message": "Patient health summary retrieved successfully",
                "data": health_summary
            }
            
        except Exception as e:
            logger.error(f"Error getting patient health summary: {str(e)}")
            return {
                "success": False,
                "message": "Failed to retrieve patient health summary",
                "data": None
            }
    
    def get_chat_analytics(self, doctor_id: str, room_id: str) -> Dict[str, Any]:
        """
        Get chat analytics for a room
        
        Args:
            doctor_id: Doctor ID
            room_id: Room ID
        
        Returns:
            dict: Response with analytics
        """
        try:
            # Verify chat room access
            chat_room = self.repository.get_chat_room(room_id)
            if not chat_room or chat_room.doctor_id != doctor_id:
                return {
                    "success": False,
                    "message": "Chat room not found or access denied",
                    "data": None
                }
            
            # Get analytics
            analytics = self.repository.get_chat_analytics(room_id)
            
            return {
                "success": True,
                "message": "Analytics retrieved successfully",
                "data": analytics
            }
            
        except Exception as e:
            logger.error(f"Error getting chat analytics: {str(e)}")
            return {
                "success": False,
                "message": "Failed to retrieve analytics",
                "data": None
            }


# Global service instance
doctor_chat_service = None


def init_doctor_chat_service(db):
    """
    Initialize the global doctor chat service
    
    Args:
        db: Database instance
    
    Returns:
        DoctorChatService instance
    """
    global doctor_chat_service
    doctor_chat_service = DoctorChatService(db)
    return doctor_chat_service


def get_doctor_chat_service():
    """
    Get the global doctor chat service instance
    
    Returns:
        DoctorChatService instance
    
    Raises:
        RuntimeError: If service hasn't been initialized
    """
    if doctor_chat_service is None:
        raise RuntimeError(
            "Doctor chat service has not been initialized. "
            "Call init_doctor_chat_service(db) first."
        )
    return doctor_chat_service


