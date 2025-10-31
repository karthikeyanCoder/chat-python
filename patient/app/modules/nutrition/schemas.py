"""
Nutrition Schemas - Request/Response Validation
"""

from marshmallow import Schema, fields


class TranscribeAudioSchema(Schema):
    """Schema for audio transcription"""
    audio = fields.Str(required=True)
    use_n8n = fields.Bool()
    method = fields.Str()
    context = fields.Str()


class AnalyzeFoodGPT4Schema(Schema):
    """Schema for GPT-4 food analysis"""
    food_input = fields.Str(required=True)
    pregnancy_week = fields.Int()
    userId = fields.Str()


class SaveFoodEntrySchema(Schema):
    """Schema for saving food entry"""
    userId = fields.Str(required=True)
    food_input = fields.Str()
    food_details = fields.Str()
    pregnancy_week = fields.Int()
    meal_type = fields.Str()
    notes = fields.Str()
    transcribed_text = fields.Str()
    nutritional_breakdown = fields.Dict()
    gpt4_analysis = fields.Dict()
    timestamp = fields.Str()

