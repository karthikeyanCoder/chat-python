"""
Doctor Chat Schemas - Enhanced Pydantic validation schemas
Request/Response schemas for doctor chat API endpoints
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator


# ==================== Request Schemas ====================

class SendMessageSchema(BaseModel):
    """Schema for sending a message from doctor to patient"""
    doctor_id: str = Field(..., description="Doctor ID")
    patient_id: str = Field(..., description="Patient ID")
    message_content: str = Field(..., min_length=1, max_length=5000, description="Message content")
    message_type: str = Field(default="text", description="Message type")
    is_urgent: bool = Field(default=False, description="Urgent message flag")
    priority: str = Field(default="normal", description="Message priority")
    reply_to_message_id: Optional[str] = Field(None, description="Reply to message ID")
    attachment: Optional[dict] = Field(None, description="File attachment data (for image/document/voice messages)")
    
    @validator('message_type')
    def validate_message_type(cls, v):
        allowed_types = ['text', 'image', 'file', 'audio', 'video', 'voice', 'document']
        if v not in allowed_types:
            raise ValueError(f"message_type must be one of {allowed_types}")
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        allowed_priorities = ['low', 'normal', 'high', 'urgent']
        if v not in allowed_priorities:
            raise ValueError(f"priority must be one of {allowed_priorities}")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "doctor_id": "DOC123456",
                "patient_id": "PAT789012",
                "message_content": "Hello, I've reviewed your test results.",
                "message_type": "text",
                "is_urgent": False,
                "priority": "normal",
                "attachment": {
                    "file_url": "https://s3.amazonaws.com/...",
                    "file_name": "test_result.pdf",
                    "file_type": "document",
                    "file_size": 245760
                }
            }
        }


class StartChatSchema(BaseModel):
    """Schema for starting a chat with a patient"""
    doctor_id: str = Field(..., description="Doctor ID")
    patient_id: str = Field(..., description="Patient ID")
    
    class Config:
        schema_extra = {
            "example": {
                "doctor_id": "DOC123456",
                "patient_id": "PAT789012"
            }
        }


class GetMessagesSchema(BaseModel):
    """Schema for getting messages from a chat room"""
    doctor_id: str = Field(..., description="Doctor ID")
    room_id: str = Field(..., description="Room ID")
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=50, ge=1, le=100, description="Messages per page")
    
    class Config:
        schema_extra = {
            "example": {
                "doctor_id": "DOC123456",
                "room_id": "ROOM1234567890ABCDEF",
                "page": 1,
                "limit": 50
            }
        }


class MarkAsReadSchema(BaseModel):
    """Schema for marking messages as read"""
    doctor_id: str = Field(..., description="Doctor ID")
    room_id: str = Field(..., description="Room ID")
    message_id: Optional[str] = Field(None, description="Specific message ID (optional)")
    
    class Config:
        schema_extra = {
            "example": {
                "doctor_id": "DOC123456",
                "room_id": "ROOM1234567890ABCDEF"
            }
        }


class EditMessageSchema(BaseModel):
    """Schema for editing a message"""
    doctor_id: str = Field(..., description="Doctor ID")
    message_id: str = Field(..., description="Message ID")
    new_content: str = Field(..., min_length=1, max_length=5000, description="New message content")
    
    class Config:
        schema_extra = {
            "example": {
                "doctor_id": "DOC123456",
                "message_id": "MSG1234567890ABCD",
                "new_content": "Updated message content"
            }
        }


class DeleteMessageSchema(BaseModel):
    """Schema for deleting a message"""
    doctor_id: str = Field(..., description="Doctor ID")
    message_id: str = Field(..., description="Message ID")
    
    class Config:
        schema_extra = {
            "example": {
                "doctor_id": "DOC123456",
                "message_id": "MSG1234567890ABCD"
            }
        }


class SearchMessagesSchema(BaseModel):
    """Schema for searching messages"""
    doctor_id: str = Field(..., description="Doctor ID")
    search_query: str = Field(..., min_length=1, max_length=100, description="Search query")
    room_id: Optional[str] = Field(None, description="Specific room ID (optional)")
    limit: int = Field(default=20, ge=1, le=50, description="Maximum results")
    
    class Config:
        schema_extra = {
            "example": {
                "doctor_id": "DOC123456",
                "search_query": "prescription",
                "limit": 20
            }
        }


class SearchPatientsSchema(BaseModel):
    """Schema for searching patients"""
    doctor_id: str = Field(..., description="Doctor ID")
    search_query: str = Field(..., min_length=1, max_length=100, description="Search query")
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=20, ge=1, le=50, description="Maximum results")
    
    class Config:
        schema_extra = {
            "example": {
                "doctor_id": "DOC123456",
                "search_query": "Jane",
                "page": 1,
                "limit": 20
            }
        }


class AddReactionSchema(BaseModel):
    """Schema for adding a reaction to a message"""
    doctor_id: str = Field(..., description="Doctor ID")
    message_id: str = Field(..., description="Message ID")
    reaction: str = Field(..., description="Reaction emoji or type")
    
    class Config:
        schema_extra = {
            "example": {
                "doctor_id": "DOC123456",
                "message_id": "MSG1234567890ABCD",
                "reaction": "👍"
            }
        }


class UpdateRoomSettingsSchema(BaseModel):
    """Schema for updating chat room settings"""
    doctor_id: str = Field(..., description="Doctor ID")
    room_id: str = Field(..., description="Room ID")
    room_name: Optional[str] = Field(None, description="Room name")
    room_description: Optional[str] = Field(None, description="Room description")
    tags: Optional[List[str]] = Field(None, description="Room tags")
    pinned: Optional[bool] = Field(None, description="Pin room")
    notifications_enabled: Optional[bool] = Field(None, description="Enable notifications")
    archived: Optional[bool] = Field(None, description="Archive room")
    
    class Config:
        schema_extra = {
            "example": {
                "doctor_id": "DOC123456",
                "room_id": "ROOM1234567890ABCDEF",
                "pinned": True,
                "tags": ["urgent", "pregnancy"]
            }
        }


# ==================== Response Schemas ====================

class AttachmentSchema(BaseModel):
    """Schema for file attachment in response"""
    file_name: str
    file_type: str
    file_url: str
    file_size: int
    uploaded_at: Optional[datetime] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[float] = None
    mime_type: Optional[str] = None
    s3_key: Optional[str] = None


class ReactionSchema(BaseModel):
    """Schema for message reaction in response"""
    user_id: str
    user_type: str
    reaction: str
    created_at: Optional[datetime] = None


class MessageResponseSchema(BaseModel):
    """Schema for message response"""
    message_id: str
    chat_room_id: str
    sender_id: str
    sender_type: str
    receiver_id: str
    receiver_type: str
    message_type: str
    content: str
    attachments: List[AttachmentSchema] = []
    reactions: List[ReactionSchema] = []
    is_read: bool
    read_at: Optional[datetime] = None
    is_edited: bool
    edited_at: Optional[datetime] = None
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    is_urgent: bool
    priority: str
    reply_to_message_id: Optional[str] = None
    sender_name: Optional[str] = None


class PatientInfoSchema(BaseModel):
    """Schema for patient information in chat"""
    patient_id: str
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    is_pregnant: Optional[bool] = None
    pregnancy_week: Optional[int] = None
    profile_picture: Optional[str] = None
    last_seen: Optional[datetime] = None
    is_online: Optional[bool] = False


class ChatRoomResponseSchema(BaseModel):
    """Schema for chat room response"""
    room_id: str
    doctor_id: str
    patient_id: str
    last_message: Optional[str] = None
    last_message_time: Optional[datetime] = None
    last_message_id: Optional[str] = None
    unread_count_doctor: int
    unread_count_patient: int
    is_active: bool
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    room_name: Optional[str] = None
    room_description: Optional[str] = None
    tags: List[str] = []
    pinned_by_doctor: bool
    notifications_enabled_doctor: bool
    notifications_enabled_patient: bool


class EnrichedChatRoomSchema(ChatRoomResponseSchema):
    """Schema for enriched chat room with patient info"""
    patient_info: Optional[PatientInfoSchema] = None


class ApiResponseSchema(BaseModel):
    """Generic API response schema"""
    success: bool
    message: str
    data: Optional[dict] = None


class PaginatedMessagesSchema(BaseModel):
    """Schema for paginated messages response"""
    messages: List[MessageResponseSchema]
    total_messages: int
    page: int
    limit: int
    has_more: bool


class UnreadCountSchema(BaseModel):
    """Schema for unread count response"""
    total_unread: int
    unread_by_room: List[dict] = []


class ChatAnalyticsSchema(BaseModel):
    """Schema for chat analytics"""
    room_id: str
    total_messages: int
    messages_by_doctor: int
    messages_by_patient: int
    avg_response_time_doctor: float
    avg_response_time_patient: float
    total_attachments: int
    last_updated: datetime


class PatientHealthSummarySchema(BaseModel):
    """Schema for patient health summary"""
    patient_id: str
    basic_info: dict
    pregnancy_info: Optional[dict] = None
    health_data: dict
    emergency_contact: Optional[dict] = None
    recent_logs: dict


# ==================== Socket Event Schemas ====================

class SocketAuthSchema(BaseModel):
    """Schema for socket authentication"""
    user_id: str
    user_type: str
    user_name: Optional[str] = None


class SocketJoinRoomSchema(BaseModel):
    """Schema for joining a room via socket"""
    room_id: str


class SocketSendMessageSchema(BaseModel):
    """Schema for sending a message via socket"""
    room_id: str
    content: str
    message_type: str = "text"
    is_urgent: bool = False
    priority: str = "normal"
    reply_to_message_id: Optional[str] = None


class SocketTypingSchema(BaseModel):
    """Schema for typing indicator"""
    room_id: str
    is_typing: bool


class SocketReadReceiptSchema(BaseModel):
    """Schema for read receipt"""
    message_id: str
    room_id: str


