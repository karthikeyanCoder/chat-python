"""
Doctors Schemas - Request/Response Validation
"""

from marshmallow import Schema, fields


class GetDoctorsSchema(Schema):
    """Schema for getting doctors list"""
    specialty = fields.Str()
    location = fields.Str()
    limit = fields.Int()
    offset = fields.Int()

