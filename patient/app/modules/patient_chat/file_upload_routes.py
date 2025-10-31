"""
Chat File Upload Routes - REST API endpoints for file attachments
"""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import logging

from app.shared.s3_service import get_s3_service
from app.core.auth import token_required

logger = logging.getLogger(__name__)

# Create Blueprint
file_upload_bp = Blueprint('chat_file_upload', __name__)


@file_upload_bp.route('/upload', methods=['POST'])
def upload_file():
    """
    Upload a file attachment for chat
    
    Form Data:
        file: File to upload
        file_type: Type of file (image, document, voice)
        user_id: User ID (patient or doctor)
        chat_room_id: Chat room ID
    
    Returns:
        JSON response with file URL and metadata
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "message": "No file provided",
                "data": None
            }), 400
        
        file = request.files['file']
        
        # Check if file is empty
        if file.filename == '':
            return jsonify({
                "success": False,
                "message": "No file selected",
                "data": None
            }), 400
        
        # Get form data
        file_type = request.form.get('file_type', 'image')
        user_id = request.form.get('user_id')
        chat_room_id = request.form.get('chat_room_id')
        
        # Validate required fields
        if not user_id or not chat_room_id:
            return jsonify({
                "success": False,
                "message": "user_id and chat_room_id are required",
                "data": None
            }), 400
        
        # Validate file type
        if file_type not in ['image', 'document', 'voice', 'audio']:
            return jsonify({
                "success": False,
                "message": "Invalid file_type. Must be: image, document, or voice",
                "data": None
            }), 400
        
        # Get S3 service
        s3_service = get_s3_service()
        
        if not s3_service.is_enabled():
            return jsonify({
                "success": False,
                "message": "File upload service is not available",
                "data": None
            }), 503
        
        # Secure filename
        original_filename = secure_filename(file.filename)
        
        # Read file data
        file_data = file.read()
        
        # Upload to S3
        upload_result = s3_service.upload_file(
            file_data=file_data,
            file_name=original_filename,
            file_type=file_type,
            user_id=user_id,
            chat_room_id=chat_room_id
        )
        
        if not upload_result:
            return jsonify({
                "success": False,
                "message": "Failed to upload file. Check file size and format.",
                "data": None
            }), 400
        
        return jsonify({
            "success": True,
            "message": "File uploaded successfully",
            "data": {
                "file_url": upload_result['file_url'],
                "file_key": upload_result['file_key'],
                "file_name": upload_result['file_name'],
                "file_type": upload_result['file_type'],
                "file_size": upload_result['file_size'],
                "content_type": upload_result['content_type'],
                "uploaded_at": upload_result['uploaded_at']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Internal server error during file upload",
            "data": None
        }), 500


@file_upload_bp.route('/files/delete', methods=['DELETE'])
def delete_file():
    """
    Delete a file attachment
    
    Request Body:
        file_key: S3 file key to delete
        user_id: User ID (for authorization)
    
    Returns:
        JSON response with deletion status
    """
    try:
        data = request.get_json()
        
        file_key = data.get('file_key')
        user_id = data.get('user_id')
        
        if not file_key or not user_id:
            return jsonify({
                "success": False,
                "message": "file_key and user_id are required",
                "data": None
            }), 400
        
        # Get S3 service
        s3_service = get_s3_service()
        
        if not s3_service.is_enabled():
            return jsonify({
                "success": False,
                "message": "File upload service is not available",
                "data": None
            }), 503
        
        # Delete file
        success = s3_service.delete_file(file_key)
        
        if success:
            return jsonify({
                "success": True,
                "message": "File deleted successfully",
                "data": None
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Failed to delete file",
                "data": None
            }), 400
        
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Internal server error during file deletion",
            "data": None
        }), 500


@file_upload_bp.route('/info', methods=['GET'])
def get_upload_info():
    """
    Get file upload configuration and limits
    
    Returns:
        JSON response with upload limits and allowed formats
    """
    try:
        from app.core.config import (
            MAX_IMAGE_SIZE, MAX_DOCUMENT_SIZE, MAX_VOICE_SIZE,
            ALLOWED_IMAGE_EXTENSIONS, ALLOWED_DOCUMENT_EXTENSIONS,
            ALLOWED_VOICE_EXTENSIONS
        )
        
        s3_service = get_s3_service()
        
        return jsonify({
            "success": True,
            "message": "Upload configuration retrieved",
            "data": {
                "enabled": s3_service.is_enabled(),
                "limits": {
                    "max_image_size_mb": MAX_IMAGE_SIZE,
                    "max_document_size_mb": MAX_DOCUMENT_SIZE,
                    "max_voice_size_mb": MAX_VOICE_SIZE
                },
                "allowed_formats": {
                    "image": ALLOWED_IMAGE_EXTENSIONS,
                    "document": ALLOWED_DOCUMENT_EXTENSIONS,
                    "voice": ALLOWED_VOICE_EXTENSIONS
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


@file_upload_bp.route('/health', methods=['GET'])
def upload_service_health():
    """
    Health check for file upload service
    
    Returns:
        JSON response with service status
    """
    try:
        s3_service = get_s3_service()
        is_enabled = s3_service.is_enabled()
        
        return jsonify({
            "success": True,
            "message": "File upload service health check",
            "data": {
                "service": "chat_file_upload",
                "status": "operational" if is_enabled else "disabled",
                "enabled": is_enabled,
                "endpoints": {
                    "upload": "/chat/files/upload",
                    "delete": "/chat/files/delete",
                    "info": "/chat/files/info",
                    "health": "/chat/files/health"
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Health check failed",
            "data": None
        }), 500

