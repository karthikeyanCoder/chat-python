"""
Doctor Chat Routes - Enhanced Flask REST API endpoints
REST API layer for doctor chat functionality
"""
from flask import Blueprint, request, jsonify
from pydantic import ValidationError
import logging

from app.modules.doctor_chat.schemas import (
    SendMessageSchema, StartChatSchema, GetMessagesSchema,
    MarkAsReadSchema, EditMessageSchema, DeleteMessageSchema,
    SearchMessagesSchema, SearchPatientsSchema, AddReactionSchema,
    UpdateRoomSettingsSchema
)
from app.modules.doctor_chat.services import get_doctor_chat_service

logger = logging.getLogger(__name__)

# Create Blueprint
doctor_chat_bp = Blueprint('doctor_chat', __name__)


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


@doctor_chat_bp.route('/test', methods=['GET'])
def test_route():
    """
    Test route to verify blueprint is working
    """
    return jsonify({"success": True, "message": "Chat blueprint is working"}), 200

@doctor_chat_bp.route('/rooms', methods=['GET'])
def get_chat_rooms():
    """
    Get all chat rooms for a doctor
    
    Query Parameters:
        doctor_id (str): Doctor ID
        include_archived (bool): Include archived rooms (optional)
    
    Returns:
        JSON response with chat rooms
    """
    try:
        doctor_id = request.args.get('doctor_id')
        include_archived = request.args.get('include_archived', 'false').lower() == 'true'
        
        if not doctor_id:
            return jsonify({
                "success": False,
                "message": "doctor_id is required",
                "data": None
            }), 400
        
        service = get_doctor_chat_service()
        result = service.get_doctor_chat_rooms(doctor_id, include_archived)
        return handle_response(result)
        
    except Exception as e:
        logger.error(f"Error in get_chat_rooms: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Internal server error",
            "data": None
        }), 500


@doctor_chat_bp.route('/start', methods=['POST'])
def start_chat():
    """
    Start a new chat with a patient
    
    Request Body:
        doctor_id (str): Doctor ID
        patient_id (str): Patient ID
    
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
        
        service = get_doctor_chat_service()
        result = service.start_chat_with_patient(schema.doctor_id, schema.patient_id)
        return handle_response(result, success_code=201)
        
    except Exception as e:
        logger.error(f"Error in start_chat: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Internal server error",
            "data": None
        }), 500


@doctor_chat_bp.route('/send', methods=['POST'])
def send_message():
    """
    Send a message to a patient
    
    Request Body:
        doctor_id (str): Doctor ID
        patient_id (str): Patient ID
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
        
        service = get_doctor_chat_service()
        result = service.send_message_to_patient(
            schema.doctor_id,
            schema.patient_id,
            schema.message_content,
            schema.message_type,
            schema.is_urgent,
            schema.priority,
            schema.reply_to_message_id,
            schema.attachment  # Pass attachment data
        )
        return handle_response(result, success_code=201)
        
    except Exception as e:
        logger.error(f"Error in send_message: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Internal server error",
            "data": None
        }), 500


