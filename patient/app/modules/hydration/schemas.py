"""
Hydration Schemas - Request/Response Validation
"""

from marshmallow import Schema, fields, validate


class SaveHydrationIntakeSchema(Schema):
    """Schema for saving hydration intake"""
    user_id = fields.Str(required=True)
    hydration_type = fields.Str(required=True)
    amount_ml = fields.Float(required=True, validate=validate.Range(min=0))
    notes = fields.Str()
    temperature = fields.Str()
    additives = fields.List(fields.Str())


class SetHydrationGoalSchema(Schema):
    """Schema for setting hydration goal"""
    daily_goal_ml = fields.Float(required=True, validate=validate.Range(min=0))
    reminder_enabled = fields.Bool()
    reminder_times = fields.List(fields.Str())


class CreateHydrationReminderSchema(Schema):
    """Schema for creating hydration reminder"""
    reminder_time = fields.Str(required=True)
    message = fields.Str(required=True)
    days_of_week = fields.List(fields.Int())

