"""
Pregnancy Schemas - Request/Response Validation
"""

from marshmallow import Schema, fields, validate


class CalculateDueDateSchema(Schema):
    """Schema for calculating due date"""
    last_period_date = fields.Str(required=True)
    patient_id = fields.Str(required=True)


class UpdateWeekSchema(Schema):
    """Schema for updating pregnancy week"""
    patient_id = fields.Str(required=True)
    pregnancy_week = fields.Int(required=True, validate=validate.Range(min=1, max=42))
    last_period_date = fields.Str()
    expected_delivery_date = fields.Str()


class KickCountSchema(Schema):
    """Schema for logging kick count"""
    patient_id = fields.Str(required=True)
    kick_count = fields.Int(required=True, validate=validate.Range(min=0))
    duration_minutes = fields.Int()
    notes = fields.Str()
    timestamp = fields.Str()


class MilestoneSchema(Schema):
    """Schema for pregnancy milestone"""
    patient_id = fields.Str(required=True)
    milestone_type = fields.Str(required=True)
    milestone_date = fields.Str()
    description = fields.Str()
    notes = fields.Str()

