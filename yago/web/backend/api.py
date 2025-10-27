"""
YAGO Web Dashboard - FastAPI Backend
Provides REST API and WebSocket for web UI
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import json
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from agents.yago_agents import YagoAgents
from tasks.yago_tasks import YagoTasks
from utils.template_loader import get_template_loader
from utils.report_generator import get_report_generator, reset_report_generator
from utils.token_tracker import get_tracker, reset_tracker
from utils.interactive_chat import reset_interactive_chat, get_interactive_chat
from utils.auto_debug import reset_auto_debugger, get_auto_debugger


app = FastAPI(
    title="YAGO Web Dashboard API",
    description="API for YAGO Multi-AI Code Generator",
    version="3.5.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Data Models
# ============================================================================

class ProjectRequest(BaseModel):
    """Request to create a new project"""
    idea: str
    mode: str = "minimal"  # minimal or full
    template: Optional[str] = None
    interactive: bool = False
    auto_debug: bool = True


class ProjectResponse(BaseModel):
    """Response for project creation"""
    project_id: str
    status: str
    message: str


class TemplateInfo(BaseModel):
    """Template information"""
    name: str
    category: str
    description: str
    project_idea: str


class SystemStatus(BaseModel):
    """System status information"""
    status: str
    active_projects: int
    total_projects_completed: int
    uptime: str


class ChatMessage(BaseModel):
    """Chat message for interactive mode"""
    project_id: str
    message: str


# ============================================================================
# In-Memory State (In production, use Redis or Database)
# ============================================================================

class ProjectState:
    def __init__(self):
        self.active_projects = {}  # project_id -> project_info
        self.project_counter = 0
        self.websocket_connections = {}  # project_id -> WebSocket
        self.start_time = datetime.now()

    def create_project(self, request: ProjectRequest) -> str:
        """Create a new project and return ID"""
        self.project_counter += 1
        project_id = f"yago_{self.project_counter}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.active_projects[project_id] = {
            "id": project_id,
            "request": request.dict(),
            "status": "queued",
            "created_at": datetime.now().isoformat(),
            "progress": 0,
            "current_step": "Initializing...",
            "logs": [],
            "result": None,
        }

        return project_id

    def get_project(self, project_id: str) -> Optional[Dict]:
        """Get project info"""
        return self.active_projects.get(project_id)

    def update_project(self, project_id: str, updates: Dict):
        """Update project state"""
        if project_id in self.active_projects:
            self.active_projects[project_id].update(updates)

    def add_log(self, project_id: str, log: str):
        """Add log entry to project"""
        if project_id in self.active_projects:
            self.active_projects[project_id]["logs"].append({
                "timestamp": datetime.now().isoformat(),
                "message": log
            })


state = ProjectState()


# ============================================================================
# REST API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """API root"""
    return {
        "name": "YAGO Web Dashboard API",
        "version": "3.5.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/api/status", response_model=SystemStatus)
async def get_status():
    """Get system status"""
    uptime = datetime.now() - state.start_time
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)

    return SystemStatus(
        status="running",
        active_projects=len([p for p in state.active_projects.values() if p["status"] == "running"]),
        total_projects_completed=len([p for p in state.active_projects.values() if p["status"] == "completed"]),
        uptime=f"{hours}h {minutes}m {seconds}s"
    )


@app.get("/api/templates", response_model=List[TemplateInfo])
async def get_templates():
    """Get all available templates"""
    loader = get_template_loader()
    templates = []

    for category in loader.templates_dir.iterdir():
        if category.is_dir() and not category.name.startswith("."):
            for template_file in category.glob("*.yaml"):
                template_data = loader.get_template(template_file.stem)
                templates.append(TemplateInfo(
                    name=template_file.stem,
                    category=category.name,
                    description=template_data.get("description", ""),
                    project_idea=template_data.get("project_idea", "")
                ))

    return templates


@app.post("/api/projects", response_model=ProjectResponse)
async def create_project(request: ProjectRequest, background_tasks: BackgroundTasks):
    """Create a new YAGO project"""
    try:
        # Create project
        project_id = state.create_project(request)

        # Start execution in background
        background_tasks.add_task(execute_project, project_id)

        return ProjectResponse(
            project_id=project_id,
            status="queued",
            message=f"Project {project_id} created and queued for execution"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    """Get project details"""
    project = state.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


@app.get("/api/projects")
async def list_projects():
    """List all projects"""
    return {
        "projects": list(state.active_projects.values()),
        "total": len(state.active_projects)
    }


@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete a project"""
    if project_id not in state.active_projects:
        raise HTTPException(status_code=404, detail="Project not found")

    project = state.active_projects[project_id]
    if project["status"] == "running":
        raise HTTPException(status_code=400, detail="Cannot delete running project")

    del state.active_projects[project_id]

    return {"message": f"Project {project_id} deleted"}


