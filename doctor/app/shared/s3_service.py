"""
AWS S3 File Storage Service
Handles file uploads, downloads, and deletions for chat attachments
"""
import os
import uuid
import logging
from typing import Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
import mimetypes

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    print("[WARN] boto3 not installed. Install with: pip install boto3")

from app.core.config import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    S3_BUCKET_NAME,
    S3_UPLOAD_ENABLED,
    S3_URL_EXPIRATION,
    MAX_IMAGE_SIZE,
    MAX_DOCUMENT_SIZE,
    MAX_VOICE_SIZE,
    ALLOWED_IMAGE_EXTENSIONS,
    ALLOWED_DOCUMENT_EXTENSIONS,
    ALLOWED_VOICE_EXTENSIONS
)

logger = logging.getLogger(__name__)


class S3Service:
    """Service for handling file uploads to AWS S3"""
    
    def __init__(self):
        """Initialize S3 client"""
        self.s3_client = None
        self.bucket_name = S3_BUCKET_NAME
        self.enabled = S3_UPLOAD_ENABLED
        
        if not BOTO3_AVAILABLE:
            logger.warning("boto3 not available - S3 file uploads disabled")
            self.enabled = False
            return
        
        if not self.enabled:
            logger.info("S3 uploads are disabled in configuration")
            return
        
        if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
            logger.warning("AWS credentials not configured - S3 uploads disabled")
            self.enabled = False
            return
        
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name=AWS_REGION
            )
            
            # Don't verify bucket on startup - do it lazily
            logger.info(f"[OK] S3 Service initialized - Bucket: {self.bucket_name} (verification deferred)")
            
        except NoCredentialsError:
            logger.error("AWS credentials are invalid")
            self.enabled = False
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            self.enabled = False
    
    def _verify_bucket(self):
        """Verify that the S3 bucket exists and is accessible"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"S3 bucket '{self.bucket_name}' is accessible")
            
            # Configure CORS for web access
            self._configure_cors()
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.warning(f"S3 bucket '{self.bucket_name}' does not exist - attempting to create")
                try:
                    if AWS_REGION == 'us-east-1':
                        self.s3_client.create_bucket(Bucket=self.bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': AWS_REGION}
                        )
                    logger.info(f"Created S3 bucket '{self.bucket_name}'")
                    self._configure_cors()
                except Exception as create_error:
                    logger.error(f"Failed to create S3 bucket: {create_error}")
                    logger.warning("S3 service will be disabled")
                    self.enabled = False
            else:
                logger.error(f"S3 bucket access error: {e}")
                logger.warning("S3 service will be disabled")
                self.enabled = False
        except Exception as e:
            logger.error(f"S3 bucket verification failed: {e}")
            logger.warning("S3 service will be disabled")
            self.enabled = False
    
    def _configure_cors(self):
        """Configure CORS policy for S3 bucket to allow web access"""
        try:
            cors_configuration = {
                'CORSRules': [
                    {
                        'AllowedHeaders': ['*'],
                        'AllowedMethods': ['GET', 'HEAD', 'PUT', 'POST'],
                        'AllowedOrigins': ['*'],  # Allow all origins for development
                        'ExposeHeaders': [
                            'ETag',
                            'Content-Length',
                            'Content-Type',
                            'x-amz-request-id'
                        ],
                        'MaxAgeSeconds': 3600
                    }
                ]
            }
            
            self.s3_client.put_bucket_cors(
                Bucket=self.bucket_name,
                CORSConfiguration=cors_configuration
            )
            logger.info("✅ S3 CORS configuration applied successfully")
            
        except ClientError as e:
            # CORS configuration is optional, don't fail if it errors
            logger.warning(f"⚠️ Could not configure CORS (bucket may already have CORS): {e}")
        except Exception as e:
            logger.warning(f"⚠️ CORS configuration error: {e}")
    
    def is_enabled(self) -> bool:
        """Check if S3 service is enabled and configured"""
        return self.enabled and self.s3_client is not None
    
    def validate_file(self, file_data: bytes, file_name: str, file_type: str) -> Tuple[bool, Optional[str]]:
        """
        Validate file before upload
        
        Args:
            file_data: File binary data
            file_name: Original file name
            file_type: File type (image, document, voice)
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Get file extension
        file_ext = file_name.split('.')[-1].lower() if '.' in file_name else ''
        
        # Get file size in MB
        file_size_mb = len(file_data) / (1024 * 1024)
        
        # Validate based on file type
        if file_type == 'image':
            if file_ext not in ALLOWED_IMAGE_EXTENSIONS:
                return False, f"Invalid image format. Allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
            if file_size_mb > MAX_IMAGE_SIZE:
                return False, f"Image too large. Maximum size: {MAX_IMAGE_SIZE}MB"
        
        elif file_type == 'document':
            if file_ext not in ALLOWED_DOCUMENT_EXTENSIONS:
                return False, f"Invalid document format. Allowed: {', '.join(ALLOWED_DOCUMENT_EXTENSIONS)}"
            if file_size_mb > MAX_DOCUMENT_SIZE:
                return False, f"Document too large. Maximum size: {MAX_DOCUMENT_SIZE}MB"
        
        elif file_type == 'voice' or file_type == 'audio':
            if file_ext not in ALLOWED_VOICE_EXTENSIONS:
                return False, f"Invalid audio format. Allowed: {', '.join(ALLOWED_VOICE_EXTENSIONS)}"
            if file_size_mb > MAX_VOICE_SIZE:
                return False, f"Audio file too large. Maximum size: {MAX_VOICE_SIZE}MB"
        
        else:
            return False, f"Unsupported file type: {file_type}"
        
        return True, None
    
    def upload_file(self, file_data: bytes, file_name: str, file_type: str,
                   user_id: str, chat_room_id: str) -> Optional[Dict[str, Any]]:
        """
        Upload file to S3
        
        Args:
            file_data: File binary data
            file_name: Original file name
            file_type: File type (image, document, voice)
            user_id: User ID for folder organization
            chat_room_id: Chat room ID for folder organization
        
        Returns:
            Dict with file_url, file_key, file_size, etc. or None if failed
        """
        if not self.is_enabled():
            logger.error("S3 service is not enabled")
            return None
        
        # Validate file
        is_valid, error_msg = self.validate_file(file_data, file_name, file_type)
        if not is_valid:
            logger.error(f"File validation failed: {error_msg}")
            return None
        
        try:
            # Generate unique file key
            file_ext = file_name.split('.')[-1].lower() if '.' in file_name else ''
            unique_id = uuid.uuid4().hex[:16]
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            
            # Organize files in folders: chat/{room_id}/{file_type}/{timestamp}_{unique_id}.{ext}
            file_key = f"chat/{chat_room_id}/{file_type}/{timestamp}_{unique_id}.{file_ext}"
            
            # Determine content type
            content_type = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_data,
                ContentType=content_type,
                Metadata={
                    'user_id': user_id,
                    'chat_room_id': chat_room_id,
                    'original_filename': file_name,
                    'file_type': file_type,
                    'uploaded_at': datetime.utcnow().isoformat()
                }
            )
            
            # Generate public URL (or signed URL if bucket is private)
            file_url = self.generate_presigned_url(file_key)
            
            logger.info(f"File uploaded successfully: {file_key}")
            
            return {
                'file_url': file_url,
                'file_key': file_key,
                'file_name': file_name,
                'file_type': file_type,
                'file_size': len(file_data),
                'content_type': content_type,
                'uploaded_at': datetime.utcnow().isoformat()
            }
            
        except ClientError as e:
            logger.error(f"S3 upload error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during upload: {e}")
            return None
    
    def generate_presigned_url(self, file_key: str, expiration: int = None) -> str:
        """
        Generate a presigned URL for accessing a file
        
        Args:
            file_key: S3 object key
            expiration: URL expiration time in seconds
        
        Returns:
            Presigned URL string
        """
        if not self.is_enabled():
            return ""
        
        try:
            expiration = expiration or S3_URL_EXPIRATION
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_key
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {e}")
            return ""
    
    def delete_file(self, file_key: str) -> bool:
        """
        Delete a file from S3
        
        Args:
            file_key: S3 object key to delete
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            logger.error("S3 service is not enabled")
            return False
        
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            logger.info(f"File deleted successfully: {file_key}")
            return True
        except ClientError as e:
            logger.error(f"S3 delete error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during deletion: {e}")
            return False
    
    def get_file_metadata(self, file_key: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a file
        
        Args:
            file_key: S3 object key
        
        Returns:
            Dict with file metadata or None if failed
        """
        if not self.is_enabled():
            return None
        
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return {
                'file_key': file_key,
                'file_size': response.get('ContentLength'),
                'content_type': response.get('ContentType'),
                'last_modified': response.get('LastModified'),
                'metadata': response.get('Metadata', {})
            }
        except ClientError as e:
            logger.error(f"Error getting file metadata: {e}")
            return None
    
    def ensure_bucket_accessible(self):
        """Ensure bucket is accessible before use (lazy verification)"""
        if not self.enabled or not hasattr(self, 's3_client'):
            return False
        
        if not hasattr(self, '_bucket_verified'):
            try:
                self._verify_bucket()
                self._bucket_verified = True
                return self.enabled
            except Exception as e:
                logger.error(f"Lazy bucket verification failed: {e}")
                self.enabled = False
                return False
        
        return self.enabled


# Global S3 service instance
s3_service = S3Service()


def get_s3_service() -> S3Service:
    """Get the global S3 service instance"""
    return s3_service

