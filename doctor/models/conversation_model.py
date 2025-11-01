#!/usr/bin/env python3
"""
Conversation Model - Database operations for conversation management
"""

from datetime import datetime
from typing import Dict, Any, List, Optional

class ConversationModel:
    """Model for conversation-related database operations"""
    
    def __init__(self, db):
        self.db = db
        # Check if database connection is valid
        is_connected = getattr(db, 'is_connected', False)
        if db is not None and db.db is not None and is_connected:
            self.conversations_collection = db.db.conversations
            self._create_indexes()
        else:
            self.conversations_collection = None
            print("⚠️ Warning: Database not connected. ConversationModel operating in fallback mode.")
    
    def _create_indexes(self):
        """Create database indexes for conversations collection"""
        if self.conversations_collection is None:
            return
        try:
            # Create indexes for conversations collection
            self.conversations_collection.create_index("conversation_id", unique=True)
            self.conversations_collection.create_index("title")
            self.conversations_collection.create_index("language")
            self.conversations_collection.create_index("is_active")
            self.conversations_collection.create_index("created_at")
            self.conversations_collection.create_index("updated_at")
        except Exception as e:
            error_msg = str(e)
            if 'IndexKeySpecsConflict' in error_msg or 'already exists' in error_msg.lower():
                pass  # Index already exists, that's fine
            else:
                print(f"Warning: Could not create conversation indexes: {e}")
    
    def create_conversation(self, conversation_data: Dict[str, Any]) -> str:
        """Create a new conversation"""
        try:
            # Generate conversation ID
            conversation_id = int(datetime.now().timestamp() * 1000)
            
            # Prepare conversation document
            conversation_doc = {
                "conversation_id": conversation_id,
                "title": conversation_data.get("title", "New Conversation"),
                "language": conversation_data.get("language", "en"),
                "is_active": conversation_data.get("is_active", True),
                "duration_seconds": conversation_data.get("duration_seconds", 0.0),
                "transcription_count": conversation_data.get("transcription_count", 0),
                "extra_data": conversation_data.get("extra_data", {}),
                "created_at": conversation_data.get("created_at", datetime.now().isoformat()),
                "updated_at": conversation_data.get("updated_at", datetime.now().isoformat())
            }
            
            # Insert conversation
            result = self.conversations_collection.insert_one(conversation_doc)
            
            return conversation_id
            
        except Exception as e:
            print(f"Error creating conversation: {e}")
            raise e
    
    def get_conversation_by_id(self, conversation_id: int) -> Optional[Dict[str, Any]]:
        """Get conversation by ID"""
        try:
            conversation = self.conversations_collection.find_one({"conversation_id": conversation_id})
            
            if not conversation:
                return None
            
            return {
                'id': conversation_id,
                'conversation_id': conversation['conversation_id'],
                'title': conversation['title'],
                'language': conversation['language'],
                'is_active': conversation['is_active'],
                'duration_seconds': conversation['duration_seconds'],
                'transcription_count': conversation['transcription_count'],
                'extra_data': conversation.get('extra_data', {}),
                'created_at': conversation['created_at'],
                'updated_at': conversation['updated_at']
            }
            
        except Exception as e:
            print(f"Error getting conversation: {e}")
            return None
    
    def get_conversations(self, filters: Dict[str, Any] = None, page: int = 1, limit: int = 10) -> List[Dict[str, Any]]:
        """Get conversations with pagination and filters"""
        try:
            if filters is None:
                filters = {}
            
            # Calculate skip
            skip = (page - 1) * limit
            
            # Find conversations
            cursor = self.conversations_collection.find(filters).skip(skip).limit(limit).sort("created_at", -1)
            conversations = []
            
            for conversation in cursor:
                conversations.append({
                    'id': conversation['conversation_id'],
                    'conversation_id': conversation['conversation_id'],
                    'title': conversation['title'],
                    'language': conversation['language'],
                    'is_active': conversation['is_active'],
                    'duration_seconds': conversation['duration_seconds'],
                    'transcription_count': conversation['transcription_count'],
                    'extra_data': conversation.get('extra_data', {}),
                    'created_at': conversation['created_at'],
                    'updated_at': conversation['updated_at']
                })
            
            return conversations
            
        except Exception as e:
            print(f"Error getting conversations: {e}")
            return []
    
    def update_conversation(self, conversation_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update conversation"""
        try:
            update_data["updated_at"] = datetime.now().isoformat()
            
            result = self.conversations_collection.update_one(
                {"conversation_id": conversation_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return self.get_conversation_by_id(conversation_id)
            
            return None
            
        except Exception as e:
            print(f"Error updating conversation: {e}")
            return None
    
    def delete_conversation(self, conversation_id: int) -> bool:
        """Delete conversation"""
        try:
            result = self.conversations_collection.delete_one({"conversation_id": conversation_id})
            return result.deleted_count > 0
            
        except Exception as e:
            print(f"Error deleting conversation: {e}")
            return False
    
    def count_conversations(self, filters: Dict[str, Any] = None) -> int:
        """Count conversations with filters"""
        try:
            if filters is None:
                filters = {}
            
            return self.conversations_collection.count_documents(filters)
            
        except Exception as e:
            print(f"Error counting conversations: {e}")
            return 0
    
    def get_conversation_transcriptions(self, conversation_id: int, page: int = 1, limit: int = 50, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get transcriptions for a conversation"""
        try:
            if filters is None:
                filters = {}
            
            # Add conversation_id to filters
            filters["conversation_id"] = conversation_id
            
            # Calculate skip
            skip = (page - 1) * limit
            
            # Find transcriptions
            cursor = self.db.db.transcriptions.find(filters).skip(skip).limit(limit).sort("created_at", 1)
            transcriptions = []
            
            for transcription in cursor:
                transcriptions.append({
                    'id': transcription['transcription_id'],
                    'transcription_id': transcription['transcription_id'],
                    'conversation_id': transcription['conversation_id'],
                    'text': transcription['text'],
                    'confidence': transcription['confidence'],
                    'is_final': transcription['is_final'],
                    'start_time': transcription['start_time'],
                    'end_time': transcription['end_time'],
                    'language': transcription['language'],
                    'speaker_id': transcription['speaker_id'],
                    'created_at': transcription['created_at']
                })
            
            return transcriptions
            
        except Exception as e:
            print(f"Error getting conversation transcriptions: {e}")
            return []
    
    def update_conversation_stats(self, conversation_id: int, duration_seconds: float = None, transcription_count: int = None) -> bool:
        """Update conversation statistics"""
        try:
            update_data = {"updated_at": datetime.now().isoformat()}
            
            if duration_seconds is not None:
                update_data["duration_seconds"] = duration_seconds
            
            if transcription_count is not None:
                update_data["transcription_count"] = transcription_count
            
            result = self.conversations_collection.update_one(
                {"conversation_id": conversation_id},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error updating conversation stats: {e}")
            return False
