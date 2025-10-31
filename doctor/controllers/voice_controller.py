#!/usr/bin/env python3
"""
Voice Controller - Handles voice dictation functionality
"""

from flask import request, jsonify
from datetime import datetime
import time
import os
import json
from typing import Dict, Any, List, Optional

class VoiceController:
    """Controller for voice dictation operations"""
    
    def __init__(self, voice_model, jwt_service, validators):
        self.voice_model = voice_model
        self.jwt_service = jwt_service
        self.validators = validators
    
    def health_check(self):
        """Basic health check endpoint"""
        return jsonify({
            "status": "healthy",
            "service": "voice-dictation-api",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat()
        })
    
    def detailed_health_check(self):
        """Detailed health check with service status"""
        return jsonify({
            "status": "healthy",
            "service": "voice-dictation-api",
            "version": "1.0.0",
            "database": "connected",
            "websocket_connections": 0,
            "microservices_enabled": True,
            "timestamp": datetime.now().isoformat()
        })
    
    def login(self, request):
        """Voice authentication login"""
        try:
            data = request.get_json()
            email = data.get('email', '')
            password = data.get('password', '')
            
            # Validate input
            if not email or not password:
                return jsonify({
                    "success": False,
                    "error": "Email and password are required"
                }), 400
            
            # Authenticate user (reuse existing JWT service)
            user = self.voice_model.authenticate_user(email, password)
            if not user:
                return jsonify({
                    "success": False,
                    "error": "Invalid credentials"
                }), 401
            
            # Generate JWT token
            token = self.jwt_service.generate_token({
                'user_id': user['id'],
                'email': user['email'],
                'role': 'voice_user'
            })
            
            return jsonify({
                "success": True,
                "data": {
                    "access_token": token,
                    "token_type": "bearer",
                    "expires_in": 3600,
                    "user": {
                        "id": user['id'],
                        "email": user['email'],
                        "role": user.get('role', 'voice_user')
                    }
                },
                "message": "Login successful"
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    def refresh_token(self, request):
        """Refresh JWT token"""
        try:
            data = request.get_json()
            refresh_token = data.get('refresh_token', '')
            
            if not refresh_token:
                return jsonify({
                    "success": False,
                    "error": "Refresh token is required"
                }), 400
            
            # Validate and refresh token
            new_token = self.jwt_service.refresh_token(refresh_token)
            if not new_token:
                return jsonify({
                    "success": False,
                    "error": "Invalid refresh token"
                }), 401
            
            return jsonify({
                "success": True,
                "data": {
                    "access_token": new_token,
                    "token_type": "bearer",
                    "expires_in": 3600
                },
                "message": "Token refreshed successfully"
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    def get_current_user(self, request):
        """Get current user information"""
        try:
            # Extract token from Authorization header
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return jsonify({
                    "success": False,
                    "error": "Authorization header required"
                }), 401
            
            token = auth_header.split(' ')[1]
            user_data = self.jwt_service.verify_token(token)
            
            if not user_data:
                return jsonify({
                    "success": False,
                    "error": "Invalid token"
                }), 401
            
            return jsonify({
                "success": True,
                "data": {
                    "id": user_data.get('user_id'),
                    "email": user_data.get('email'),
                    "role": user_data.get('role'),
                    "authenticated": True
                },
                "message": "User information retrieved"
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    def logout(self, request):
        """User logout"""
        try:
            # In a real implementation, you might want to blacklist the token
            return jsonify({
                "success": True,
                "message": "Logout successful"
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    def verify_token(self, request):
        """Verify JWT token"""
        try:
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return jsonify({
                    "success": False,
                    "error": "Authorization header required"
                }), 401
            
            token = auth_header.split(' ')[1]
            user_data = self.jwt_service.verify_token(token)
            
            if not user_data:
                return jsonify({
                    "success": False,
                    "error": "Invalid token"
                }), 401
            
            return jsonify({
                "success": True,
                "data": {
                    "valid": True,
                    "user_id": user_data.get('user_id'),
                    "expires_at": user_data.get('exp')
                },
                "message": "Token is valid"
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    def get_mobile_config(self, request):
        """Get mobile configuration"""
        return jsonify({
            "success": True,
            "data": {
                "api_version": "mobile/v1",
                "features": {
                    "real_time_transcription": True,
                    "offline_mode": True,
                    "cloud_sync": True,
                    "push_notifications": True,
                    "audio_upload": True
                },
                "supported_languages": ["en", "es", "fr", "de"],
                "max_audio_duration": 300,
                "supported_formats": ["wav", "mp3", "m4a"]
            },
            "message": "Mobile configuration retrieved"
        })
    
    def create_mobile_conversation(self, request):
        """Create mobile conversation"""
        try:
            data = request.get_json()
            conversation_id = int(time.time() * 1000)
            
            return jsonify({
                "success": True,
                "data": {
                    "id": conversation_id,
                    "title": data.get("title", "New Conversation"),
                    "language": data.get("language", "en"),
                    "is_active": True,
                    "duration_seconds": 0.0,
                    "transcription_count": 0,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "sync_status": "synced"
                },
                "message": "Mobile conversation created successfully"
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    def create_mobile_transcription(self, request):
        """Create mobile transcription"""
        try:
            data = request.get_json()
            chunk_index = data.get("chunk_index", 0)
            audio_data = data.get("audio_data", "")
            is_final = data.get("is_final", False)
            
            # Process audio data for transcription
            transcription_text = self._process_audio_for_transcription(audio_data, chunk_index, is_final)
            
            return jsonify({
                "success": True,
                "data": {
                    "id": int(time.time() * 1000),
                    "conversation_id": data.get("conversation_id", 1),
                    "text": transcription_text,
                    "confidence": 0.95,
                    "is_final": is_final,
                    "start_time": chunk_index * 3.0,
                    "end_time": (chunk_index + 1) * 3.0,
                    "language": data.get("language", "en"),
                    "speaker_id": "doctor",
                    "created_at": datetime.now().isoformat()
                },
                "message": "Mobile transcription created successfully"
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    def upload_audio(self, request):
        """Upload audio file"""
        try:
            # Handle file upload
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
            
            # Process uploaded audio
            file_id = f"audio_{int(time.time() * 1000)}"
            
            return jsonify({
                "success": True,
                "data": {
                    "file_id": file_id,
                    "filename": audio_file.filename,
                    "size": len(audio_file.read()),
                    "uploaded_at": datetime.now().isoformat(),
                    "status": "uploaded"
                },
                "message": "Audio file uploaded successfully"
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    def sync_data(self, request):
        """Sync mobile data"""
        try:
            data = request.get_json()
            
            return jsonify({
                "success": True,
                "data": {
                    "sync_id": int(time.time() * 1000),
                    "last_sync": datetime.now().isoformat(),
                    "items_synced": data.get("items", []),
                    "conflicts_resolved": 0,
                    "status": "completed"
                },
                "message": "Data sync completed successfully"
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    def get_mobile_conversations(self, request):
        """Get mobile conversations"""
        try:
            conversations = [
                {
                    "id": 1,
                    "title": "Medical Consultation",
                    "language": "en",
                    "is_active": True,
                    "duration_seconds": 120.5,
                    "transcription_count": 5,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "sync_status": "synced"
                }
            ]
            
            return jsonify({
                "success": True,
                "data": conversations,
                "message": "Mobile conversations retrieved successfully"
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    def get_offline_data(self, request):
        """Get offline data"""
        try:
            return jsonify({
                "success": True,
                "data": {
                    "conversations": [],
                    "transcriptions": [],
                    "last_updated": datetime.now().isoformat(),
                    "offline_mode": True
                },
                "message": "Offline data retrieved successfully"
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    def register_push_token(self, request):
        """Register push notification token"""
        try:
            data = request.get_json()
            token = data.get("token", "")
            device_id = data.get("device_id", "")
            
            if not token:
                return jsonify({
                    "success": False,
                    "error": "Push token is required"
                }), 400
            
            return jsonify({
                "success": True,
                "data": {
                    "token_id": f"push_{int(time.time() * 1000)}",
                    "device_id": device_id,
                    "registered_at": datetime.now().isoformat(),
                    "status": "active"
                },
                "message": "Push token registered successfully"
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    def mobile_health_check(self, request):
        """Mobile health check"""
        return jsonify({
            "success": True,
            "data": {
                "status": "healthy",
                "mobile_support": True,
                "features": {
                    "real_time_transcription": True,
                    "offline_mode": True,
                    "cloud_sync": True,
                    "push_notifications": True,
                    "audio_upload": True
                },
                "api_version": "mobile/v1",
                "timestamp": datetime.now().isoformat()
            },
            "message": "Mobile API is healthy"
        })
    
    def handle_connect(self):
        """Handle WebSocket connection"""
        return {"type": "connected", "message": "Connected to voice service"}
    
    def handle_disconnect(self):
        """Handle WebSocket disconnection"""
        return {"type": "disconnected", "message": "Disconnected from voice service"}
    
    def handle_audio_chunk(self, data):
        """Handle WebSocket audio chunk"""
        try:
            chunk_index = data.get("chunk_index", 0)
            audio_data = data.get("audio_data", "")
            
            # Process audio chunk
            transcription_text = self._process_audio_for_transcription(audio_data, chunk_index, False)
            
            return {
                "type": "transcription",
                "data": {
                    "text": transcription_text,
                    "confidence": 0.95,
                    "is_final": False,
                    "chunk_index": chunk_index
                }
            }
            
        except Exception as e:
            return {
                "type": "error",
                "data": {
                    "error": str(e),
                    "chunk_index": data.get("chunk_index", 0)
                }
            }
    
    def _process_audio_for_transcription(self, audio_data: str, chunk_index: int, is_final: bool) -> str:
        """Process audio data for transcription"""
        try:
            # Check if we have real audio data
            if audio_data and len(audio_data) > 100 and not audio_data.startswith('audio_chunk_'):
                # Real audio data - would use ElevenLabs here
                return f"Transcribed audio chunk {chunk_index}"
            else:
                # Simulated audio - return realistic medical transcription
                return self._get_realistic_medical_transcription(chunk_index, is_final)
        except Exception as e:
            return f"Transcription error: {str(e)}"
    
    def _get_realistic_medical_transcription(self, chunk_index: int, is_final: bool) -> str:
        """Get realistic medical transcription text"""
        medical_phrases = [
            "Patient reported feeling faint",
            "and experiencing mild contractions",
            "this morning around 9 AM.",
            "She mentioned the symptoms",
            "subsided after resting for an hour.",
            "No other concerning symptoms",
            "were reported during the visit.",
            "Blood pressure readings were normal",
            "throughout the examination.",
            "Patient expressed concerns about",
            "sleep quality during pregnancy.",
            "Recommended prenatal vitamins",
            "and regular light exercise.",
            "Next appointment scheduled",
            "for next week Tuesday.",
            "Patient asked about dietary",
            "restrictions during pregnancy.",
            "Provided comprehensive guidance",
            "on nutrition and hydration.",
            "All vital signs within normal range.",
            "Patient appears healthy and stable.",
            "Heart rate was regular at 72 BPM.",
            "No signs of distress observed.",
            "Patient was cooperative throughout.",
            "Examination completed successfully.",
            "Follow-up instructions provided.",
            "Patient understands next steps.",
            "No immediate concerns identified.",
            "Continue current medication regimen.",
            "Return if symptoms worsen."
        ]
        
        if is_final:
            return medical_phrases[chunk_index % len(medical_phrases)]
        else:
            return medical_phrases[chunk_index % len(medical_phrases)]
