"""
Configuration settings for the application
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "patients_db")

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24  # Token expires in 24 hours

# Email Configuration
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("SENDER_EMAIL", "")  # Changed from EMAIL_USER
EMAIL_PASSWORD = os.getenv("SENDER_PASSWORD", "")  # Changed from EMAIL_PASSWORD
EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@patientalert.com")

# Webhook Configuration
DEFAULT_WEBHOOK_URL = os.getenv('DEFAULT_WEBHOOK_URL', 'https://n8n.srv795087.hstgr.cloud/webhook/bf25c478-c4a9-44c5-8f43-08c3fcae51f9')

# Server Configuration
PORT = int(os.getenv("PORT", "5000"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# AI Services Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "pregnancy_knowledge")
QDRANT_TIMEOUT_SEC = float(os.getenv("QDRANT_TIMEOUT_SEC", "60"))
QDRANT_BATCH_SIZE = int(os.getenv("QDRANT_BATCH_SIZE", "64"))

# Embeddings Configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
VECTOR_SIZE = int(os.getenv("VECTOR_SIZE", "384"))

# LLM Configuration
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
TOP_K = int(os.getenv("TOP_K", "5"))
RETRIEVAL_MIN_SCORE = float(os.getenv("RETRIEVAL_MIN_SCORE", "0.70"))

# User-visible text and prompts (dynamic via env)
DISCLAIMER_TEXT = os.getenv(
    "DISCLAIMER_TEXT",
    "This information is educational and not a medical diagnosis. If you have red-flag symptoms such as heavy bleeding, severe pain, high fever, severe headache with vision changes, reduced fetal movement, or feeling very unwell, seek urgent care immediately."
)

FALLBACK_STATIC_TEXT = os.getenv(
    "FALLBACK_STATIC_TEXT",
    "General guidance: rest, hydrate, track symptoms, avoid triggers, and contact your prenatal provider for advice."
)

FALLBACK_SYSTEM_PROMPT = os.getenv(
    "FALLBACK_SYSTEM_PROMPT",
    "You are a cautious pregnancy symptom assistant. Provide 3-5 concise, trimester-aware self-care suggestions, avoid medications/doses, include when to seek urgent care, and always add a medical disclaimer."
)

SUMMARY_SYSTEM_PROMPT = os.getenv(
    "SUMMARY_SYSTEM_PROMPT",
    "You are a cautious medical assistant supporting an obstetrician. Your ONLY knowledge source is the evidence bullets provided in the user message. Do NOT use outside knowledge. Primary task: Based on the evidence, determine the overall urgency level (mild, moderate, urgent) for the patient's symptoms. Provide a concise, trimester-specific guidance summary for a pregnant patient. Instructions: Use 3–5 short bullets. Include one bullet explicitly stating when to seek urgent care, based on evidence triage tags. Be clear, factual, and non-alarmist. If evidence is conflicting or insufficient, state that clearly. Do NOT invent facts not present in evidence. Do NOT recommend medications, dosages, diagnostic codes, or brand names. DO NOT make definitive diagnoses; frame as possible concerns and next steps. Keep lay-friendly tone; avoid jargon where possible. Assume this is general guidance, not a substitute for clinical judgment. Output format: Start with: 'Urgency level: <mild/moderate/urgent/uncertain>' Then list plain text bullets (no numbering, no markdown headings). Each bullet ≤ 25 words."
)

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
S3_URL_EXPIRATION = int(os.getenv("S3_URL_EXPIRATION", "3600"))  # Signed URL expiration in seconds

