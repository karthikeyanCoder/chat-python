"""
Chat Socket Handlers - Real-time Socket.IO event handlers for chat
"""
from flask_socketio import emit, join_room, leave_room, disconnect
from datetime import datetime
import logging

from app.shared.socket_service import (
    get_socketio, add_connected_user, remove_connected_user,
    get_connected_user_by_socket, emit_to_user, emit_to_room,
    add_user_to_room, remove_user_from_room
)
from app.modules.patient_chat.models import Message
from app.modules.patient_chat.repository import get_chat_repository
from app.modules.patient_chat.services import get_chat_service

logger = logging.getLogger(__name__)


def init_chat_socket_handlers(socketio, db):
    """
    Initialize Socket.IO event handlers for chat
    
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
            logger.info(f"Client connection attempt from {auth}")
            
            if not auth or 'user_id' not in auth or 'user_type' not in auth:
                logger.warning("Connection rejected: Missing authentication")
                disconnect()
                return False
            
            user_id = auth.get('user_id')
            user_type = auth.get('user_type')
            user_name = auth.get('user_name', 'Unknown')
            
            # Verify user exists
            if user_type == 'patient':
                user = db.patients_collection.find_one({"patient_id": user_id})
            elif user_type == 'doctor':
                user = db.doctors_collection.find_one({"doctor_id": user_id})
                if not user:
                    user = db.doctor_v2_collection.find_one({"doctor_id": user_id})
            else:
                logger.warning(f"Invalid user type: {user_type}")
                disconnect()
                return False
            
            if not user:
                logger.warning(f"User not found: {user_id}")
                disconnect()
                return False
            
            # Add to connected users
            from flask import request
            socket_id = request.sid
            add_connected_user(user_id, socket_id, user_type, user_name)
            
            # Send welcome message
            emit('connected', {
                'message': 'Connected successfully',
                'user_id': user_id,
                'user_type': user_type,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            # Send unread count for patients
            if user_type == 'patient':
                try:
                    service = get_chat_service()
                    result = service.get_unread_count(user_id)
                    if result['success']:
                        emit('unread_count', result['data'])
                except Exception as e:
                    logger.error(f"Failed to send unread count: {str(e)}")
            
            logger.info(f"User {user_id} ({user_type}) connected successfully")
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
            user_id, user_info = get_connected_user_by_socket(socket_id)
            
            if user_id:
                user_type = user_info.get('user_type', 'unknown')
                logger.info(f"User {user_id} ({user_type}) disconnected")
                remove_connected_user(user_id)
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
            user_id, user_info = get_connected_user_by_socket(socket_id)
            
            if not user_id:
                emit('error', {'message': 'Unauthorized'})
                return
            
            room_id = data.get('room_id')
            if not room_id:
                emit('error', {'message': 'room_id is required'})
                return
            
            # Handle composite room IDs (doctor_patient format)
            if '_' in room_id and len(room_id.split('_')) == 2:
                doctor_id, patient_id = room_id.split('_')
                repository = get_chat_repository()
                chat_room = repository.get_chat_room_by_participants(doctor_id, patient_id)
                if not chat_room:
                    chat_room = repository.create_chat_room(doctor_id, patient_id)
                actual_room_id = chat_room.room_id if chat_room else room_id
            else:
                actual_room_id = room_id
            
            # Verify access to room
            repository = get_chat_repository()
            chat_room = repository.get_chat_room(actual_room_id)
            
            if not chat_room:
                emit('error', {'message': 'Chat room not found'})
                return
            
            user_type = user_info.get('user_type')
            
            # Check access permissions
            if user_type == 'patient' and chat_room.patient_id != user_id:
                emit('error', {'message': 'Access denied'})
                return
            elif user_type == 'doctor' and chat_room.doctor_id != user_id:
                emit('error', {'message': 'Access denied'})
                return
            
            # Join the room
            join_room(actual_room_id)
            add_user_to_room(user_id, actual_room_id)
            
            # Notify others in the room
            emit('user_joined', {
                'user_id': user_id,
                'user_type': user_type,
                'user_name': user_info.get('user_name', 'Unknown'),
                'room_id': actual_room_id,
                'timestamp': datetime.utcnow().isoformat()
            }, room=actual_room_id, skip_sid=socket_id)
            
            # Send confirmation to user
            emit('room_joined', {
                'room_id': actual_room_id,
                'message': 'Successfully joined chat room',
                'timestamp': datetime.utcnow().isoformat()
            })
            
            logger.info(f"User {user_id} joined room {actual_room_id}")
            
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
            user_id, user_info = get_connected_user_by_socket(socket_id)
            
            if not user_id:
                return
            
            room_id = data.get('room_id')
            if not room_id:
                return
            
            # Leave the room
            leave_room(room_id)
            remove_user_from_room(user_id, room_id)
            
            # Notify others in the room
            emit('user_left', {
                'user_id': user_id,
                'user_type': user_info.get('user_type'),
                'room_id': room_id,
                'timestamp': datetime.utcnow().isoformat()
            }, room=room_id)
            
            logger.info(f"User {user_id} left room {room_id}")
            
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
            user_id, user_info = get_connected_user_by_socket(socket_id)
            
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
            repository = get_chat_repository()
            chat_room = repository.get_chat_room(room_id)
            
            if not chat_room:
                emit('error', {'message': 'Chat room not found'})
                return
            
            # Determine sender and receiver
            user_type = user_info.get('user_type')
            
            if user_type == 'patient':
                if chat_room.patient_id != user_id:
                    emit('error', {'message': 'Access denied'})
                    return
                sender_id = user_id
                sender_type = 'patient'
                receiver_id = chat_room.doctor_id
                receiver_type = 'doctor'
            elif user_type == 'doctor':
                if chat_room.doctor_id != user_id:
                    emit('error', {'message': 'Access denied'})
                    return
                sender_id = user_id
                sender_type = 'doctor'
                receiver_id = chat_room.patient_id
                receiver_type = 'patient'
            else:
                emit('error', {'message': 'Invalid user type'})
                return
            
            # Create message
            message = Message(
                chat_room_id=room_id,
                sender_id=sender_id,
                sender_type=sender_type,
                receiver_id=receiver_id,
                receiver_type=receiver_type,
                message_type=message_type,
                content=content,
                is_urgent=is_urgent,
                priority=priority,
                reply_to_message_id=reply_to_message_id
            )
            
            # Save message
            created_message = repository.create_message(message)
            
            if not created_message:
                emit('error', {'message': 'Failed to send message'})
                return
            
            # Broadcast message to room
            message_data = created_message.to_dict()
            message_data['sender_name'] = user_info.get('user_name', 'Unknown')
            
            emit('new_message', message_data, room=room_id)
            
            # Send push notification to receiver if offline
            # (This would integrate with your push notification service)
            
            logger.info(f"Message sent from {sender_id} to {receiver_id} in room {room_id}")
            
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
            user_id, user_info = get_connected_user_by_socket(socket_id)
            
            if not user_id:
                return
            
            room_id = data.get('room_id')
            if not room_id:
                return
            
            # Notify others in the room
            emit('user_typing', {
                'user_id': user_id,
                'user_type': user_info.get('user_type'),
                'user_name': user_info.get('user_name', 'Unknown'),
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
            user_id, user_info = get_connected_user_by_socket(socket_id)
            
            if not user_id:
                return
            
            room_id = data.get('room_id')
            if not room_id:
                return
            
            # Notify others in the room
            emit('user_typing', {
                'user_id': user_id,
                'user_type': user_info.get('user_type'),
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
            user_id, user_info = get_connected_user_by_socket(socket_id)
            
            if not user_id:
                return
            
            message_id = data.get('message_id')
            room_id = data.get('room_id')
            
            if not message_id or not room_id:
                return
            
            # Mark message as read
            repository = get_chat_repository()
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
    
    logger.info("Chat Socket.IO handlers initialized successfully")
