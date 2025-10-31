"""
Doctor Chat Socket Handlers - Real-time Socket.IO event handlers
Enhanced real-time communication for doctor-patient messaging
"""
from flask_socketio import emit, join_room, leave_room, disconnect
from datetime import datetime
import logging

from app.modules.doctor_chat.models import Message
from app.modules.doctor_chat.repository import get_doctor_chat_repository

logger = logging.getLogger(__name__)

# Store connected users (can be replaced with Redis for production)
connected_users = {}
user_rooms = {}


def init_doctor_chat_socket_handlers(socketio, db):
    """
    Initialize Socket.IO event handlers for doctor chat
    
    Args:
        socketio: SocketIO instance
        db: Database instance
    """
    
    @socketio.on('connect')
    def handle_connect(auth):
        """
        Handle client connection
        
        Args:
            auth: Authentication data containing user_id, user_type, user_name
        """
        try:
            logger.info(f"Doctor connection attempt from {auth}")
            
            if not auth or 'user_id' not in auth or 'user_type' not in auth:
                logger.warning("Connection rejected: Missing authentication")
                disconnect()
                return False
            
            user_id = auth.get('user_id')
            user_type = auth.get('user_type')
            user_name = auth.get('user_name', 'Unknown')
            
            # Only allow doctor connections in this handler
            if user_type != 'doctor':
                logger.warning(f"Non-doctor connection attempt: {user_type}")
                disconnect()
                return False
            
            # Verify doctor exists
            if hasattr(db, 'doctors_collection'):
                doctors_collection = db.doctors_collection
            else:
                doctors_collection = db['doctors']
            
            doctor = doctors_collection.find_one({"doctor_id": user_id})
            if not doctor:
                logger.warning(f"Doctor not found: {user_id}")
                disconnect()
                return False
            
            # Add to connected users
            from flask import request
            socket_id = request.sid
            connected_users[user_id] = {
                'socket_id': socket_id,
                'user_type': user_type,
                'user_name': user_name,
                'connected_at': datetime.utcnow()
            }
            user_rooms[user_id] = []
            
            # Send welcome message
            emit('connected', {
                'message': 'Connected successfully',
                'user_id': user_id,
                'user_type': user_type,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            # Send unread count
            try:
                repository = get_doctor_chat_repository()
                unread_count = repository.get_unread_message_count(user_id, 'doctor')
                emit('unread_count', {'total_unread': unread_count})
            except Exception as e:
                logger.error(f"Failed to send unread count: {str(e)}")
            
            logger.info(f"Doctor {user_id} connected successfully")
            return True
            
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            disconnect()
            return False
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        try:
            from flask import request
            socket_id = request.sid
            
            # Find and remove user
            user_id = None
            for uid, user_info in connected_users.items():
                if user_info['socket_id'] == socket_id:
                    user_id = uid
                    break
            
            if user_id:
                logger.info(f"Doctor {user_id} disconnected")
                del connected_users[user_id]
                if user_id in user_rooms:
                    del user_rooms[user_id]
                    
        except Exception as e:
            logger.error(f"Disconnect error: {str(e)}")
    
    @socketio.on('join_chat_room')
    def handle_join_room(data):
        """
        Handle joining a chat room
        
        Args:
            data: Dict containing room_id
        """
        try:
            from flask import request
            socket_id = request.sid
            
            # Find user by socket ID
            user_id = None
            user_info = None
            for uid, info in connected_users.items():
                if info['socket_id'] == socket_id:
                    user_id = uid
                    user_info = info
                    break
            
            if not user_id:
                emit('error', {'message': 'Unauthorized'})
                return
            
            room_id = data.get('room_id')
            if not room_id:
                emit('error', {'message': 'room_id is required'})
                return
            
            # Verify access to room
            repository = get_doctor_chat_repository()
            chat_room = repository.get_chat_room(room_id)
            
            if not chat_room:
                emit('error', {'message': 'Chat room not found'})
                return
            
            if chat_room.doctor_id != user_id:
                emit('error', {'message': 'Access denied'})
                return
            
            # Join the room
            join_room(room_id)
            if user_id not in user_rooms:
                user_rooms[user_id] = []
            if room_id not in user_rooms[user_id]:
                user_rooms[user_id].append(room_id)
            
            # Notify others in the room
            emit('user_joined', {
                'user_id': user_id,
                'user_type': 'doctor',
                'user_name': user_info.get('user_name', 'Unknown'),
                'room_id': room_id,
                'timestamp': datetime.utcnow().isoformat()
            }, room=room_id, skip_sid=socket_id)
            
            # Send confirmation to user
            emit('room_joined', {
                'room_id': room_id,
                'message': 'Successfully joined chat room',
                'timestamp': datetime.utcnow().isoformat()
            })
            
            logger.info(f"Doctor {user_id} joined room {room_id}")
            
        except Exception as e:
            logger.error(f"Join room error: {str(e)}")
            emit('error', {'message': 'Failed to join room'})
    
    @socketio.on('leave_chat_room')
    def handle_leave_room(data):
        """
        Handle leaving a chat room
        
        Args:
            data: Dict containing room_id
        """
        try:
            from flask import request
            socket_id = request.sid
            
            # Find user by socket ID
            user_id = None
            for uid, info in connected_users.items():
                if info['socket_id'] == socket_id:
                    user_id = uid
                    break
            
            if not user_id:
                return
            
            room_id = data.get('room_id')
            if not room_id:
                return
            
            # Leave the room
            leave_room(room_id)
            if user_id in user_rooms and room_id in user_rooms[user_id]:
                user_rooms[user_id].remove(room_id)
            
            # Notify others in the room
            emit('user_left', {
                'user_id': user_id,
                'user_type': 'doctor',
                'room_id': room_id,
                'timestamp': datetime.utcnow().isoformat()
            }, room=room_id)
            
            logger.info(f"Doctor {user_id} left room {room_id}")
            
        except Exception as e:
            logger.error(f"Leave room error: {str(e)}")
    
    @socketio.on('send_message')
    def handle_send_message(data):
        """
        Handle sending a message
        
        Args:
            data: Dict containing room_id, content, message_type, etc.
        """
        try:
            from flask import request
            socket_id = request.sid
            
            # Find user by socket ID
            user_id = None
            user_info = None
            for uid, info in connected_users.items():
                if info['socket_id'] == socket_id:
                    user_id = uid
                    user_info = info
                    break
            
            if not user_id:
                emit('error', {'message': 'Unauthorized'})
                return
            
            room_id = data.get('room_id')
            content = data.get('content')
            message_type = data.get('message_type', 'text')
            is_urgent = data.get('is_urgent', False)
            priority = data.get('priority', 'normal')
            reply_to_message_id = data.get('reply_to_message_id')
            
            if not room_id or not content:
                emit('error', {'message': 'room_id and content are required'})
                return
            
            # Get chat room
            repository = get_doctor_chat_repository()
            chat_room = repository.get_chat_room(room_id)
            
            if not chat_room:
                emit('error', {'message': 'Chat room not found'})
                return
            
            if chat_room.doctor_id != user_id:
                emit('error', {'message': 'Access denied'})
                return
            
            # Create message
            message = Message(
                chat_room_id=room_id,
                sender_id=user_id,
                sender_type='doctor',
                receiver_id=chat_room.patient_id,
                receiver_type='patient',
                message_type=message_type,
                content=content,
                is_urgent=is_urgent,
                priority=priority,
                reply_to_message_id=reply_to_message_id,
                sender_name=user_info.get('user_name', 'Doctor')
            )
            
            # Save message
            created_message = repository.create_message(message)
            
            if not created_message:
                emit('error', {'message': 'Failed to send message'})
                return
            
            # Broadcast message to room
            message_data = created_message.to_dict()
            
            emit('new_message', message_data, room=room_id)
            
            logger.info(f"Message sent from doctor {user_id} in room {room_id}")
            
        except Exception as e:
            logger.error(f"Send message error: {str(e)}")
            emit('error', {'message': 'Failed to send message'})
    
    @socketio.on('typing_start')
    def handle_typing_start(data):
        """
        Handle typing indicator start
        
        Args:
            data: Dict containing room_id
        """
        try:
            from flask import request
            socket_id = request.sid
            
            # Find user by socket ID
            user_id = None
            user_info = None
            for uid, info in connected_users.items():
                if info['socket_id'] == socket_id:
                    user_id = uid
                    user_info = info
                    break
            
            if not user_id:
                return
            
            room_id = data.get('room_id')
            if not room_id:
                return
            
            # Notify others in the room
            emit('user_typing', {
                'user_id': user_id,
                'user_type': 'doctor',
                'user_name': user_info.get('user_name', 'Doctor'),
                'room_id': room_id,
                'is_typing': True
            }, room=room_id, skip_sid=socket_id)
            
        except Exception as e:
            logger.error(f"Typing start error: {str(e)}")
    
    @socketio.on('typing_stop')
    def handle_typing_stop(data):
        """
        Handle typing indicator stop
        
        Args:
            data: Dict containing room_id
        """
        try:
            from flask import request
            socket_id = request.sid
            
            # Find user by socket ID
            user_id = None
            for uid, info in connected_users.items():
                if info['socket_id'] == socket_id:
                    user_id = uid
                    break
            
            if not user_id:
                return
            
            room_id = data.get('room_id')
            if not room_id:
                return
            
            # Notify others in the room
            emit('user_typing', {
                'user_id': user_id,
                'user_type': 'doctor',
                'room_id': room_id,
                'is_typing': False
            }, room=room_id, skip_sid=socket_id)
            
        except Exception as e:
            logger.error(f"Typing stop error: {str(e)}")
    
    @socketio.on('message_read')
    def handle_message_read(data):
        """
        Handle message read receipt
        
        Args:
            data: Dict containing message_id and room_id
        """
        try:
            from flask import request
            socket_id = request.sid
            
            # Find user by socket ID
            user_id = None
            for uid, info in connected_users.items():
                if info['socket_id'] == socket_id:
                    user_id = uid
                    break
            
            if not user_id:
                return
            
            message_id = data.get('message_id')
            room_id = data.get('room_id')
            
            if not message_id or not room_id:
                return
            
            # Mark message as read
            repository = get_doctor_chat_repository()
            success = repository.mark_message_as_read(message_id)
            
            if success:
                # Notify sender
                emit('message_read_receipt', {
                    'message_id': message_id,
                    'room_id': room_id,
                    'read_by': user_id,
                    'read_at': datetime.utcnow().isoformat()
                }, room=room_id, skip_sid=socket_id)
            
        except Exception as e:
            logger.error(f"Message read error: {str(e)}")
    
    logger.info("Doctor chat Socket.IO handlers initialized successfully")


def emit_to_doctor(doctor_id: str, event: str, data: dict):
    """
    Emit an event to a specific doctor if online
    
    Args:
        doctor_id: Doctor ID
        event: Event name
        data: Event data
    """
    try:
        if doctor_id in connected_users:
            user_info = connected_users[doctor_id]
            socket_id = user_info['socket_id']
            from flask_socketio import emit
            emit(event, data, room=socket_id)
    except Exception as e:
        logger.error(f"Failed to emit to doctor {doctor_id}: {str(e)}")


def is_doctor_online(doctor_id: str) -> bool:
    """
    Check if a doctor is online
    
    Args:
        doctor_id: Doctor ID
    
    Returns:
        bool: True if online, False otherwise
    """
    return doctor_id in connected_users


