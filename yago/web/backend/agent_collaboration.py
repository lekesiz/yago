"""
YAGO v7.1 - Agent Collaboration Protocols
Multi-agent coordination and message passing system
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from collections import defaultdict
import json

router = APIRouter(prefix="/api/v1/collaboration", tags=["collaboration"])


# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class MessageType(str, Enum):
    """Types of messages agents can send"""
    CODE_READY = "code_ready"
    TEST_RESULTS = "test_results"
    REVIEW_NEEDED = "review_needed"
    ISSUE_FOUND = "issue_found"
    FIX_REQUESTED = "fix_requested"
    DOCUMENTATION_READY = "documentation_ready"
    CLARIFICATION_NEEDED = "clarification_needed"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    CONFLICT_DETECTED = "conflict_detected"


class MessagePriority(str, Enum):
    """Message priority levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AgentType(str, Enum):
    """YAGO Agent types"""
    PLANNER = "Planner"
    CODER = "Coder"
    TESTER = "Tester"
    REVIEWER = "Reviewer"
    DOCUMENTER = "Documenter"
    SECURITY = "SecurityAgent"
    DEVOPS = "DevOpsAgent"
    DATABASE = "DatabaseAgent"
    FRONTEND = "FrontendAgent"
    BACKEND = "BackendAgent"


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class AgentMessage(BaseModel):
    """Message between agents"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    from_agent: AgentType
    to_agent: Optional[AgentType] = None  # None = broadcast
    message_type: MessageType
    priority: MessagePriority = MessagePriority.MEDIUM
    data: Dict[str, Any]
    requires_ack: bool = False
    timeout: int = 300  # seconds
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    project_id: str
    session_id: Optional[str] = None
    acknowledged: bool = False
    ack_timestamp: Optional[datetime] = None


class AgentStatus(BaseModel):
    """Agent status information"""
    agent_id: str
    agent_type: AgentType
    status: str  # idle, busy, waiting, error
    current_task: Optional[str] = None
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    messages_sent: int = 0
    messages_received: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0


class SharedContext(BaseModel):
    """Shared context for all agents in a project"""
    project_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    tech_stack: Dict[str, Any] = {}
    architecture: Dict[str, Any] = {}
    security_requirements: List[str] = []
    test_requirements: Dict[str, Any] = {}
    deployment_target: Dict[str, Any] = {}
    agent_outputs: Dict[str, Dict[str, Any]] = {}
    active_issues: List[Dict[str, Any]] = []
    decisions: List[Dict[str, Any]] = []


class Conflict(BaseModel):
    """Represents a conflict between agents"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    agent_a: AgentType
    agent_b: AgentType
    description: str
    agent_a_proposal: Dict[str, Any]
    agent_b_proposal: Dict[str, Any]
    resolution: Optional[Dict[str, Any]] = None
    resolved: bool = False
    resolved_by: Optional[str] = None  # "SuperAdmin" or agent name
    resolution_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None


class TaskDependency(BaseModel):
    """Task dependency between agents"""
    task_id: str
    agent: AgentType
    depends_on: List[str] = []  # List of task_ids
    status: str  # pending, ready, in_progress, completed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


# ============================================================================
# IN-MEMORY STORAGE (Redis would be used in production)
# ============================================================================

