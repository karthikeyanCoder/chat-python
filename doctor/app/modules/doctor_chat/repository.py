"""
Doctor Chat Repository - Enhanced database operations
Database layer for messages, chat rooms, and analytics
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pymongo import DESCENDING, ASCENDING
from pymongo.collection import Collection
import logging

from .models import Message, ChatRoom, MessageAttachment, MessageReaction

logger = logging.getLogger(__name__)


class DoctorChatRepository:
    """Enhanced repository for doctor chat operations"""
    
    def __init__(self, db):
        """
        Initialize repository with database connection
        
        Args:
            db: Database instance or MongoDB client
        """
        self.db = db
        self.messages_collection = None
        self.chat_rooms_collection = None
        self._init_collections()
    
    def _init_collections(self):
        """Initialize chat collections"""
        try:
            logger.info(f"Initializing collections with db type: {type(self.db)}")
            
            # Get or create collections
            if hasattr(self.db, 'chat_messages_collection') and hasattr(self.db, 'chat_rooms_collection'):
                # Our custom Database class
                logger.info("Using Database class collections")
                self.messages_collection = self.db.chat_messages_collection
                self.chat_rooms_collection = self.db.chat_rooms_collection
            elif hasattr(self.db, 'get_collection'):
                logger.info("Using get_collection method")
                self.messages_collection = self.db.get_collection('chat_messages')
                self.chat_rooms_collection = self.db.get_collection('chat_rooms')
            elif hasattr(self.db, 'db') and hasattr(self.db, 'client'):
                # If database instance has db and client attributes (our Database class)
                logger.info("Using db and client attributes")
                db_instance = self.db.db
                self.messages_collection = db_instance['chat_messages']
                self.chat_rooms_collection = db_instance['chat_rooms']
            elif hasattr(self.db, 'client'):
                # If database instance has client attribute
                logger.info("Using client attribute")
                try:
                    default_db = self.db.client.get_database()
                    logger.info(f"Default database: {default_db}")
                    if default_db:
                        db_name = default_db.name
                        logger.info(f"Database name: {db_name}")
                        db_client = self.db.client[db_name]
                        self.messages_collection = db_client['chat_messages']
                        self.chat_rooms_collection = db_client['chat_rooms']
                    else:
                        logger.error("No default database found on client")
                        raise ValueError("No default database defined")
                except Exception as e:
                    logger.error(f"Failed to get database from client: {e}")
                    raise
            else:
                # Direct MongoDB database object
                logger.info("Using direct database object")
                self.messages_collection = self.db['chat_messages']
                self.chat_rooms_collection = self.db['chat_rooms']
            
            logger.info(f"Messages collection initialized: {self.messages_collection is not None}")
            logger.info(f"Chat rooms collection initialized: {self.chat_rooms_collection is not None}")
            
            # Create indexes for better performance
            self._create_indexes()
            
            logger.info("Doctor chat collections initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize chat collections: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def _create_indexes(self):
        """Create database indexes for chat collections"""
        try:
            # Message indexes
            self.messages_collection.create_index([("chat_room_id", ASCENDING)])
            self.messages_collection.create_index([("message_id", ASCENDING)], unique=True)
            self.messages_collection.create_index([("sender_id", ASCENDING)])
            self.messages_collection.create_index([("receiver_id", ASCENDING)])
            self.messages_collection.create_index([("created_at", DESCENDING)])
            self.messages_collection.create_index([
                ("chat_room_id", ASCENDING),
                ("created_at", DESCENDING)
            ])
            self.messages_collection.create_index([
                ("content", "text")  # Text search index
            ])
            
            # Chat room indexes
            self.chat_rooms_collection.create_index([("room_id", ASCENDING)], unique=True)
            self.chat_rooms_collection.create_index([("doctor_id", ASCENDING)])
            self.chat_rooms_collection.create_index([("patient_id", ASCENDING)])
            self.chat_rooms_collection.create_index([
                ("doctor_id", ASCENDING),
                ("patient_id", ASCENDING)
            ], unique=True)
            self.chat_rooms_collection.create_index([("last_message_time", DESCENDING)])
            
            logger.info("Doctor chat indexes created successfully")
        except Exception as e:
            logger.warning(f"Some indexes may already exist: {str(e)}")
    
    # ==================== Chat Room Operations ====================
    
    def create_chat_room(self, doctor_id: str, patient_id: str) -> Optional[ChatRoom]:
        """
        Create a new chat room or return existing one
        
        Args:
            doctor_id: Doctor ID
            patient_id: Patient ID
        
        Returns:
            ChatRoom object or None
        """
        try:
            # Check if room already exists
            existing_room = self.get_chat_room_by_participants(doctor_id, patient_id)
            if existing_room:
                return existing_room
            
            # Create new room
            chat_room = ChatRoom(
                doctor_id=doctor_id,
                patient_id=patient_id,
                room_name=f"Dr. {doctor_id[-6:]} - Patient {patient_id[-6:]}"
            )
            
            # Validate
            errors = chat_room.validate()
            if errors:
                logger.error(f"Chat room validation failed: {errors}")
                return None
            
            # Insert into database
            result = self.chat_rooms_collection.insert_one(chat_room.to_dict())
            
            if result.inserted_id:
                logger.info(f"Created chat room: {chat_room.room_id}")
                return chat_room
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to create chat room: {str(e)}")
            return None
    
    def get_chat_room(self, room_id: str) -> Optional[ChatRoom]:
        """
        Get a chat room by ID
        
        Args:
            room_id: Room ID
        
        Returns:
            ChatRoom object or None
        """
        try:
            room_data = self.chat_rooms_collection.find_one({"room_id": room_id})
            if room_data:
                return ChatRoom.from_dict(room_data)
            return None
        except Exception as e:
            logger.error(f"Failed to get chat room: {str(e)}")
            return None
    
    def get_chat_room_by_participants(self, doctor_id: str, patient_id: str) -> Optional[ChatRoom]:
        """
        Get a chat room by doctor and patient IDs
        
        Args:
            doctor_id: Doctor ID
            patient_id: Patient ID
        
        Returns:
            ChatRoom object or None
        """
        try:
            room_data = self.chat_rooms_collection.find_one({
                "doctor_id": doctor_id,
                "patient_id": patient_id
            })
            if room_data:
                return ChatRoom.from_dict(room_data)
            return None
        except Exception as e:
            logger.error(f"Failed to get chat room by participants: {str(e)}")
            return None
    
    def get_doctor_chat_rooms(self, doctor_id: str, include_archived: bool = False) -> List[Dict[str, Any]]:
        """
        Get all chat rooms for a doctor
        
        Args:
            doctor_id: Doctor ID
            include_archived: Whether to include archived rooms
        
        Returns:
            List of chat room dictionaries
        """
        try:
            query = {"doctor_id": doctor_id}
            if not include_archived:
                query["is_archived"] = False
            
            rooms = list(
                self.chat_rooms_collection.find(query)
                .sort([("pinned_by_doctor", DESCENDING), ("last_message_time", DESCENDING)])
            )
            
            # Convert raw MongoDB documents to ChatRoom objects and serialize them
            serialized_rooms = []
            for room_data in rooms:
                try:
                    # Convert ObjectId fields to strings for JSON serialization
                    if '_id' in room_data:
                        room_data['_id'] = str(room_data['_id'])
                    
                    # Create ChatRoom object from data and convert to dict
                    chat_room = ChatRoom.from_dict(room_data)
                    serialized_rooms.append(chat_room.to_dict())
                except Exception as e:
                    logger.warning(f"Failed to serialize chat room {room_data.get('room_id', 'unknown')}: {str(e)}")
                    # Fallback: manually convert ObjectId fields and return raw data
                    clean_room_data = {}
                    for key, value in room_data.items():
                        if hasattr(value, 'generation_time'):  # ObjectId
                            clean_room_data[key] = str(value)
                        else:
                            clean_room_data[key] = value
                    serialized_rooms.append(clean_room_data)
            
            return serialized_rooms
            
        except Exception as e:
            logger.error(f"Failed to get doctor chat rooms: {str(e)}")
            return []
    
    def update_chat_room_last_message(self, room_id: str, message: str, 
                                     message_id: str, message_time: datetime) -> bool:
        """
        Update the last message in a chat room
        
        Args:
            room_id: Room ID
            message: Last message content
            message_id: Message ID
            message_time: Message timestamp
        
        Returns:
            bool: Success status
        """
        try:
            result = self.chat_rooms_collection.update_one(
                {"room_id": room_id},
                {
                    "$set": {
                        "last_message": message[:100],  # Store first 100 chars
                        "last_message_id": message_id,
                        "last_message_time": message_time,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update chat room last message: {str(e)}")
            return False
    
    def increment_unread_count(self, room_id: str, user_type: str) -> bool:
        """
        Increment unread message count for a user in a room
        
        Args:
            room_id: Room ID
            user_type: User type (patient or doctor)
        
        Returns:
            bool: Success status
        """
        try:
            field = f"unread_count_{user_type}"
            result = self.chat_rooms_collection.update_one(
                {"room_id": room_id},
                {"$inc": {field: 1}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to increment unread count: {str(e)}")
            return False
    
    def reset_unread_count(self, room_id: str, user_type: str) -> bool:
        """
        Reset unread message count for a user in a room
        
        Args:
            room_id: Room ID
            user_type: User type (patient or doctor)
        
        Returns:
            bool: Success status
        """
        try:
            field = f"unread_count_{user_type}"
            result = self.chat_rooms_collection.update_one(
                {"room_id": room_id},
                {"$set": {field: 0}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to reset unread count: {str(e)}")
            return False
    
    def update_room_settings(self, room_id: str, doctor_id: str, settings: Dict[str, Any]) -> bool:
        """
        Update chat room settings for a doctor
        
        Args:
            room_id: Room ID
            doctor_id: Doctor ID
            settings: Settings to update
        
        Returns:
            bool: Success status
        """
        try:
            # Filter allowed settings
            allowed_fields = [
                'room_name', 'room_description', 'tags', 'pinned_by_doctor',
                'notifications_enabled_doctor', 'is_archived'
            ]
            
            update_data = {
                k: v for k, v in settings.items() if k in allowed_fields
            }
            update_data['updated_at'] = datetime.utcnow()
            
            result = self.chat_rooms_collection.update_one(
                {"room_id": room_id, "doctor_id": doctor_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update room settings: {str(e)}")
            return False
    
    # ==================== Message Operations ====================
    
    def create_message(self, message: Message) -> Optional[Message]:
        """
        Create a new message
        
        Args:
            message: Message object
        
        Returns:
            Message object or None
        """
        try:
            # Validate
            errors = message.validate()
            if errors:
                logger.error(f"Message validation failed: {errors}")
                return None
            
            # Insert into database
            result = self.messages_collection.insert_one(message.to_dict())
            
            if result.inserted_id:
                # Update chat room
                self.update_chat_room_last_message(
                    message.chat_room_id,
                    message.content,
                    message.message_id,
                    message.created_at
                )
                
                # Increment unread count for receiver
                self.increment_unread_count(message.chat_room_id, message.receiver_type)
                
                logger.info(f"Created message: {message.message_id}")
                return message
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to create message: {str(e)}")
            return None
    
    def get_message(self, message_id: str) -> Optional[Message]:
        """
        Get a message by ID
        
        Args:
            message_id: Message ID
        
        Returns:
            Message object or None
        """
        try:
            message_data = self.messages_collection.find_one({"message_id": message_id})
            if message_data:
                return Message.from_dict(message_data)
            return None
        except Exception as e:
            logger.error(f"Failed to get message: {str(e)}")
            return None
    
    def get_chat_messages(self, room_id: str, page: int = 1, 
                         limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get messages from a chat room with pagination
        
        Args:
            room_id: Room ID
            page: Page number (1-indexed)
            limit: Messages per page
        
        Returns:
            List of message dictionaries
        """
        try:
            skip = (page - 1) * limit
            
            messages = list(
                self.messages_collection.find({
                    "chat_room_id": room_id,
                    "is_deleted": False
                })
                .sort("created_at", DESCENDING)
                .skip(skip)
                .limit(limit)
            )
            
            # Convert raw MongoDB documents to Message objects and then to dict
            message_objects = []
            for msg_data in messages:
                try:
                    # Convert ObjectId to string for message_id if needed
                    if '_id' in msg_data and 'message_id' not in msg_data:
                        msg_data['message_id'] = str(msg_data['_id'])
                    
                    # Convert ObjectId fields to strings
                    for key, value in msg_data.items():
                        if hasattr(value, '__class__') and 'ObjectId' in str(type(value)):
                            msg_data[key] = str(value)
                    
                    message_obj = Message.from_dict(msg_data)
                    message_objects.append(message_obj.to_dict())
                except Exception as e:
                    logger.error(f"Error converting message {msg_data.get('_id', 'unknown')}: {str(e)}")
                    continue
            
            # Reverse to get chronological order
            return list(reversed(message_objects))
            
        except Exception as e:
            logger.error(f"Failed to get chat messages: {str(e)}")
            return []
    
    def mark_message_as_read(self, message_id: str) -> bool:
        """
        Mark a message as read
        
        Args:
            message_id: Message ID
        
        Returns:
            bool: Success status
        """
        try:
            result = self.messages_collection.update_one(
                {"message_id": message_id},
                {
                    "$set": {
                        "is_read": True,
                        "read_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to mark message as read: {str(e)}")
            return False
    
    def mark_room_messages_as_read(self, room_id: str, user_id: str, 
                                   user_type: str) -> int:
        """
        Mark all messages in a room as read for a user
        
        Args:
            room_id: Room ID
            user_id: User ID
            user_type: User type
        
        Returns:
            int: Number of messages marked as read
        """
        try:
            result = self.messages_collection.update_many(
                {
                    "chat_room_id": room_id,
                    "receiver_id": user_id,
                    "receiver_type": user_type,
                    "is_read": False
                },
                {
                    "$set": {
                        "is_read": True,
                        "read_at": datetime.utcnow()
                    }
                }
            )
            
            # Reset unread count
            if result.modified_count > 0:
                self.reset_unread_count(room_id, user_type)
            
            return result.modified_count
            
        except Exception as e:
            logger.error(f"Failed to mark room messages as read: {str(e)}")
            return 0
    
    def get_unread_message_count(self, user_id: str, user_type: str) -> int:
        """
        Get total unread message count for a user
        
        Args:
            user_id: User ID
            user_type: User type
        
        Returns:
            int: Unread message count
        """
        try:
            count = self.messages_collection.count_documents({
                "receiver_id": user_id,
                "receiver_type": user_type,
                "is_read": False,
                "is_deleted": False
            })
            return count
        except Exception as e:
            logger.error(f"Failed to get unread message count: {str(e)}")
            return 0
    
    def edit_message(self, message_id: str, new_content: str) -> bool:
        """
        Edit a message
        
        Args:
            message_id: Message ID
            new_content: New message content
        
        Returns:
            bool: Success status
        """
        try:
            result = self.messages_collection.update_one(
                {"message_id": message_id},
                {
                    "$set": {
                        "content": new_content,
                        "is_edited": True,
                        "edited_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to edit message: {str(e)}")
            return False
    
    def delete_message(self, message_id: str) -> bool:
        """
        Soft delete a message
        
        Args:
            message_id: Message ID
        
        Returns:
            bool: Success status
        """
        try:
            result = self.messages_collection.update_one(
                {"message_id": message_id},
                {
                    "$set": {
                        "is_deleted": True,
                        "deleted_at": datetime.utcnow(),
                        "content": "[Message deleted]"
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to delete message: {str(e)}")
            return False
    
    def search_messages(self, user_id: str, user_type: str, 
                       search_query: str, room_id: Optional[str] = None,
                       limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search messages for a user
        
        Args:
            user_id: User ID
            user_type: User type
            search_query: Search query
            room_id: Optional room ID to limit search
            limit: Maximum results
        
        Returns:
            List of message dictionaries
        """
        try:
            # Build query based on user type
            base_query = {
                "$or": [
                    {"sender_id": user_id, "sender_type": user_type},
                    {"receiver_id": user_id, "receiver_type": user_type}
                ],
                "content": {"$regex": search_query, "$options": "i"},
                "is_deleted": False
            }
            
            if room_id:
                base_query["chat_room_id"] = room_id
            
            messages = list(
                self.messages_collection.find(base_query)
                .sort("created_at", DESCENDING)
                .limit(limit)
            )
            
            return messages
            
        except Exception as e:
            logger.error(f"Failed to search messages: {str(e)}")
            return []
    
    def add_reaction(self, message_id: str, user_id: str, user_type: str, reaction: str) -> bool:
        """
        Add a reaction to a message
        
        Args:
            message_id: Message ID
            user_id: User ID
            user_type: User type
            reaction: Reaction emoji or type
        
        Returns:
            bool: Success status
        """
        try:
            # Remove existing reaction from this user
            self.messages_collection.update_one(
                {"message_id": message_id},
                {"$pull": {"reactions": {"user_id": user_id}}}
            )
            
            # Add new reaction
            reaction_obj = MessageReaction(user_id, user_type, reaction)
            result = self.messages_collection.update_one(
                {"message_id": message_id},
                {"$push": {"reactions": reaction_obj.to_dict()}}
            )
            
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to add reaction: {str(e)}")
            return False
    
    def get_chat_analytics(self, room_id: str) -> Dict[str, Any]:
        """
        Get analytics for a chat room
        
        Args:
            room_id: Room ID
        
        Returns:
            Analytics dictionary
        """
        try:
            pipeline = [
                {"$match": {"chat_room_id": room_id, "is_deleted": False}},
                {
                    "$group": {
                        "_id": None,
                        "total_messages": {"$sum": 1},
                        "doctor_messages": {
                            "$sum": {"$cond": [{"$eq": ["$sender_type", "doctor"]}, 1, 0]}
                        },
                        "patient_messages": {
                            "$sum": {"$cond": [{"$eq": ["$sender_type", "patient"]}, 1, 0]}
                        },
                        "total_attachments": {"$sum": {"$size": "$attachments"}}
                    }
                }
            ]
            
            result = list(self.messages_collection.aggregate(pipeline))
            
            if result:
                return {
                    "room_id": room_id,
                    "total_messages": result[0]["total_messages"],
                    "messages_by_doctor": result[0]["doctor_messages"],
                    "messages_by_patient": result[0]["patient_messages"],
                    "total_attachments": result[0]["total_attachments"],
                    "last_updated": datetime.utcnow()
                }
            
            return {
                "room_id": room_id,
                "total_messages": 0,
                "messages_by_doctor": 0,
                "messages_by_patient": 0,
                "total_attachments": 0,
                "last_updated": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Failed to get chat analytics: {str(e)}")
            return {}


# Global repository instance (will be initialized with database)
doctor_chat_repository = None


def init_doctor_chat_repository(db):
    """
    Initialize the global doctor chat repository
    
    Args:
        db: Database instance
    
    Returns:
        DoctorChatRepository instance
    """
    global doctor_chat_repository
    doctor_chat_repository = DoctorChatRepository(db)
    return doctor_chat_repository


def get_doctor_chat_repository():
    """
    Get the global doctor chat repository instance
    
    Returns:
        DoctorChatRepository instance
    
    Raises:
        RuntimeError: If repository hasn't been initialized
    """
    if doctor_chat_repository is None:
        raise RuntimeError(
            "Doctor chat repository has not been initialized. "
            "Call init_doctor_chat_repository(db) first."
        )
    return doctor_chat_repository


