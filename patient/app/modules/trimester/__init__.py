"""
Trimester Module Blueprint

This module provides trimester-related functionality including
pregnancy data, baby size calculations, and RAG-based features.
"""

from flask import Blueprint

# Create the trimester blueprint
trimester_bp = Blueprint('trimester', __name__, url_prefix='/trimester')

# Import routes to register them with the blueprint
# Note: Import is deferred to avoid heavy dependency loading during module import
def register_routes():
    """Register routes with the blueprint - call this after app initialization"""
    try:
        from . import routes
        return True
    except ImportError as e:
        print(f"Warning: Could not import trimester routes: {e}")
        return False
