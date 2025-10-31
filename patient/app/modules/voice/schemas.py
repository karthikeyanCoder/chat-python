"""
Voice Schemas - Request/Response Validation
"""

from marshmallow import Schema, fields


class TranscribeAudioSchema(Schema):
    """Schema for audio transcription"""
    # File upload handled separately
    pass


class TranscribeBase64Schema(Schema):
    """Schema for base64 audio transcription"""
    audio = fields.Str(required=True)


class AIResponseSchema(Schema):
    """Schema for AI response generation"""
    text = fields.Str(required=True)
    conversation_history = fields.List(fields.Dict())


class TextToSpeechSchema(Schema):
    """Schema for text-to-speech"""
    text = fields.Str(required=True)


class ProcessVoiceSchema(Schema):
    """Schema for complete voice processing"""
    enable_tts = fields.Bool()

