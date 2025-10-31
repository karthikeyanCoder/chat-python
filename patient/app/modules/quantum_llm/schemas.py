"""
Quantum & LLM Schemas - Request/Response Validation
"""

from marshmallow import Schema, fields


class LLMTestSchema(Schema):
    """Schema for LLM test"""
    prompt = fields.Str()


class AddKnowledgeSchema(Schema):
    """Schema for adding knowledge to vector DB"""
    text = fields.Str(required=True)
    source = fields.Str(required=True)
    trimester = fields.Str(required=True)
    tags = fields.List(fields.Str())
    triage = fields.Str()


class SearchKnowledgeSchema(Schema):
    """Schema for searching knowledge base"""
    text = fields.Str(required=True)
    weeks_pregnant = fields.Int()
    limit = fields.Int()

