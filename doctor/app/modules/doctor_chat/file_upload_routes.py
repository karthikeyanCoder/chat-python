"""
Doctor Chat File Upload Routes - File attachment handling
REST API endpoints for uploading and managing file attachments
Files are stored in AWS S3 (not local storage)
"""
from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequest
from datetime import datetime
import logging
import os
import uuid
from pathlib import Path
import mimetypes

# Import S3 service
from app.shared.s3_service import get_s3_service

logger = logging.getLogger(__name__)

# Create Blueprint
doctor_file_upload_bp = Blueprint('doctor_chat_file_upload', __name__)

# Get S3 service instance
s3_service = get_s3_service()

# File upload configuration
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads', 'chat_files')
ALLOWED_EXTENSIONS = {
    'image': {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'},
    'document': {'pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx', 'ppt', 'pptx'},
    'voice': {'mp3', 'wav', 'ogg', 'm4a', 'aac', 'webm'},
    'audio': {'mp3', 'wav', 'ogg', 'm4a', 'aac', 'webm'}
}
MAX_FILE_SIZE = {
    'image': 10 * 1024 * 1024,  # 10 MB
    'document': 20 * 1024 * 1024,  # 20 MB
    'voice': 5 * 1024 * 1024,  # 5 MB
    'audio': 5 * 1024 * 1024  # 5 MB
}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename, file_type):
    """Check if file extension is allowed for the given file type"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS.get(file_type, set())


@doctor_file_upload_bp.route('/upload', methods=['POST'])
def upload_file():
    """
    Upload a file attachment for chat - Stores in AWS S3
    
    Form Data:
        file: File to upload
        file_type: Type of file (image, document, voice, audio)
        user_id: User ID (doctor_id or patient_id)
        user_type: User type (doctor or patient)
        room_id: Chat room ID
    
    Returns:
        JSON response with S3 file URL and metadata
    """
    try:
        # Check if S3 is enabled
        if not s3_service.is_enabled():
            return jsonify({
                "success": False,
                "message": "File upload service is not configured. Please contact administrator.",
                "data": None
            }), 503
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "message": "No file provided",
                "data": None
            }), 400
        
        file = request.files['file']
        
        # Check if file is empty - improved validation
        if not file or file.filename == '' or not file.filename:
            logger.error(f"❌ No file selected - file object: {file}, filename: {file.filename if file else 'None'}")
            return jsonify({
                "success": False,
                "message": "No file selected",
                "data": None
            }), 400
        
        # Log received file info for debugging
        logger.info(f"📥 Received file: {file.filename}, content_type: {file.content_type}, size: {file.content_length}")
        
        # Get form data
        file_type = request.form.get('file_type', 'image')
        user_id = request.form.get('user_id') or request.form.get('doctor_id')
        user_type = request.form.get('user_type', 'doctor')
        room_id = request.form.get('room_id') or request.form.get('chat_room_id')
        
        # Validate required fields
        if not user_id or not room_id:
            return jsonify({
                "success": False,
                "message": "user_id and room_id are required",
                "data": None
            }), 400
        
        # Validate file type
        if file_type not in ['image', 'document', 'voice', 'audio']:
            return jsonify({
                "success": False,
                "message": "Invalid file_type. Must be: image, document, voice, or audio",
                "data": None
            }), 400
        
        # Normalize audio file type
        if file_type == 'audio':
            file_type = 'voice'
        
        # Read file data
        file_data = file.read()
        original_filename = secure_filename(file.filename)
        
        # Upload to S3 using S3 service
        upload_result = s3_service.upload_file(
            file_data=file_data,
            file_name=original_filename,
            file_type=file_type,
            user_id=user_id,
            chat_room_id=room_id
        )
        
        if not upload_result:
            return jsonify({
                "success": False,
                "message": "Failed to upload file to storage. Please check file format and size.",
                "data": None
            }), 500
        
        # Calculate duration for audio/voice files (optional)
        duration = None
        if file_type in ['voice', 'audio']:
            try:
                from pydub import AudioSegment
                import io
                audio = AudioSegment.from_file(io.BytesIO(file_data))
                duration = len(audio) / 1000.0  # Convert to seconds
            except Exception as e:
                logger.warning(f"Could not calculate audio duration: {str(e)}")
        
        # Prepare response data
        response_data = {
            "file_url": upload_result['file_url'],
            "file_key": upload_result['file_key'],
            "file_name": upload_result['file_name'],
            "file_type": upload_result['file_type'],
            "file_size": upload_result['file_size'],
            "mime_type": upload_result['content_type'],
            "uploaded_at": upload_result['uploaded_at'],
            "storage": "s3",
            "bucket": s3_service.bucket_name
        }
        
        if duration:
            response_data["duration"] = duration
        
        logger.info(f"✅ File uploaded to S3: {upload_result['file_key']} ({file_type}, {upload_result['file_size']} bytes)")
        
        return jsonify({
            "success": True,
            "message": "File uploaded successfully to AWS S3",
            "data": response_data
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error uploading file: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Internal server error during file upload",
            "error": str(e),
            "data": None
        }), 500


@doctor_file_upload_bp.route('/delete', methods=['DELETE'])
def delete_file():
    """
    Delete a file attachment from AWS S3
    
    Request Body:
        file_key: S3 file key to delete
        doctor_id: Doctor ID (for authorization)
    
    Returns:
        JSON response with deletion status
    """
    try:
        # Check if S3 is enabled
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
        doctor_id = data.get('doctor_id')
        
        if not file_key or not doctor_id:
            return jsonify({
                "success": False,
                "message": "file_key and doctor_id are required",
                "data": None
            }), 400
        
        # Delete from S3
        success = s3_service.delete_file(file_key)
        
        if success:
            logger.info(f"✅ File deleted from S3: {file_key}")
            return jsonify({
                "success": True,
                "message": "File deleted successfully from AWS S3",
                "data": None
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Failed to delete file from storage",
                "data": None
            }), 500
        
    except Exception as e:
        logger.error(f"❌ Error deleting file: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Internal server error during file deletion",
            "data": None
        }), 500


@doctor_file_upload_bp.route('/info', methods=['GET'])
def get_upload_info():
    """
    Get file upload configuration and limits
    
    Returns:
        JSON response with upload limits and allowed formats
    """
    try:
        from app.core.config import (
            MAX_IMAGE_SIZE, MAX_DOCUMENT_SIZE, MAX_VOICE_SIZE,
            ALLOWED_IMAGE_EXTENSIONS, ALLOWED_DOCUMENT_EXTENSIONS, ALLOWED_VOICE_EXTENSIONS
        )
        
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


@doctor_file_upload_bp.route('/health', methods=['GET'])
def upload_service_health():
    """
    Health check for file upload service
    
    Returns:
        JSON response with service status
    """
    try:
        s3_enabled = s3_service.is_enabled()
        
        return jsonify({
            "success": True,
            "message": "File upload service health check",
            "data": {
                "service": "doctor_chat_file_upload",
                "status": "operational" if s3_enabled else "disabled",
                "enabled": s3_enabled,
                "storage": "aws_s3" if s3_enabled else "not_configured",
                "bucket": s3_service.bucket_name if s3_enabled else None,
                "endpoints": {
                    "upload": "/doctor/chat/files/upload",
                    "delete": "/doctor/chat/files/delete",
                    "info": "/doctor/chat/files/info",
                    "health": "/doctor/chat/files/health"
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


@doctor_file_upload_bp.route('/presigned-url', methods=['POST'])
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


