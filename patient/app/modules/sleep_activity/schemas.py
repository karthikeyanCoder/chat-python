"""
Sleep & Activity Schemas - Request/Response Validation
"""

from marshmallow import Schema, fields, validate


class SaveSleepLogSchema(Schema):
    """Schema for saving sleep log"""
    userId = fields.Str(required=True)
    userRole = fields.Str(required=True)
    username = fields.Str()
    email = fields.Str()
    startTime = fields.Str(required=True)
    endTime = fields.Str(required=True)
    totalSleep = fields.Str(required=True)
    smartAlarmEnabled = fields.Bool()
    optimalWakeUpTime = fields.Str()
    sleepRating = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    notes = fields.Str()
    timestamp = fields.Str()


class TrackActivitySchema(Schema):
    """Schema for tracking activity"""
    email = fields.Str(required=True)
    activity_type = fields.Str(required=True)
    activity_data = fields.Dict()
    session_id = fields.Str()

