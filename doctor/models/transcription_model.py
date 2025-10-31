#!/usr/bin/env python3
"""
Transcription Model - Database operations for transcription management
"""

from datetime import datetime
from typing import Dict, Any, List, Optional

class TranscriptionModel:
    """Model for transcription-related database operations"""
    
    def __init__(self, db):
        self.db = db
        self.transcriptions_collection = db.db.transcriptions
        self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes for transcriptions collection"""
        try:
            # Create indexes for transcriptions collection
            self.transcriptions_collection.create_index("transcription_id", unique=True)
            self.transcriptions_collection.create_index("conversation_id")
            self.transcriptions_collection.create_index("is_final")
            self.transcriptions_collection.create_index("language")
            self.transcriptions_collection.create_index("speaker_id")
            self.transcriptions_collection.create_index("created_at")
        except Exception as e:
            print(f"Warning: Could not create transcription indexes: {e}")
    
    def create_transcription(self, transcription_data: Dict[str, Any]) -> str:
        """Create a new transcription"""
        try:
            # Generate transcription ID
            transcription_id = int(datetime.now().timestamp() * 1000)
            
            # Prepare transcription document
            transcription_doc = {
                "transcription_id": transcription_id,
                "conversation_id": transcription_data.get("conversation_id"),
                "text": transcription_data.get("text", ""),
                "confidence": transcription_data.get("confidence", 0.0),
                "is_final": transcription_data.get("is_final", False),
                "start_time": transcription_data.get("start_time", 0.0),
                "end_time": transcription_data.get("end_time", 0.0),
                "language": transcription_data.get("language", "en"),
                "speaker_id": transcription_data.get("speaker_id", "unknown"),
                "created_at": transcription_data.get("created_at", datetime.now().isoformat()),
                "updated_at": transcription_data.get("created_at", datetime.now().isoformat())
            }
            
            # Insert transcription
            result = self.transcriptions_collection.insert_one(transcription_doc)
            
            return transcription_id
            
        except Exception as e:
            print(f"Error creating transcription: {e}")
            raise e
    
    def get_transcription_by_id(self, transcription_id: int) -> Optional[Dict[str, Any]]:
        """Get transcription by ID"""
        try:
            transcription = self.transcriptions_collection.find_one({"transcription_id": transcription_id})
            
            if not transcription:
                return None
            
            return {
                'id': transcription_id,
                'transcription_id': transcription['transcription_id'],
                'conversation_id': transcription['conversation_id'],
                'text': transcription['text'],
                'confidence': transcription['confidence'],
                'is_final': transcription['is_final'],
                'start_time': transcription['start_time'],
                'end_time': transcription['end_time'],
                'language': transcription['language'],
                'speaker_id': transcription['speaker_id'],
                'created_at': transcription['created_at'],
                'updated_at': transcription['updated_at']
            }
            
        except Exception as e:
            print(f"Error getting transcription: {e}")
            return None
    
    def get_transcriptions(self, filters: Dict[str, Any] = None, page: int = 1, limit: int = 50) -> List[Dict[str, Any]]:
        """Get transcriptions with pagination and filters"""
        try:
            if filters is None:
                filters = {}
            
            # Calculate skip
            skip = (page - 1) * limit
            
            # Find transcriptions
            cursor = self.transcriptions_collection.find(filters).skip(skip).limit(limit).sort("created_at", -1)
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
                    'created_at': transcription['created_at'],
                    'updated_at': transcription['updated_at']
                })
            
            return transcriptions
            
        except Exception as e:
            print(f"Error getting transcriptions: {e}")
            return []
    
    def update_transcription(self, transcription_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update transcription"""
        try:
            update_data["updated_at"] = datetime.now().isoformat()
            
            result = self.transcriptions_collection.update_one(
                {"transcription_id": transcription_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return self.get_transcription_by_id(transcription_id)
            
            return None
            
        except Exception as e:
            print(f"Error updating transcription: {e}")
            return None
    
    def delete_transcription(self, transcription_id: int) -> bool:
        """Delete transcription"""
        try:
            result = self.transcriptions_collection.delete_one({"transcription_id": transcription_id})
            return result.deleted_count > 0
            
        except Exception as e:
            print(f"Error deleting transcription: {e}")
            return False
    
    def count_transcriptions(self, filters: Dict[str, Any] = None) -> int:
        """Count transcriptions with filters"""
        try:
            if filters is None:
                filters = {}
            
            return self.transcriptions_collection.count_documents(filters)
            
        except Exception as e:
            print(f"Error counting transcriptions: {e}")
            return 0
    
    def get_transcriptions_by_conversation(self, conversation_id: int, page: int = 1, limit: int = 50, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get transcriptions for a specific conversation"""
        try:
            if filters is None:
                filters = {}
            
            # Add conversation_id to filters
            filters["conversation_id"] = conversation_id
            
            # Calculate skip
            skip = (page - 1) * limit
            
            # Find transcriptions
            cursor = self.transcriptions_collection.find(filters).skip(skip).limit(limit).sort("created_at", 1)
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
                    'created_at': transcription['created_at'],
                    'updated_at': transcription['updated_at']
                })
            
            return transcriptions
            
        except Exception as e:
            print(f"Error getting transcriptions by conversation: {e}")
            return []
    
    def get_final_transcriptions_by_conversation(self, conversation_id: int, page: int = 1, limit: int = 50) -> List[Dict[str, Any]]:
        """Get only final transcriptions for a conversation"""
        try:
            filters = {
                "conversation_id": conversation_id,
                "is_final": True
            }
            
            return self.get_transcriptions_by_conversation(conversation_id, page, limit, filters)
            
        except Exception as e:
            print(f"Error getting final transcriptions: {e}")
            return []
    
    def update_conversation_transcription_count(self, conversation_id: int) -> bool:
        """Update transcription count for a conversation"""
        try:
            # Count transcriptions for this conversation
            count = self.transcriptions_collection.count_documents({"conversation_id": conversation_id})
            
            # Update conversation with new count
            result = self.db.db.conversations.update_one(
                {"conversation_id": conversation_id},
                {
                    "$set": {
                        "transcription_count": count,
                        "updated_at": datetime.now().isoformat()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error updating conversation transcription count: {e}")
            return False
