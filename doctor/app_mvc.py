#!/usr/bin/env python3
"""
Patient Alert System - MVC Architecture
Main application file with MVC structure
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from datetime import datetime, timedelta
import threading
import time

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv not installed. Install with: pip install python-dotenv")

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import MVC components
from models.database import Database
from models.doctor_model import DoctorModel
from models.patient_model import PatientModel
from models.otp_model import OTPModel
from controllers.auth_controller import AuthController
from controllers.doctor_controller import DoctorController
from controllers.patient_controller import PatientController
from controllers.otp_controller import OTPController
from services.email_service import EmailService
from services.jwt_service import JWTService
from controllers.dictation_controller import DictationController
from models.dictation_model import DictationModel
from models.nurse_model import NurseModel
from utils.validators import Validators
from utils.helpers import Helpers
import hashlib
import re
from functools import wraps

# Import token_required decorator from app_simple
from app_simple import token_required


# Import Voice Dictation components
from controllers.voice_controller import VoiceController
from controllers.conversation_controller import ConversationController
from controllers.transcription_controller import TranscriptionController
from models.voice_model import VoiceModel
from models.conversation_model import ConversationModel
from models.transcription_model import TranscriptionModel
from services.elevenlabs_service import ElevenLabsService
from services.websocket_service import WebSocketService
from services.audio_processing_service import AudioProcessingService

# Import Doctor Availability components
from models.doctor_availability_model import DoctorAvailabilityModel
from controllers.doctor_availability_controller import DoctorAvailabilityController

# Import Doctor Chat Module
from app.shared.socket_service import init_socketio
from app.modules.doctor_chat.routes import doctor_chat_bp
from app.modules.doctor_chat.file_upload_routes import doctor_file_upload_bp
from app.modules.doctor_chat.socket_handlers import init_doctor_chat_socket_handlers
from app.modules.doctor_chat.repository import init_doctor_chat_repository
from app.modules.doctor_chat.services import init_doctor_chat_service

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize Socket.IO for real-time chat
socketio = init_socketio(app)
print("✅ Socket.IO initialized for doctor chat")

# Configuration
class Config:
    MONGODB_URI = os.environ.get('MONGO_URI')
    DATABASE_NAME = os.environ.get('DB_NAME')
    SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
    SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM')

app.config.from_object(Config)

# Initialize services
db = Database()
# Ensure database connection is established
db.connect()

email_service = EmailService()
jwt_service = JWTService()
# voice_service = VoiceService()  # Removed voice functionality
validators = Validators()
helpers = Helpers()

# Initialize models
doctor_model = DoctorModel(db)
patient_model = PatientModel(db)
otp_model = OTPModel(db)
nurse_model = NurseModel(db)

# Initialize voice models
voice_model = VoiceModel(db)
conversation_model = ConversationModel(db)
transcription_model = TranscriptionModel(db)

# Initialize voice services
elevenlabs_service = ElevenLabsService()
websocket_service = WebSocketService()
audio_processing_service = AudioProcessingService()

# Initialize availability models and controllers
availability_model = DoctorAvailabilityModel(db)
availability_controller = DoctorAvailabilityController(availability_model, jwt_service, validators)

# Initialize controllers
auth_controller = AuthController(doctor_model, patient_model, nurse_model, otp_model, jwt_service, email_service, validators)
doctor_controller = DoctorController(doctor_model, jwt_service, validators)
patient_controller = PatientController()
otp_controller = OTPController(otp_model, jwt_service, email_service, validators)
dictation_model = DictationModel(db)
dictation_controller = DictationController(dictation_model, jwt_service, validators)

# Initialize nurse controller
from controllers.nurse_controller import NurseController
nurse_controller = NurseController(nurse_model, validators)

# Initialize voice controllers
voice_controller = VoiceController(voice_model, jwt_service, validators)
conversation_controller = ConversationController(conversation_model, jwt_service, validators)
transcription_controller = TranscriptionController(transcription_model, jwt_service, validators)
# voice_controller = VoiceController()  # Removed voice functionality


# Initialize Doctor Chat Module (MUST be done before registering blueprints)
print("🔧 Initializing doctor chat repository and service...")
init_doctor_chat_repository(db)
init_doctor_chat_service(db)
print("✅ Doctor chat repository and service initialized")

# Initialize and check S3 Service
print("🔧 Checking S3 file storage service...")
from app.shared.s3_service import s3_service
if s3_service.is_enabled():
    print(f"✅ S3 Service ENABLED - Bucket: {s3_service.bucket_name}")
    print(f"📂 Files will be stored in AWS S3")
else:
    print("⚠️  S3 Service DISABLED - Check AWS credentials in .env file")
    print("⚠️  File uploads may fail or use fallback storage")

# Register Doctor Chat Blueprints
app.register_blueprint(doctor_chat_bp, url_prefix='/doctor/chat')
app.register_blueprint(doctor_file_upload_bp, url_prefix='/doctor/chat/files')
print("✅ Doctor chat blueprints registered at /doctor/chat and /doctor/chat/files")

# Initialize Doctor Chat Socket Handlers  
init_doctor_chat_socket_handlers(socketio, db)
print("✅ Doctor chat socket handlers initialized")

# ==================== AUTHENTICATION DECORATOR ====================

def token_required(f):
    """Decorator to require JWT token for protected routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({"success": False, "error": "Invalid token format"}), 401
        
        if not token:
            return jsonify({"success": False, "error": "Token is missing"}), 401
        
        try:
            # Verify token using JWT service
            payload = jwt_service.verify_access_token(token)
            if not payload or not payload.get('success'):
                return jsonify({"success": False, "error": "Invalid or expired token"}), 401
            
            # Add user data to request
            request.user_data = payload.get('data', {})
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({"success": False, "error": f"Token verification failed: {str(e)}"}), 401
    
    return decorated
    
# Routes
@app.route('/', methods=['GET'])
def root_endpoint():
    """Root endpoint with API information"""
    return jsonify({
        'message': 'Doctor Patient Management API',
        'version': '2.0.0',
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'endpoints': {
            'health': '/health',
            'patients': '/patients',
            'doctors': '/doctors',
            'auth': '/doctor-login',
            'ai_summary': '/doctor/patient/{patient_id}/ai-summary',
            'debug': '/debug/openai-config',
            'invite': {
                'generate': 'POST /api/doctor/generate-invite',
                'verify': 'GET /api/invite/verify/{code}',
                'list': 'GET /api/doctor/invites'
            },
            'connections': {
                'requests': 'GET /api/doctor/connection-requests',
                'respond': 'POST /api/doctor/respond-to-request',
                'remove': 'POST /api/doctor/remove-connection',
                'connected_patients': 'GET /api/doctor/connected-patients'
            }
        },
        'documentation': 'See API documentation for detailed endpoint usage'
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

# Debug endpoints for OpenAI configuration
@app.route('/debug/openai-config', methods=['GET'])
def debug_openai_config():
    """Debug OpenAI API key configuration"""
    try:
        import os
        
        # Check environment variables
        api_key = os.getenv('OPENAI_API_KEY')
        
        debug_info = {
            'openai_api_key_present': bool(api_key),
            'openai_api_key_format': f"{api_key[:10]}...{api_key[-4:]}" if api_key else None,
            'openai_api_key_valid_format': api_key.startswith('sk-') if api_key else False,
            'environment_vars': {k: v for k, v in os.environ.items() if 'OPENAI' in k or 'API' in k},
            'python_path': os.getcwd(),
            'environment': os.getenv('ENVIRONMENT', 'development')
        }
        
        return jsonify({
            'success': True,
            'debug_info': debug_info,
            'message': 'OpenAI configuration debug info'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Debug failed'
        }), 500

@app.route('/debug/test-openai', methods=['GET'])
def test_openai_api():
    """Test OpenAI API connection"""
    try:
        import os
        from openai import OpenAI
        
        # Check OpenAI library version
        try:
            import openai
            openai_version = openai.__version__
        except:
            openai_version = "Unknown"
        
        # Get API key
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'OPENAI_API_KEY not found in environment variables',
                'message': 'Please set OPENAI_API_KEY in your environment',
                'openai_version': openai_version
            }), 400
        
        if not api_key.startswith('sk-'):
            return jsonify({
                'success': False,
                'error': 'Invalid API key format (should start with sk-)',
                'message': 'Please check your OpenAI API key',
                'openai_version': openai_version
            }), 400
        
        # Simple OpenAI client initialization for version 1.3.0
        try:
            import openai
            openai.api_key = api_key
            print('✅ OpenAI client initialized with simple method')
        except Exception as client_error:
            return jsonify({
                'success': False,
                'error': f'Failed to initialize OpenAI client: {str(client_error)}',
                'message': 'OpenAI client initialization failed',
                'error_type': type(client_error).__name__
            }), 500
        
        # Test API connection with simple method
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say 'Hello, OpenAI API is working!'"}
                ],
                max_tokens=50,
                temperature=0.3
            )
            print('✅ OpenAI API call successful')
                
        except Exception as api_error:
            return jsonify({
                'success': False,
                'error': f'OpenAI API call failed: {str(api_error)}',
                'message': 'OpenAI API test failed',
                'error_type': type(api_error).__name__
            }), 500
        
        return jsonify({
            'success': True,
            'openai_response': response.choices[0].message.content,
            'model_used': response.model,
            'tokens_used': response.usage.total_tokens,
            'message': 'OpenAI API test successful',
            'openai_version': openai_version
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'OpenAI API test failed'
        }), 500

