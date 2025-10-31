"""
Profile Utilities Schemas - Request/Response Validation
"""

from marshmallow import Schema, fields


# Profile endpoints are primarily GET requests with no body
# Validation is minimal for this module
class ProfileSchema(Schema):
    """Base profile schema"""
    pass

