"""
Timezone Utilities - Convert UTC to local timezones
Handles timezone conversion for chat messages and timestamps
"""
from datetime import datetime, timezone
from typing import Optional
import pytz

from app.core.config import TIMEZONE

# Get Indian Standard Time timezone
IST = pytz.timezone(TIMEZONE)


def utc_to_ist(utc_time: datetime) -> datetime:
    """
    Convert UTC datetime to Indian Standard Time (IST)
    
    Args:
        utc_time: UTC datetime object
    
    Returns:
        IST datetime object
    """
    if utc_time is None:
        return None
    
    # If datetime is naive (no timezone info), assume it's UTC
    if utc_time.tzinfo is None:
        utc_time = utc_time.replace(tzinfo=timezone.utc)
    
    # Convert to IST
    ist_time = utc_time.astimezone(IST)
    return ist_time


def ist_to_utc(ist_time: datetime) -> datetime:
    """
    Convert IST datetime to UTC
    
    Args:
        ist_time: IST datetime object
    
    Returns:
        UTC datetime object
    """
    if ist_time is None:
        return None
    
    # If datetime is naive, assume it's IST
    if ist_time.tzinfo is None:
        ist_time = IST.localize(ist_time)
    
    # Convert to UTC
    utc_time = ist_time.astimezone(timezone.utc)
    return utc_time


def get_current_ist_time() -> datetime:
    """
    Get current time in IST
    
    Returns:
        Current IST datetime
    """
    return datetime.now(IST)


def format_ist_time(dt: datetime, format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format IST datetime to string
    
    Args:
        dt: datetime object (UTC or IST)
        format_string: strftime format string
    
    Returns:
        Formatted time string in IST
    """
    if dt is None:
        return ""
    
    # Convert to IST if not already
    ist_time = utc_to_ist(dt)
    return ist_time.strftime(format_string)


def get_ist_isoformat(dt: datetime) -> str:
    """
    Get ISO format string in IST timezone
    
    Args:
        dt: datetime object
    
    Returns:
        ISO format string with IST timezone
    """
    if dt is None:
        return ""
    
    ist_time = utc_to_ist(dt)
    return ist_time.isoformat()


