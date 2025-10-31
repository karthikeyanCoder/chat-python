#!/usr/bin/env python3
"""
WebSocket Service - Handles WebSocket connections for real-time voice communication
"""

from typing import Dict, Any, List, Set
import json
import asyncio
from datetime import datetime

class WebSocketService:
    """Service for managing WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Set[Any] = set()
        self.conversation_connections: Dict[int, Set[Any]] = {}
        self.connection_data: Dict[Any, Dict[str, Any]] = {}
    
    def add_connection(self, websocket, conversation_id: int = None):
        """Add a new WebSocket connection"""
        try:
            self.active_connections.add(websocket)
            
            if conversation_id:
                if conversation_id not in self.conversation_connections:
                    self.conversation_connections[conversation_id] = set()
                self.conversation_connections[conversation_id].add(websocket)
            
            # Store connection metadata
            self.connection_data[websocket] = {
                "conversation_id": conversation_id,
                "connected_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat()
            }
            
            print(f"WebSocket connection added. Total connections: {len(self.active_connections)}")
            
        except Exception as e:
            print(f"Error adding WebSocket connection: {e}")
    
    def remove_connection(self, websocket):
        """Remove a WebSocket connection"""
        try:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
            
            # Remove from conversation connections
            if websocket in self.connection_data:
                conversation_id = self.connection_data[websocket].get("conversation_id")
                if conversation_id and conversation_id in self.conversation_connections:
                    self.conversation_connections[conversation_id].discard(websocket)
                    if not self.conversation_connections[conversation_id]:
                        del self.conversation_connections[conversation_id]
                
                del self.connection_data[websocket]
            
            print(f"WebSocket connection removed. Total connections: {len(self.active_connections)}")
            
        except Exception as e:
            print(f"Error removing WebSocket connection: {e}")
    
    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return len(self.active_connections)
    
    def get_conversation_connection_count(self, conversation_id: int) -> int:
        """Get number of connections for a specific conversation"""
        return len(self.conversation_connections.get(conversation_id, set()))
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get information about all connections"""
        try:
            connections_info = []
            
            for websocket, data in self.connection_data.items():
                connections_info.append({
                    "conversation_id": data.get("conversation_id"),
                    "connected_at": data.get("connected_at"),
                    "last_activity": data.get("last_activity")
                })
            
            return {
                "total_connections": len(self.active_connections),
                "conversation_connections": {
                    str(conv_id): len(connections) 
                    for conv_id, connections in self.conversation_connections.items()
                },
                "connections": connections_info
            }
            
        except Exception as e:
            print(f"Error getting connection info: {e}")
            return {"error": str(e)}
    
    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Broadcast message to all active connections"""
        try:
            if not self.active_connections:
                return
            
            message_str = json.dumps(message)
            disconnected = set()
            
            for websocket in self.active_connections:
                try:
                    await websocket.send_text(message_str)
                except Exception as e:
                    print(f"Error sending message to WebSocket: {e}")
                    disconnected.add(websocket)
            
            # Remove disconnected connections
            for websocket in disconnected:
                self.remove_connection(websocket)
                
        except Exception as e:
            print(f"Error broadcasting message: {e}")
    
    async def broadcast_to_conversation(self, conversation_id: int, message: Dict[str, Any]):
        """Broadcast message to all connections in a specific conversation"""
        try:
            if conversation_id not in self.conversation_connections:
                return
            
            message_str = json.dumps(message)
            disconnected = set()
            
            for websocket in self.conversation_connections[conversation_id]:
                try:
                    await websocket.send_text(message_str)
                except Exception as e:
                    print(f"Error sending message to conversation WebSocket: {e}")
                    disconnected.add(websocket)
            
            # Remove disconnected connections
            for websocket in disconnected:
                self.remove_connection(websocket)
                
        except Exception as e:
            print(f"Error broadcasting to conversation: {e}")
    
    async def send_to_connection(self, websocket, message: Dict[str, Any]):
        """Send message to a specific WebSocket connection"""
        try:
            message_str = json.dumps(message)
            await websocket.send_text(message_str)
            
            # Update last activity
            if websocket in self.connection_data:
                self.connection_data[websocket]["last_activity"] = datetime.now().isoformat()
                
        except Exception as e:
            print(f"Error sending message to specific WebSocket: {e}")
            self.remove_connection(websocket)
    
    def update_connection_activity(self, websocket):
        """Update last activity timestamp for a connection"""
        try:
            if websocket in self.connection_data:
                self.connection_data[websocket]["last_activity"] = datetime.now().isoformat()
        except Exception as e:
            print(f"Error updating connection activity: {e}")
    
    def get_conversation_connections(self, conversation_id: int) -> List[Any]:
        """Get all connections for a specific conversation"""
        return list(self.conversation_connections.get(conversation_id, set()))
    
    def cleanup_inactive_connections(self, max_inactive_minutes: int = 30):
        """Clean up connections that have been inactive for too long"""
        try:
            from datetime import datetime, timedelta
            
            cutoff_time = datetime.now() - timedelta(minutes=max_inactive_minutes)
            inactive_connections = set()
            
            for websocket, data in self.connection_data.items():
                last_activity_str = data.get("last_activity", "")
                if last_activity_str:
                    try:
                        last_activity = datetime.fromisoformat(last_activity_str)
                        if last_activity < cutoff_time:
                            inactive_connections.add(websocket)
                    except ValueError:
                        # If we can't parse the date, consider it inactive
                        inactive_connections.add(websocket)
            
            # Remove inactive connections
            for websocket in inactive_connections:
                self.remove_connection(websocket)
            
            if inactive_connections:
                print(f"Cleaned up {len(inactive_connections)} inactive connections")
                
        except Exception as e:
            print(f"Error cleaning up inactive connections: {e}")
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get WebSocket service status"""
        try:
            return {
                "active_connections": len(self.active_connections),
                "conversation_connections": len(self.conversation_connections),
                "total_conversations": len(self.conversation_connections),
                "service_status": "running",
                "last_cleanup": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": str(e),
                "service_status": "error"
            }
