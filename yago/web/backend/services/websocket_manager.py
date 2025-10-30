"""
YAGO v8.3 - WebSocket Manager
Real-time progress updates for project execution
"""
from typing import Dict, List, Set
from fastapi import WebSocket
import json
import asyncio
from datetime import datetime


class ConnectionManager:
    """Manage WebSocket connections and broadcast messages"""

    def __init__(self):
        # Active connections: project_id -> set of websockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Connection metadata
        self.connection_metadata: Dict[WebSocket, Dict] = {}

    async def connect(self, websocket: WebSocket, project_id: str):
        """Accept a new WebSocket connection for a project"""
        await websocket.accept()

        if project_id not in self.active_connections:
            self.active_connections[project_id] = set()

        self.active_connections[project_id].add(websocket)
        self.connection_metadata[websocket] = {
            'project_id': project_id,
            'connected_at': datetime.now().isoformat(),
            'messages_sent': 0
        }

        # Send connection success message
        await self.send_personal_message({
            'type': 'connection',
            'status': 'connected',
            'project_id': project_id,
            'timestamp': datetime.now().isoformat()
        }, websocket)

    def disconnect(self, websocket: WebSocket, project_id: str):
        """Remove a WebSocket connection"""
        if project_id in self.active_connections:
            self.active_connections[project_id].discard(websocket)

            # Clean up empty project connection sets
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]

        if websocket in self.connection_metadata:
            del self.connection_metadata[websocket]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific client"""
        try:
            await websocket.send_json(message)
            if websocket in self.connection_metadata:
                self.connection_metadata[websocket]['messages_sent'] += 1
        except Exception as e:
            print(f"Error sending personal message: {e}")

    async def broadcast_to_project(self, project_id: str, message: dict):
        """Broadcast a message to all clients watching a specific project"""
        if project_id not in self.active_connections:
            return

        # Add timestamp to message
        message['timestamp'] = datetime.now().isoformat()

        # Send to all connected clients for this project
        disconnected = set()
        for connection in self.active_connections[project_id]:
            try:
                await connection.send_json(message)
                if connection in self.connection_metadata:
                    self.connection_metadata[connection]['messages_sent'] += 1
            except Exception as e:
                print(f"Error broadcasting to project {project_id}: {e}")
                disconnected.add(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection, project_id)

    async def send_progress_update(
        self,
        project_id: str,
        progress: int,
        status: str,
        message: str,
        details: dict = None
    ):
        """Send a progress update to all clients watching a project"""
        update = {
            'type': 'progress',
            'project_id': project_id,
            'progress': progress,
            'status': status,
            'message': message,
            'details': details or {}
        }
        await self.broadcast_to_project(project_id, update)

    async def send_log(self, project_id: str, log: str, level: str = 'info'):
        """Send a log message to all clients watching a project"""
        log_message = {
            'type': 'log',
            'project_id': project_id,
            'log': log,
            'level': level
        }
        await self.broadcast_to_project(project_id, log_message)

    async def send_error(self, project_id: str, error: str):
        """Send an error message to all clients watching a project"""
        error_message = {
            'type': 'error',
            'project_id': project_id,
            'error': error
        }
        await self.broadcast_to_project(project_id, error_message)

    async def send_completion(
        self,
        project_id: str,
        success: bool,
        files_generated: int = 0,
        lines_of_code: int = 0,
        cost: float = 0.0
    ):
        """Send a completion message when project execution finishes"""
        completion_message = {
            'type': 'completion',
            'project_id': project_id,
            'success': success,
            'files_generated': files_generated,
            'lines_of_code': lines_of_code,
            'cost': cost
        }
        await self.broadcast_to_project(project_id, completion_message)

    async def send_clarification_needed(
        self,
        project_id: str,
        question: str,
        options: List[str] = None
    ):
        """Send a clarification request to clients"""
        clarification_message = {
            'type': 'clarification',
            'project_id': project_id,
            'question': question,
            'options': options or []
        }
        await self.broadcast_to_project(project_id, clarification_message)

    async def send_file_created(self, project_id: str, file_path: str, size: int):
        """Send notification when a file is created"""
        file_message = {
            'type': 'file_created',
            'project_id': project_id,
            'file_path': file_path,
            'size': size
        }
        await self.broadcast_to_project(project_id, file_message)

    def get_connection_count(self, project_id: str = None) -> int:
        """Get the number of active connections for a project or total"""
        if project_id:
            return len(self.active_connections.get(project_id, set()))
        return sum(len(conns) for conns in self.active_connections.values())

    def get_stats(self) -> dict:
        """Get statistics about WebSocket connections"""
        return {
            'total_connections': self.get_connection_count(),
            'projects_watched': len(self.active_connections),
            'projects': {
                project_id: len(connections)
                for project_id, connections in self.active_connections.items()
            }
        }


# Global WebSocket manager instance
manager = ConnectionManager()
