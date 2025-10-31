"""
Doctor Chat Models - Enhanced data models for doctor-patient messaging
Improved version with additional features and better validation
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import pytz


class MessageAttachment:
    """Enhanced message attachment schema with metadata"""
    
    def __init__(self, file_name: str, file_type: str, file_url: str, 
                 file_size: int, uploaded_at: datetime = None,
                 thumbnail_url: str = None, duration: float = None,
                 mime_type: str = None, s3_key: str = None):
        self.file_name = file_name
        self.file_type = file_type  # image, document, audio, video, voice
        self.file_url = file_url
        self.file_size = file_size  # in bytes
        self.uploaded_at = uploaded_at or datetime.utcnow()
        self.thumbnail_url = thumbnail_url  # For images and videos
        self.duration = duration  # For audio/video in seconds
        self.mime_type = mime_type
        self.s3_key = s3_key  # S3 storage key
    
    def to_dict(self):
        return {
            'file_name': self.file_name,
            'file_type': self.file_type,
            'file_url': self.file_url,
            'file_size': self.file_size,
            'uploaded_at': self.uploaded_at,
            'thumbnail_url': self.thumbnail_url,
            'duration': self.duration,
            'mime_type': self.mime_type,
            's3_key': self.s3_key
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            file_name=data.get('file_name'),
            file_type=data.get('file_type'),
            file_url=data.get('file_url'),
            file_size=data.get('file_size'),
            uploaded_at=data.get('uploaded_at'),
            thumbnail_url=data.get('thumbnail_url'),
            duration=data.get('duration'),
            mime_type=data.get('mime_type'),
            s3_key=data.get('s3_key')
        )


class MessageReaction:
    """Message reaction schema with enhanced tracking"""
    
    def __init__(self, user_id: str, user_type: str, reaction: str, 
                 created_at: datetime = None):
        self.user_id = user_id
        self.user_type = user_type  # doctor, patient
        self.reaction = reaction  # emoji or reaction type
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'user_type': self.user_type,
            'reaction': self.reaction,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            user_id=data.get('user_id'),
            user_type=data.get('user_type'),
            reaction=data.get('reaction'),
            created_at=data.get('created_at')
        )


class Message:
    """Enhanced message model with advanced features"""
    
    def __init__(self, chat_room_id: str, sender_id: str, sender_type: str, 
                 receiver_id: str, receiver_type: str, content: str,
                 message_id: str = None, message_type: str = "text",
                 attachments: List[MessageAttachment] = None, 
                 reactions: List[MessageReaction] = None,
                 is_read: bool = False, read_at: datetime = None, 
                 is_edited: bool = False, edited_at: datetime = None, 
                 is_deleted: bool = False, deleted_at: datetime = None,
                 created_at: datetime = None, updated_at: datetime = None,
                 is_urgent: bool = False, priority: str = "normal", 
                 reply_to_message_id: str = None,
                 metadata: Dict[str, Any] = None,
                 sender_name: str = None):
        
        self.message_id = message_id or f"MSG{uuid.uuid4().hex[:16].upper()}"
        self.chat_room_id = chat_room_id
        self.sender_id = sender_id
        self.sender_type = sender_type
        self.receiver_id = receiver_id
        self.receiver_type = receiver_type
        
        self.message_type = message_type
        self.content = content
        
        # Message metadata
        self.attachments = attachments or []
        self.reactions = reactions or []
        
        # Message status
        self.is_read = is_read
        self.read_at = read_at
        self.is_edited = is_edited
        self.edited_at = edited_at
        self.is_deleted = is_deleted
        self.deleted_at = deleted_at
        
        # Timestamps
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        
        # Priority and urgency
        self.is_urgent = is_urgent
        self.priority = priority
        
        # Reply to message
        self.reply_to_message_id = reply_to_message_id
        
        # Additional metadata
        self.metadata = metadata or {}
        self.sender_name = sender_name
    
    def validate(self) -> List[str]:
        """Validate message data"""
        errors = []
        
        if not self.chat_room_id or len(self.chat_room_id.strip()) == 0:
            errors.append("Chat room ID is required")
        
        if not self.sender_id or len(self.sender_id.strip()) == 0:
            errors.append("Sender ID is required")
        
        if self.sender_type not in ['doctor', 'patient', 'system']:
            errors.append("Sender type must be 'doctor', 'patient', or 'system'")
        
        if not self.receiver_id or len(self.receiver_id.strip()) == 0:
            errors.append("Receiver ID is required")
        
        if self.receiver_type not in ['doctor', 'patient']:
            errors.append("Receiver type must be 'doctor' or 'patient'")
        
        if self.message_type not in ['text', 'image', 'file', 'audio', 'video', 'voice', 'document', 'system']:
            errors.append("Invalid message type")
        
        if not self.content or len(self.content.strip()) == 0:
            errors.append("Message content is required")
        
        if len(self.content) > 5000:
            errors.append("Message content cannot exceed 5000 characters")
        
        if self.priority not in ['low', 'normal', 'high', 'urgent']:
            errors.append("Invalid priority")
        
        return errors
    
    def _serialize_datetime(self, dt):
        """Helper to serialize datetime objects or strings with IST timezone"""
        if dt is None:
            return None
        if isinstance(dt, str):
            return dt
        if hasattr(dt, 'isoformat'):
            # Convert UTC to IST (India Standard Time - UTC+5:30)
            try:
                ist_tz = pytz.timezone('Asia/Kolkata')
                if dt.tzinfo is None:
                    # Assume naive datetime is UTC
                    dt = pytz.utc.localize(dt)
                ist_time = dt.astimezone(ist_tz)
                return ist_time.isoformat()
            except:
                # Fallback to original if conversion fails
                return dt.isoformat()
        return str(dt)
    
    def to_dict(self):
        return {
            'message_id': self.message_id,
            'chat_room_id': self.chat_room_id,
            'sender_id': self.sender_id,
            'sender_type': self.sender_type,
            'receiver_id': self.receiver_id,
            'receiver_type': self.receiver_type,
            'message_type': self.message_type,
            'content': self.content,
            'attachments': [att.to_dict() for att in self.attachments],
            'reactions': [react.to_dict() for react in self.reactions],
            'is_read': self.is_read,
            'read_at': self._serialize_datetime(self.read_at),
            'is_edited': self.is_edited,
            'edited_at': self._serialize_datetime(self.edited_at),
            'is_deleted': self.is_deleted,
            'deleted_at': self._serialize_datetime(self.deleted_at),
            'created_at': self._serialize_datetime(self.created_at),
            'updated_at': self._serialize_datetime(self.updated_at),
            'is_urgent': self.is_urgent,
            'priority': self.priority,
            'reply_to_message_id': self.reply_to_message_id,
            'metadata': self.metadata,
            'sender_name': self.sender_name
        }
    
    @classmethod
    def _parse_datetime(cls, value):
        """Helper to parse datetime from various formats"""
        from dateutil import parser as date_parser
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return date_parser.parse(value)
            except:
                return None
        return None
    
    @classmethod
    def from_dict(cls, data: dict):
        attachments = [MessageAttachment.from_dict(att) for att in data.get('attachments', [])]
        reactions = [MessageReaction.from_dict(react) for react in data.get('reactions', [])]
        
        return cls(
            message_id=data.get('message_id'),
            chat_room_id=data.get('chat_room_id'),
            sender_id=data.get('sender_id'),
            sender_type=data.get('sender_type'),
            receiver_id=data.get('receiver_id'),
            receiver_type=data.get('receiver_type'),
            message_type=data.get('message_type', 'text'),
            content=data.get('content'),
            attachments=attachments,
            reactions=reactions,
            is_read=data.get('is_read', False),
            read_at=cls._parse_datetime(data.get('read_at')),
            is_edited=data.get('is_edited', False),
            edited_at=cls._parse_datetime(data.get('edited_at')),
            is_deleted=data.get('is_deleted', False),
            deleted_at=cls._parse_datetime(data.get('deleted_at')),
            created_at=cls._parse_datetime(data.get('created_at')) or datetime.utcnow(),
            updated_at=cls._parse_datetime(data.get('updated_at')) or datetime.utcnow(),
            is_urgent=data.get('is_urgent', False),
            priority=data.get('priority', 'normal'),
            reply_to_message_id=data.get('reply_to_message_id'),
            metadata=data.get('metadata', {}),
            sender_name=data.get('sender_name')
        )


class ChatRoom:
    """Enhanced chat room model with advanced features"""
    
    def __init__(self, doctor_id: str, patient_id: str, room_id: str = None,
                 last_message: str = None, last_message_time: datetime = None,
                 last_message_id: str = None,
                 unread_count_doctor: int = 0, unread_count_patient: int = 0,
                 is_active: bool = True, is_archived: bool = False,
                 created_at: datetime = None, updated_at: datetime = None,
                 room_name: str = None, room_description: str = None,
                 tags: List[str] = None, pinned_by_doctor: bool = False,
                 notifications_enabled_doctor: bool = True,
                 notifications_enabled_patient: bool = True):
        
        self.room_id = room_id or f"ROOM{uuid.uuid4().hex[:16].upper()}"
        self.doctor_id = doctor_id
        self.patient_id = patient_id
        
        self.last_message = last_message
        self.last_message_time = last_message_time
        self.last_message_id = last_message_id
        
        self.unread_count_doctor = unread_count_doctor
        self.unread_count_patient = unread_count_patient
        
        self.is_active = is_active
        self.is_archived = is_archived
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        
        # Enhanced features
        self.room_name = room_name
        self.room_description = room_description
        self.tags = tags or []
        self.pinned_by_doctor = pinned_by_doctor
        self.notifications_enabled_doctor = notifications_enabled_doctor
        self.notifications_enabled_patient = notifications_enabled_patient
    
    def validate(self) -> List[str]:
        """Validate chat room data"""
        errors = []
        
        if not self.doctor_id or len(self.doctor_id.strip()) == 0:
            errors.append("Doctor ID is required")
        
        if not self.patient_id or len(self.patient_id.strip()) == 0:
            errors.append("Patient ID is required")
        
        return errors
    
    def _serialize_datetime(self, dt):
        """Helper to serialize datetime objects or strings with IST timezone"""
        if dt is None:
            return None
        if isinstance(dt, str):
            return dt
        if hasattr(dt, 'isoformat'):
            # Convert UTC to IST (India Standard Time - UTC+5:30)
            try:
                ist_tz = pytz.timezone('Asia/Kolkata')
                if dt.tzinfo is None:
                    # Assume naive datetime is UTC
                    dt = pytz.utc.localize(dt)
                ist_time = dt.astimezone(ist_tz)
                return ist_time.isoformat()
            except:
                # Fallback to original if conversion fails
                return dt.isoformat()
        return str(dt)
    
    def to_dict(self):
        return {
            'room_id': self.room_id,
            'doctor_id': self.doctor_id,
            'patient_id': self.patient_id,
            'last_message': self.last_message,
            'last_message_at': self._serialize_datetime(self.last_message_time),
            'last_message_id': self.last_message_id,
            'unread_count': self.unread_count_doctor,
            'is_active': self.is_active,
            'is_archived': self.is_archived,
            'created_at': self._serialize_datetime(self.created_at),
            'updated_at': self._serialize_datetime(self.updated_at),
            'room_name': self.room_name,
            'room_description': self.room_description,
            'tags': self.tags,
            'pinned_by_doctor': self.pinned_by_doctor,
            'notifications_enabled_doctor': self.notifications_enabled_doctor,
            'notifications_enabled_patient': self.notifications_enabled_patient
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            room_id=data.get('room_id'),
            doctor_id=data.get('doctor_id'),
            patient_id=data.get('patient_id'),
            last_message=data.get('last_message'),
            last_message_time=data.get('last_message_time'),
            last_message_id=data.get('last_message_id'),
            unread_count_doctor=data.get('unread_count_doctor', 0),
            unread_count_patient=data.get('unread_count_patient', 0),
            is_active=data.get('is_active', True),
            is_archived=data.get('is_archived', False),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            room_name=data.get('room_name'),
            room_description=data.get('room_description'),
            tags=data.get('tags', []),
            pinned_by_doctor=data.get('pinned_by_doctor', False),
            notifications_enabled_doctor=data.get('notifications_enabled_doctor', True),
            notifications_enabled_patient=data.get('notifications_enabled_patient', True)
        )


class ChatAnalytics:
    """Analytics model for chat statistics"""
    
    def __init__(self, room_id: str, total_messages: int = 0,
                 messages_by_doctor: int = 0, messages_by_patient: int = 0,
                 avg_response_time_doctor: float = 0.0,
                 avg_response_time_patient: float = 0.0,
                 total_attachments: int = 0, last_updated: datetime = None):
        
        self.room_id = room_id
        self.total_messages = total_messages
        self.messages_by_doctor = messages_by_doctor
        self.messages_by_patient = messages_by_patient
        self.avg_response_time_doctor = avg_response_time_doctor
        self.avg_response_time_patient = avg_response_time_patient
        self.total_attachments = total_attachments
        self.last_updated = last_updated or datetime.utcnow()
    
    def to_dict(self):
        return {
            'room_id': self.room_id,
            'total_messages': self.total_messages,
            'messages_by_doctor': self.messages_by_doctor,
            'messages_by_patient': self.messages_by_patient,
            'avg_response_time_doctor': self.avg_response_time_doctor,
            'avg_response_time_patient': self.avg_response_time_patient,
            'total_attachments': self.total_attachments,
            'last_updated': self.last_updated
        }


