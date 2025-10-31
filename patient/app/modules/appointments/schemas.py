"""
Appointments Schemas - Request/Response Validation
"""

from marshmallow import Schema, fields, validate


class CreateAppointmentSchema(Schema):
    """Schema for creating appointment"""
    appointment_date = fields.Str(required=True)
    appointment_time = fields.Str(required=True)
    type = fields.Str(required=True)  # Consultation type
    appointment_type = fields.Str(required=True)  # Video Call or In-person
    slot_id = fields.Str()  # Optional slot ID from doctor availability
    notes = fields.Str()
    patient_notes = fields.Str()
    doctor_id = fields.Str()


class UpdateAppointmentSchema(Schema):
    """Schema for updating appointment"""
    appointment_date = fields.Str()
    appointment_time = fields.Str()
    type = fields.Str()
    appointment_type = fields.Str()
    appointment_status = fields.Str(validate=validate.OneOf(['pending', 'confirmed', 'cancelled', 'completed', 'rejected']))
    notes = fields.Str()
    patient_notes = fields.Str()
    doctor_notes = fields.Str()
    doctor_id = fields.Str()


class ApproveAppointmentSchema(Schema):
    """Schema for approving appointment"""
    doctor_notes = fields.Str()


class RejectAppointmentSchema(Schema):
    """Schema for rejecting appointment"""
    doctor_notes = fields.Str()
    rejection_reason = fields.Str()