# Authentication Routes
@app.route('/doctor-signup', methods=['POST'])
def doctor_signup():
    """Doctor signup endpoint"""
    return auth_controller.doctor_signup(request)

@app.route('/doctor-send-otp', methods=['POST'])
def doctor_send_otp():
    """Send OTP to doctor email"""
    return otp_controller.doctor_send_otp(request)

@app.route('/doctor-verify-otp', methods=['POST'])
def doctor_verify_otp():
    """Verify doctor OTP"""
    return otp_controller.doctor_verify_otp(request)

@app.route('/resend-otp', methods=['POST'])
def resend_otp():
    """Resend OTP"""
    return otp_controller.resend_otp(request)

# Doctor Routes
@app.route('/doctor/profile/<doctor_id>', methods=['GET'])
def get_doctor_profile(doctor_id):
    """Get doctor profile"""
    return doctor_controller.get_profile(doctor_id)

@app.route('/doctor/profile/<doctor_id>', methods=['PUT'])
def update_doctor_profile(doctor_id):
    """Update doctor profile"""
    return doctor_controller.update_profile(doctor_id, request)

@app.route('/doctor/complete-profile', methods=['POST'])
def complete_doctor_profile():
    """Complete doctor profile"""
    return doctor_controller.complete_profile(request)

# Public doctor endpoints for patient selection
@app.route('/doctors', methods=['GET'])
def get_all_doctors():
    """Get all doctors list for patient selection"""
    return doctor_controller.get_all_doctors(request)

@app.route('/doctors/search', methods=['GET'])
def search_doctors():
    """Search doctors with filters for patient selection"""
    return doctor_controller.get_all_doctors(request)

@app.route('/doctors/<doctor_id>', methods=['GET'])
def get_public_doctor_profile(doctor_id):
    """Get public doctor profile for patient selection"""
    return doctor_controller.get_public_doctor_profile(doctor_id)

# Kebab-case endpoints for Flutter app compatibility
@app.route('/doctor-reset-password', methods=['POST'])
def doctor_reset_password():
    """Reset doctor password - kebab-case endpoint"""
    return auth_controller.doctor_reset_password(request)

@app.route('/doctor-forgot-password', methods=['POST'])
def doctor_forgot_password():
    """Forgot doctor password - kebab-case endpoint"""
    return auth_controller.doctor_forgot_password(request)

@app.route('/doctor-complete-profile', methods=['POST'])
def doctor_complete_profile_kebab():
    """Complete doctor profile - kebab-case endpoint"""
    return doctor_controller.complete_profile(request)

# Doctor Profile CRUD Operations - Kebab-case endpoints
@app.route('/doctor-profile/<doctor_id>', methods=['GET'])
def get_doctor_profile_kebab(doctor_id):
    """Get doctor profile by ID - kebab-case endpoint"""
    return doctor_controller.get_profile(doctor_id)

@app.route('/doctor-profile/<doctor_id>', methods=['PUT'])
def update_doctor_profile_kebab(doctor_id):
    """Update doctor profile - kebab-case endpoint"""
    return doctor_controller.update_profile(doctor_id, request)

@app.route('/doctor-profile/<doctor_id>', methods=['DELETE'])
def delete_doctor_profile_kebab(doctor_id):
    """Delete doctor profile (soft delete) - kebab-case endpoint"""
    return doctor_controller.delete_profile(doctor_id)

@app.route('/doctor-profile-fields', methods=['GET'])
def doctor_profile_fields():
    """Get doctor profile fields - kebab-case endpoint"""
    return doctor_controller.get_profile_fields(request)

@app.route('/complete-profile', methods=['POST'])
def complete_profile():
    """Complete profile - generic endpoint for Flutter compatibility"""
    return doctor_controller.complete_profile(request)

@app.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password - generic endpoint for Flutter compatibility"""
    return auth_controller.doctor_reset_password(request)

@app.route('/doctor/patients', methods=['GET'])
def get_doctor_patients():
    """Get patients list for doctor"""
    return doctor_controller.get_patients(request)

@app.route('/doctor/patient/<patient_id>', methods=['GET'])
def get_doctor_patient_details(patient_id):
    """Get detailed patient information for doctor"""
    return doctor_controller.get_patient_details(request, patient_id)

@app.route('/doctor/patient/<patient_id>/full-details', methods=['GET'])
def get_patient_full_details(patient_id):
    """Get complete patient details with all health data"""
    return doctor_controller.get_patient_full_details(request, patient_id)

@app.route('/doctor/patient/<patient_id>/ai-summary', methods=['GET'])
def get_patient_ai_summary(patient_id):
    """Get AI-powered medical summary for a patient"""
    return doctor_controller.get_patient_ai_summary(request, patient_id)

# Dictations - text only
@app.route('/doctor/patient/<patient_id>/dictations', methods=['POST'])
def create_patient_dictation(patient_id):
    return dictation_controller.create_dictation(request, patient_id)

# Dictation history - doctor view
@app.route('/doctor/patient/<patient_id>/dictations', methods=['GET'])
def list_patient_dictations_doctor(patient_id):
    return dictation_controller.list_for_doctor(request, patient_id)

# Dictation history - patient view (future-ready)
@app.route('/patient/<patient_id>/dictations', methods=['GET'])
def list_patient_dictations_patient(patient_id):
    return dictation_controller.list_for_patient(request, patient_id)

@app.route('/doctor/appointments', methods=['GET'])
def get_doctor_appointments():
    """Get appointments for doctor"""
    return doctor_controller.get_appointments(request)

@app.route('/doctor/appointments', methods=['POST'])
def create_doctor_appointment():
    """Create new appointment for doctor"""
    return doctor_controller.create_appointment(request)

@app.route('/doctor/appointments/<appointment_id>', methods=['GET'])
def get_single_appointment(appointment_id):
    """Get single appointment by ID"""
    return doctor_controller.get_appointment_by_id(request, appointment_id)

@app.route('/doctor/appointments/<appointment_id>', methods=['PUT'])
def update_doctor_appointment(appointment_id):
    """Update appointment for doctor"""
    return doctor_controller.update_appointment(request, appointment_id)

@app.route('/doctor/appointments/<appointment_id>', methods=['DELETE'])
def delete_doctor_appointment(appointment_id):
    """Delete appointment for doctor"""
    return doctor_controller.delete_appointment(request, appointment_id)

@app.route('/doctor/dashboard-stats', methods=['GET'])
def get_doctor_dashboard_stats():
    """Get dashboard statistics for doctor"""
    return doctor_controller.get_dashboard_stats(request)

# Patient Health Data Endpoints
@app.route('/medication/get-medication-history/<patient_id>', methods=['GET'])
def get_medication_history(patient_id):
    """Get medication history for patient"""
    return doctor_controller.get_medication_history(request, patient_id)

@app.route('/symptoms/get-analysis-reports/<patient_id>', methods=['GET'])
def get_symptom_analysis_reports(patient_id):
    """Get symptom analysis reports for patient"""
    return doctor_controller.get_symptom_analysis_reports(request, patient_id)

@app.route('/nutrition/get-food-entries/<patient_id>', methods=['GET'])
def get_food_entries(patient_id):
    """Get food entries for patient"""
    return doctor_controller.get_food_entries(request, patient_id)

@app.route('/medication/get-tablet-tracking-history/<patient_id>', methods=['GET'])
def get_tablet_tracking_history(patient_id):
    """Get tablet tracking history for patient"""
    return doctor_controller.get_tablet_tracking_history(request, patient_id)

@app.route('/profile/<patient_id>', methods=['GET'])
def get_patient_profile(patient_id):
    """Get patient profile"""
    return doctor_controller.get_patient_profile(request, patient_id)

@app.route('/kick-count/get-kick-history/<patient_id>', methods=['GET'])
def get_kick_count_history(patient_id):
    """Get kick count history for patient"""
    return doctor_controller.get_kick_count_history(request, patient_id)

@app.route('/mental-health/history/<patient_id>', methods=['GET'])
def get_mental_health_history(patient_id):
    """Get mental health history for patient"""
    return doctor_controller.get_mental_health_history(request, patient_id)

@app.route('/prescription/documents/<patient_id>', methods=['GET'])
def get_prescription_documents(patient_id):
    """Get prescription documents for patient"""
    return doctor_controller.get_prescription_documents(request, patient_id)

@app.route('/vital-signs/history/<patient_id>', methods=['GET'])
def get_vital_signs_history(patient_id):
    """Get vital signs history for patient"""
    return doctor_controller.get_vital_signs_history(request, patient_id)

# Patient Routes
@app.route('/patient/signup', methods=['POST'])
def patient_signup():
    """Patient signup"""
    return auth_controller.patient_signup(request)

@app.route('/patient/verify-otp', methods=['POST'])
def patient_verify_otp():
    """Verify patient OTP"""
    return otp_controller.patient_verify_otp(request)

# Patient CRUD Routes
@app.route('/patients', methods=['POST'])
def create_patient():
    """Create a new patient"""
    return patient_controller.create_patient(request)

@app.route('/patients', methods=['GET'])
def get_all_patients():
    """Get all patients with pagination and search"""
    return patient_controller.get_all_patients(request)

@app.route('/patients/<patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Get patient by ID"""
    return patient_controller.get_patient(request, patient_id)

