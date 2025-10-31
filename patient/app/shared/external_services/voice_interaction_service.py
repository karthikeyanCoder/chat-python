#!/usr/bin/env python3
"""
Voice Interaction Service for Patient Alert System
Direct integration of Voice Interaction module
"""

import os
import base64
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceInteractionService:
    """Voice Interaction Service for Patient Alert System"""
    
    def __init__(self):
        self.service_name = "Voice Interaction Service"
        self.version = "1.0.0"
        self.status = "initialized"
        
        # Initialize voice interaction components
        self._initialize_services()
        
        logger.info(f"[OK] {self.service_name} initialized successfully")
    
    def _initialize_services(self):
        """Initialize voice interaction services"""
        try:
            # Import voice interaction services
            from voice_intraction.app.services.stt_service import stt_service
            from voice_intraction.app.services.ai_service import ai_service
            from voice_intraction.app.services.tts_service import tts_service
            from voice_intraction.app.services.simple_websocket_service import simple_websocket_service
            
            self.stt_service = stt_service
            self.ai_service = ai_service
            self.tts_service = tts_service
            self.websocket_service = simple_websocket_service
            
            logger.info("[OK] Voice interaction services imported successfully")
            
        except ImportError as e:
            logger.error(f"[ERROR] Failed to import voice interaction services: {e}")
            self._setup_fallback_services()
    
    def _setup_fallback_services(self):
        """Setup fallback services when voice interaction modules are not available"""
        logger.warning("Setting up fallback voice interaction services")
        
        # Mock services for fallback
        self.stt_service = MockSTTService()
        self.ai_service = MockAIService()
        self.tts_service = MockTTSService()
        self.websocket_service = None
    
    async def transcribe_audio(self, audio_data: bytes, **kwargs) -> Dict[str, Any]:
        """Transcribe audio data to text"""
        try:
            result = await self.stt_service.transcribe_audio(audio_data, **kwargs)
            return {
                'success': True,
                'transcription': result,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def transcribe_base64_audio(self, base64_audio: str, **kwargs) -> Dict[str, Any]:
        """Transcribe base64 encoded audio"""
        try:
            # Decode base64 audio
            audio_data = base64.b64decode(base64_audio)
            return await self.transcribe_audio(audio_data, **kwargs)
        except Exception as e:
            logger.error(f"Error decoding base64 audio: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def generate_ai_response(self, text: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Generate AI response for text input"""
        try:
            if conversation_history is None:
                conversation_history = []
            
            result = await self.ai_service.generate_response(text, conversation_history)
            return {
                'success': True,
                'response': result,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def text_to_speech(self, text: str, **kwargs) -> Dict[str, Any]:
        """Convert text to speech"""
        try:
            result = await self.tts_service.text_to_speech(text, **kwargs)
            return {
                'success': True,
                'audio': result,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error converting text to speech: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def process_voice_interaction(self, audio_data: bytes, enable_tts: bool = True) -> Dict[str, Any]:
        """Complete voice interaction pipeline: STT -> AI -> TTS"""
        try:
            # Step 1: Speech to Text
            stt_result = await self.transcribe_audio(audio_data)
            if not stt_result['success']:
                return stt_result
            
            transcription_text = stt_result['transcription'].get('text', '').strip()
            if not transcription_text:
                return {
                    'success': False,
                    'error': 'No speech detected in audio',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Step 2: Generate AI Response
            ai_result = await self.generate_ai_response(transcription_text)
            if not ai_result['success']:
                return ai_result
            
            ai_text = ai_result['response'].get('text', '').strip()
            if not ai_text:
                return {
                    'success': False,
                    'error': 'No AI response generated',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Step 3: Text to Speech (if enabled)
            tts_result = None
            if enable_tts:
                tts_result = await self.text_to_speech(ai_text)
            
            return {
                'success': True,
                'transcription': stt_result['transcription'],
                'ai_response': ai_result['response'],
                'tts_audio': tts_result['audio'] if tts_result and tts_result['success'] else None,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in voice interaction pipeline: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        return {
            'service_name': self.service_name,
            'version': self.version,
            'status': self.status,
            'capabilities': [
                'speech_to_text',
                'text_to_speech',
                'ai_response_generation',
                'voice_interaction_pipeline'
            ],
            'supported_formats': ['wav', 'mp3', 'm4a', 'flac', 'webm'],
            'supported_languages': ['en', 'ta', 'hi', 'es', 'fr', 'de', 'zh', 'ja', 'ko']
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status"""
        return {
            'service': self.service_name,
            'status': 'healthy' if self.status == 'initialized' else 'unhealthy',
            'version': self.version,
            'timestamp': datetime.now().isoformat(),
            'components': {
                'stt_service': 'available' if hasattr(self, 'stt_service') else 'unavailable',
                'ai_service': 'available' if hasattr(self, 'ai_service') else 'unavailable',
                'tts_service': 'available' if hasattr(self, 'tts_service') else 'unavailable',
                'websocket_service': 'available' if hasattr(self, 'websocket_service') and self.websocket_service else 'unavailable'
            }
        }


# Mock Services for Fallback
class MockSTTService:
    """Mock Speech-to-Text service"""
    
    async def transcribe_audio(self, audio_data: bytes, **kwargs) -> Dict[str, Any]:
        """Mock transcription"""
        await asyncio.sleep(0.5)  # Simulate processing time
        return {
            "text": "Mock transcription: Audio received and processed successfully.",
            "language": "en",
            "confidence": 0.85,
            "segments": [{"start": 0.0, "end": 2.0, "text": "Mock transcription"}],
            "provider": "mock",
            "model": "mock"
        }
    
    async def transcribe_base64_audio(self, base64_audio: str, **kwargs) -> Dict[str, Any]:
        """Mock base64 transcription"""
        return await self.transcribe_audio(b"mock_audio", **kwargs)


class MockAIService:
    """Mock AI service"""
    
    async def generate_response(self, text: str, history: List[Dict] = None) -> Dict[str, Any]:
        """Mock AI response"""
        await asyncio.sleep(1.0)  # Simulate processing time
        return {
            "text": f"Mock AI response to: {text}",
            "confidence": 0.9,
            "provider": "mock",
            "model": "mock"
        }


class MockTTSService:
    """Mock Text-to-Speech service"""
    
    async def text_to_speech(self, text: str, **kwargs) -> Dict[str, Any]:
        """Mock TTS"""
        await asyncio.sleep(1.0)  # Simulate processing time
        return {
            "audio_data": base64.b64encode(f"Mock audio for: {text}".encode()).decode(),
            "format": "wav",
            "provider": "mock",
            "model": "mock"
        }


# Global voice interaction service instance
voice_interaction_service = VoiceInteractionService()
