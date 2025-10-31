"""
System Health Repository - Data Access Layer (Model)
Handles database health checks
"""

from app.core.database import db


class SystemHealthRepository:
    """Data access layer for system health operations"""
    
    def __init__(self, db_instance):
        self.db = db_instance
    
    # System health primarily uses db.is_connected() and db.reconnect()
    # No direct collection access needed
    pass

