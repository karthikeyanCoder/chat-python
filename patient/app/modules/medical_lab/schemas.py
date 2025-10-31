"""
Medical Lab Schemas - Request/Response Validation
"""

from marshmallow import Schema, fields


class UploadMedicalLabSchema(Schema):
    """Schema for medical lab document upload"""
    # File upload handled separately
    pass


class ProcessBase64ImageSchema(Schema):
    """Schema for base64 image processing"""
    image = fields.Str(required=True)
    filename = fields.Str()

