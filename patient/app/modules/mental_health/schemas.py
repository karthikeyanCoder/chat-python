"""
Mental Health Schemas - Request/Response Validation
"""

from marshmallow import Schema, fields, validate


class MoodCheckinSchema(Schema):
    """Schema for mood check-in"""
    patient_id = fields.Str(required=True)
    mood = fields.Str(required=True)
    note = fields.Str()
    date = fields.Str()


class MentalHealthAssessmentSchema(Schema):
    """Schema for mental health assessment"""
    patient_id = fields.Str(required=True)
    score = fields.Float(required=True, validate=validate.Range(min=1, max=10))
    date = fields.Str()
    questions = fields.List(fields.Str())
    answers = fields.List(fields.Str())
    notes = fields.Str()


class GenerateStorySchema(Schema):
    """Schema for generating mental health story"""
    story_type = fields.Str()
    scenario = fields.Str()


class AssessMentalHealthSchema(Schema):
    """Schema for mental health assessment"""
    answers = fields.List(fields.Str(), required=True)
    story_id = fields.Str()


class MentalHealthChatSchema(Schema):
    """Schema for mental health chat"""
    message = fields.Str(required=True)
    context = fields.Str()
    mood = fields.Str()
    session_id = fields.Str()
    user_profile = fields.Dict()


class StartChatSessionSchema(Schema):
    """Schema for starting chat session"""
    initial_mood = fields.Str()
    user_profile = fields.Dict()

