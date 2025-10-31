"""
Chat Routes - REST API endpoints for patient chat functionality
"""
from flask import Blueprint, request, jsonify
from pydantic import ValidationError
import logging

from app.modules.patient_chat.schemas import (
    SendMessageSchema, StartChatSchema, GetMessagesSchema,
    MarkAsReadSchema, EditMessageSchema, DeleteMessageSchema,
    SearchMessagesSchema
)
from app.modules.patient_chat.services import get_chat_service
from app.core.auth import token_required

logger = logging.getLogger(__name__)

# Create Blueprint
chat_bp = Blueprint('chat', __name__)


def handle_response(result: dict, success_code: int = 200, error_code: int = 400):
    """
    Handle service response and return appropriate HTTP status
    
    Args:
        result: Service response dict
        success_code: HTTP status for success
        error_code: Default HTTP status for error
    
    Returns:
        Flask response tuple
    """
    if result["success"]:
        return jsonify(result), success_code
    else:
        # Determine appropriate error status code
        error_message = result["message"].lower()
        if "not found" in error_message:
            status_code = 404
        elif "access denied" in error_message or "unauthorized" in error_message:
            status_code = 403
        elif "already exists" in error_message:
            status_code = 409
        elif "invalid" in error_message or "required" in error_message:
            status_code = 400
        else:
            status_code = error_code
        
        return jsonify(result), status_code


@chat_bp.route('/test', methods=['GET'])
def test_route():
    """
    Test route to verify blueprint is working
    """
    return jsonify({"success": True, "message": "Patient chat blueprint is working"}), 200


@chat_bp.route('/rooms', methods=['GET'])
def get_chat_rooms():
    """
    Get all chat rooms for a patient
    
    Query Parameters:
        patient_id (str): Patient ID
        include_archived (bool): Include archived rooms (optional)
    
    Returns:
        JSON response with chat rooms
    """
    try:
        patient_id = request.args.get('patient_id')
        include_archived = request.args.get('include_archived', 'false').lower() == 'true'
        
        if not patient_id:
            return jsonify({
                "success": False,
                "message": "patient_id is required",
                "data": None
            }), 400
        
        service = get_chat_service()
        result = service.get_patient_chat_rooms(patient_id, include_archived)
        return handle_response(result)
        
    except Exception as e:
        logger.error(f"Error in get_chat_rooms: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Internal server error",
            "data": None
        }), 500


@chat_bp.route('/start', methods=['POST'])
def start_chat():
    """
    Start a new chat with a doctor
    
    Request Body:
        patient_id (str): Patient ID
        doctor_id (str): Doctor ID
    
    Returns:
        JSON response with chat room information
    """
    try:
        data = request.get_json()
        
        # Validate request
        try:
            schema = StartChatSchema(**data)
        except ValidationError as e:
            return jsonify({
                "success": False,
                "message": "Validation error",
                "data": {"errors": e.errors()}
            }), 400
        
        service = get_chat_service()
        result = service.start_chat_with_doctor(schema.patient_id, schema.doctor_id)
        return handle_response(result, success_code=201)
        
    except Exception as e:
        logger.error(f"Error in start_chat: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Internal server error",
            "data": None
        }), 500


@chat_bp.route('/send', methods=['POST'])
def send_message():
    """
    Send a message to a doctor
    
    Request Body:
        patient_id (str): Patient ID
        doctor_id (str): Doctor ID
        message_content (str): Message content
        message_type (str, optional): Message type (default: "text")
        is_urgent (bool, optional): Urgent flag (default: false)
        priority (str, optional): Message priority (default: "normal")
        reply_to_message_id (str, optional): Reply to message ID
    
    Returns:
        JSON response with sent message
    """
    try:
        data = request.get_json()
        
        # Validate request
        try:
            schema = SendMessageSchema(**data)
        except ValidationError as e:
            return jsonify({
                "success": False,
                "message": "Validation error",
                "data": {"errors": e.errors()}
            }), 400
        
        service = get_chat_service()
        
        # Extract attachment from request if present
        attachment = data.get('attachment')
        
        result = service.send_message_to_doctor(
            schema.patient_id,
            schema.doctor_id,
            schema.message_content,
            schema.message_type,
            schema.is_urgent,
            schema.priority,
            schema.reply_to_message_id,
            attachment
        )
        return handle_response(result, success_code=201)
        
    except Exception as e:
        logger.error(f"Error in send_message: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Internal server error",
            "data": None
        }), 500


@chat_bp.route('/messages', methods=['GET'])
def get_messages():
    """
    Get messages from a specific chat room
    
    Query Parameters:
        patient_id (str): Patient ID
        room_id (str): Room ID
        page (int, optional): Page number (default: 1)
        limit (int, optional): Messages per page (default: 50)
    
    Returns:
        JSON response with messages
    """
    try:
        patient_id = request.args.get('patient_id')
        room_id = request.args.get('room_id')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        
        if not patient_id or not room_id:
            return jsonify({
                "success": False,
                "message": "patient_id and room_id are required",
                "data": None
            }), 400
        
        # Validate with schema
        try:
            schema = GetMessagesSchema(
                patient_id=patient_id,
                room_id=room_id,
                page=page,
                limit=limit
            )
        except ValidationError as e:
            return jsonify({
                "success": False,
                "message": "Validation error",
                "data": {"errors": e.errors()}
            }), 400
        
        service = get_chat_service()
        result = service.get_chat_messages(
            schema.patient_id,
            schema.room_id,
            schema.page,
            schema.limit
        )
        return handle_response(result)
        
    except Exception as e:
        logger.error(f"Error in get_messages: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Internal server error",
            "data": None
        }), 500


