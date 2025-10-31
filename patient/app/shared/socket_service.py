"""
Socket Service - Shared Socket.IO module for real-time communication
Provides a centralized Socket.IO instance for use across the application
"""
from flask_socketio import SocketIO
import logging

logger = logging.getLogger(__name__)

# Global Socket.IO instance
socketio = None


def init_socketio(app):
    """
    Initialize Socket.IO with the Flask application
    
    Args:
        app: Flask application instance
    
    Returns:
        SocketIO instance
    """
    global socketio
    
    socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        async_mode='threading',
        logger=True,
        engineio_logger=False,
        ping_timeout=60,
        ping_interval=25
    )
    
    logger.info("Socket.IO initialized successfully")
    return socketio


def get_socketio():
    """
    Get the Socket.IO instance
    
    Returns:
        SocketIO instance
    
    Raises:
        RuntimeError: If Socket.IO hasn't been initialized
    """
    global socketio
    
    if socketio is None:
        raise RuntimeError(
            "Socket.IO has not been initialized. "
            "Call init_socketio(app) first."
        )
    
    return socketio


def emit_to_user(user_id: str, event: str, data: dict):
    """
    Emit an event to a specific user by their user ID
    
    Args:
        user_id: User ID to send the event to
        event: Event name
        data: Event data
    """
    try:
        sio = get_socketio()
        sio.emit(event, data, room=user_id)
        logger.debug(f"Emitted {event} to user {user_id}")
    except Exception as e:
        logger.error(f"Failed to emit {event} to user {user_id}: {str(e)}")


def emit_to_room(room_id: str, event: str, data: dict, skip_sid: str = None):
    """
    Emit an event to all users in a room
    
    Args:
        room_id: Room ID to send the event to
        event: Event name
        data: Event data
        skip_sid: Optional socket ID to skip (e.g., sender)
    """
    try:
        sio = get_socketio()
        sio.emit(event, data, room=room_id, skip_sid=skip_sid)
        logger.debug(f"Emitted {event} to room {room_id}")
    except Exception as e:
        logger.error(f"Failed to emit {event} to room {room_id}: {str(e)}")


def broadcast_event(event: str, data: dict):
    """
    Broadcast an event to all connected clients
    
    Args:
        event: Event name
        data: Event data
    """
    try:
        sio = get_socketio()
        sio.emit(event, data, broadcast=True)
        logger.debug(f"Broadcasted {event}")
    except Exception as e:
        logger.error(f"Failed to broadcast {event}: {str(e)}")


# Connection state management
connected_users = {}


def add_connected_user(user_id: str, socket_id: str, user_type: str, user_name: str = None):
    """
    Add a user to the connected users registry
    
    Args:
        user_id: User ID
        socket_id: Socket ID
        user_type: Type of user (patient, doctor)
        user_name: Optional user name
    """
    connected_users[user_id] = {
        'sid': socket_id,
        'user_type': user_type,
        'user_name': user_name,
        'rooms': []
    }
    logger.info(f"User {user_id} ({user_type}) connected with socket {socket_id}")


def remove_connected_user(user_id: str):
    """
    Remove a user from the connected users registry
    
    Args:
        user_id: User ID
    """
    if user_id in connected_users:
        del connected_users[user_id]
        logger.info(f"User {user_id} disconnected")


def get_connected_user_by_socket(socket_id: str):
    """
    Get user info by socket ID
    
    Args:
        socket_id: Socket ID
    
    Returns:
        tuple: (user_id, user_info) or (None, None)
    """
    for user_id, info in connected_users.items():
        if info.get('sid') == socket_id:
            return user_id, info
    return None, None


def is_user_online(user_id: str) -> bool:
    """
    Check if a user is currently online
    
    Args:
        user_id: User ID
    
    Returns:
        bool: True if user is online
    """
    return user_id in connected_users


def get_user_socket_id(user_id: str) -> str:
    """
    Get the socket ID for a user
    
    Args:
        user_id: User ID
    
    Returns:
        str: Socket ID or None
    """
    user_info = connected_users.get(user_id)
    return user_info.get('sid') if user_info else None


def add_user_to_room(user_id: str, room_id: str):
    """
    Track that a user has joined a room
    
    Args:
        user_id: User ID
        room_id: Room ID
    """
    if user_id in connected_users:
        rooms = connected_users[user_id].get('rooms', [])
        if room_id not in rooms:
            rooms.append(room_id)
            connected_users[user_id]['rooms'] = rooms


def remove_user_from_room(user_id: str, room_id: str):
    """
    Track that a user has left a room
    
    Args:
        user_id: User ID
        room_id: Room ID
    """
    if user_id in connected_users:
        rooms = connected_users[user_id].get('rooms', [])
        if room_id in rooms:
            rooms.remove(room_id)
            connected_users[user_id]['rooms'] = rooms


def get_online_users_count() -> int:
    """
    Get the count of currently online users
    
    Returns:
        int: Number of online users
    """
    return len(connected_users)


def get_online_users_by_type(user_type: str) -> list:
    """
    Get list of online users by type
    
    Args:
        user_type: Type of user (patient, doctor)
    
    Returns:
        list: List of user IDs
    """
    return [
        user_id for user_id, info in connected_users.items()
        if info.get('user_type') == user_type
    ]

