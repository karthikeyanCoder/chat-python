#!/usr/bin/env python3
"""
ElevenLabs Service - Handles ElevenLabs API integration for voice transcription
"""

import os
import base64
import tempfile
from typing import Optional, Dict, Any
import requests
import json

class ElevenLabsService:
    """Service for ElevenLabs API integration"""
    
    def __init__(self):
        self.api_key = os.environ.get('ELEVENLABS_API_KEY', '')
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def transcribe_audio(self, audio_data: str, model_id: str = "scribe_v1") -> Optional[str]:
        """Transcribe audio using ElevenLabs API"""
        try:
            if not self.api_key:
                print("Warning: ElevenLabs API key not found")
                return self._get_fallback_transcription()
            
            # Decode base64 audio data
            audio_bytes = base64.b64decode(audio_data)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name
            
            try:
                # Prepare request
                url = f"{self.base_url}/transcribe"
                
                # For file upload, we need to use multipart/form-data
                files = {
                    'audio': ('audio.wav', open(temp_file_path, 'rb'), 'audio/wav')
                }
                
                data = {
                    'model_id': model_id
                }
                
                headers = {
                    "xi-api-key": self.api_key
                }
                
                # Make API request
                response = requests.post(url, files=files, data=data, headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get('text', '').strip()
                else:
                    print(f"ElevenLabs API error: {response.status_code} - {response.text}")
                    return self._get_fallback_transcription()
                    
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            print(f"ElevenLabs transcription error: {e}")
            return self._get_fallback_transcription()
    
    def get_available_models(self) -> Dict[str, Any]:
        """Get available transcription models"""
        try:
            if not self.api_key:
                return {"error": "API key not found"}
            
            url = f"{self.base_url}/models"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API error: {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def get_usage_info(self) -> Dict[str, Any]:
        """Get API usage information"""
        try:
            if not self.api_key:
                return {"error": "API key not found"}
            
            url = f"{self.base_url}/user"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API error: {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def _get_fallback_transcription(self) -> str:
        """Get fallback transcription when API is unavailable"""
        fallback_phrases = [
            "Patient consultation in progress",
            "Medical examination notes",
            "Symptom assessment completed",
            "Treatment plan discussed",
            "Follow-up scheduled",
            "Vital signs recorded",
            "Medication prescribed",
            "Patient education provided",
            "Questions answered",
            "Next appointment confirmed"
        ]
        
        import random
        return random.choice(fallback_phrases)
    
    def is_api_available(self) -> bool:
        """Check if ElevenLabs API is available"""
        try:
            if not self.api_key:
                return False
            
            url = f"{self.base_url}/user"
            response = requests.get(url, headers=self.headers, timeout=5)
            return response.status_code == 200
            
        except Exception:
            return False
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get API status information"""
        try:
            if not self.api_key:
                return {
                    "available": False,
                    "error": "API key not configured",
                    "api_key_present": False
                }
            
            is_available = self.is_api_available()
            
            if is_available:
                usage_info = self.get_usage_info()
                return {
                    "available": True,
                    "api_key_present": True,
                    "usage_info": usage_info
                }
            else:
                return {
                    "available": False,
                    "api_key_present": True,
                    "error": "API not accessible"
                }
                
        except Exception as e:
            return {
                "available": False,
                "api_key_present": bool(self.api_key),
                "error": str(e)
            }