class CollaborationStorage:
    """In-memory storage for collaboration data"""

    def __init__(self):
        self.messages: Dict[str, List[AgentMessage]] = defaultdict(list)
        self.agent_statuses: Dict[str, AgentStatus] = {}
        self.shared_contexts: Dict[str, SharedContext] = {}
        self.conflicts: Dict[str, List[Conflict]] = defaultdict(list)
        self.dependencies: Dict[str, List[TaskDependency]] = defaultdict(list)
        self.message_queues: Dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)
        self.websocket_connections: Dict[str, List[WebSocket]] = defaultdict(list)

    def add_message(self, message: AgentMessage):
        """Add message to project's message history"""
        self.messages[message.project_id].append(message)
        # Add to recipient's queue if specified
        if message.to_agent:
            queue_key = f"{message.project_id}:{message.to_agent.value}"
            # asyncio.create_task would be used in production

    def get_messages(self, project_id: str, agent: Optional[AgentType] = None) -> List[AgentMessage]:
        """Get messages for a project, optionally filtered by agent"""
        project_messages = self.messages.get(project_id, [])
        if agent:
            # Get messages TO this agent or broadcasts (to_agent=None)
            return [
                msg for msg in project_messages
                if msg.to_agent == agent or msg.to_agent is None
            ]
        return project_messages

    def update_agent_status(self, agent_id: str, status: AgentStatus):
        """Update agent status"""
        self.agent_statuses[agent_id] = status

    def get_agent_status(self, agent_id: str) -> Optional[AgentStatus]:
        """Get agent status"""
        return self.agent_statuses.get(agent_id)

    def update_shared_context(self, project_id: str, context: SharedContext):
        """Update shared context"""
        self.shared_contexts[project_id] = context

    def get_shared_context(self, project_id: str) -> Optional[SharedContext]:
        """Get shared context"""
        return self.shared_contexts.get(project_id)

    def add_conflict(self, conflict: Conflict):
        """Add conflict"""
        self.conflicts[conflict.project_id].append(conflict)

    def get_conflicts(self, project_id: str, resolved: Optional[bool] = None) -> List[Conflict]:
        """Get conflicts for a project"""
        project_conflicts = self.conflicts.get(project_id, [])
        if resolved is not None:
            return [c for c in project_conflicts if c.resolved == resolved]
        return project_conflicts

    def resolve_conflict(self, conflict_id: str, resolution: Dict[str, Any], resolved_by: str, reason: str):
        """Resolve a conflict"""
        for project_id, conflicts in self.conflicts.items():
            for conflict in conflicts:
                if conflict.id == conflict_id:
                    conflict.resolved = True
                    conflict.resolution = resolution
                    conflict.resolved_by = resolved_by
                    conflict.resolution_reason = reason
                    conflict.resolved_at = datetime.utcnow()
                    return True
        return False

    def add_dependency(self, project_id: str, dependency: TaskDependency):
        """Add task dependency"""
        self.dependencies[project_id].append(dependency)

    def get_dependencies(self, project_id: str) -> List[TaskDependency]:
        """Get dependencies for a project"""
        return self.dependencies.get(project_id, [])

    async def broadcast_to_websockets(self, project_id: str, data: Dict):
        """Broadcast data to all websocket connections for a project"""
        connections = self.websocket_connections.get(project_id, [])
        disconnected = []

        for ws in connections:
            try:
                await ws.send_json(data)
            except:
                disconnected.append(ws)

        # Remove disconnected websockets
        for ws in disconnected:
            self.websocket_connections[project_id].remove(ws)


# Global storage instance
storage = CollaborationStorage()


# ============================================================================
# MESSAGE BROKER
# ============================================================================