@doctor_chat_bp.route('/messages', methods=['GET'])
def get_messages():
    """
    Get messages from a specific chat room
    
    Query Parameters:
        doctor_id (str): Doctor ID
        room_id (str): Room ID
        page (int, optional): Page number (default: 1)
        limit (int, optional): Messages per page (default: 50)
    
    Returns:
        JSON response with messages
    """
    try:
        doctor_id = request.args.get('doctor_id')
        room_id = request.args.get('room_id')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        
        if not doctor_id or not room_id:
            return jsonify({
                "success": False,
                "message": "doctor_id and room_id are required",
                "data": None
            }), 400
        
        # Validate with schema
        try:
            schema = GetMessagesSchema(
                doctor_id=doctor_id,
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
        
        service = get_doctor_chat_service()
        result = service.get_chat_messages(
            schema.doctor_id,
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


@doctor_chat_bp.route('/mark-read', methods=['POST'])
def mark_as_read():
    """
    Mark messages as read
    
    Request Body:
        doctor_id (str): Doctor ID
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
        
        service = get_doctor_chat_service()
        result = service.mark_messages_as_read(
            schema.doctor_id,
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


@doctor_chat_bp.route('/unread-count', methods=['GET'])
def get_unread_count():
    """
    Get unread message count for a doctor
    
    Query Parameters:
        doctor_id (str): Doctor ID
    
    Returns:
        JSON response with unread count
    """
    try:
        doctor_id = request.args.get('doctor_id')
        
        if not doctor_id:
            return jsonify({
                "success": False,
                "message": "doctor_id is required",
                "data": None
            }), 400
        
        service = get_doctor_chat_service()
        result = service.get_unread_count(doctor_id)
        return handle_response(result)
        
    except Exception as e:
        logger.error(f"Error in get_unread_count: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Internal server error",
            "data": None
        }), 500


@doctor_chat_bp.route('/search', methods=['POST'])
def search_messages():
    """
    Search messages
    
    Request Body:
        doctor_id (str): Doctor ID
        search_query (str): Search query
        room_id (str, optional): Specific room ID
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
        
        service = get_doctor_chat_service()
        result = service.search_messages(
            schema.doctor_id,
            schema.search_query,
            schema.room_id,
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


@doctor_chat_bp.route('/search/patients', methods=['POST'])
def search_patients():
    """
    Search patients for starting new chats
    
    Request Body:
        doctor_id (str): Doctor ID
        search_query (str): Search query
        page (int, optional): Page number (default: 1)
        limit (int, optional): Maximum results (default: 20)
    
    Returns:
        JSON response with patients
    """
    try:
        data = request.get_json()
        
        # Validate request
        try:
            schema = SearchPatientsSchema(**data)
        except ValidationError as e:
            return jsonify({
                "success": False,
                "message": "Validation error",
                "data": {"errors": e.errors()}
            }), 400
        
        service = get_doctor_chat_service()
        result = service.search_patients(
            schema.doctor_id,
            schema.search_query,
            schema.page,
            schema.limit
        )
        return handle_response(result)
        
    except Exception as e:
        logger.error(f"Error in search_patients: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Internal server error",
            "data": None
        }), 500


@doctor_chat_bp.route('/edit', methods=['PUT'])
def edit_message():
    """
    Edit a message
    
    Request Body:
        doctor_id (str): Doctor ID
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
        
        service = get_doctor_chat_service()
        result = service.edit_message(
            schema.doctor_id,
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


@doctor_chat_bp.route('/delete', methods=['DELETE'])
def delete_message():
    """
    Delete a message
    
    Request Body:
        doctor_id (str): Doctor ID
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
        
        service = get_doctor_chat_service()
        result = service.delete_message(
            schema.doctor_id,
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


@doctor_chat_bp.route('/reaction', methods=['POST'])
def add_reaction():
    """
    Add a reaction to a message
    
    Request Body:
        doctor_id (str): Doctor ID
        message_id (str): Message ID
        reaction (str): Reaction emoji or type
    
    Returns:
        JSON response with success status
    """
    try:
        data = request.get_json()
        
        # Validate request
        try:
            schema = AddReactionSchema(**data)
        except ValidationError as e:
            return jsonify({
                "success": False,
                "message": "Validation error",
                "data": {"errors": e.errors()}
            }), 400
        
        service = get_doctor_chat_service()
        result = service.add_reaction(
            schema.doctor_id,
            schema.message_id,
            schema.reaction
        )
        return handle_response(result)
        
    except Exception as e:
        logger.error(f"Error in add_reaction: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Internal server error",
            "data": None
        }), 500


@doctor_chat_bp.route('/room/settings', methods=['PUT'])
def update_room_settings():
    """
    Update chat room settings
    
    Request Body:
        doctor_id (str): Doctor ID
        room_id (str): Room ID
        room_name (str, optional): Room name
        room_description (str, optional): Room description
        tags (list, optional): Room tags
        pinned (bool, optional): Pin room
        notifications_enabled (bool, optional): Enable notifications
        archived (bool, optional): Archive room
    
    Returns:
        JSON response with success status
    """
    try:
        data = request.get_json()
        
        # Validate request
        try:
            schema = UpdateRoomSettingsSchema(**data)
        except ValidationError as e:
            return jsonify({
                "success": False,
                "message": "Validation error",
                "data": {"errors": e.errors()}
            }), 400
        
        # Build settings dictionary
        settings = {}
        if schema.room_name is not None:
            settings['room_name'] = schema.room_name
        if schema.room_description is not None:
            settings['room_description'] = schema.room_description
        if schema.tags is not None:
            settings['tags'] = schema.tags
        if schema.pinned is not None:
            settings['pinned_by_doctor'] = schema.pinned
        if schema.notifications_enabled is not None:
            settings['notifications_enabled_doctor'] = schema.notifications_enabled
        if schema.archived is not None:
            settings['is_archived'] = schema.archived
        
        service = get_doctor_chat_service()
        result = service.update_room_settings(
            schema.doctor_id,
            schema.room_id,
            settings
        )
        return handle_response(result)
        
    except Exception as e:
        logger.error(f"Error in update_room_settings: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Internal server error",
            "data": None
        }), 500


@doctor_chat_bp.route('/patient/health-summary', methods=['GET'])
def get_patient_health_summary():
    """
    Get patient health summary
    
    Query Parameters:
        doctor_id (str): Doctor ID
        patient_id (str): Patient ID
    
    Returns:
        JSON response with health summary
    """
    try:
        doctor_id = request.args.get('doctor_id')
        patient_id = request.args.get('patient_id')
        
        if not doctor_id or not patient_id:
            return jsonify({
                "success": False,
                "message": "doctor_id and patient_id are required",
                "data": None
            }), 400
        
        service = get_doctor_chat_service()
        result = service.get_patient_health_summary(doctor_id, patient_id)
        return handle_response(result)
        
    except Exception as e:
        logger.error(f"Error in get_patient_health_summary: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Internal server error",
            "data": None
        }), 500


