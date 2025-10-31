"""
Vital Signs Schemas - Request/Response Validation
"""

from marshmallow import Schema, fields, validate


class SaveVitalSignsSchema(Schema):
    """Schema for saving vital signs"""
    patient_id = fields.Str(required=True)
    blood_pressure_systolic = fields.Int(validate=validate.Range(min=0, max=300))
    blood_pressure_diastolic = fields.Int(validate=validate.Range(min=0, max=200))
    heart_rate = fields.Int(validate=validate.Range(min=0, max=300))
    temperature = fields.Float(validate=validate.Range(min=90, max=110))
    respiratory_rate = fields.Int(validate=validate.Range(min=0, max=60))
    oxygen_saturation = fields.Float(validate=validate.Range(min=0, max=100))
    weight = fields.Float(validate=validate.Range(min=0))
    notes = fields.Str()
    timestamp = fields.Str()


class AnalyzeVitalSignsSchema(Schema):
    """Schema for analyzing vital signs"""
    patient_id = fields.Str(required=True)
    vital_signs = fields.Dict(required=True)
    pregnancy_week = fields.Int(validate=validate.Range(min=1, max=42))

