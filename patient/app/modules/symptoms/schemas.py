"""
Symptoms Schemas - Request/Response Validation
"""

from marshmallow import Schema, fields, validate


class SymptomAssistSchema(Schema):
    """Schema for symptom assist request"""
    patient_id = fields.Str(required=True)
    symptoms = fields.Str(required=True)
    pregnancy_week = fields.Int(validate=validate.Range(min=1, max=42))
    additional_context = fields.Str()


class SaveSymptomLogSchema(Schema):
    """Schema for saving symptom log"""
    patient_id = fields.Str(required=True)
    symptom_description = fields.Str(required=True)
    severity = fields.Str(validate=validate.OneOf(['mild', 'moderate', 'severe']))
    timestamp = fields.Str()
    notes = fields.Str()


class SaveAnalysisReportSchema(Schema):
    """Schema for saving analysis report"""
    patient_id = fields.Str(required=True)
    analysis = fields.Dict(required=True)
    symptom_description = fields.Str()
    timestamp = fields.Str()


class AddKnowledgeSchema(Schema):
    """Schema for adding knowledge"""
    text = fields.Str(required=True)
    source = fields.Str(required=True)
    trimester = fields.Str(required=True)
    tags = fields.List(fields.Str())
    triage = fields.Str()

