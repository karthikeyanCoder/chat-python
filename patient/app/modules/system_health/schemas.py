"""
System Health Schemas - Request/Response Validation
"""

from marshmallow import Schema, fields


# Database health endpoints are GET/POST with no body
# Minimal validation needed
class HealthCheckSchema(Schema):
    """Base health check schema"""
    pass

