"""
Invite Schemas - Request/Response Validation
"""
from marshmallow import Schema, fields, validate, ValidationError


class AcceptInviteSchema(Schema):
    """Schema for accepting doctor invite"""
    invite_code = fields.Str(required=True, validate=validate.Regexp(r'^[A-Z0-9]{3}-[A-Z0-9]{3}-[A-Z0-9]{3}$'))


class RequestConnectionSchema(Schema):
    """Schema for requesting connection with doctor"""
    doctor_id = fields.Str(required=False)
    doctor_email = fields.Email(required=False)
    message = fields.Str(required=True, validate=validate.Length(min=10, max=500))
    connection_type = fields.Str(validate=validate.OneOf(['primary', 'secondary', 'consultation']))
    send_invite_code = fields.Bool(missing=True)  # Default to True for backward compatibility
    expires_in_days = fields.Int(validate=validate.Range(min=1, max=30), missing=7)
    
    def validate_data(self, data, **kwargs):
        """Custom validation to ensure either doctor_id or doctor_email is provided"""
        if not data.get('doctor_id') and not data.get('doctor_email'):
            raise ValidationError("Either 'doctor_id' or 'doctor_email' must be provided")
        if data.get('doctor_id') and data.get('doctor_email'):
            raise ValidationError("Provide either 'doctor_id' or 'doctor_email', not both")
        return data


class RemoveConnectionSchema(Schema):
    """Schema for removing connection"""
    connection_id = fields.Str(required=True)
    reason = fields.Str(validate=validate.Length(max=500))


class SearchDoctorsSchema(Schema):
    """Schema for searching doctors"""
    query = fields.Str()
    specialty = fields.Str()
    city = fields.Str()
    limit = fields.Int(validate=validate.Range(min=1, max=100))


class CancelRequestSchema(Schema):
    """Schema for cancelling connection request"""
    connection_id = fields.Str(required=True)
    reason = fields.Str(validate=validate.Length(max=500))


class GetInviteDetailsSchema(Schema):
    """Schema for getting invite details"""
    invite_id = fields.Str(required=True)


