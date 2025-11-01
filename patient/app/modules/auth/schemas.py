"""
Authentication Schemas - Request/Response Validation
"""
from marshmallow import Schema, fields, validate, ValidationError, post_load


class SignupSchema(Schema):
    """Schema for user signup"""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    mobile = fields.Str(required=True, validate=validate.Regexp(regex=r'^\d{10}$', error='Mobile must be exactly 10 digits'))
    password = fields.Str(required=True, validate=validate.Length(min=6))

    @post_load
    def capitalize_strings(self, data, **kwargs):
        """Capitalize first letter of string values (excluding email, password, mobile)"""
        exclude_fields = ['email', 'password', 'mobile']
        for key, value in data.items():
            if key in exclude_fields:
                continue
            if isinstance(value, str) and value:
                data[key] = value[0].upper() + value[1:] if len(value) > 1 else value.upper()
        return data


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
    emergency_contact_phone = fields.Str(required=True, validate=validate.Regexp(regex=r'^\d{10}$', error='Emergency contact phone must be exactly 10 digits'))
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

    @post_load
    def capitalize_strings(self, data, **kwargs):
        """Capitalize first letter of string values (excluding email, IDs, dates, numbers)"""
        exclude_fields = ['patient_id', 'date_of_birth', 'last_period_date', 'expected_delivery_date',
                         'height', 'weight', 'is_pregnant', 'pregnancy_week', 'emergency_contact_phone']
        for key, value in data.items():
            if key in exclude_fields:
                continue
            if isinstance(value, str) and value:
                data[key] = value[0].upper() + value[1:] if len(value) > 1 else value.upper()
            elif isinstance(value, list):
                # Capitalize first letter of strings in lists (medical_conditions, allergies, medications)
                data[key] = [v[0].upper() + v[1:] if isinstance(v, str) and v and len(v) > 1 else (v.upper() if isinstance(v, str) and v else v) for v in value]
        return data


class EditProfileSchema(Schema):
    """Schema for editing profile"""
    patient_id = fields.Str(required=True)
    first_name = fields.Str(validate=validate.Length(min=1))
    last_name = fields.Str(validate=validate.Length(min=1))
    mobile = fields.Str(validate=validate.Regexp(regex=r'^\d{10}$', error='Mobile must be exactly 10 digits'))
    address = fields.Str()
    emergency_contact = fields.Str()
    height = fields.Float()
    weight = fields.Float()

    @post_load
    def capitalize_strings(self, data, **kwargs):
        """Capitalize first letter of string values (excluding patient_id, mobile, height, weight)"""
        exclude_fields = ['patient_id', 'mobile', 'height', 'weight']
        for key, value in data.items():
            if key in exclude_fields:
                continue
            if isinstance(value, str) and value:
                data[key] = value[0].upper() + value[1:] if len(value) > 1 else value.upper()
            elif isinstance(value, list):
                # Capitalize first letter of strings in lists (medical_conditions, allergies, medications)
                data[key] = [v[0].upper() + v[1:] if isinstance(v, str) and v and len(v) > 1 else (v.upper() if isinstance(v, str) and v else v) for v in value]
        return data