class AgentMessageBroker:
    """Message broker for agent communication"""

    def __init__(self, storage: CollaborationStorage):
        self.storage = storage

    async def send_message(self, message: AgentMessage) -> str:
        """
        Send message from one agent to another
        Returns message_id
        """
        # Store message
        self.storage.add_message(message)

        # Update sender's status
        sender_id = f"{message.project_id}:{message.from_agent.value}"
        sender_status = self.storage.get_agent_status(sender_id)
        if sender_status:
            sender_status.messages_sent += 1
            sender_status.last_activity = datetime.utcnow()
            self.storage.update_agent_status(sender_id, sender_status)

        # Update receiver's status if not broadcast
        if message.to_agent:
            receiver_id = f"{message.project_id}:{message.to_agent.value}"
            receiver_status = self.storage.get_agent_status(receiver_id)
            if receiver_status:
                receiver_status.messages_received += 1
                self.storage.update_agent_status(receiver_id, receiver_status)

        # Broadcast to websockets
        await self.storage.broadcast_to_websockets(message.project_id, {
            "type": "agent_message",
            "message": message.model_dump(mode='json')
        })

        return message.id

    async def broadcast_message(self, message: AgentMessage) -> str:
        """
        Send message to all agents
        Sets to_agent to None to indicate broadcast
        """
        message.to_agent = None
        return await self.send_message(message)

    async def acknowledge_message(self, message_id: str) -> bool:
        """Acknowledge receipt of a message"""
        for project_messages in self.storage.messages.values():
            for msg in project_messages:
                if msg.id == message_id:
                    msg.acknowledged = True
                    msg.ack_timestamp = datetime.utcnow()
                    return True
        return False

    async def get_unacknowledged_messages(self, project_id: str, timeout_seconds: int = 300) -> List[AgentMessage]:
        """Get messages that haven't been acknowledged within timeout"""
        cutoff_time = datetime.utcnow() - timedelta(seconds=timeout_seconds)
        project_messages = self.storage.get_messages(project_id)

        return [
            msg for msg in project_messages
            if msg.requires_ack and not msg.acknowledged and msg.timestamp < cutoff_time
        ]


# Global broker instance
broker = AgentMessageBroker(storage)


# ============================================================================
# SHARED CONTEXT MANAGER
# ============================================================================

