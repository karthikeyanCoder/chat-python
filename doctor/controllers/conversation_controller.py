#!/usr/bin/env python3
"""
Conversation Controller - Handles conversation management
"""

from flask import request, jsonify
from datetime import datetime
import time
from typing import Dict, Any, List, Optional

class ConversationController:
    """Controller for conversation management operations"""
    
    def __init__(self, conversation_model, jwt_service, validators):
        self.conversation_model = conversation_model
        self.jwt_service = jwt_service
        self.validators = validators
    
    def create_conversation(self, request):
        """Create a new conversation"""
        try:
            data = request.get_json()
            
            # Validate required fields
            if not data:
                return jsonify({
                    "success": False,
                    "error": "Request body is required"
                }), 400
            
            # Extract conversation data
            conversation_data = {
                "title": data.get("title", "New Conversation"),
                "language": data.get("language", "en"),
                "extra_data": data.get("extra_data", {}),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "is_active": True,
                "duration_seconds": 0.0,
                "transcription_count": 0
            }
            
            # Create conversation in database
            conversation_id = self.conversation_model.create_conversation(conversation_data)
            
            return jsonify({
                "success": True,
                "data": {
                    "id": conversation_id,
                    "title": conversation_data["title"],
                    "language": conversation_data["language"],
                    "is_active": conversation_data["is_active"],
                    "duration_seconds": conversation_data["duration_seconds"],
                    "transcription_count": conversation_data["transcription_count"],
                    "extra_data": conversation_data["extra_data"],
                    "created_at": conversation_data["created_at"],
                    "updated_at": conversation_data["updated_at"]
                },
                "message": "Conversation created successfully"
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    def get_conversations(self, request):
        """Get all conversations with pagination and filters"""
        try:
            # Get query parameters
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 10))
            search = request.args.get('search', '')
            language = request.args.get('language', '')
            is_active = request.args.get('is_active', '')
            
            # Build filters
            filters = {}
            if search:
                filters['title'] = {'$regex': search, '$options': 'i'}
            if language:
                filters['language'] = language
            if is_active:
                filters['is_active'] = is_active.lower() == 'true'
            
            # Get conversations from database
            conversations = self.conversation_model.get_conversations(
                filters=filters,
                page=page,
                limit=limit
            )
            
            # Get total count
            total_count = self.conversation_model.count_conversations(filters)
            
            return jsonify({
                "success": True,
                "data": {
                    "conversations": conversations,
                    "pagination": {
                        "page": page,
                        "limit": limit,
                        "total": total_count,
                        "pages": (total_count + limit - 1) // limit
                    }
                },
                "message": "Conversations retrieved successfully"
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    def get_conversation(self, request, conversation_id):
        """Get conversation by ID"""
        try:
            conversation = self.conversation_model.get_conversation_by_id(conversation_id)
            
            if not conversation:
                return jsonify({
                    "success": False,
                    "error": "Conversation not found"
                }), 404
            
            return jsonify({
                "success": True,
                "data": conversation,
                "message": "Conversation retrieved successfully"
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    def update_conversation(self, request, conversation_id):
        """Update conversation by ID"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    "success": False,
                    "error": "Request body is required"
                }), 400
            
            # Check if conversation exists
            existing_conversation = self.conversation_model.get_conversation_by_id(conversation_id)
            if not existing_conversation:
                return jsonify({
                    "success": False,
                    "error": "Conversation not found"
                }), 404
            
            # Prepare update data
            update_data = {
                "updated_at": datetime.now().isoformat()
            }
            
            if "title" in data:
                update_data["title"] = data["title"]
            if "language" in data:
                update_data["language"] = data["language"]
            if "extra_data" in data:
                update_data["extra_data"] = data["extra_data"]
            if "is_active" in data:
                update_data["is_active"] = data["is_active"]
            
            # Update conversation
            updated_conversation = self.conversation_model.update_conversation(conversation_id, update_data)
            
            return jsonify({
                "success": True,
                "data": updated_conversation,
                "message": "Conversation updated successfully"
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    def delete_conversation(self, request, conversation_id):
        """Delete conversation by ID"""
        try:
            # Check if conversation exists
            existing_conversation = self.conversation_model.get_conversation_by_id(conversation_id)
            if not existing_conversation:
                return jsonify({
                    "success": False,
                    "error": "Conversation not found"
                }), 404
            
            # Delete conversation
            self.conversation_model.delete_conversation(conversation_id)
            
            return jsonify({
                "success": True,
                "message": "Conversation deleted successfully"
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    def get_transcriptions(self, request, conversation_id):
        """Get all transcriptions for a conversation"""
        try:
            # Check if conversation exists
            conversation = self.conversation_model.get_conversation_by_id(conversation_id)
            if not conversation:
                return jsonify({
                    "success": False,
                    "error": "Conversation not found"
                }), 404
            
            # Get query parameters
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 50))
            is_final = request.args.get('is_final', '')
            
            # Build filters
            filters = {"conversation_id": conversation_id}
            if is_final:
                filters["is_final"] = is_final.lower() == 'true'
            
            # Get transcriptions
            transcriptions = self.conversation_model.get_conversation_transcriptions(
                conversation_id,
                page=page,
                limit=limit,
                filters=filters
            )
            
            return jsonify({
                "success": True,
                "data": {
                    "conversation_id": conversation_id,
                    "transcriptions": transcriptions,
                    "pagination": {
                        "page": page,
                        "limit": limit
                    }
                },
                "message": "Conversation transcriptions retrieved successfully"
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    def activate_conversation(self, request, conversation_id):
        """Activate a conversation"""
        try:
            # Check if conversation exists
            conversation = self.conversation_model.get_conversation_by_id(conversation_id)
            if not conversation:
                return jsonify({
                    "success": False,
                    "error": "Conversation not found"
                }), 404
            
            # Activate conversation
            update_data = {
                "is_active": True,
                "updated_at": datetime.now().isoformat()
            }
            
            updated_conversation = self.conversation_model.update_conversation(conversation_id, update_data)
            
            return jsonify({
                "success": True,
                "data": updated_conversation,
                "message": "Conversation activated successfully"
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    def deactivate_conversation(self, request, conversation_id):
        """Deactivate a conversation"""
        try:
            # Check if conversation exists
            conversation = self.conversation_model.get_conversation_by_id(conversation_id)
            if not conversation:
                return jsonify({
                    "success": False,
                    "error": "Conversation not found"
                }), 404
            
            # Deactivate conversation
            update_data = {
                "is_active": False,
                "updated_at": datetime.now().isoformat()
            }
            
            updated_conversation = self.conversation_model.update_conversation(conversation_id, update_data)
            
            return jsonify({
                "success": True,
                "data": updated_conversation,
                "message": "Conversation deactivated successfully"
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