@chat_bp.route('/mark-read', methods=['POST'])
def mark_as_read():
    """
    Mark messages as read
    
    Request Body:
        patient_id (str): Patient ID
        room_id (str): Room ID
        message_id (str, optional): Specific message ID
    
    Returns:
        JSON response with success status
    """
    try:
        data = request.get_json()
        
        # Validate request
        try:
            schema = MarkAsReadSchema(**data)
        except ValidationError as e:
            return jsonify({
                "success": False,
                "message": "Validation error",
                "data": {"errors": e.errors()}
            }), 400
        
        service = get_chat_service()
        result = service.mark_messages_as_read(
            schema.patient_id,
            schema.room_id,
            schema.message_id
        )
        return handle_response(result)
        
    except Exception as e:
        logger.error(f"Error in mark_as_read: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Internal server error",
            "data": None
        }), 500


@chat_bp.route('/unread-count', methods=['GET'])
def get_unread_count():
    """
    Get unread message count for a patient
    
    Query Parameters:
        patient_id (str): Patient ID
    
    Returns:
        JSON response with unread count
    """
    try:
        patient_id = request.args.get('patient_id')
        
        if not patient_id:
            return jsonify({
                "success": False,
                "message": "patient_id is required",
                "data": None
            }), 400
        
        service = get_chat_service()
        result = service.get_unread_count(patient_id)
        return handle_response(result)
        
    except Exception as e:
        logger.error(f"Error in get_unread_count: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Internal server error",
            "data": None
        }), 500


@chat_bp.route('/search', methods=['POST'])
def search_messages():
    """
    Search messages
    
    Request Body:
        patient_id (str): Patient ID
        search_query (str): Search query
        limit (int, optional): Maximum results (default: 20)
    
    Returns:
        JSON response with search results
    """
    try:
        data = request.get_json()
        
        # Validate request
        try:
            schema = SearchMessagesSchema(**data)
        except ValidationError as e:
            return jsonify({
                "success": False,
                "message": "Validation error",
                "data": {"errors": e.errors()}
            }), 400
        
        service = get_chat_service()
        result = service.search_messages(
            schema.patient_id,
            schema.search_query,
            schema.limit
        )
        return handle_response(result)
        
    except Exception as e:
        logger.error(f"Error in search_messages: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Internal server error",
            "data": None
        }), 500


@chat_bp.route('/edit', methods=['PUT'])
def edit_message():
    """
    Edit a message
    
    Request Body:
        patient_id (str): Patient ID
        message_id (str): Message ID
        new_content (str): New message content
    
    Returns:
        JSON response with success status
    """
    try:
        data = request.get_json()
        
        # Validate request
        try:
            schema = EditMessageSchema(**data)
        except ValidationError as e:
            return jsonify({
                "success": False,
                "message": "Validation error",
                "data": {"errors": e.errors()}
            }), 400
        
        service = get_chat_service()
        result = service.edit_message(
            schema.patient_id,
            schema.message_id,
            schema.new_content
        )
        return handle_response(result)
        
    except Exception as e:
        logger.error(f"Error in edit_message: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Internal server error",
            "data": None
        }), 500


@chat_bp.route('/delete', methods=['DELETE'])
def delete_message():
    """
    Delete a message
    
    Request Body:
        patient_id (str): Patient ID
        message_id (str): Message ID
    
    Returns:
        JSON response with success status
    """
    try:
        data = request.get_json()
        
        # Validate request
        try:
            schema = DeleteMessageSchema(**data)
        except ValidationError as e:
            return jsonify({
                "success": False,
                "message": "Validation error",
                "data": {"errors": e.errors()}
            }), 400
        
        service = get_chat_service()
        result = service.delete_message(
            schema.patient_id,
            schema.message_id
        )
        return handle_response(result)
        
    except Exception as e:
        logger.error(f"Error in delete_message: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Internal server error",
            "data": None
        }), 500


@chat_bp.route('/health', methods=['GET'])
def chat_health():
    """
    Health check endpoint for chat module
    
    Returns:
        JSON response with module health status
    """
    try:
        return jsonify({
            "success": True,
            "message": "Chat module is healthy",
            "data": {
                "module": "patient_chat",
                "version": "1.0.0",
                "status": "operational",
                "endpoints": {
                    "get_rooms": "/chat/rooms",
                    "start_chat": "/chat/start",
                    "send_message": "/chat/send",
                    "get_messages": "/chat/messages",
                    "mark_read": "/chat/mark-read",
                    "unread_count": "/chat/unread-count",
                    "search": "/chat/search",
                    "edit": "/chat/edit",
                    "delete": "/chat/delete"
                }
            }
        }), 200
    except Exception as e:
        logger.error(f"Error in chat_health: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Chat module health check failed",
            "data": None
        }), 500