@app.route('/patients/<patient_id>', methods=['PUT'])
def update_patient(patient_id):
    """Update patient"""
    return patient_controller.update_patient(request, patient_id)

@app.route('/patients/<patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    """Delete patient"""
    return patient_controller.delete_patient(request, patient_id)

@app.route('/doctors/<doctor_id>/patients', methods=['GET'])
def get_patients_by_doctor(doctor_id):
    """Get all patients assigned to a specific doctor"""
    return patient_controller.get_patients_by_doctor(request, doctor_id)

@app.route('/doctor-login', methods=['POST'])
def login():
    """Login endpoint for both doctors and patients"""
    return auth_controller.login(request)

@app.route('/doctor-login', methods=['POST'])
def doctor_login():
    """Doctor-only login endpoint"""
    return auth_controller.doctor_login(request)

# ===== VOICE DICTATION ENDPOINTS (42 endpoints) =====

# Nurse Management Routes
def get_current_user_from_token(request):
    """Extract current user from JWT token"""
    try:
        # Get the token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        # Verify and decode token
        user_data = jwt_service.verify_access_token(token)
        if not user_data['success']:
            return None
            
        return user_data['data']
    except Exception as e:
        print(f"Error extracting user from token: {e}")
        return None

@app.route('/api/nurses', methods=['POST'])
def create_nurse():
    """Create a new nurse"""
    current_user = get_current_user_from_token(request)
    if not current_user:
        return jsonify({'error': 'Authentication required'}), 401
    return nurse_controller.create_nurse(request, current_user)

@app.route('/api/nurses', methods=['GET'])
def get_nurses():
    """Get all nurses for the logged-in doctor"""
    current_user = get_current_user_from_token(request)
    if not current_user:
        return jsonify({'error': 'Authentication required'}), 401
    return nurse_controller.get_nurses(request, current_user)

@app.route('/api/nurses/delete', methods=['POST'])
def delete_nurse():
    """Delete a nurse by email"""
    current_user = get_current_user_from_token(request)
    if not current_user:
        return jsonify({'error': 'Authentication required'}), 401
    return nurse_controller.delete_nurse(request, current_user)

@app.route('/api/nurses/<string:nurse_id>/reset-password', methods=['POST'])
def reset_nurse_password(nurse_id):
    """Reset nurse password"""
    current_user = get_current_user_from_token(request)
    if not current_user:
        return jsonify({'error': 'Authentication required'}), 401
    return nurse_controller.reset_nurse_password(request, nurse_id, current_user)

# Health Endpoints (2)
@app.route('/voice/health', methods=['GET'])
def voice_health_check():
    """Voice service health check"""
    return voice_controller.health_check()

@app.route('/voice/health/detailed', methods=['GET'])
def voice_detailed_health():
    """Detailed voice service health check"""
    return voice_controller.detailed_health_check()

# Authentication Endpoints (5)
@app.route('/voice/auth/login', methods=['POST'])
def voice_login():
    """Voice authentication login"""
    return voice_controller.login(request)

@app.route('/voice/auth/refresh', methods=['POST'])
def voice_refresh_token():
    """Refresh voice authentication token"""
    return voice_controller.refresh_token(request)

@app.route('/voice/auth/me', methods=['GET'])
def voice_get_user():
    """Get current voice user information"""
    return voice_controller.get_current_user(request)

@app.route('/voice/auth/logout', methods=['POST'])
def voice_logout():
    """Voice user logout"""
    return voice_controller.logout(request)

@app.route('/voice/auth/verify', methods=['GET'])
def voice_verify_token():
    """Verify voice authentication token"""
    return voice_controller.verify_token(request)

# Conversation Management (8)
@app.route('/voice/conversations', methods=['POST'])
def create_voice_conversation():
    """Create a new voice conversation"""
    return conversation_controller.create_conversation(request)

@app.route('/voice/conversations', methods=['GET'])
def get_voice_conversations():
    """Get all voice conversations with pagination"""
    return conversation_controller.get_conversations(request)

@app.route('/voice/conversations/<int:conversation_id>', methods=['GET'])
def get_voice_conversation(conversation_id):
    """Get voice conversation by ID"""
    return conversation_controller.get_conversation(request, conversation_id)

@app.route('/voice/conversations/<int:conversation_id>', methods=['PUT'])
def update_voice_conversation(conversation_id):
    """Update voice conversation by ID"""
    return conversation_controller.update_conversation(request, conversation_id)

@app.route('/voice/conversations/<int:conversation_id>', methods=['DELETE'])
def delete_voice_conversation(conversation_id):
    """Delete voice conversation by ID"""
    return conversation_controller.delete_conversation(request, conversation_id)

@app.route('/voice/conversations/<int:conversation_id>/transcriptions', methods=['GET'])
def get_conversation_transcriptions(conversation_id):
    """Get all transcriptions for a voice conversation"""
    return conversation_controller.get_transcriptions(request, conversation_id)

@app.route('/voice/conversations/<int:conversation_id>/activate', methods=['POST'])
def activate_voice_conversation(conversation_id):
    """Activate a voice conversation"""
    return conversation_controller.activate_conversation(request, conversation_id)

@app.route('/voice/conversations/<int:conversation_id>/deactivate', methods=['POST'])
def deactivate_voice_conversation(conversation_id):
    """Deactivate a voice conversation"""
    return conversation_controller.deactivate_conversation(request, conversation_id)

# Transcription Management (7)
@app.route('/voice/transcriptions', methods=['POST'])
def create_voice_transcription():
    """Create a new voice transcription"""
    return transcription_controller.create_transcription(request)

@app.route('/voice/transcriptions', methods=['GET'])
def get_voice_transcriptions():
    """Get all voice transcriptions with pagination"""
    return transcription_controller.get_transcriptions(request)

@app.route('/voice/transcriptions/<int:transcription_id>', methods=['GET'])
def get_voice_transcription(transcription_id):
    """Get voice transcription by ID"""
    return transcription_controller.get_transcription(request, transcription_id)

@app.route('/voice/transcriptions/<int:transcription_id>', methods=['PUT'])
def update_voice_transcription(transcription_id):
    """Update voice transcription by ID"""
    return transcription_controller.update_transcription(request, transcription_id)

@app.route('/voice/transcriptions/<int:transcription_id>', methods=['DELETE'])
def delete_voice_transcription(transcription_id):
    """Delete voice transcription by ID"""
    return transcription_controller.delete_transcription(request, transcription_id)

@app.route('/voice/transcriptions/conversation/<int:conversation_id>', methods=['GET'])
def get_transcriptions_by_conversation(conversation_id):
    """Get all transcriptions for a specific conversation"""
    return transcription_controller.get_by_conversation(request, conversation_id)

@app.route('/voice/transcriptions/conversation/<int:conversation_id>/final', methods=['GET'])
def get_final_transcriptions(conversation_id):
    """Get only final transcriptions for a conversation"""
    return transcription_controller.get_final_transcriptions(request, conversation_id)

# Mobile API Endpoints (10)
@app.route('/voice/mobile/config', methods=['GET'])
def voice_mobile_config():
    """Get mobile configuration for voice service"""
    return voice_controller.get_mobile_config(request)

@app.route('/voice/mobile/conversation', methods=['POST'])
def create_mobile_conversation():
    """Create a mobile voice conversation"""
    return voice_controller.create_mobile_conversation(request)

@app.route('/voice/mobile/transcription', methods=['POST'])
def create_mobile_transcription():
    """Create a mobile voice transcription"""
    return voice_controller.create_mobile_transcription(request)

@app.route('/voice/mobile/audio/upload', methods=['POST'])
def upload_mobile_audio():
    """Upload audio file for mobile voice service"""
    return voice_controller.upload_audio(request)

@app.route('/voice/mobile/sync', methods=['POST'])
def sync_mobile_data():
    """Sync mobile voice data"""
    return voice_controller.sync_data(request)

@app.route('/voice/mobile/conversations', methods=['GET'])
def get_mobile_conversations():
    """Get mobile voice conversations"""
    return voice_controller.get_mobile_conversations(request)

@app.route('/voice/mobile/offline/data', methods=['GET'])
def get_offline_data():
    """Get offline voice data for mobile"""
    return voice_controller.get_offline_data(request)

@app.route('/voice/mobile/push/register', methods=['POST'])
def register_push_token():
    """Register push notification token for mobile"""
    return voice_controller.register_push_token(request)

@app.route('/voice/mobile/health', methods=['GET'])
def mobile_health_check():
    """Mobile voice service health check"""
    return voice_controller.mobile_health_check(request)

# Audio Processing (1)
@app.route('/voice/transcriptions/process-audio', methods=['POST'])
def process_audio_chunk():
    """Process audio chunk for transcription"""
    return transcription_controller.process_audio(request)

# WebSocket Support (1) - Note: Requires Flask-SocketIO for full WebSocket support
# For now, we'll provide HTTP endpoints that simulate WebSocket functionality
@app.route('/voice/ws/connect/<int:conversation_id>', methods=['POST'])
def websocket_connect(conversation_id):
    """Connect to voice WebSocket (HTTP simulation)"""
    return jsonify({
        "success": True,
        "data": {
            "conversation_id": conversation_id,
            "connection_id": f"ws_{int(time.time() * 1000)}",
            "status": "connected",
            "message": "WebSocket connection established (HTTP simulation)"
        },
        "message": "Connected to voice service"
    })

# Additional Voice Integration Endpoints (8)
@app.route('/voice/patient/<patient_id>/conversations', methods=['GET'])
def get_patient_voice_conversations(patient_id):
    """Get voice conversations for a specific patient"""
    try:
        # Get conversations with patient context
        conversations = conversation_model.get_conversations({
            "extra_data.patient_id": patient_id
        })
        
        return jsonify({
            "success": True,
            "data": {
                "patient_id": patient_id,
                "conversations": conversations
            },
            "message": "Patient voice conversations retrieved"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/voice/patient/<patient_id>/conversations', methods=['POST'])
def create_patient_voice_conversation(patient_id):
    """Create voice conversation for a specific patient"""
    try:
        data = request.get_json()
        
        # Add patient context to conversation
        conversation_data = {
            "title": data.get("title", f"Patient {patient_id} Consultation"),
            "language": data.get("language", "en"),
            "extra_data": {
                "patient_id": patient_id,
                "doctor_id": data.get("doctor_id", ""),
                "department": data.get("department", "General")
            }
        }
        
        conversation_id = conversation_model.create_conversation(conversation_data)
        
        return jsonify({
            "success": True,
            "data": {
                "conversation_id": conversation_id,
                "patient_id": patient_id,
                "title": conversation_data["title"]
            },
            "message": "Patient voice conversation created"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/voice/status', methods=['GET'])
def get_voice_service_status():
    """Get comprehensive voice service status"""
    try:
        return jsonify({
            "success": True,
            "data": {
                "service_status": "running",
                "total_endpoints": 42,
                "active_connections": websocket_service.get_connection_count(),
                "elevenlabs_status": elevenlabs_service.get_api_status(),
                "supported_formats": audio_processing_service.get_supported_formats(),
                "max_file_size": audio_processing_service.get_max_file_size(),
                "max_duration": audio_processing_service.get_max_duration()
            },
            "message": "Voice service status retrieved"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/voice/elevenlabs/status', methods=['GET'])
def get_elevenlabs_status():
    """Get ElevenLabs API status"""
    try:
        status = elevenlabs_service.get_api_status()
        return jsonify({
            "success": True,
            "data": status,
            "message": "ElevenLabs status retrieved"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/voice/elevenlabs/models', methods=['GET'])
def get_elevenlabs_models():
    """Get available ElevenLabs models"""
    try:
        models = elevenlabs_service.get_available_models()
        return jsonify({
            "success": True,
            "data": models,
            "message": "ElevenLabs models retrieved"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/voice/audio/validate', methods=['POST'])
def validate_audio_file():
    """Validate uploaded audio file"""
    try:
        if 'audio_file' not in request.files:
            return jsonify({
                "success": False,
                "error": "No audio file provided"
            }), 400
        
        audio_file = request.files['audio_file']
        if audio_file.filename == '':
            return jsonify({
                "success": False,
                "error": "No file selected"
            }), 400
        
        # Read file data
        file_data = audio_file.read()
        
        # Validate audio
        validation_result = audio_processing_service.validate_audio_file(file_data, audio_file.filename)
        
        return jsonify({
            "success": True,
            "data": validation_result,
            "message": "Audio file validation completed"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/voice/audio/features', methods=['POST'])
def extract_audio_features():
    """Extract features from audio file"""
    try:
        if 'audio_file' not in request.files:
            return jsonify({
                "success": False,
                "error": "No audio file provided"
            }), 400
        
        audio_file = request.files['audio_file']
        file_data = audio_file.read()
        
        # Extract features
        features = audio_processing_service.extract_audio_features(file_data)
        
        return jsonify({
            "success": True,
            "data": features,
            "message": "Audio features extracted"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/voice/websocket/status', methods=['GET'])
def get_websocket_status():
    """Get WebSocket service status"""
    try:
        status = websocket_service.get_service_status()
        return jsonify({
            "success": True,
            "data": status,
            "message": "WebSocket status retrieved"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ==================== INVITE & CONNECTION MANAGEMENT ROUTES ====================

@app.route('/api/doctor/generate-invite', methods=['POST'])
@token_required
def doctor_generate_invite():
    """Doctor generates specific invite code for patient email"""
    try:
        data = request.get_json()
        doctor_id = request.user_data.get('user_id')
        
        if not doctor_id:
            return jsonify({"success": False, "error": "Doctor authentication required"}), 403
        
        # Validate required fields
        if not data.get('patient_email'):
            return jsonify({"success": False, "error": "patient_email is required"}), 400
        
        patient_email = data['patient_email'].strip()
        expires_in_days = data.get('expires_in_days', 7)
        custom_message = data.get('message', '')
        email_sent = False  # Initialize email status
        
        # Validate email format
        if not validators.validate_email(patient_email):
            return jsonify({"success": False, "error": "Invalid email format"}), 400
        
        # Check if connection already exists
        patient = db.patients_collection.find_one({"email": patient_email})
        if patient:
            patient_id = patient.get('patient_id')
            # Check in connections collection
            existing_connection = db.connections_collection.find_one({
                "doctor_id": doctor_id,
                "patient_id": patient_id,
                "status": {"$in": ["active", "pending"]}
            })
            if existing_connection:
                return jsonify({
                    "success": False,
                    "error": "Connection already exists with this patient"
                }), 400
        
        # Get doctor info
        doctor = db.doctors_collection.find_one({"doctor_id": doctor_id})
        if not doctor:
            return jsonify({"success": False, "error": "Doctor not found"}), 404
        
        doctor_info = {
            "name": f"{doctor.get('first_name', '')} {doctor.get('last_name', '')}".strip() or doctor.get('username', 'Doctor'),
            "specialty": doctor.get('specialization', 'General Practice'),
            "hospital": doctor.get('hospital_name', '')
        }
        
        # Generate invite code
        invite_code = helpers.generate_invite_code()
        invite_hash = helpers.hash_invite_code(invite_code)
        
        # Store invite in database
        invite_data = {
            "invite_code": invite_code,
            "invite_code_hash": invite_hash,
            "doctor_id": doctor_id,
            "doctor_info": doctor_info,
            "patient_email": patient_email,
            "custom_message": custom_message,
            "usage_limit": 1,
            "usage_count": 0,
            "status": "active",
            "expires_at": datetime.utcnow() + timedelta(days=expires_in_days),
            "security": {
                "max_attempts": 5,
                "attempts_count": 0,
                "last_attempt_at": None
            },
            "metadata": {
                "sent_via": "api",
                "sent_at": datetime.utcnow()
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        db.invite_codes_collection.insert_one(invite_data)
        
        print(f"✅ Doctor {doctor_id} created invite for {patient_email}: {invite_code}")
        
        # Send email to patient with invite code
        try:
            from services.email_service import EmailService
            email_service = EmailService()
            
            # Send email to patient with invite code
            email_result = email_service.send_invite_email(patient_email, invite_code, doctor_info, custom_message)
            
            if email_result['success']:
                print(f"✅ Email sent successfully to {patient_email}")
                email_sent = True
            else:
                print(f"❌ Email sending failed: {email_result['error']}")
                email_sent = False
                
        except Exception as e:
            print(f"❌ Email service error: {e}")
            email_sent = False
        
        return jsonify({
            "success": True,
            "message": f"Invite code generated for {patient_email}",
            "invite": {
                "invite_code": invite_code,
                "patient_email": patient_email,
                "expires_at": invite_data['expires_at'].isoformat(),
                "status": "active",
                "usage_limit": 1,
                "deep_link": f"myapp://invite/{invite_code}"
            },
            "email_sent": email_sent,
            "email_status": "success" if email_sent else "failed"
        }), 201
        
    except Exception as e:
        print(f"❌ Error generating invite: {e}")
        return jsonify({"success": False, "error": f"Failed to generate invite: {str(e)}"}), 500


@app.route('/api/invite/verify/<invite_code>', methods=['GET'])
def verify_invite_code(invite_code):
    """Verify invite code - Public endpoint (no auth required)"""
    try:
        # Validate code format
        if not re.match(r'^[A-Z0-9]{3}-[A-Z0-9]{3}-[A-Z0-9]{3}$', invite_code):
            return jsonify({
                "success": False,
                "valid": False,
                "error": "Invalid invite code format"
            }), 400
        
        # Find invite
        invite = db.invite_codes_collection.find_one({"invite_code": invite_code})
        
        if not invite:
            return jsonify({
                "success": False,
                "valid": False,
                "message": "Invalid invite code"
            }), 404
        
        # Check status
        if invite['status'] != 'active':
            return jsonify({
                "success": False,
                "valid": False,
                "message": f"Invite code is {invite['status']}"
            }), 400
        
        # Check expiration
        if datetime.utcnow() > invite['expires_at']:
            db.invite_codes_collection.update_one(
                {"invite_code": invite_code},
                {"$set": {"status": "expired", "updated_at": datetime.utcnow()}}
            )
            return jsonify({
                "success": False,
                "valid": False,
                "message": "Invite code has expired"
            }), 400
        
        # Check usage
        if invite['usage_count'] >= invite['usage_limit']:
            return jsonify({
                "success": False,
                "valid": False,
                "message": "Invite code has been used"
            }), 400
        
        return jsonify({
            "success": True,
            "valid": True,
            "message": "Valid invite code",
            "doctor": invite['doctor_info'],
            "invite_info": {
                "expires_at": invite['expires_at'].isoformat(),
                "remaining_uses": invite['usage_limit'] - invite['usage_count'],
                "custom_message": invite.get('custom_message', '')
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error verifying invite: {e}")
        return jsonify({
            "success": False,
            "valid": False,
            "error": f"Verification failed: {str(e)}"
        }), 500


@app.route('/api/doctor/invites', methods=['GET'])
@token_required
def get_doctor_invites():
    """Get all invites generated by doctor"""
    try:
        doctor_id = request.user_data.get('user_id')
        
        if not doctor_id:
            return jsonify({"success": False, "error": "Doctor authentication required"}), 403
        
        # Get query parameters
        status = request.args.get('status')  # active, expired, used, or None for all
        
        # Build query
        query = {"doctor_id": doctor_id}
        if status:
            query["status"] = status
        
        # Get invites
        invites = list(db.invite_codes_collection.find(query).sort("created_at", -1).limit(100))
        
        # Format invites
        formatted_invites = []
        for invite in invites:
            formatted_invites.append({
                "invite_code": invite['invite_code'],
                "patient_email": invite['patient_email'],
                "custom_message": invite.get('custom_message', ''),
                "status": invite['status'],
                "usage_count": invite['usage_count'],
                "usage_limit": invite['usage_limit'],
                "created_at": invite['created_at'].isoformat(),
                "expires_at": invite['expires_at'].isoformat(),
                "sent_via": invite.get('metadata', {}).get('sent_via')
            })
        
        print(f"✅ Retrieved {len(formatted_invites)} invites for doctor {doctor_id}")
        
        return jsonify({
            "success": True,
            "invites": formatted_invites,
            "total_count": len(formatted_invites),
            "filter": status or "all"
        }), 200
        
    except Exception as e:
        print(f"❌ Error getting invites: {e}")
        return jsonify({"success": False, "error": f"Failed to fetch invites: {str(e)}"}), 500


@app.route('/api/doctor/connection-requests', methods=['GET'])
@token_required
def get_connection_requests():
    """Doctor views connection requests from patients"""
    try:
        doctor_id = request.user_data.get('user_id')
        
        if not doctor_id:
            return jsonify({"success": False, "error": "Doctor authentication required"}), 403
        
        # Get query parameters
        status = request.args.get('status', 'pending')  # pending, active, rejected, all
        
        # Get connections
        query = {"doctor_id": doctor_id}
        if status != "all":
            query["status"] = status
        
        connections = list(db.connections_collection.find(query).sort("dates.request_sent_at", -1).limit(100))
        
        # Enrich with patient details
        requests = []
        for conn in connections:
            patient = db.patients_collection.find_one({"patient_id": conn['patient_id']})
            if not patient:
                continue
            
            requests.append({
                "connection_id": conn['connection_id'],
                "request_id": conn['connection_id'],
                "patient_id": conn['patient_id'],
                "patient_name": f"{patient.get('first_name', '')} {patient.get('last_name', '')}".strip() or patient.get('username', 'Unknown'),
                "patient_email": patient.get('email'),
                "patient_mobile": patient.get('mobile'),
                "patient_photo": patient.get('profile_photo'),
                "message": conn.get('request_message'),
                "connection_type": conn['connection_type'],
                "status": conn['status'],
                "requested_at": conn['dates']['request_sent_at'].isoformat() if conn['dates'].get('request_sent_at') else None,
                "patient_info": {
                    "age": patient.get('age'),
                    "blood_type": patient.get('blood_type'),
                    "is_pregnant": patient.get('is_pregnant', False),
                    "pregnancy_week": patient.get('pregnancy_week')
                }
            })
        
        print(f"✅ Found {len(requests)} {status} connection requests for doctor {doctor_id}")
        
        return jsonify({
            "success": True,
            "requests": requests,
            "total_count": len(requests),
            "status_filter": status
        }), 200
        
    except Exception as e:
        print(f"❌ Error getting connection requests: {e}")
        return jsonify({"success": False, "error": f"Failed to fetch requests: {str(e)}"}), 500


@app.route('/api/doctor/respond-to-request', methods=['POST'])
@token_required
def respond_to_connection_request():
    """Doctor accepts or rejects patient connection request"""
    try:
        data = request.get_json()
        doctor_id = request.user_data.get('user_id')
        
        if not doctor_id:
            return jsonify({"success": False, "error": "Doctor authentication required"}), 403
        
        # Validate required fields - either connection_id OR invite_code
        if not data.get('connection_id') and not data.get('invite_code'):
            return jsonify({"success": False, "error": "Either 'connection_id' or 'invite_code' is required"}), 400
        
        if data.get('connection_id') and data.get('invite_code'):
            return jsonify({"success": False, "error": "Provide either 'connection_id' or 'invite_code', not both"}), 400
        
        if not data.get('action'):
            return jsonify({"success": False, "error": "action is required (accept or reject)"}), 400
        
        if data['action'] not in ['accept', 'reject']:
            return jsonify({"success": False, "error": "action must be 'accept' or 'reject'"}), 400
        
        action = data['action']
        message = data.get('message', '')
        
        # Get connection - either by connection_id or invite_code
        connection = None
        connection_id = None
        
        if data.get('connection_id'):
            # Method 1: Direct connection_id lookup
            connection_id = data['connection_id']
            connection = db.connections_collection.find_one({"connection_id": connection_id})
            
            if not connection:
                return jsonify({"success": False, "error": "Connection request not found"}), 404
                
        elif data.get('invite_code'):
            # Method 2: Invite code lookup
            invite_code = data['invite_code']
            
            # Find invite code
            invite = db.invite_codes_collection.find_one({"invite_code": invite_code})
            if not invite:
                return jsonify({"success": False, "error": "Invalid invite code"}), 404
            
            # Check if invite is active and not expired
            if invite['status'] != 'active':
                return jsonify({"success": False, "error": f"Invite code is {invite['status']}"}), 400
            
            if datetime.utcnow() > invite['expires_at']:
                return jsonify({"success": False, "error": "Invite code has expired"}), 400
            
            # Find connection request using invite data
            connection = db.connections_collection.find_one({
                "doctor_id": invite['doctor_id'],
                "patient_email": invite['patient_email'],
                "status": "pending"
            })
            
            if not connection:
                return jsonify({"success": False, "error": "No pending connection request found for this invite code"}), 404
            
            connection_id = connection['connection_id']
        
        # Verify doctor owns this connection
        if connection['doctor_id'] != doctor_id:
            return jsonify({"success": False, "error": "Unauthorized"}), 403
        
        # Verify status is pending
        if connection['status'] != 'pending':
            return jsonify({
                "success": False,
                "error": f"Connection request is not pending (current: {connection['status']})"
            }), 400
        
        # Get patient info for notification
        patient = db.patients_collection.find_one({"patient_id": connection['patient_id']})
        
        # Accept or reject
        if action == "accept":
            # Update connection to active
            db.connections_collection.update_one(
                {"connection_id": connection_id},
                {
                    "$set": {
                        "status": "active",
                        "response_message": message,
                        "dates.connected_at": datetime.utcnow(),
                        "dates.updated_at": datetime.utcnow()
                    },
                    "$push": {
                        "audit_log": {
                            "action": "connection_accepted",
                            "actor_id": doctor_id,
                            "actor_type": "doctor",
                            "timestamp": datetime.utcnow(),
                            "details": {"response_message": message}
                        }
                    }
                }
            )
            
            # Update doctor statistics
            db.doctors_collection.update_one(
                {"doctor_id": doctor_id},
                {
                    "$inc": {
                        "statistics.total_patients": 1,
                        "statistics.active_patients": 1
                    }
                }
            )
            
            # If accepted via invite code, mark it as used
            if data.get('invite_code'):
                invite_code = data['invite_code']
                db.invite_codes_collection.update_one(
                    {"invite_code": invite_code},
                    {
                        "$set": {
                            "status": "used",
                            "used_at": datetime.utcnow(),
                            "used_by": doctor_id,
                            "updated_at": datetime.utcnow()
                        },
                        "$inc": {"used_count": 1}
                    }
                )
                print(f"✅ Invite code {invite_code} marked as used")
            
            action_text = "accepted"
            print(f"✅ Doctor {doctor_id} accepted connection {connection_id}")
            
        else:  # reject
            # Update connection to rejected
            db.connections_collection.update_one(
                {"connection_id": connection_id},
                {
                    "$set": {
                        "status": "rejected",
                        "response_message": message,
                        "dates.rejected_at": datetime.utcnow(),
                        "dates.updated_at": datetime.utcnow()
                    },
                    "$push": {
                        "audit_log": {
                            "action": "connection_rejected",
                            "actor_id": doctor_id,
                            "actor_type": "doctor",
                            "timestamp": datetime.utcnow(),
                            "details": {"reason": message}
                        }
                    }
                }
            )
            
            action_text = "rejected"
            print(f"✅ Doctor {doctor_id} rejected connection {connection_id}")
        
        # TODO: Send email notification to patient
        # email_service.send_connection_response_email(patient['email'], doctor_info, action, message)
        
        # Prepare response data
        response_data = {
            "success": True,
            "message": f"Patient connection {action_text}",
            "connection": {
                "connection_id": connection_id,
                "status": "active" if action == "accept" else "rejected",
                "updated_at": datetime.utcnow().isoformat()
            }
        }
        
        # Add method used information
        if data.get('invite_code'):
            response_data["method"] = "invite_code"
            response_data["invite_code"] = data['invite_code']
        else:
            response_data["method"] = "connection_id"
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"❌ Error responding to connection: {e}")
        return jsonify({"success": False, "error": f"Failed to respond to request: {str(e)}"}), 500


@app.route('/api/doctor/remove-connection', methods=['POST'])
@token_required
def doctor_remove_connection():
    """Doctor removes connection with patient"""
    try:
        data = request.get_json()
        doctor_id = request.user_data.get('user_id')
        
        if not doctor_id:
            return jsonify({"success": False, "error": "Doctor authentication required"}), 403
        
        # Validate required fields
        if not data.get('connection_id'):
            return jsonify({"success": False, "error": "connection_id is required"}), 400
        
        connection_id = data['connection_id']
        reason = data.get('reason', '')
        
        # Get connection
        connection = db.connections_collection.find_one({"connection_id": connection_id})
        
        if not connection:
            return jsonify({"success": False, "error": "Connection not found"}), 404
        
        # Verify doctor owns this connection
        if connection['doctor_id'] != doctor_id:
            return jsonify({"success": False, "error": "Not your connection"}), 403
        
        # Remove connection
        db.connections_collection.update_one(
            {"connection_id": connection_id},
            {
                "$set": {
                    "status": "removed",
                    "dates.removed_at": datetime.utcnow(),
                    "dates.updated_at": datetime.utcnow(),
                    "removal_info": {
                        "removed_by": doctor_id,
                        "removed_by_type": "doctor",
                        "reason": reason,
                        "removed_at": datetime.utcnow()
                    }
                },
                "$push": {
                    "audit_log": {
                        "action": "connection_removed",
                        "actor_id": doctor_id,
                        "actor_type": "doctor",
                        "timestamp": datetime.utcnow(),
                        "details": {"reason": reason}
                    }
                }
            }
        )
        
        # Update doctor statistics if connection was active
        if connection['status'] == 'active':
            db.doctors_collection.update_one(
                {"doctor_id": doctor_id},
                {"$inc": {"statistics.active_patients": -1}}
            )
        
        print(f"✅ Doctor {doctor_id} removed connection {connection_id}")
        
        # TODO: Send email notification to patient
        # email_service.send_connection_removed_email(patient_email, doctor_info, reason)
        
        return jsonify({
            "success": True,
            "message": "Connection removed successfully",
            "connection": {
                "connection_id": connection_id,
                "status": "removed"
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error removing connection: {e}")
        return jsonify({"success": False, "error": f"Failed to remove connection: {str(e)}"}), 500


@app.route('/api/doctor/cancel-request', methods=['POST'])
@token_required
def doctor_cancel_request():
    """Doctor cancels pending connection request"""
    return doctor_controller.cancel_connection_request(request)


@app.route('/api/doctor/connected-patients', methods=['GET'])
@token_required
def get_connected_patients():
    """Get all connected patients for doctor"""
    try:
        doctor_id = request.user_data.get('user_id')
        
        if not doctor_id:
            return jsonify({"success": False, "error": "Doctor authentication required"}), 403
        
        # Get active connections
        connections = list(db.connections_collection.find({
            "doctor_id": doctor_id,
            "status": "active"
        }).sort("dates.connected_at", -1).limit(100))
        
        # Enrich with patient details
        patients = []
        for conn in connections:
            patient = db.patients_collection.find_one({"patient_id": conn['patient_id']})
            if not patient:
                continue
            
            patients.append({
                "connection_id": conn['connection_id'],
                "patient_id": patient['patient_id'],
                "name": f"{patient.get('first_name', '')} {patient.get('last_name', '')}".strip() or patient.get('username', 'Unknown'),
                "age": patient.get('age'),
                "email": patient.get('email'),
                "mobile": patient.get('mobile'),
                "profile_photo": patient.get('profile_photo'),
                "pregnancy_info": {
                    "is_pregnant": patient.get('is_pregnant', False),
                    "pregnancy_week": patient.get('pregnancy_week'),
                    "expected_delivery_date": patient.get('expected_delivery_date')
                },
                "connection_info": {
                    "connected_since": conn['dates']['connected_at'].isoformat() if conn['dates'].get('connected_at') else None,
                    "connection_type": conn['connection_type'],
                    "status": conn['status']
                },
                "statistics": conn.get('statistics', {})
            })
        
        # Get summary statistics
        total_count = len(patients)
        active_pregnancies = sum(1 for p in patients if p.get('pregnancy_info', {}).get('is_pregnant'))
        
        print(f"✅ Retrieved {total_count} connected patients for doctor {doctor_id}")
        
        return jsonify({
            "success": True,
            "patients": patients,
            "summary": {
                "total_count": total_count,
                "active_pregnancies": active_pregnancies
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error getting connected patients: {e}")
        return jsonify({"success": False, "error": f"Failed to fetch patients: {str(e)}"}), 500


# Error Handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

# Initialize database connection
def initialize_database():
    """Initialize database connection"""
    try:
        if db.connect():
            print("✅ Database connected successfully")
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

@app.route('/debug/email', methods=['GET'])
def debug_email():
    """Debug email service"""
    try:
        # Test network connectivity
        connectivity_results = email_service.test_network_connectivity()
        
        return jsonify({
            'email_service_configured': email_service.is_configured(),
            'sender_email': email_service.sender_email,
            'sender_password_set': bool(email_service.sender_password),
            'smtp_configs': email_service.smtp_configs,
            'network_connectivity': connectivity_results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/debug/test-email', methods=['POST'])
def test_email():
    """Test email sending"""
    try:
        data = request.get_json()
        test_email = data.get('email', 'test@example.com')
        
        # Send test OTP
        result = email_service.send_otp_email(test_email, '123456')
        
        return jsonify({
            'test_email': test_email,
            'result': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# DOCTOR AVAILABILITY ROUTES
# ============================================================================

@app.route('/doctor/<doctor_id>/availability', methods=['POST'])
def create_doctor_availability(doctor_id):
    """Create availability slots for doctor"""
    try:
        # Verify JWT token
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'success': False, 'error': 'Authorization header required'}), 401
        
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else auth_header
        verification_result = jwt_service.verify_access_token(token)
        if verification_result['success']:
            decoded_token = verification_result['data']
        else:
            decoded_token = None
        
        if not decoded_token or decoded_token.get('user_id') != doctor_id:
            return jsonify({'success': False, 'error': 'Invalid or unauthorized token'}), 401
        
        return availability_controller.create_availability(request, doctor_id)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to create availability: {str(e)}'}), 500

@app.route('/doctor/<doctor_id>/availability', methods=['GET'])
def get_doctor_availability(doctor_id):
    """Get doctor's availability"""
    try:
        # Verify JWT token
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'success': False, 'error': 'Authorization header required'}), 401
        
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else auth_header
        verification_result = jwt_service.verify_access_token(token)
        if verification_result['success']:
            decoded_token = verification_result['data']
        else:
            decoded_token = None
        
        if not decoded_token or decoded_token.get('user_id') != doctor_id:
            return jsonify({'success': False, 'error': 'Invalid or unauthorized token'}), 401
        
        return availability_controller.get_availability(request, doctor_id)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get availability: {str(e)}'}), 500

@app.route('/doctor/<doctor_id>/availability/<date>', methods=['GET'])
def get_doctor_availability_by_date(doctor_id, date):
    """Get doctor's availability for specific date"""
    try:
        # Verify JWT token
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'success': False, 'error': 'Authorization header required'}), 401
        
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else auth_header
        verification_result = jwt_service.verify_access_token(token)
        if verification_result['success']:
            decoded_token = verification_result['data']
        else:
            decoded_token = None
        
        if not decoded_token or decoded_token.get('user_id') != doctor_id:
            return jsonify({'success': False, 'error': 'Invalid or unauthorized token'}), 401
        
        return availability_controller.get_availability_by_date(request, doctor_id, date)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get availability by date: {str(e)}'}), 500

@app.route('/doctor/<doctor_id>/availability/<date>/<appointment_type>', methods=['GET'])
def get_available_slots_by_type(doctor_id, date, appointment_type):
    """Get available slots for specific appointment type"""
    try:
        # Verify JWT token
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'success': False, 'error': 'Authorization header required'}), 401
        
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else auth_header
        verification_result = jwt_service.verify_access_token(token)
        if verification_result['success']:
            decoded_token = verification_result['data']
        else:
            decoded_token = None
        
        if not decoded_token or decoded_token.get('user_id') != doctor_id:
            return jsonify({'success': False, 'error': 'Invalid or unauthorized token'}), 401
        
        return availability_controller.get_available_slots_by_type(request, doctor_id, date, appointment_type)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get available slots: {str(e)}'}), 500

@app.route('/availability/<availability_id>', methods=['PUT'])
def update_doctor_availability(availability_id):
    """Update availability document"""
    try:
        # Verify JWT token
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'success': False, 'error': 'Authorization header required'}), 401
        
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else auth_header
        verification_result = jwt_service.verify_access_token(token)
        if verification_result['success']:
            decoded_token = verification_result['data']
        else:
            decoded_token = None
        
        if not decoded_token:
            return jsonify({'success': False, 'error': 'Invalid token'}), 401
        
        return availability_controller.update_availability(request, availability_id)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to update availability: {str(e)}'}), 500

@app.route('/availability/<availability_id>', methods=['DELETE'])
def delete_doctor_availability(availability_id):
    """Delete availability document"""
    try:
        # Verify JWT token
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'success': False, 'error': 'Authorization header required'}), 401
        
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else auth_header
        verification_result = jwt_service.verify_access_token(token)
        if verification_result['success']:
            decoded_token = verification_result['data']
        else:
            decoded_token = None
        
        if not decoded_token:
            return jsonify({'success': False, 'error': 'Invalid token'}), 401
        
        return availability_controller.delete_availability(request, availability_id)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to delete availability: {str(e)}'}), 500

# ============================================================================
# DOCTOR APPOINTMENT CANCELLATION ROUTES
# ============================================================================

@app.route('/doctor/<doctor_id>/availability/<date>/booked-slots', methods=['GET'])
def get_doctor_booked_slots(doctor_id, date):
    """Get all booked slots for a specific date"""
    try:
        # Verify JWT token
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'success': False, 'error': 'Authorization header required'}), 401
        
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else auth_header
        verification_result = jwt_service.verify_access_token(token)
        if verification_result['success']:
            decoded_token = verification_result['data']
        else:
            decoded_token = None
        
        if not decoded_token or decoded_token.get('user_id') != doctor_id:
            return jsonify({'success': False, 'error': 'Invalid or unauthorized token'}), 401
        
        return availability_controller.get_booked_slots(request, doctor_id, date)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get booked slots: {str(e)}'}), 500

@app.route('/doctor/<doctor_id>/availability/<date>/available-slots', methods=['GET'])
def get_doctor_available_slots_only(doctor_id, date):
    """Get only unbooked slots for a specific date"""
    try:
        # Verify JWT token
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'success': False, 'error': 'Authorization header required'}), 401
        
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else auth_header
        verification_result = jwt_service.verify_access_token(token)
        if verification_result['success']:
            decoded_token = verification_result['data']
        else:
            decoded_token = None
        
        if not decoded_token or decoded_token.get('user_id') != doctor_id:
            return jsonify({'success': False, 'error': 'Invalid or unauthorized token'}), 401
        
        return availability_controller.get_available_slots_only(request, doctor_id, date)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get available slots: {str(e)}'}), 500

@app.route('/doctor/<doctor_id>/availability/<date>/book-slot', methods=['POST'])
def book_doctor_slot(doctor_id, date):
    """Book a specific slot - called by patient module"""
    try:
        return availability_controller.book_slot(request, doctor_id, date)
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to book slot: {str(e)}'}), 500

@app.route('/doctor/<doctor_id>/availability/<date>/<slot_id>/cancel', methods=['POST'])
def cancel_doctor_appointment_slot(doctor_id, date, slot_id):
    """Cancel a specific appointment slot"""
    try:
        # Verify JWT token
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'success': False, 'error': 'Authorization header required'}), 401
        
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else auth_header
        verification_result = jwt_service.verify_access_token(token)
        if verification_result['success']:
            decoded_token = verification_result['data']
        else:
            decoded_token = None
        
        # Accept any valid token (doctor or patient)
        if not decoded_token:
            return jsonify({'success': False, 'error': 'Invalid token'}), 401
        
        return availability_controller.cancel_appointment_slot(request, doctor_id, date, slot_id)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to cancel appointment slot: {str(e)}'}), 500

@app.route('/doctor/<doctor_id>/availability/<date>/summary', methods=['GET'])
def get_doctor_date_summary(doctor_id, date):
    """Get appointment summary for a specific date"""
    try:
        # Verify JWT token
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'success': False, 'error': 'Authorization header required'}), 401
        
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else auth_header
        verification_result = jwt_service.verify_access_token(token)
        if verification_result['success']:
            decoded_token = verification_result['data']
        else:
            decoded_token = None
        
        if not decoded_token or decoded_token.get('user_id') != doctor_id:
            return jsonify({'success': False, 'error': 'Invalid or unauthorized token'}), 401
        
        return availability_controller.get_date_appointment_summary(request, doctor_id, date)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get date summary: {str(e)}'}), 500

@app.route('/doctor/<doctor_id>/availability/<date>/cancel-all', methods=['POST'])
def cancel_all_doctor_appointments(doctor_id, date):
    """Cancel all appointments for a specific date"""
    try:
        # Verify JWT token
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'success': False, 'error': 'Authorization header required'}), 401
        
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else auth_header
        verification_result = jwt_service.verify_access_token(token)
        if verification_result['success']:
            decoded_token = verification_result['data']
        else:
            decoded_token = None
        
        if not decoded_token or decoded_token.get('user_id') != doctor_id:
            return jsonify({'success': False, 'error': 'Invalid or unauthorized token'}), 401
        
        return availability_controller.cancel_all_appointments_for_date(request, doctor_id, date)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to cancel all appointments: {str(e)}'}), 500

# ============================================================================
# PUBLIC AVAILABILITY ROUTES (for patients to view availability)
# ============================================================================

@app.route('/public/doctor/<doctor_id>/availability/<date>', methods=['GET'])
def get_public_doctor_availability(doctor_id, date):
    """Get doctor's availability for patients (public endpoint)"""
    try:
        return availability_controller.get_availability_by_date(request, doctor_id, date)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get public availability: {str(e)}'}), 500

@app.route('/public/doctor/<doctor_id>/availability/<date>/<appointment_type>', methods=['GET'])
def get_public_available_slots(doctor_id, date, appointment_type):
    """Get available slots for patients (public endpoint)"""
    try:
        return availability_controller.get_available_slots_by_type(request, doctor_id, date, appointment_type)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get public available slots: {str(e)}'}), 500

# ============================================================================
# PATIENT AUTHENTICATED AVAILABILITY ROUTES (JWT Required)
# ============================================================================

@app.route('/patient/doctor/<doctor_id>/availability', methods=['GET'])
def get_patient_doctor_availability_overall(doctor_id):
    """Patient-authenticated: overall availability (optional filters)
    Query params:
      - date=YYYY-MM-DD (optional)
      - start_date=YYYY-MM-DD & end_date=YYYY-MM-DD (optional)
      - consultation_type=Online|In-Person (optional)
      - appointment_type=... (optional, filters types.type)
    If no date/range provided, returns all active availability for the doctor.
    """
    try:
        # Verify patient JWT token
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'success': False, 'error': 'Authorization header required'}), 401

        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else auth_header
        verification_result = jwt_service.verify_access_token(token)
        if verification_result['success']:
            decoded_token = verification_result['data']
        else:
            decoded_token = None
        if not decoded_token:
            return jsonify({'success': False, 'error': 'Invalid or expired token'}), 401

        # Parse filters
        date = request.args.get('date')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        consultation_type = request.args.get('consultation_type')
        appointment_type = request.args.get('appointment_type')

        date_range = None
        if not date and start_date and end_date:
            date_range = {'start_date': start_date, 'end_date': end_date}

        # Get availability using model directly (patient context)
        result = availability_model.get_doctor_availability(
            doctor_id=doctor_id,
            date=date,
            date_range=date_range,
            consultation_type=consultation_type
        )

        if not result.get('success'):
            return jsonify({'success': False, 'error': result.get('error', 'Unknown error')}), 500

        availability_list = result.get('availability', [])

        # Optional filter by appointment_type (filter types list inside each doc)
        if appointment_type:
            filtered = []
            for avail in availability_list:
                types_arr = avail.get('types', [])
                kept_types = [t for t in types_arr if str(t.get('type', '')).strip() == appointment_type]
                if kept_types:
                    new_avail = dict(avail)
                    new_avail['types'] = kept_types
                    filtered.append(new_avail)
            availability_list = filtered

        return jsonify({
            'success': True,
            'availability': availability_list,
            'total_count': len(availability_list)
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get availability: {str(e)}'}), 500

@app.route('/patient/doctor/<doctor_id>/availability/<date>', methods=['GET'])
def get_patient_doctor_availability(doctor_id, date):
    """Get doctor availability for authenticated patients (JWT required)"""
    try:
        # Verify patient JWT token
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'success': False, 'error': 'Authorization header required'}), 401
        
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else auth_header
        
        # Verify patient token (reuse existing JWT service)
        verification_result = jwt_service.verify_access_token(token)
        if verification_result['success']:
            decoded_token = verification_result['data']
        else:
            decoded_token = None
        
        if not decoded_token:
            return jsonify({'success': False, 'error': 'Invalid or expired token'}), 401
        
        # Extract patient_id from token (assuming patient tokens use 'user_id' field)
        patient_id = decoded_token.get('user_id')
        if not patient_id:
            return jsonify({'success': False, 'error': 'Invalid token format'}), 401
        
        # Log access for audit
        print(f"[AUDIT] Patient {patient_id} accessed doctor {doctor_id} availability for {date}")
        
        # Return availability using existing controller
        return availability_controller.get_availability_by_date(request, doctor_id, date)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get availability: {str(e)}'}), 500

@app.route('/patient/doctor/<doctor_id>/availability/<date>/<appointment_type>', methods=['GET'])
def get_patient_available_slots(doctor_id, date, appointment_type):
    """Get available slots for authenticated patients (JWT required)"""
    try:
        # Verify patient JWT token
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'success': False, 'error': 'Authorization header required'}), 401
        
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else auth_header
        
        # Verify patient token
        verification_result = jwt_service.verify_access_token(token)
        if verification_result['success']:
            decoded_token = verification_result['data']
        else:
            decoded_token = None
        
        if not decoded_token:
            return jsonify({'success': False, 'error': 'Invalid or expired token'}), 401
        
        # Extract patient_id from token
        patient_id = decoded_token.get('user_id')
        if not patient_id:
            return jsonify({'success': False, 'error': 'Invalid token format'}), 401
        
        # Log access for audit
        print(f"[AUDIT] Patient {patient_id} accessed doctor {doctor_id} slots for {date}/{appointment_type}")
        
        # Return available slots using existing controller
        return availability_controller.get_available_slots_by_type(request, doctor_id, date, appointment_type)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get available slots: {str(e)}'}), 500

# ============================================================================
# SCHEDULER ENDPOINTS (must be defined before if __name__ == '__main__')
# ============================================================================

@app.route('/scheduler/status', methods=['GET'])
def scheduler_status():
    """Get scheduler status"""
    global scheduler_service
    try:
        if scheduler_service is None:
            return jsonify({
                'success': False,
                'status': 'not_initialized',
                'message': 'Scheduler service is not initialized'
            }), 503
        
        is_running = scheduler_service.is_running
        return jsonify({
            'success': True,
            'status': 'running' if is_running else 'stopped',
            'is_running': is_running,
            'message': 'Scheduler is operational' if is_running else 'Scheduler is stopped'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/scheduler/test-reminder', methods=['POST'])
def test_reminder():
    """Test reminder email functionality"""
    global scheduler_service
    try:
        from services.appointment_reminder_service import AppointmentReminderService
        
        # Create a test reminder service using the existing db instance
        reminder_service = AppointmentReminderService(email_service, db)
        
        # Get test data from request
        data = request.get_json() or {}
        
        # Test sending a reminder
        result = reminder_service.send_appointment_reminder_email(
            patient_email=data.get('patient_email', 'ramyayashva@gmail.com'),
            patient_name=data.get('patient_name', 'Test Patient'),
            doctor_name=data.get('doctor_name', 'Dr. Test Doctor'),
            appointment_date=data.get('appointment_date', '2025-10-28'),
            appointment_time=data.get('appointment_time', '10:00:00'),
            appointment_type=data.get('appointment_type', 'Test Appointment')
        )
        
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/scheduler/trigger-check', methods=['POST'])
def trigger_check():
    """Manually trigger appointment check"""
    global scheduler_service
    try:
        if scheduler_service is None:
            return jsonify({
                'success': False,
                'error': 'Scheduler service is not initialized'
            }), 503
        
        # Manually trigger the check
        scheduler_service.check_upcoming_appointments()
        
        return jsonify({
            'success': True,
            'message': 'Appointment check triggered successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/scheduler/config', methods=['GET'])
def scheduler_config():
    """Get scheduler configuration"""
    return jsonify({
        'success': True,
        'config': {
            'reminder_hours_before': int(os.environ.get('REMINDER_HOURS_BEFORE', 24)),
            'check_interval_minutes': int(os.environ.get('SCHEDULER_CHECK_INTERVAL', 60))
        }
    })

@app.route('/scheduler/config', methods=['PUT'])
def update_scheduler_config():
    """Update scheduler configuration"""
    try:
        data = request.get_json()
        
        if 'reminder_hours_before' in data:
            os.environ['REMINDER_HOURS_BEFORE'] = str(data['reminder_hours_before'])
        
        if 'check_interval_minutes' in data:
            os.environ['SCHEDULER_CHECK_INTERVAL'] = str(data['check_interval_minutes'])
        
        return jsonify({
            'success': True,
            'message': 'Configuration updated successfully',
            'config': {
                'reminder_hours_before': int(os.environ.get('REMINDER_HOURS_BEFORE', 24)),
                'check_interval_minutes': int(os.environ.get('SCHEDULER_CHECK_INTERVAL', 60))
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/scheduler/email-example', methods=['GET'])
def email_example():
    """Get example of reminder email"""
    return jsonify({
        'success': True,
        'example': {
            'to': 'patient@example.com',
            'subject': 'Appointment Reminder - Monday, October 28, 2024 at 10:00 AM',
            'body': """Hello Test Patient,

This is a reminder for your upcoming appointment:

Date: Monday, October 28, 2024
Time: 10:00 AM
Type: Test Appointment
Doctor: Dr. Test Doctor

Please arrive 10 minutes early for check-in.

If you need to reschedule, please contact us.

Best regards,
Patient Alert System Team"""
        }
    })

# Main application
# Global variable for scheduler service (initialized in main)
global scheduler_service
scheduler_service = None

if __name__ == '__main__':
    print("🚀 Starting Patient Alert System - MVC Architecture")
    print("=" * 60)
    
    # Initialize database
    if not initialize_database():
        print("❌ Failed to initialize database. Exiting...")
        sys.exit(1)
    
    # Initialize Appointment Reminder Services
    print("🔧 Initializing appointment reminder services...")
    try:
        from services.appointment_reminder_service import AppointmentReminderService
        from services.scheduler_service import SchedulerService
        
        # Initialize reminder service
        reminder_service = AppointmentReminderService(email_service, db)
        
        # Initialize and start scheduler
        scheduler_service = SchedulerService(db, email_service, reminder_service)
        scheduler_service.start()
        
        print("✅ Appointment reminder scheduler initialized")
        print(f"⏰ Reminders configured: {os.environ.get('REMINDER_HOURS_BEFORE', '24')} hours before appointments")
        print(f"🔄 Scheduler checks every {os.environ.get('SCHEDULER_CHECK_INTERVAL', '60')} minutes")
        
    except Exception as e:
        print(f"⚠️ Warning: Could not initialize appointment reminder scheduler: {str(e)}")
        print("⚠️ Appointment reminders will be disabled")
        import traceback
        traceback.print_exc()
        scheduler_service = None
    
    # Start the application
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV', 'development') != 'production'
    
    print(f"📱 API will be available at: http://localhost:{port}")
    print(f"🌐 Debug mode: {debug_mode}")
    print("💬 Real-time Chat: Enabled (Socket.IO)")
    print("📂 File Uploads: Supported (AWS S3)")
    print("📧 Appointment Reminders: Enabled")
    print(f"🕐 Timezone: Indian Standard Time (IST - UTC+5:30)")
    print("=" * 60)
    
    try:
        app.run(host='0.0.0.0', port=port, debug=debug_mode)
    finally:
        # Graceful shutdown
        if scheduler_service:
            print("🛑 Shutting down appointment reminder scheduler...")
            scheduler_service.stop()

# Debug endpoints for troubleshooting authentication issues
@app.route('/debug/env', methods=['GET'])
def debug_environment():
    """Debug environment variables"""
    return jsonify({
        'mongodb_uri_set': bool(os.environ.get('MONGODB_URI')),
        'database_name_set': bool(os.environ.get('DATABASE_NAME')),
        'jwt_secret_set': bool(os.environ.get('JWT_SECRET_KEY')),
        'sender_email_set': bool(os.environ.get('SENDER_EMAIL')),
        'database_name': os.environ.get('DATABASE_NAME', 'NOT_SET'),
        'mongodb_uri_prefix': os.environ.get('MONGODB_URI', 'NOT_SET')[:20] + '...' if os.environ.get('MONGODB_URI') else 'NOT_SET'
    })

@app.route('/debug/db', methods=['GET'])
def debug_database():
    """Debug database connection"""
    try:
        # Test database connection
        if db.is_connected:
            # Try to get a doctor count
            doctor_count = db.doctors_collection.count_documents({})
            return jsonify({
                'status': 'connected',
                'doctor_count': doctor_count,
                'database_name': db.db.name,
                'collections': list(db.db.list_collection_names())
            })
        else:
            return jsonify({
                'status': 'not_connected',
                'error': 'Database not connected'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        })

@app.route('/debug/doctors', methods=['GET'])
def debug_doctors():
    """Debug doctor data and create test doctor if needed"""
    try:
        doctors = list(db.doctors_collection.find({}, {'username': 1, 'email': 1, 'doctor_id': 1, 'role': 1, '_id': 0}))
        
        # Create test doctor if no doctors exist
        if not doctors:
            try:
                from scripts.create_test_doctor import create_test_doctor
                if create_test_doctor():
                    print("✅ Created test doctor account")
                    # Fetch updated list
                    doctors = list(db.doctors_collection.find({}, {'username': 1, 'email': 1, 'doctor_id': 1, 'role': 1, '_id': 0}))
            except Exception as e:
                print(f"Failed to create test doctor: {e}")
        
        return jsonify({
            'doctor_count': len(doctors),
            'doctors': doctors[:5],  # Show first 5 doctors
            'test_credentials': {
                'email': 'doctor@test.com',
                'password': 'password123'
            } if doctors else None
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        })

@app.route('/debug/test-login', methods=['POST'])
def debug_test_login():
    """Debug test login with specific credentials"""
    try:
        data = request.get_json()
        email = data.get('email', '')
        password = data.get('password', '')
        
        # Find doctor
        doctor = db.doctors_collection.find_one({'email': email})
        
        if not doctor:
            return jsonify({
                'found': False,
                'error': 'Doctor not found',
                'searched_email': email
            })
        
        # Check if password_hash exists
        has_password_hash = 'password_hash' in doctor
        
        return jsonify({
            'found': True,
            'doctor_id': doctor.get('doctor_id'),
            'username': doctor.get('username'),
            'email': doctor.get('email'),
            'has_password_hash': has_password_hash,
            'role': doctor.get('role')
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        })
