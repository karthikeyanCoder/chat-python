"""
Chat Services - Business logic for chat operations
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import os

from app.modules.patient_chat.models import Message, ChatRoom, MessageAttachment
from app.modules.patient_chat.repository import get_chat_repository
from app.shared.socket_service import emit_to_user, emit_to_room, is_user_online

logger = logging.getLogger(__name__)


class ChatService:
    """Service for chat business logic"""
    
    # Define collection name constants from environment variables
    PATIENT_COLLECTION = os.getenv("PATIENTS_COLLECTION", "patient")
    DOCTOR_COLLECTION = os.getenv("DOCTORS_COLLECTION", "doctor_v2")
    CONNECTIONS_COLLECTION = os.getenv("CHAT_CONNECTIONS_COLLECTION", "connections")
    MESSAGES_COLLECTION = os.getenv("CHAT_MESSAGES_COLLECTION", "chat_messages")
    ROOMS_COLLECTION = os.getenv("CHAT_ROOMS_COLLECTION", "chat_rooms")
    
    def __init__(self, db):
        """
        Initialize chat service
        
        Args:
            db: Database instance
        """
        self.db = db
        self.repository = get_chat_repository()
        self._init_collections()
    
    def _init_collections(self):
        """Initialize database collections"""
        try:
            # Use the Database class get_collection method for all collections
            self.messages_collection = self.db.get_collection(self.MESSAGES_COLLECTION)
            self.chat_rooms_collection = self.db.get_collection(self.ROOMS_COLLECTION)
            self.connections_collection = self.db.get_collection(self.CONNECTIONS_COLLECTION)
            self.patients_collection = self.db.get_collection(self.PATIENT_COLLECTION)
            self.doctors_collection = self.db.get_collection(self.DOCTOR_COLLECTION)
            
            # Fallback to direct access if get_collection fails
            if self.messages_collection is None and hasattr(self.db, 'client'):
                db_name = os.getenv("DB_NAME", "patients_db")
                db_instance = self.db.client[db_name]
                self.messages_collection = db_instance[self.MESSAGES_COLLECTION]
                self.chat_rooms_collection = db_instance[self.ROOMS_COLLECTION]
                self.connections_collection = db_instance[self.CONNECTIONS_COLLECTION]
                self.patients_collection = db_instance[self.PATIENT_COLLECTION]
                self.doctors_collection = db_instance[self.DOCTOR_COLLECTION]
            
            logger.info("Chat collections initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize collections: {str(e)}")
            raise
    
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
    
    def sync_connected_doctors_from_appointments(self, patient_id: str) -> Dict[str, Any]:
        """
        Sync connected doctors from patient's appointments
        
        Args:
            patient_id: Patient ID
        
        Returns:
            dict: Response with sync status
        """
        try:
            # Get patient data
            patient = self.db.patients_collection.find_one({"patient_id": patient_id})
            if not patient:
                return {
                    "success": False,
                    "message": "Patient not found",
                    "data": None
                }
            
            # Extract unique doctor IDs from appointments
            appointments = patient.get("appointments", [])
            connected_doctor_ids = set()
            
            for appointment in appointments:
                doctor_id = appointment.get("doctor_id")
                if doctor_id and doctor_id.strip():
                    connected_doctor_ids.add(doctor_id.strip())
            
            # Convert to list for database storage
            connected_doctors_list = list(connected_doctor_ids)
            
            # Update patient's connected_doctors field
            update_result = self.db.patients_collection.update_one(
                {"patient_id": patient_id},
                {"$set": {"connected_doctors": connected_doctors_list}}
            )
            
            if update_result.modified_count > 0:
                logger.info(f"Updated connected_doctors for patient {patient_id}: {connected_doctors_list}")
            
            return {
                "success": True,
                "message": "Connected doctors synced successfully",
                "data": {
                    "connected_doctors": connected_doctors_list,
                    "total_doctors": len(connected_doctors_list)
                }
            }
            
        except Exception as e:
            logger.error(f"Error syncing connected doctors: {str(e)}")
            return {
                "success": False,
                "message": "Failed to sync connected doctors",
                "data": None
            }
    
    def get_patient_chat_rooms(self, patient_id: str, include_archived: bool = False) -> Dict[str, Any]:
        """
        Get all chat rooms for a patient with enriched doctor information
        Auto-creates chat rooms for connected doctors if they don't exist
        
        Args:
            patient_id: Patient ID
            include_archived: Whether to include archived rooms
        
        Returns:
            dict: Response with chat rooms
        """
        try:
            # Verify patient exists
            patient = self.db.patients_collection.find_one({"patient_id": patient_id})
            if not patient:
                return {
                    "success": False,
                    "message": "Patient not found",
                    "data": None
                }
            
            # First, sync connected doctors from appointments
            sync_result = self.sync_connected_doctors_from_appointments(patient_id)
            if not sync_result["success"]:
                logger.warning(f"Failed to sync connected doctors for {patient_id}: {sync_result['message']}")
            
            # Get active connections for this patient
            active_connections = list(self.connections_collection.find({
                "patient_id": patient_id,
                "status": "active"
            }))
            
            connected_doctor_ids = {conn["doctor_id"] for conn in active_connections}
            
            # Get existing chat rooms
            chat_rooms = self.repository.get_user_chat_rooms(patient_id, "patient", include_archived)
            
            # Filter chat rooms to only include those with active connections
            chat_rooms = [room for room in chat_rooms if room.get("doctor_id") in connected_doctor_ids]
            
            existing_room_doctor_ids = {room.get("doctor_id") for room in chat_rooms}
            
            # Auto-create chat rooms for connected doctors who don't have rooms yet
            for doctor_id in connected_doctor_ids:
                if doctor_id not in existing_room_doctor_ids:
                    try:
                        # Create chat room for this doctor
                        new_room = self.repository.create_chat_room(doctor_id, patient_id)
                        if new_room:
                            chat_rooms.append(new_room.to_dict())
                            logger.info(f"Auto-created chat room for patient {patient_id} with doctor {doctor_id}")
                    except Exception as e:
                        logger.error(f"Failed to auto-create room for doctor {doctor_id}: {str(e)}")
            
            # Refresh chat rooms after auto-creation
            chat_rooms = self.repository.get_user_chat_rooms(patient_id, "patient", include_archived)
            # Filter again after creation
            chat_rooms = [room for room in chat_rooms if room.get("doctor_id") in connected_doctor_ids]
            
            # Enrich with doctor information
            enriched_rooms = []
            for room in chat_rooms:
                doctor_id = room.get("doctor_id")
                
                # Try to get doctor from either collection
                doctor = self.db.doctors_collection.find_one({"doctor_id": doctor_id})
                if not doctor:
                    doctor = self.db.doctor_v2_collection.find_one({"doctor_id": doctor_id})
                
                if doctor:
                    # Extract doctor information
                    room["doctor_info"] = {
                        "doctor_id": doctor_id,
                        "name": f"Dr. {doctor.get('first_name', 'Unknown')} {doctor.get('last_name', '')}".strip(),
                        "specialization": doctor.get('specialization'),
                        "hospital": doctor.get('hospital_name'),
                        "consultation_fee": doctor.get('consultation_fee'),
                        "experience_years": doctor.get('experience_years'),
                        "is_online": is_user_online(doctor_id)
                    }
                else:
                    room["doctor_info"] = {
                        "doctor_id": doctor_id,
                        "name": "Unknown Doctor",
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
            logger.error(f"Error getting patient chat rooms: {str(e)}")
            return {
                "success": False,
                "message": "Failed to retrieve chat rooms",
                "data": None
            }
    
    def start_chat_with_doctor(self, patient_id: str, doctor_id: str) -> Dict[str, Any]:
        """
        Start a new chat conversation with a doctor
        
        Args:
            patient_id: Patient ID
            doctor_id: Doctor ID
        
        Returns:
            dict: Response with chat room information
        """
        try:
            # Verify patient exists
            patient = self.db.patients_collection.find_one({"patient_id": patient_id})
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
                    "message": "No active connection found with this doctor. Please connect with the doctor first.",
                    "data": None
                }
            
            # Verify doctor exists
            doctor = self.db.doctors_collection.find_one({"doctor_id": doctor_id})
            if not doctor:
                doctor = self.db.doctor_v2_collection.find_one({"doctor_id": doctor_id})
            
            if not doctor:
                return {
                    "success": False,
                    "message": "Doctor not found",
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
            
            # Add doctor info to response
            response_data = chat_room.to_dict()
            response_data["doctor_info"] = {
                "doctor_id": doctor_id,
                "name": f"Dr. {doctor.get('first_name', 'Unknown')} {doctor.get('last_name', '')}".strip(),
                "specialization": doctor.get('specialization'),
                "hospital": doctor.get('hospital_name'),
                "consultation_fee": doctor.get('consultation_fee'),
                "experience_years": doctor.get('experience_years'),
                "is_online": is_user_online(doctor_id)
            }
            
            return {
                "success": True,
                "message": "Chat room created successfully",
                "data": response_data
            }
            
        except Exception as e:
            logger.error(f"Error starting chat with doctor: {str(e)}")
            return {
                "success": False,
                "message": "Failed to start chat",
                "data": None
            }
    
    def send_message_to_doctor(self, patient_id: str, doctor_id: str, 
                              message_content: str, message_type: str = "text",
                              is_urgent: bool = False, priority: str = "normal",
                              reply_to_message_id: Optional[str] = None,
                              attachment: Optional[dict] = None) -> Dict[str, Any]:
        """
        Send a message from patient to doctor
        
        Args:
            patient_id: Patient ID
            doctor_id: Doctor ID
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
            logger.info(f"📨 Patient sending message - Type: {message_type}, Has Attachment: {attachment is not None}")
            if attachment:
                logger.info(f"   Attachment Type: {attachment.get('file_type')}, File: {attachment.get('file_name')}")
            # Verify patient exists
            patient = self.db.patients_collection.find_one({"patient_id": patient_id})
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
                    "message": "No active connection found with this doctor. Please connect with the doctor first.",
                    "data": None
                }
            
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
                sender_id=patient_id,
                sender_type="patient",
                receiver_id=doctor_id,
                receiver_type="doctor",
                message_type=message_type,
                content=message_content,
                is_urgent=is_urgent,
                priority=priority,
                reply_to_message_id=reply_to_message_id,
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
            
            # Emit real-time event to doctor if online
            try:
                patient_name = patient.get('name', 'Patient')
                emit_to_user(doctor_id, 'new_message', {
                    'message': created_message.to_dict(),
                    'sender_name': patient_name,
                    'room_id': chat_room.room_id
                })
            except Exception as socket_error:
                logger.warning(f"Failed to emit socket event: {str(socket_error)}")
            
            return {
                "success": True,
                "message": "Message sent successfully",
                "data": created_message.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error sending message to doctor: {str(e)}")
            return {
                "success": False,
                "message": "Failed to send message",
                "data": None
            }
    
    def get_chat_messages(self, patient_id: str, room_id: str, 
                         page: int = 1, limit: int = 50) -> Dict[str, Any]:
        """
        Get messages from a chat room
        
        Args:
            patient_id: Patient ID
            room_id: Room ID
            page: Page number
            limit: Messages per page
        
        Returns:
            dict: Response with messages
        """
        try:
            # Verify patient exists
            patient = self.db.patients_collection.find_one({"patient_id": patient_id})
            if not patient:
                return {
                    "success": False,
                    "message": "Patient not found",
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
            
            if chat_room.patient_id != patient_id:
                return {
                    "success": False,
                    "message": "Access denied",
                    "data": None
                }
            
            # Check if active connection exists
            if not self.check_active_connection(patient_id, chat_room.doctor_id):
                return {
                    "success": False,
                    "message": "No active connection found with this doctor. Please connect with the doctor first.",
                    "data": None
                }
            
            # Get messages
            messages = self.repository.get_chat_messages(room_id, page, limit)
            
            # Calculate pagination info
            total_messages = len(messages)
            has_more = total_messages == limit
            
            return {
                "success": True,
                "message": "Messages retrieved successfully",
                "data": {
                    "messages": messages,
                    "total_messages": total_messages,
                    "page": page,
                    "limit": limit,
                    "has_more": has_more
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting chat messages: {str(e)}")
            return {
                "success": False,
                "message": "Failed to retrieve messages",
                "data": None
            }
    
    def delete_message(self, patient_id: str, message_id: str) -> Dict[str, Any]:
        """
        Delete a message
        
        Args:
            patient_id: Patient ID
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
            if message.sender_id != patient_id or message.sender_type != "patient":
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
            else:
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
    
    def mark_messages_as_read(self, patient_id: str, room_id: str, message_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Mark messages as read
        
        Args:
            patient_id: Patient ID
            room_id: Room ID
            message_id: Specific message ID (optional)
        
        Returns:
            dict: Response with success status
        """
        try:
            # Verify room access
            chat_room = self.repository.get_chat_room(room_id)
            if not chat_room:
                return {
                    "success": False,
                    "message": "Chat room not found",
                    "data": None
                }
            
            if chat_room.patient_id != patient_id:
                return {
                    "success": False,
                    "message": "Access denied",
                    "data": None
                }
            
            # Mark messages as read
            if message_id:
                # Mark specific message
                success = self.repository.mark_message_as_read(message_id, patient_id)
            else:
                # Mark all messages in room as read
                success = self.repository.mark_room_messages_as_read(room_id, patient_id)
            
            if success:
                # Emit read receipt to doctor if online
                try:
                    emit_to_user(chat_room.doctor_id, 'message_read', {
                        'room_id': room_id,
                        'message_id': message_id,
                        'read_by': patient_id,
                        'read_at': datetime.utcnow().isoformat()
                    })
                except Exception as socket_error:
                    logger.warning(f"Failed to emit read receipt: {str(socket_error)}")
                
                return {
                    "success": True,
                    "message": "Messages marked as read",
                    "data": None
                }
            
            return {
                "success": False,
                "message": "Failed to mark messages as read",
                "data": None
            }
            
        except Exception as e:
            logger.error(f"Error marking messages as read: {str(e)}")
            return {
                "success": False,
                "message": "Failed to mark messages as read",
                "data": None
            }
    
    def get_unread_count(self, patient_id: str) -> Dict[str, Any]:
        """
        Get unread message count for patient
        
        Args:
            patient_id: Patient ID
        
        Returns:
            dict: Response with unread count
        """
        try:
            # Get unread messages count
            count = self.repository.get_unread_message_count(patient_id, "patient")
            
            return {
                "success": True,
                "message": "Unread count retrieved successfully",
                "data": {"unread_count": count}
            }
                
        except Exception as e:
            logger.error(f"Error getting unread count: {str(e)}")
            return {
                "success": False,
                "message": "Failed to get unread count",
                "data": None
            }
    
    def edit_message(self, patient_id: str, message_id: str, 
                    new_content: str) -> Dict[str, Any]:
        """
        Edit a message
        
        Args:
            patient_id: Patient ID
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
            if message.sender_id != patient_id or message.sender_type != "patient":
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
            else:
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
    
    def mark_message_as_read(self, patient_id: str, message_id: str) -> Dict[str, Any]:
        """
        Mark a message as read
        
        Args:
            patient_id: Patient ID
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
            
            # Verify recipient
            if message.recipient_id != patient_id or message.recipient_type != "patient":
                return {
                    "success": False,
                    "message": "You can only mark messages addressed to you as read",
                    "data": None
                }
            
            # Mark as read
            success = self.repository.mark_message_as_read(message_id)
            
            if success:
                return {
                    "success": True,
                    "message": "Message marked as read",
                    "data": {"message_id": message_id}
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to mark message as read",
                    "data": None
                }
                
        except Exception as e:
            logger.error(f"Error marking message as read: {str(e)}")
            return {
                "success": False,
                "message": "Failed to mark message as read",
                "data": None
            }
    
    def get_chat_history(self, patient_id: str, doctor_id: str, 
                        limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        Get chat history between patient and doctor
        
        Args:
            patient_id: Patient ID
            doctor_id: Doctor ID
            limit: Maximum number of messages to return
            offset: Number of messages to skip
        
        Returns:
            dict: Response with chat history
        """
        try:
            # Get chat room
            chat_room = self.repository.get_chat_room_by_participants(
                patient_id, doctor_id
            )
            
            if not chat_room:
                return {
                    "success": False,
                    "message": "Chat room not found",
                    "data": None
                }
            
            # Get messages
            messages = self.repository.get_messages_by_room(
                chat_room.id, limit=limit, offset=offset
            )
            
            return {
                "success": True,
                "message": "Chat history retrieved successfully",
                "data": {
                    "chat_room": chat_room.to_dict(),
                    "messages": [msg.to_dict() for msg in messages]
                }
            }
                
        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}")
            return {
                "success": False,
                "message": "Failed to get chat history",
                "data": None
            }
    
    def get_connected_doctors(self, patient_id: str) -> Dict[str, Any]:
        """
        Get list of doctors connected to patient
        
        Args:
            patient_id: Patient ID
        
        Returns:
            dict: Response with connected doctors
        """
        try:
            # Get connected doctors
            doctors = self.repository.get_connected_doctors(patient_id)
            
            return {
                "success": True,
                "message": "Connected doctors retrieved successfully",
                "data": {"doctors": [doctor.to_dict() for doctor in doctors]}
            }
                
        except Exception as e:
            logger.error(f"Error getting connected doctors: {str(e)}")
            return {
                "success": False,
                "message": "Failed to get connected doctors",
                "data": None
            }
    
    def connect_to_doctor(self, patient_id: str, doctor_id: str) -> Dict[str, Any]:
        """
        Connect patient to doctor
        
        Args:
            patient_id: Patient ID
            doctor_id: Doctor ID
        
        Returns:
            dict: Response with success status
        """
        try:
            # Check if already connected
            existing_connection = self.repository.get_connection(patient_id, doctor_id)
            if existing_connection:
                return {
                    "success": False,
                    "message": "Already connected to this doctor",
                    "data": None
                }
            
            # Create connection
            success = self.repository.create_connection(patient_id, doctor_id)
            
            if success:
                # Create chat room
                chat_room = self.repository.create_chat_room(patient_id, doctor_id)
                
                return {
                    "success": True,
                    "message": "Connected to doctor successfully",
                    "data": {
                        "connection": {"patient_id": patient_id, "doctor_id": doctor_id},
                        "chat_room": chat_room.to_dict() if chat_room else None
                    }
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to connect to doctor",
                    "data": None
                }
                
        except Exception as e:
            logger.error(f"Error connecting to doctor: {str(e)}")
            return {
                "success": False,
                "message": "Failed to connect to doctor",
                "data": None
            }
    
    def disconnect_from_doctor(self, patient_id: str, doctor_id: str) -> Dict[str, Any]:
        """
        Disconnect patient from doctor
        
        Args:
            patient_id: Patient ID
            doctor_id: Doctor ID
        
        Returns:
            dict: Response with success status
        """
        try:
            # Remove connection
            success = self.repository.remove_connection(patient_id, doctor_id)
            
            if success:
                return {
                    "success": True,
                    "message": "Disconnected from doctor successfully",
                    "data": {"patient_id": patient_id, "doctor_id": doctor_id}
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to disconnect from doctor",
                    "data": None
                }
                
        except Exception as e:
            logger.error(f"Error disconnecting from doctor: {str(e)}")
            return {
                "success": False,
                "message": "Failed to disconnect from doctor",
                "data": None
            }
    
    def get_chat_room(self, patient_id: str, doctor_id: str) -> Dict[str, Any]:
        """
        Get chat room between patient and doctor
        
        Args:
            patient_id: Patient ID
            doctor_id: Doctor ID
        
        Returns:
            dict: Response with chat room
        """
        try:
            # Get chat room
            chat_room = self.repository.get_chat_room_by_participants(
                patient_id, doctor_id
            )
            
            if chat_room:
                return {
                    "success": True,
                    "message": "Chat room retrieved successfully",
                    "data": {"chat_room": chat_room.to_dict()}
                }
            else:
                return {
                    "success": False,
                    "message": "Chat room not found",
                    "data": None
                }
                
        except Exception as e:
            logger.error(f"Error getting chat room: {str(e)}")
            return {
                "success": False,
                "message": "Failed to get chat room",
                "data": None
            }
    
    def get_messages(self, patient_id: str, room_id: str, 
                    limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        Get messages from chat room
        
        Args:
            patient_id: Patient ID
            room_id: Chat room ID
            limit: Maximum number of messages to return
            offset: Number of messages to skip
        
        Returns:
            dict: Response with messages
        """
        try:
            # Verify patient has access to room
            chat_room = self.repository.get_chat_room(room_id)
            if not chat_room or chat_room.patient_id != patient_id:
                return {
                    "success": False,
                    "message": "Access denied to chat room",
                    "data": None
                }
            
            # Get messages
            messages = self.repository.get_messages_by_room(
                room_id, limit=limit, offset=offset
            )
            
            return {
                "success": True,
                "message": "Messages retrieved successfully",
                "data": {"messages": [msg.to_dict() for msg in messages]}
            }
                
        except Exception as e:
            logger.error(f"Error getting messages: {str(e)}")
            return {
                "success": False,
                "message": "Failed to get messages",
                "data": None
            }
    
    def search_messages(self, patient_id: str, search_query: str, 
                       limit: int = 20) -> Dict[str, Any]:
        """
        Search messages for a patient
        
        Args:
            patient_id: Patient ID
            search_query: Search query string
            limit: Maximum number of results to return
        
        Returns:
            dict: Response with search results
        """
        try:
            # Verify patient exists
            patient = self.patients_collection.find_one({"patient_id": patient_id})
            if not patient:
                return {
                    "success": False,
                    "message": "Patient not found",
                    "data": None
                }
            
            # Search messages using repository
            messages = self.repository.search_messages(
                user_id=patient_id,
                user_type="patient", 
                search_query=search_query,
                limit=limit
            )
            
            return {
                "success": True,
                "message": f"Found {len(messages)} messages matching '{search_query}'",
                "data": {
                    "messages": messages,
                    "total_results": len(messages),
                    "search_query": search_query,
                    "limit": limit
                }
            }
            
        except Exception as e:
            logger.error(f"Error searching messages: {str(e)}")
            return {
                "success": False,
                "message": "Failed to search messages",
                "data": None
            }
    
    def handle_socket_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming socket message
        
        Args:
            data: Socket message data
        
        Returns:
            dict: Response with handling result
        """
        try:
            message_type = data.get("type")
            
            if message_type == "send_message":
                return self.send_message_to_doctor(
                    patient_id=data.get("patient_id"),
                    doctor_id=data.get("doctor_id"),
                    message_content=data.get("content"),
                    message_type=data.get("message_type", "text")
                )
            elif message_type == "edit_message":
                return self.edit_message(
                    patient_id=data.get("patient_id"),
                    message_id=data.get("message_id"),
                    new_content=data.get("content")
                )
            elif message_type == "delete_message":
                return self.delete_message(
                    patient_id=data.get("patient_id"),
                    message_id=data.get("message_id")
                )
            elif message_type == "mark_as_read":
                return self.mark_message_as_read(
                    patient_id=data.get("patient_id"),
                    message_id=data.get("message_id")
                )
            else:
                return {
                    "success": False,
                    "message": f"Unknown message type: {message_type}",
                    "data": None
                }
                
        except Exception as e:
            logger.error(f"Error handling socket message: {str(e)}")
            return {
                "success": False,
                "message": "Failed to handle socket message",
                "data": None
            }
    


# Global service instance
chat_service = None


def init_chat_service(db):
    """
    Initialize the global chat service
    
    Args:
        db: Database instance
    
    Returns:
        ChatService instance
    """
    global chat_service
    chat_service = ChatService(db)
    return chat_service


def get_chat_service():
    """
    Get the global chat service instance
    
    Returns:
        ChatService instance
    
    Raises:
        RuntimeError: If service hasn't been initialized
    """
    if chat_service is None:
        raise RuntimeError(
            "Chat service has not been initialized. "
            "Call init_chat_service(db) first."
        )
    return chat_service
