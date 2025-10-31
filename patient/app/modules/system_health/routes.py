"""
System Health Module Routes
Handles database health, system status endpoints
EXTRACTED FROM app_simple.py lines 5915-5985
"""

from flask import Blueprint
from .services import (
    check_database_health_service,
    force_database_reconnect_service
)

system_health_bp = Blueprint('system_health', __name__)


@system_health_bp.route('/health/database', methods=['GET'])
def check_database_health():
    """Check database connection status"""
    return check_database_health_service()


@system_health_bp.route('/health/database/reconnect', methods=['POST'])
def force_database_reconnect():
    """Force database reconnection"""
    return force_database_reconnect_service()