class SharedContextManager:
    """Manages shared context between agents"""

    def __init__(self, storage: CollaborationStorage):
        self.storage = storage

    async def get_or_create_context(self, project_id: str) -> SharedContext:
        """Get existing context or create new one"""
        context = self.storage.get_shared_context(project_id)
        if not context:
            context = SharedContext(project_id=project_id)
            self.storage.update_shared_context(project_id, context)
        return context

    async def update_agent_output(self, project_id: str, agent: AgentType, output: Dict[str, Any]):
        """Update an agent's output in shared context"""
        context = await self.get_or_create_context(project_id)
        context.agent_outputs[agent.value] = output
        context.timestamp = datetime.utcnow()
        self.storage.update_shared_context(project_id, context)

        # Broadcast update
        await self.storage.broadcast_to_websockets(project_id, {
            "type": "context_update",
            "agent": agent.value,
            "timestamp": context.timestamp.isoformat()
        })

    async def add_decision(self, project_id: str, decision: Dict[str, Any]):
        """Add a decision to shared context"""
        context = await self.get_or_create_context(project_id)
        context.decisions.append({
            **decision,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.storage.update_shared_context(project_id, context)

    async def add_issue(self, project_id: str, issue: Dict[str, Any]):
        """Add an issue to shared context"""
        context = await self.get_or_create_context(project_id)
        context.active_issues.append({
            **issue,
            "id": str(uuid.uuid4()),
            "created_at": datetime.utcnow().isoformat(),
            "status": "open"
        })
        self.storage.update_shared_context(project_id, context)

    async def resolve_issue(self, project_id: str, issue_id: str, resolution: str):
        """Resolve an issue"""
        context = await self.get_or_create_context(project_id)
        for issue in context.active_issues:
            if issue.get("id") == issue_id:
                issue["status"] = "resolved"
                issue["resolution"] = resolution
                issue["resolved_at"] = datetime.utcnow().isoformat()
                break
        self.storage.update_shared_context(project_id, context)


# Global context manager
context_manager = SharedContextManager(storage)


# ============================================================================
# CONFLICT RESOLUTION
# ============================================================================

class ConflictResolver:
    """Handles conflicts between agents"""

    def __init__(self, storage: CollaborationStorage, broker: AgentMessageBroker):
        self.storage = storage
        self.broker = broker

    async def detect_conflict(self, project_id: str, agent_a: AgentType, agent_b: AgentType,
                            description: str, proposal_a: Dict, proposal_b: Dict) -> Conflict:
        """Detect and register a new conflict"""
        conflict = Conflict(
            project_id=project_id,
            agent_a=agent_a,
            agent_b=agent_b,
            description=description,
            agent_a_proposal=proposal_a,
            agent_b_proposal=proposal_b
        )

        self.storage.add_conflict(conflict)

        # Notify via message
        await self.broker.send_message(AgentMessage(
            from_agent=AgentType.PLANNER,  # System message
            to_agent=None,  # Broadcast
            message_type=MessageType.CONFLICT_DETECTED,
            priority=MessagePriority.HIGH,
            data={
                "conflict_id": conflict.id,
                "description": description,
                "agents": [agent_a.value, agent_b.value]
            },
            project_id=project_id
        ))

        return conflict

    async def resolve_conflict(self, conflict_id: str, resolution: Dict,
                              resolved_by: str, reason: str) -> bool:
        """Resolve a conflict"""
        success = self.storage.resolve_conflict(conflict_id, resolution, resolved_by, reason)

        if success:
            # Find the conflict to get project_id
            for project_id, conflicts in self.storage.conflicts.items():
                for conflict in conflicts:
                    if conflict.id == conflict_id and conflict.resolved:
                        # Notify agents
                        await self.broker.broadcast_message(AgentMessage(
                            from_agent=AgentType.PLANNER,
                            message_type=MessageType.TASK_COMPLETED,
                            priority=MessagePriority.HIGH,
                            data={
                                "conflict_id": conflict_id,
                                "resolution": resolution,
                                "resolved_by": resolved_by,
                                "reason": reason
                            },
                            project_id=project_id
                        ))
                        break

        return success


# Global conflict resolver
conflict_resolver = ConflictResolver(storage, broker)


# ============================================================================
# FASTAPI ENDPOINTS
# ============================================================================

@router.post("/messages/send")
async def send_message(message: AgentMessage):
    """Send a message from one agent to another"""
    try:
        message_id = await broker.send_message(message)
        return {
            "success": True,
            "message_id": message_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/messages/broadcast")
async def broadcast_message(message: AgentMessage):
    """Broadcast a message to all agents"""
    try:
        message_id = await broker.broadcast_message(message)
        return {
            "success": True,
            "message_id": message_id,
            "broadcast": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/messages/{project_id}")
async def get_messages(project_id: str, agent: Optional[AgentType] = None):
    """Get messages for a project, optionally filtered by agent"""
    messages = storage.get_messages(project_id, agent)
    return {
        "project_id": project_id,
        "agent": agent.value if agent else "all",
        "total": len(messages),
        "messages": [msg.model_dump(mode='json') for msg in messages]
    }


@router.post("/messages/{message_id}/acknowledge")
async def acknowledge_message(message_id: str):
    """Acknowledge receipt of a message"""
    success = await broker.acknowledge_message(message_id)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"success": True, "message_id": message_id}


@router.get("/context/{project_id}")
async def get_shared_context(project_id: str):
    """Get shared context for a project"""
    context = await context_manager.get_or_create_context(project_id)
    return context.model_dump(mode='json')


@router.put("/context/{project_id}/agent-output")
async def update_agent_output(project_id: str, agent: AgentType, output: Dict[str, Any]):
    """Update an agent's output in shared context"""
    await context_manager.update_agent_output(project_id, agent, output)
    return {"success": True, "agent": agent.value, "project_id": project_id}


@router.post("/context/{project_id}/decision")
async def add_decision(project_id: str, decision: Dict[str, Any]):
    """Add a decision to shared context"""
    await context_manager.add_decision(project_id, decision)
    return {"success": True, "project_id": project_id}


@router.post("/context/{project_id}/issue")
async def add_issue(project_id: str, issue: Dict[str, Any]):
    """Add an issue to shared context"""
    await context_manager.add_issue(project_id, issue)
    return {"success": True, "project_id": project_id}


@router.post("/context/{project_id}/issue/{issue_id}/resolve")
async def resolve_issue(project_id: str, issue_id: str, resolution: str):
    """Resolve an issue"""
    await context_manager.resolve_issue(project_id, issue_id, resolution)
    return {"success": True, "issue_id": issue_id}


@router.get("/conflicts/{project_id}")
async def get_conflicts(project_id: str, resolved: Optional[bool] = None):
    """Get conflicts for a project"""
    conflicts = storage.get_conflicts(project_id, resolved)
    return {
        "project_id": project_id,
        "total": len(conflicts),
        "conflicts": [c.model_dump(mode='json') for c in conflicts]
    }


@router.post("/conflicts/detect")
async def detect_conflict(
    project_id: str,
    agent_a: AgentType,
    agent_b: AgentType,
    description: str,
    proposal_a: Dict[str, Any],
    proposal_b: Dict[str, Any]
):
    """Detect and register a new conflict"""
    conflict = await conflict_resolver.detect_conflict(
        project_id, agent_a, agent_b, description, proposal_a, proposal_b
    )
    return conflict.model_dump(mode='json')


@router.post("/conflicts/{conflict_id}/resolve")
async def resolve_conflict_endpoint(
    conflict_id: str,
    resolution: Dict[str, Any],
    resolved_by: str,
    reason: str
):
    """Resolve a conflict"""
    success = await conflict_resolver.resolve_conflict(conflict_id, resolution, resolved_by, reason)
    if not success:
        raise HTTPException(status_code=404, detail="Conflict not found")
    return {"success": True, "conflict_id": conflict_id}


@router.post("/agents/{project_id}/register")
async def register_agent(project_id: str, agent_type: AgentType):
    """Register an agent for a project"""
    agent_id = f"{project_id}:{agent_type.value}"
    status = AgentStatus(
        agent_id=agent_id,
        agent_type=agent_type,
        status="idle"
    )
    storage.update_agent_status(agent_id, status)
    return status.model_dump(mode='json')


@router.get("/agents/{project_id}/status")
async def get_agents_status(project_id: str):
    """Get status of all agents for a project"""
    all_statuses = []
    for agent_id, status in storage.agent_statuses.items():
        if agent_id.startswith(f"{project_id}:"):
            all_statuses.append(status.model_dump(mode='json'))
    return {
        "project_id": project_id,
        "total_agents": len(all_statuses),
        "agents": all_statuses
    }


@router.put("/agents/{project_id}/{agent_type}/status")
async def update_agent_status_endpoint(
    project_id: str,
    agent_type: AgentType,
    status: str,
    current_task: Optional[str] = None
):
    """Update agent status"""
    agent_id = f"{project_id}:{agent_type.value}"
    agent_status = storage.get_agent_status(agent_id)

    if not agent_status:
        agent_status = AgentStatus(
            agent_id=agent_id,
            agent_type=agent_type,
            status=status,
            current_task=current_task
        )
    else:
        agent_status.status = status
        agent_status.current_task = current_task
        agent_status.last_activity = datetime.utcnow()

    storage.update_agent_status(agent_id, agent_status)
    return agent_status.model_dump(mode='json')


@router.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    """WebSocket endpoint for real-time collaboration updates"""
    await websocket.accept()
    storage.websocket_connections[project_id].append(websocket)

    try:
        while True:
            # Keep connection alive and handle incoming messages if needed
            data = await websocket.receive_text()
            # Echo back or process as needed
            await websocket.send_json({"type": "pong", "data": data})
    except WebSocketDisconnect:
        storage.websocket_connections[project_id].remove(websocket)


@router.get("/health")
async def collaboration_health():
    """Health check for collaboration system"""
    return {
        "status": "healthy",
        "total_projects": len(storage.messages),
        "total_messages": sum(len(msgs) for msgs in storage.messages.values()),
        "active_agents": len(storage.agent_statuses),
        "active_conflicts": sum(
            len([c for c in conflicts if not c.resolved])
            for conflicts in storage.conflicts.values()
        ),
        "websocket_connections": sum(len(conns) for conns in storage.websocket_connections.values())
    }
