"""
Authentication Schemas - Request/Response Validation
"""
from marshmallow import Schema, fields, validate, ValidationError


class SignupSchema(Schema):
    """Schema for user signup"""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    mobile = fields.Str(required=True, validate=validate.Length(min=10, max=15))
    password = fields.Str(required=True, validate=validate.Length(min=6))


class LoginSchema(Schema):
    """Schema for user login"""
    login_identifier = fields.Str(required=True)  # Can be email or patient_id
    password = fields.Str(required=True)


class OTPVerificationSchema(Schema):
    """Schema for OTP verification"""
    signup_token = fields.Str(required=True)
    otp = fields.Str(required=True, validate=validate.Length(equal=6))


class SendOTPSchema(Schema):
    """Schema for sending OTP"""
    email = fields.Email(required=True)


class ResendOTPSchema(Schema):
    """Schema for resending OTP"""
    signup_token = fields.Str(required=True)


class ForgotPasswordSchema(Schema):
    """Schema for forgot password"""
    email = fields.Email(required=True)


class ResetPasswordSchema(Schema):
    """Schema for password reset"""
    email = fields.Email(required=True)
    otp = fields.Str(required=True, validate=validate.Length(equal=6))
    new_password = fields.Str(required=True, validate=validate.Length(min=6))


class CompleteProfileSchema(Schema):
    """Schema for completing profile"""
    patient_id = fields.Str(required=True)
    first_name = fields.Str(required=True, validate=validate.Length(min=1))
    last_name = fields.Str(required=True, validate=validate.Length(min=1))
    date_of_birth = fields.Date(required=True)
    blood_type = fields.Str(required=True)
    gender = fields.Str(required=True, validate=validate.OneOf(['Male', 'Female', 'Other']))
    emergency_contact_name = fields.Str(required=True, validate=validate.Length(min=1))
    emergency_contact_phone = fields.Str(required=True, validate=validate.Length(min=10, max=15))
    emergency_contact_relationship = fields.Str(required=True, validate=validate.Length(min=1))
    address = fields.Str(required=True)
    height = fields.Float(required=True)
    weight = fields.Float(required=True)
    is_pregnant = fields.Bool(required=True)
    last_period_date = fields.Date(required=True)
    # Auto-calculated fields (optional in input, calculated by server)
    pregnancy_week = fields.Int(validate=validate.Range(min=1, max=42))
    expected_delivery_date = fields.Date()
    # Optional medical fields
    medical_conditions = fields.List(fields.Str())
    allergies = fields.List(fields.Str())
    current_medications = fields.List(fields.Str())


class EditProfileSchema(Schema):
    """Schema for editing profile"""
    patient_id = fields.Str(required=True)
    first_name = fields.Str(validate=validate.Length(min=1))
    last_name = fields.Str(validate=validate.Length(min=1))
    mobile = fields.Str(validate=validate.Length(min=10, max=15))
    address = fields.Str()
    emergency_contact = fields.Str()
    height = fields.Float()
    weight = fields.Float()

