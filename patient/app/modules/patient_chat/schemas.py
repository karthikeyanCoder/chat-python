"""
Chat Schemas - Request/Response validation schemas
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator


class SendMessageSchema(BaseModel):
    """Schema for sending a message"""
    patient_id: str = Field(..., description="Patient ID")
    doctor_id: str = Field(..., description="Doctor ID")
    message_content: str = Field(..., min_length=1, max_length=5000, description="Message content")
    message_type: str = Field(default="text", description="Message type")
    is_urgent: bool = Field(default=False, description="Urgent message flag")
    priority: str = Field(default="normal", description="Message priority")
    reply_to_message_id: Optional[str] = Field(None, description="Reply to message ID")
    
    @validator('message_type')
    def validate_message_type(cls, v):
        allowed_types = ['text', 'image', 'file', 'audio', 'video']
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
                "patient_id": "PAT123456",
                "doctor_id": "DOC789012",
                "message_content": "Hello doctor, I have a question about my medication.",
                "message_type": "text",
                "is_urgent": False,
                "priority": "normal"
            }
        }


class StartChatSchema(BaseModel):
    """Schema for starting a chat"""
    patient_id: str = Field(..., description="Patient ID")
    doctor_id: str = Field(..., description="Doctor ID")
    
    class Config:
        schema_extra = {
            "example": {
                "patient_id": "PAT123456",
                "doctor_id": "DOC789012"
            }
        }


class GetMessagesSchema(BaseModel):
    """Schema for getting messages"""
    patient_id: str = Field(..., description="Patient ID")
    room_id: str = Field(..., description="Room ID")
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=50, ge=1, le=100, description="Messages per page")
    
    class Config:
        schema_extra = {
            "example": {
                "patient_id": "PAT123456",
                "room_id": "ROOM1234567890ABCDEF",
                "page": 1,
                "limit": 50
            }
        }


class MarkAsReadSchema(BaseModel):
    """Schema for marking messages as read"""
    patient_id: str = Field(..., description="Patient ID")
    room_id: str = Field(..., description="Room ID")
    message_id: Optional[str] = Field(None, description="Specific message ID (optional)")
    
    class Config:
        schema_extra = {
            "example": {
                "patient_id": "PAT123456",
                "room_id": "ROOM1234567890ABCDEF"
            }
        }


class EditMessageSchema(BaseModel):
    """Schema for editing a message"""
    patient_id: str = Field(..., description="Patient ID")
    message_id: str = Field(..., description="Message ID")
    new_content: str = Field(..., min_length=1, max_length=5000, description="New message content")
    
    class Config:
        schema_extra = {
            "example": {
                "patient_id": "PAT123456",
                "message_id": "MSG1234567890ABCD",
                "new_content": "Updated message content"
            }
        }


class DeleteMessageSchema(BaseModel):
    """Schema for deleting a message"""
    patient_id: str = Field(..., description="Patient ID")
    message_id: str = Field(..., description="Message ID")
    
    class Config:
        schema_extra = {
            "example": {
                "patient_id": "PAT123456",
                "message_id": "MSG1234567890ABCD"
            }
        }


class SearchMessagesSchema(BaseModel):
    """Schema for searching messages"""
    patient_id: str = Field(..., description="Patient ID")
    search_query: str = Field(..., min_length=1, max_length=100, description="Search query")
    limit: int = Field(default=20, ge=1, le=50, description="Maximum results")
    
    class Config:
        schema_extra = {
            "example": {
                "patient_id": "PAT123456",
                "search_query": "medication",
                "limit": 20
            }
        }


class AttachmentSchema(BaseModel):
    """Schema for file attachment"""
    file_name: str
    file_type: str
    file_url: str
    file_size: int
    uploaded_at: Optional[datetime] = None


class ReactionSchema(BaseModel):
    """Schema for message reaction"""
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


class ChatRoomResponseSchema(BaseModel):
    """Schema for chat room response"""
    room_id: str
    doctor_id: str
    patient_id: str
    last_message: Optional[str] = None
    last_message_time: Optional[datetime] = None
    unread_count_doctor: int
    unread_count_patient: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class DoctorInfoSchema(BaseModel):
    """Schema for doctor information in chat"""
    doctor_id: str
    name: str
    specialization: Optional[str] = None
    hospital: Optional[str] = None
    consultation_fee: Optional[float] = None
    experience_years: Optional[int] = None


class EnrichedChatRoomSchema(ChatRoomResponseSchema):
    """Schema for enriched chat room with doctor info"""
    doctor_info: Optional[DoctorInfoSchema] = None


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


# Socket event schemas
class SocketAuthSchema(BaseModel):
    """Schema for socket authentication"""
    user_id: str
    user_type: str
    user_name: Optional[str] = None


class SocketJoinRoomSchema(BaseModel):
    """Schema for joining a room"""
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
