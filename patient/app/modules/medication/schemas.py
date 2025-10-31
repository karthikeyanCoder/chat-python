"""
Medication Schemas - Request/Response Validation
"""

from marshmallow import Schema, fields, validate


class SaveMedicationLogSchema(Schema):
    """Schema for saving medication log"""
    patient_id = fields.Str(required=True)
    medication_name = fields.Str(required=True)
    date_taken = fields.Str()
    notes = fields.Str()
    prescribed_by = fields.Str()
    medication_type = fields.Str()
    side_effects = fields.List(fields.Str())
    is_prescription_mode = fields.Bool()
    prescription_details = fields.Str()
    dosages = fields.List(fields.Dict())
    dosage = fields.Str()  # Old format compatibility
    time_taken = fields.Str()  # Old format compatibility


class SaveTabletTakenSchema(Schema):
    """Schema for saving tablet taken"""
    patient_id = fields.Str(required=True)
    tablet_name = fields.Str(required=True)
    date_taken = fields.Str(required=True)
    time_taken = fields.Str()
    notes = fields.Str()
    type = fields.Str()


class UploadPrescriptionSchema(Schema):
    """Schema for uploading prescription"""
    patient_id = fields.Str(required=True)
    medication_name = fields.Str(required=True)
    prescription_details = fields.Str(required=True)
    prescribed_by = fields.Str()
    medication_type = fields.Str()
    dosage_instructions = fields.Str()
    frequency = fields.Str()
    duration = fields.Str()
    special_instructions = fields.Str()
    pregnancy_week = fields.Int()


class UpdatePrescriptionStatusSchema(Schema):
    """Schema for updating prescription status"""
    patient_id = fields.Str(required=True)
    prescription_id = fields.Str(required=True)
    status = fields.Str(required=True, validate=validate.OneOf(['active', 'inactive', 'completed']))


class ProcessPrescriptionTextSchema(Schema):
    """Schema for processing prescription text"""
    text = fields.Str(required=True)
    patient_id = fields.Str()


class ProcessWithMockN8NSchema(Schema):
    """Schema for processing with mock N8N"""
    patient_id = fields.Str(required=True)
    medication_name = fields.Str()
    extracted_text = fields.Str(required=True)
    filename = fields.Str()


class SaveTabletTrackingSchema(Schema):
    """Schema for daily tablet tracking"""
    patient_id = fields.Str(required=True)
    tablet_name = fields.Str(required=True)
    tablet_taken_today = fields.Bool(required=True)
    is_prescribed = fields.Bool()
    notes = fields.Str()
    date_taken = fields.Str()
    time_taken = fields.Str()
    type = fields.Str()
    timestamp = fields.Str()

