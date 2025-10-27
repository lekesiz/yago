"""
YAGO v7.1 - Web UI Backend for Clarification Phase
FastAPI endpoints for interactive web-based clarification
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
import asyncio
import json
from enum import Enum

# Redis for session management (will be replaced with actual Redis)
# For now, using in-memory dict
SESSIONS: Dict[str, Dict] = {}


class QuestionType(str, Enum):
    TEXT = "text"
    SELECT = "select"
    MULTISELECT = "multiselect"
    CHECKBOX = "checkbox"
    SLIDER = "slider"


class QuestionCategory(str, Enum):
    BASIC = "basic"
    TECHNICAL = "technical"
    INFRASTRUCTURE = "infrastructure"
    SECURITY = "security"
    QUALITY = "quality"


class QuestionUI(BaseModel):
    """Question model for UI"""
    id: str
    text: str
    category: QuestionCategory
    type: QuestionType
    options: Optional[List[str]] = None
    placeholder: str = ""
    required: bool = True
    hint: Optional[str] = None
    example: Optional[str] = None
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    default: Optional[Any] = None


class StartClarificationRequest(BaseModel):
    """Request to start clarification session"""
    project_idea: str = Field(..., min_length=10, max_length=5000)
    depth: str = Field(default="standard", pattern="^(minimal|standard|full)$")
    user_id: Optional[str] = None


class AnswerRequest(BaseModel):
    """Request to submit an answer"""
    answer: Any
    skip: bool = False


class DraftUpdate(BaseModel):
    """Update draft answers"""
    answers: Dict[str, Any]


class ClarificationProgress(BaseModel):
    """Progress tracking"""
    answered: int
    total: int
    percentage: float
    category_progress: Dict[str, str]
    estimated_time_remaining: int  # minutes


class ClarificationResponse(BaseModel):
    """API response for clarification state"""
    session_id: str
    current_question: Optional[QuestionUI]
    progress: ClarificationProgress
    can_skip: bool
    can_finish_early: bool
    next_available: bool
    previous_available: bool


# FastAPI app
app = FastAPI(
    title="YAGO Clarification API",
    description="Web UI backend for YAGO v7.1 Clarification Phase",
    version="7.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React/Vite dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_progress(self, session_id: str, progress: Dict):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json({
                "type": "progress_update",
                "data": progress
            })

    async def send_notification(self, session_id: str, message: str, level: str = "info"):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json({
                "type": "notification",
                "message": message,
                "level": level,
                "timestamp": datetime.now().isoformat()
            })


manager = ConnectionManager()


def generate_mock_questions(project_idea: str, depth: str) -> List[QuestionUI]:
    """Generate questions based on project idea (mock implementation)"""

    # Basic questions (always included)
    questions = [
        QuestionUI(
            id="q1",
            text="What programming language do you prefer?",
            category=QuestionCategory.BASIC,
            type=QuestionType.SELECT,
            options=["Python", "JavaScript", "TypeScript", "Go", "Java", "Other"],
            placeholder="Select language",
            required=True,
            hint="Primary language for backend development",
            default="Python"
        ),
        QuestionUI(
            id="q2",
            text="Frontend framework?",
            category=QuestionCategory.BASIC,
            type=QuestionType.SELECT,
            options=["React", "Vue", "Next.js", "Angular", "Svelte", "None"],
            placeholder="Select framework",
            required=False,
            hint="Leave as 'None' for backend-only projects",
            default="None"
        ),
        QuestionUI(
            id="q3",
            text="Backend framework?",
            category=QuestionCategory.TECHNICAL,
            type=QuestionType.SELECT,
            options=["FastAPI", "Django", "Express", "Flask", "Spring Boot", "Other"],
            placeholder="Select framework",
            required=True,
            hint="Framework for API/server development"
        ),
        QuestionUI(
            id="q4",
            text="Which database?",
            category=QuestionCategory.TECHNICAL,
            type=QuestionType.SELECT,
            options=["PostgreSQL", "MongoDB", "MySQL", "SQLite", "Redis", "None"],
            placeholder="Select database",
            required=True,
            hint="Primary data storage"
        ),
    ]

    # API-specific questions
    if any(kw in project_idea.lower() for kw in ["api", "rest", "graphql", "endpoint"]):
        questions.extend([
            QuestionUI(
                id="q5",
                text="API style?",
                category=QuestionCategory.TECHNICAL,
                type=QuestionType.SELECT,
                options=["REST", "GraphQL", "gRPC", "WebSocket"],
                placeholder="Select API style",
                required=True,
                hint="API architecture pattern"
            ),
            QuestionUI(
                id="q6",
                text="Authentication method?",
                category=QuestionCategory.SECURITY,
                type=QuestionType.SELECT,
                options=["JWT", "OAuth2", "Session-based", "API Keys", "None"],
                placeholder="Select auth method",
                required=True,
                hint="User authentication strategy"
            ),
            QuestionUI(
                id="q7",
                text="API documentation tool?",
                category=QuestionCategory.TECHNICAL,
                type=QuestionType.SELECT,
                options=["Swagger/OpenAPI", "GraphQL Playground", "Postman", "None"],
                placeholder="Select documentation tool",
                required=False,
                default="Swagger/OpenAPI"
            ),
        ])

    # Infrastructure questions
    if depth in ["standard", "full"]:
        questions.extend([
            QuestionUI(
                id="q8",
                text="Deployment target?",
                category=QuestionCategory.INFRASTRUCTURE,
                type=QuestionType.SELECT,
                options=["Docker", "Kubernetes", "AWS", "Vercel", "Heroku", "Local"],
                placeholder="Select deployment",
                required=True,
                hint="Where will the app be deployed?"
            ),
            QuestionUI(
                id="q9",
                text="Containerization?",
                category=QuestionCategory.INFRASTRUCTURE,
                type=QuestionType.CHECKBOX,
                required=False,
                hint="Use Docker for containerization?",
                default=True
            ),
            QuestionUI(
                id="q10",
                text="CI/CD pipeline?",
                category=QuestionCategory.INFRASTRUCTURE,
                type=QuestionType.SELECT,
                options=["GitHub Actions", "GitLab CI", "Jenkins", "CircleCI", "None"],
                placeholder="Select CI/CD",
                required=False,
                default="GitHub Actions"
            ),
        ])

    # Quality questions
    if depth == "full":
        questions.extend([
            QuestionUI(
                id="q11",
                text="Test coverage target?",
                category=QuestionCategory.QUALITY,
                type=QuestionType.SLIDER,
                min_value=60,
                max_value=100,
                required=True,
                hint="Minimum test coverage percentage",
                default=80
            ),
            QuestionUI(
                id="q12",
                text="Code quality tools?",
                category=QuestionCategory.QUALITY,
                type=QuestionType.MULTISELECT,
                options=["pylint", "black", "mypy", "ruff", "None"],
                placeholder="Select tools",
                required=False,
                hint="Select all that apply"
            ),
            QuestionUI(
                id="q13",
                text="Documentation level?",
                category=QuestionCategory.QUALITY,
                type=QuestionType.SELECT,
                options=["Minimal", "Standard", "Comprehensive"],
                placeholder="Select level",
                required=True,
                default="Standard"
            ),
        ])

    return questions


@app.post("/api/v1/clarifications/start", response_model=ClarificationResponse)
async def start_clarification(request: StartClarificationRequest):
    """
    Start a new clarification session

    Returns session_id and first question
    """
    # Generate session
    session_id = str(uuid.uuid4())

    # Generate questions
    questions = generate_mock_questions(request.project_idea, request.depth)

    # Initialize session
    session = {
        "session_id": session_id,
        "project_idea": request.project_idea,
        "depth": request.depth,
        "user_id": request.user_id,
        "questions": [q.model_dump() for q in questions],
        "answers": {},
        "current_index": 0,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "status": "active"
    }

    SESSIONS[session_id] = session

    # Calculate progress
    progress = ClarificationProgress(
        answered=0,
        total=len(questions),
        percentage=0.0,
        category_progress={
            cat.value: f"0/{len([q for q in questions if q.category == cat])}"
            for cat in QuestionCategory
        },
        estimated_time_remaining=len(questions) * 0.5  # 30 seconds per question
    )

    return ClarificationResponse(
        session_id=session_id,
        current_question=questions[0] if questions else None,
        progress=progress,
        can_skip=not questions[0].required if questions else False,
        can_finish_early=False,
        next_available=len(questions) > 1,
        previous_available=False
    )


@app.get("/api/v1/clarifications/{session_id}", response_model=ClarificationResponse)
async def get_clarification(session_id: str):
    """Get current clarification state"""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")

    session = SESSIONS[session_id]
    questions = [QuestionUI(**q) for q in session["questions"]]
    current_idx = session["current_index"]

    if current_idx >= len(questions):
        current_question = None
    else:
        current_question = questions[current_idx]

    # Calculate progress
    answered = len(session["answers"])
    total = len(questions)

    category_progress = {}
    for cat in QuestionCategory:
        cat_questions = [q for q in questions if q.category == cat]
        cat_answered = len([
            q for q in cat_questions
            if q.id in session["answers"]
        ])
        category_progress[cat.value] = f"{cat_answered}/{len(cat_questions)}"

    progress = ClarificationProgress(
        answered=answered,
        total=total,
        percentage=(answered / total * 100) if total > 0 else 0,
        category_progress=category_progress,
        estimated_time_remaining=max(0, (total - answered) * 0.5)
    )

    return ClarificationResponse(
        session_id=session_id,
        current_question=current_question,
        progress=progress,
        can_skip=not current_question.required if current_question else False,
        can_finish_early=answered >= total * 0.8,  # 80% answered
        next_available=current_idx < total - 1,
        previous_available=current_idx > 0
    )


@app.post("/api/v1/clarifications/{session_id}/answer")
async def submit_answer(session_id: str, request: AnswerRequest):
    """Submit answer for current question"""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")

    session = SESSIONS[session_id]
    questions = [QuestionUI(**q) for q in session["questions"]]
    current_idx = session["current_index"]

    if current_idx >= len(questions):
        raise HTTPException(status_code=400, detail="No more questions")

    current_question = questions[current_idx]

    # Validate answer if not skipping
    if not request.skip:
        if current_question.required and not request.answer:
            raise HTTPException(status_code=400, detail="Answer required")

        # Store answer
        session["answers"][current_question.id] = request.answer

    # Move to next question
    session["current_index"] = current_idx + 1
    session["updated_at"] = datetime.now().isoformat()

    # Send real-time update via WebSocket
    await manager.send_progress(session_id, {
        "answered": len(session["answers"]),
        "total": len(questions)
    })

    # Return updated state
    return await get_clarification(session_id)


@app.put("/api/v1/clarifications/{session_id}/draft")
async def update_draft(session_id: str, draft: DraftUpdate):
    """Update draft answers (auto-save)"""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")

    session = SESSIONS[session_id]
    session["draft_answers"] = draft.answers
    session["updated_at"] = datetime.now().isoformat()

    return {"status": "saved", "timestamp": session["updated_at"]}


@app.get("/api/v1/clarifications/{session_id}/progress")
async def get_progress(session_id: str):
    """Get just progress info"""
    response = await get_clarification(session_id)
    return response.progress


@app.post("/api/v1/clarifications/{session_id}/complete")
async def complete_clarification(session_id: str):
    """Mark clarification as complete and generate brief"""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")

    session = SESSIONS[session_id]
    session["status"] = "completed"
    session["completed_at"] = datetime.now().isoformat()

    # Generate brief (simplified)
    brief = {
        "session_id": session_id,
        "project_idea": session["project_idea"],
        "answers": session["answers"],
        "completed_at": session["completed_at"],
        "question_count": len(session["questions"]),
        "answer_count": len(session["answers"])
    }

    return {
        "status": "completed",
        "brief": brief,
        "message": "Clarification completed successfully!"
    }


@app.post("/api/v1/clarifications/{session_id}/navigate/{direction}")
async def navigate(session_id: str, direction: str):
    """Navigate to next/previous question"""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")

    if direction not in ["next", "previous"]:
        raise HTTPException(status_code=400, detail="Invalid direction")

    session = SESSIONS[session_id]
    questions = session["questions"]
    current_idx = session["current_index"]

    if direction == "next" and current_idx < len(questions) - 1:
        session["current_index"] = current_idx + 1
    elif direction == "previous" and current_idx > 0:
        session["current_index"] = current_idx - 1
    else:
        raise HTTPException(status_code=400, detail="Cannot navigate in that direction")

    session["updated_at"] = datetime.now().isoformat()

    return await get_clarification(session_id)


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket for real-time updates"""
    await manager.connect(websocket, session_id)

    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle different message types
            if message["type"] == "ping":
                await websocket.send_json({"type": "pong"})

            elif message["type"] == "get_progress":
                if session_id in SESSIONS:
                    session = SESSIONS[session_id]
                    await websocket.send_json({
                        "type": "progress",
                        "data": {
                            "answered": len(session["answers"]),
                            "total": len(session["questions"])
                        }
                    })

    except WebSocketDisconnect:
        manager.disconnect(session_id)


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "7.1.0",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(SESSIONS)
    }


@app.get("/api/v1/sessions")
async def list_sessions():
    """List all active sessions (for debugging)"""
    return {
        "sessions": [
            {
                "session_id": sid,
                "status": s["status"],
                "progress": f"{len(s['answers'])}/{len(s['questions'])}",
                "created_at": s["created_at"]
            }
            for sid, s in SESSIONS.items()
        ]
    }


# Include template router
try:
    from template_api import router as template_router
    app.include_router(template_router)
    print("✅ Template API routes loaded")
except Exception as e:
    print(f"⚠️  Template API routes not loaded: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
