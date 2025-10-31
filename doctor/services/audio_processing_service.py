#!/usr/bin/env python3
"""
Audio Processing Service - Handles audio file processing and validation
"""

import os
import base64
import tempfile
import wave
import struct
from typing import Optional, Dict, Any, Tuple, List
import mimetypes

class AudioProcessingService:
    """Service for audio file processing and validation"""
    
    def __init__(self):
        self.supported_formats = ['.wav', '.mp3', '.m4a', '.ogg', '.flac']
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.max_duration = 300  # 5 minutes
    
    def validate_audio_file(self, file_data: bytes, filename: str = None) -> Dict[str, Any]:
        """Validate audio file format and size"""
        try:
            # Check file size
            if len(file_data) > self.max_file_size:
                return {
                    "valid": False,
                    "error": f"File too large. Maximum size: {self.max_file_size / (1024*1024):.1f}MB"
                }
            
            # Check file extension
            if filename:
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext not in self.supported_formats:
                    return {
                        "valid": False,
                        "error": f"Unsupported format. Supported: {', '.join(self.supported_formats)}"
                    }
            
            # Try to detect format from content
            detected_format = self._detect_audio_format(file_data)
            if not detected_format:
                return {
                    "valid": False,
                    "error": "Unable to detect valid audio format"
                }
            
            # Get audio properties
            audio_info = self._get_audio_info(file_data, detected_format)
            
            # Check duration
            if audio_info.get("duration", 0) > self.max_duration:
                return {
                    "valid": False,
                    "error": f"Audio too long. Maximum duration: {self.max_duration} seconds"
                }
            
            return {
                "valid": True,
                "format": detected_format,
                "size": len(file_data),
                "duration": audio_info.get("duration", 0),
                "sample_rate": audio_info.get("sample_rate", 0),
                "channels": audio_info.get("channels", 0)
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}"
            }
    
    def process_audio_chunk(self, audio_data: str, chunk_index: int, is_final: bool = False) -> Dict[str, Any]:
        """Process audio chunk for transcription"""
        try:
            # Decode base64 audio data
            audio_bytes = base64.b64decode(audio_data)
            
            # Validate audio
            validation_result = self.validate_audio_file(audio_bytes)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"]
                }
            
            # Save to temporary file for processing
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name
            
            try:
                # Process audio
                processed_data = self._process_audio_file(temp_file_path)
                
                return {
                    "success": True,
                    "chunk_index": chunk_index,
                    "is_final": is_final,
                    "duration": processed_data.get("duration", 0),
                    "sample_rate": processed_data.get("sample_rate", 0),
                    "channels": processed_data.get("channels", 0),
                    "file_size": len(audio_bytes),
                    "processed_at": self._get_current_timestamp()
                }
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"Processing error: {str(e)}"
            }
    
    def convert_audio_format(self, input_data: bytes, target_format: str = "wav") -> Optional[bytes]:
        """Convert audio to target format"""
        try:
            # Save input to temporary file
            with tempfile.NamedTemporaryFile(suffix='.tmp', delete=False) as temp_file:
                temp_file.write(input_data)
                temp_input_path = temp_file.name
            
            # Create output file path
            temp_output_path = temp_input_path + f".{target_format}"
            
            try:
                # For now, just return the original data
                # In a real implementation, you would use ffmpeg or similar
                return input_data
                
            finally:
                # Clean up temporary files
                for path in [temp_input_path, temp_output_path]:
                    if os.path.exists(path):
                        os.unlink(path)
                        
        except Exception as e:
            print(f"Error converting audio format: {e}")
            return None
    
    def extract_audio_features(self, audio_data: bytes) -> Dict[str, Any]:
        """Extract features from audio data"""
        try:
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Extract basic features
                features = self._extract_basic_features(temp_file_path)
                return features
                
            finally:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            return {"error": str(e)}
    
    def _detect_audio_format(self, data: bytes) -> Optional[str]:
        """Detect audio format from file data"""
        try:
            # Check for common audio file signatures
            if data.startswith(b'RIFF') and b'WAVE' in data[:12]:
                return 'wav'
            elif data.startswith(b'ID3') or data.startswith(b'\xff\xfb'):
                return 'mp3'
            elif data.startswith(b'ftypM4A'):
                return 'm4a'
            elif data.startswith(b'OggS'):
                return 'ogg'
            elif data.startswith(b'fLaC'):
                return 'flac'
            
            return None
            
        except Exception:
            return None
    
    def _get_audio_info(self, data: bytes, format_type: str) -> Dict[str, Any]:
        """Get audio file information"""
        try:
            if format_type == 'wav':
                return self._get_wav_info(data)
            else:
                # For other formats, return basic info
                return {
                    "duration": 0,
                    "sample_rate": 44100,
                    "channels": 2
                }
                
        except Exception as e:
            return {
                "duration": 0,
                "sample_rate": 0,
                "channels": 0,
                "error": str(e)
            }
    
    def _get_wav_info(self, data: bytes) -> Dict[str, Any]:
        """Get WAV file information"""
        try:
            # Parse WAV header
            if len(data) < 44:
                return {"duration": 0, "sample_rate": 0, "channels": 0}
            
            # Extract header information
            sample_rate = struct.unpack('<I', data[24:28])[0]
            channels = struct.unpack('<H', data[22:24])[0]
            bits_per_sample = struct.unpack('<H', data[34:36])[0]
            
            # Calculate duration
            data_size = struct.unpack('<I', data[40:44])[0]
            bytes_per_sample = bits_per_sample // 8
            duration = data_size / (sample_rate * channels * bytes_per_sample)
            
            return {
                "duration": duration,
                "sample_rate": sample_rate,
                "channels": channels,
                "bits_per_sample": bits_per_sample
            }
            
        except Exception as e:
            return {
                "duration": 0,
                "sample_rate": 0,
                "channels": 0,
                "error": str(e)
            }
    
    def _process_audio_file(self, file_path: str) -> Dict[str, Any]:
        """Process audio file and return metadata"""
        try:
            # Get file info
            file_size = os.path.getsize(file_path)
            
            # Try to get audio info
            with open(file_path, 'rb') as f:
                data = f.read()
            
            audio_info = self._get_audio_info(data, 'wav')
            
            return {
                "file_size": file_size,
                "duration": audio_info.get("duration", 0),
                "sample_rate": audio_info.get("sample_rate", 0),
                "channels": audio_info.get("channels", 0)
            }
            
        except Exception as e:
            return {
                "file_size": 0,
                "duration": 0,
                "sample_rate": 0,
                "channels": 0,
                "error": str(e)
            }
    
    def _extract_basic_features(self, file_path: str) -> Dict[str, Any]:
        """Extract basic audio features"""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            audio_info = self._get_audio_info(data, 'wav')
            
            return {
                "duration": audio_info.get("duration", 0),
                "sample_rate": audio_info.get("sample_rate", 0),
                "channels": audio_info.get("channels", 0),
                "file_size": len(data),
                "format": "wav"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported audio formats"""
        return self.supported_formats.copy()
    
    def get_max_file_size(self) -> int:
        """Get maximum allowed file size in bytes"""
        return self.max_file_size
    
    def get_max_duration(self) -> int:
        """Get maximum allowed duration in seconds"""
        return self.max_duration