@doctor_chat_bp.route('/analytics', methods=['GET'])
def get_chat_analytics():
    """
    Get chat analytics for a room
    
    Query Parameters:
        doctor_id (str): Doctor ID
        room_id (str): Room ID
    
    Returns:
        JSON response with analytics
    """
    try:
        doctor_id = request.args.get('doctor_id')
        room_id = request.args.get('room_id')
        
        if not doctor_id or not room_id:
            return jsonify({
                "success": False,
                "message": "doctor_id and room_id are required",
                "data": None
            }), 400
        
        service = get_doctor_chat_service()
        result = service.get_chat_analytics(doctor_id, room_id)
        return handle_response(result)
        
    except Exception as e:
        logger.error(f"Error in get_chat_analytics: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Internal server error",
            "data": None
        }), 500


@doctor_chat_bp.route('/info', methods=['GET'])
def get_upload_info():
    """
    Get file upload configuration and limits
    
    Returns:
        JSON response with upload limits and allowed formats
    """
    try:
        from app.shared.s3_service import get_s3_service
        from app.core.config import (
            MAX_IMAGE_SIZE, MAX_DOCUMENT_SIZE, MAX_VOICE_SIZE,
            ALLOWED_IMAGE_EXTENSIONS, ALLOWED_DOCUMENT_EXTENSIONS, ALLOWED_VOICE_EXTENSIONS
        )
        
        s3_service = get_s3_service()
        
        return jsonify({
            "success": True,
            "message": "Upload configuration retrieved",
            "data": {
                "enabled": s3_service.is_enabled(),
                "storage": "aws_s3" if s3_service.is_enabled() else "disabled",
                "bucket": s3_service.bucket_name if s3_service.is_enabled() else None,
                "limits": {
                    "max_image_size_mb": MAX_IMAGE_SIZE,
                    "max_document_size_mb": MAX_DOCUMENT_SIZE,
                    "max_voice_size_mb": MAX_VOICE_SIZE
                },
                "allowed_formats": {
                    "image": [f".{ext}" for ext in ALLOWED_IMAGE_EXTENSIONS],
                    "document": [f".{ext}" for ext in ALLOWED_DOCUMENT_EXTENSIONS],
                    "voice": [f".{ext}" for ext in ALLOWED_VOICE_EXTENSIONS]
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting upload info: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Internal server error",
            "data": None
        }), 500


@doctor_chat_bp.route('/presigned-url', methods=['POST'])
def get_presigned_url():
    """
    Get a presigned URL for accessing a file from S3
    
    Request Body:
        file_key: S3 file key
        expiration: Optional expiration time in seconds (default: 3600)
    
    Returns:
        JSON response with presigned URL
    """
    try:
        from app.shared.s3_service import get_s3_service
        from flask import request
        from werkzeug.exceptions import BadRequest
        
        s3_service = get_s3_service()
        
        if not s3_service.is_enabled():
            return jsonify({
                "success": False,
                "message": "File storage service is not configured",
                "data": None
            }), 503
        
        # Parse JSON request body
        try:
            data = request.get_json()
        except BadRequest:
            return jsonify({
                "success": False,
                "message": "Request body must be valid JSON with Content-Type: application/json",
                "data": None
            }), 400
        
        file_key = data.get('file_key')
        expiration = data.get('expiration', 3600)
        
        if not file_key:
            return jsonify({
                "success": False,
                "message": "file_key is required",
                "data": None
            }), 400
        
        # Generate presigned URL
        presigned_url = s3_service.generate_presigned_url(file_key, expiration)
        
        if presigned_url:
            return jsonify({
                "success": True,
                "message": "Presigned URL generated successfully",
                "data": {
                    "file_key": file_key,
                    "presigned_url": presigned_url,
                    "expires_in": expiration
                }
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Failed to generate presigned URL",
                "data": None
            }), 500
        
    except Exception as e:
        logger.error(f"Error generating presigned URL: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Internal server error",
            "data": None
        }), 500


@doctor_chat_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for doctor chat module
    
    Returns:
        JSON response with module health status
    """
    try:
        return jsonify({
            "success": True,
            "message": "Doctor chat module is healthy",
            "data": {
                "module": "doctor_chat",
                "version": "2.0.0",
                "status": "operational",
                "endpoints": {
                    "get_rooms": "/doctor/chat/rooms",
                    "start_chat": "/doctor/chat/start",
                    "send_message": "/doctor/chat/send",
                    "get_messages": "/doctor/chat/messages",
                    "mark_read": "/doctor/chat/mark-read",
                    "unread_count": "/doctor/chat/unread-count",
                    "search_messages": "/doctor/chat/search",
                    "search_patients": "/doctor/chat/search/patients",
                    "edit": "/doctor/chat/edit",
                    "delete": "/doctor/chat/delete",
                    "reaction": "/doctor/chat/reaction",
                    "room_settings": "/doctor/chat/room/settings",
                    "health_summary": "/doctor/chat/patient/health-summary",
                    "analytics": "/doctor/chat/analytics",
                    "upload_info": "/doctor/chat/info",
                    "presigned_url": "/doctor/chat/presigned-url"
                }
            }
        }), 200
    except Exception as e:
        logger.error(f"Error in health_check: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Health check failed",
            "data": None
        }), 500


