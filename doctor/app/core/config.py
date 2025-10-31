"""
Configuration settings for the Doctor application
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "patients_db")
PATIENTS_COLLECTION = os.getenv("PATIENTS_COLLECTION", "patients")
DOCTORS_COLLECTION = os.getenv("DOCTORS_COLLECTION", "doctors")

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24  # Token expires in 24 hours

# Email Configuration
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@doctoralert.com")

# Server Configuration
PORT = int(os.getenv("PORT", "5001"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# AI Services Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# AWS S3 Configuration for Chat File Storage
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "pregnancy-ai-chat")

# File Upload Limits (in MB)
MAX_IMAGE_SIZE = int(os.getenv("MAX_IMAGE_SIZE", "10"))
MAX_DOCUMENT_SIZE = int(os.getenv("MAX_DOCUMENT_SIZE", "50"))
MAX_VOICE_SIZE = int(os.getenv("MAX_VOICE_SIZE", "25"))

# Allowed File Extensions
ALLOWED_IMAGE_EXTENSIONS = os.getenv("ALLOWED_IMAGE_EXTENSIONS", "jpg,jpeg,png,gif,webp").split(',')
ALLOWED_DOCUMENT_EXTENSIONS = os.getenv("ALLOWED_DOCUMENT_EXTENSIONS", "pdf,doc,docx,txt").split(',')
ALLOWED_VOICE_EXTENSIONS = os.getenv("ALLOWED_VOICE_EXTENSIONS", "mp3,wav,ogg,webm,m4a").split(',')

# S3 Upload Configuration
S3_UPLOAD_ENABLED = os.getenv("S3_UPLOAD_ENABLED", "true").lower() == "true"
S3_URL_EXPIRATION = int(os.getenv("S3_URL_EXPIRATION", "86400"))  # Signed URL expiration in seconds (24 hours)

# Timezone Configuration
TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")  # Indian Standard Time (IST)