# ============================================================================
# WebSocket Endpoint
# ============================================================================

@app.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    """WebSocket for real-time project updates"""
    await websocket.accept()
    state.websocket_connections[project_id] = websocket

    try:
        # Send initial project state
        project = state.get_project(project_id)
        if project:
            await websocket.send_json({
                "type": "project_state",
                "data": project
            })

        # Keep connection alive and listen for messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle interactive chat messages
            if message.get("type") == "chat_response":
                # Store response for interactive mode
                # This would be handled by interactive_chat module
                pass

            await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        if project_id in state.websocket_connections:
            del state.websocket_connections[project_id]


async def send_websocket_update(project_id: str, update: Dict):
    """Send update to connected WebSocket client"""
    if project_id in state.websocket_connections:
        try:
            await state.websocket_connections[project_id].send_json({
                "type": "update",
                "data": update
            })
        except:
            # Connection closed
            if project_id in state.websocket_connections:
                del state.websocket_connections[project_id]


# ============================================================================
# Background Tasks
# ============================================================================

async def execute_project(project_id: str):
    """Execute YAGO project in background"""
    project = state.get_project(project_id)
    if not project:
        return

    request = ProjectRequest(**project["request"])

    try:
        # Update status
        state.update_project(project_id, {
            "status": "running",
            "progress": 5,
            "current_step": "Initializing YAGO..."
        })
        await send_websocket_update(project_id, state.get_project(project_id))

        # Reset utilities
        reset_tracker()
        reset_report_generator()
        reset_auto_debugger()
        if request.interactive:
            reset_interactive_chat(enabled=True)

        # Create agents and tasks
        state.update_project(project_id, {
            "progress": 10,
            "current_step": "Creating AI agents..."
        })
        await send_websocket_update(project_id, state.get_project(project_id))

        agents = YagoAgents(
            interactive_mode=request.interactive,
            auto_debug=request.auto_debug
        )
        tasks = YagoTasks()

        # Apply template if specified
        idea = request.idea
        if request.template:
            loader = get_template_loader()
            template_data = loader.apply_template(request.template, request.idea)
            idea = template_data["project_idea"]

        # Execute based on mode
        state.update_project(project_id, {
            "progress": 20,
            "current_step": f"Running {request.mode} mode..."
        })
        await send_websocket_update(project_id, state.get_project(project_id))

        # This is a simplified version - in production, integrate with actual YAGO execution
        # and capture real-time progress

        from crewai import Crew, Process

        planner = agents.planner()
        coder = agents.coder()

        task_plan = tasks.planning_task(planner, idea)
        task_code = tasks.coding_task(coder)

        crew = Crew(
            agents=[planner, coder],
            tasks=[task_plan, task_code],
            process=Process.sequential,
            verbose=True
        )

        # Execute
        result = crew.kickoff()

        # Success
        state.update_project(project_id, {
            "status": "completed",
            "progress": 100,
            "current_step": "Done!",
            "result": str(result)
        })
        await send_websocket_update(project_id, state.get_project(project_id))

    except Exception as e:
        # Error
        state.update_project(project_id, {
            "status": "failed",
            "progress": 0,
            "current_step": f"Error: {str(e)}",
            "result": None
        })
        await send_websocket_update(project_id, state.get_project(project_id))


# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("🌐 Starting YAGO Web Dashboard API...")
    print("📍 API: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
