from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
import uvicorn
import uuid
import json
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import database
try:
    from .database import get_db, engine, Base
    from . import models
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from database import get_db, engine, Base
    import models

# Import AI services (relative import)
try:
    from .ai_clarification_service import get_ai_clarification_service
    from .ai_code_executor import get_code_executor
except ImportError:
    # If relative import fails, try direct import
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from ai_clarification_service import get_ai_clarification_service
    from ai_code_executor import get_code_executor

app = FastAPI(
    title="YAGO v8.0 API",
    description="Yet Another Genius Orchestrator - Enterprise AI Platform",
    version="8.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data stores
templates_db = [
    {
        "id": "web_app",
        "name": "Web Application",
        "description": "Full-stack web application with modern frontend and backend",
        "category": "web",
        "difficulty": "intermediate",
        "is_popular": True,
        "popular": True,
        "icon": "🌐",
        "tags": ["react", "nodejs", "database"],
        "estimated_time": "2-3 weeks",
        "estimated_duration": "2-3 weeks",
        "estimated_cost": 15.50,
        "file": "web_app_template.yaml"
    },
    {
        "id": "api_service",
        "name": "REST API Service",
        "description": "RESTful API backend with authentication and database",
        "category": "backend",
        "difficulty": "beginner",
        "is_popular": True,
        "popular": True,
        "icon": "🔌",
        "tags": ["api", "fastapi", "postgresql"],
        "estimated_time": "1 week",
        "estimated_duration": "1 week",
        "estimated_cost": 8.75,
        "file": "api_service_template.yaml"
    },
    {
        "id": "mobile_app",
        "name": "Mobile Application",
        "description": "Cross-platform mobile app with React Native",
        "category": "mobile",
        "difficulty": "advanced",
        "is_popular": True,
        "popular": True,
        "icon": "📱",
        "tags": ["react-native", "mobile", "ios", "android"],
        "estimated_time": "4-6 weeks",
        "estimated_duration": "4-6 weeks",
        "estimated_cost": 32.00,
        "file": "mobile_app_template.yaml"
    },
    {
        "id": "data_pipeline",
        "name": "Data Pipeline",
        "description": "ETL pipeline for data processing and analytics",
        "category": "data",
        "difficulty": "intermediate",
        "is_popular": False,
        "popular": False,
        "icon": "📊",
        "tags": ["python", "etl", "data-engineering"],
        "estimated_time": "2 weeks",
        "estimated_duration": "2 weeks",
        "estimated_cost": 12.25,
        "file": "data_pipeline_template.yaml"
    }
]

categories_db = [
    {"id": "web", "name": "Web Development", "count": 12},
    {"id": "backend", "name": "Backend Services", "count": 8},
    {"id": "mobile", "name": "Mobile Apps", "count": 5},
    {"id": "data", "name": "Data Engineering", "count": 6}
]

# Root endpoints
@app.get("/")
async def root():
    return {"message": "YAGO v8.0 API", "status": "running", "version": "8.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Template endpoints
@app.get("/api/v1/templates/")
async def get_templates(category: Optional[str] = None, difficulty: Optional[str] = None, popular_only: Optional[bool] = None):
    """Get all templates with optional filters"""
    filtered = templates_db

    if category:
        filtered = [t for t in filtered if t.get("category") == category]
    if difficulty:
        filtered = [t for t in filtered if t.get("difficulty") == difficulty]
    if popular_only:
        filtered = [t for t in filtered if t.get("is_popular")]

    return {"templates": filtered, "total": len(filtered)}

@app.get("/api/v1/templates/categories")
async def get_categories():
    """Get template categories"""
    return categories_db

@app.get("/api/v1/templates/popular")
async def get_popular_templates():
    """Get popular templates only"""
    return [t for t in templates_db if t.get("is_popular")]

@app.get("/api/v1/templates/{template_id}")
async def get_template(template_id: str):
    """Get detailed template information"""
    template = next((t for t in templates_db if t["id"] == template_id), None)
    if template:
        return {**template, "details": {
            "prerequisites": ["Basic programming knowledge"],
            "features": ["Modern architecture", "Best practices", "Documentation"],
            "tech_stack": template.get("tags", [])
        }}
    return {"error": "Template not found"}

@app.get("/api/v1/templates/{template_id}/preview")
async def get_template_preview(template_id: str):
    """Get template preview"""
    template = next((t for t in templates_db if t["id"] == template_id), None)
    if template:
        return {
            "template_id": template_id,
            "preview": {
                "structure": ["src/", "tests/", "docs/", "config/"],
                "files": ["README.md", "package.json", ".gitignore"],
                "commands": ["npm install", "npm start", "npm test"]
            }
        }
    return {"error": "Template not found"}

@app.post("/api/v1/templates/{template_id}/apply")
async def apply_template(template_id: str, customizations: Optional[Dict] = None):
    """Apply template to create new project"""
    return {
        "project_id": str(uuid.uuid4()),
        "template_id": template_id,
        "status": "created",
        "message": "Template applied successfully"
    }

@app.get("/api/v1/templates/search")
async def search_templates(q: str):
    """Search templates"""
    query_lower = q.lower()
    results = [
        t for t in templates_db
        if query_lower in t["name"].lower() or
           query_lower in t["description"].lower() or
           any(query_lower in tag for tag in t.get("tags", []))
    ]
    return results

@app.get("/api/v1/templates/health")
async def templates_health():
    """Health check for template system"""
    return {"status": "healthy", "templates_count": len(templates_db)}

# Clarification endpoints - MIGRATED TO DATABASE
# sessions_db: Dict[str, Dict] = {}  # Old in-memory storage

@app.post("/api/v1/clarifications/start")
async def start_clarification(request: Dict, db: Session = Depends(get_db)):
    """Start a new clarification session with AI-generated questions in database"""
    session_id = str(uuid.uuid4())
    project_idea = request.get("project_idea")
    depth = request.get("depth", "standard")

    print(f"🚀 Starting AI clarification session: {session_id}")
    print(f"   Project: {project_idea[:100]}...")
    print(f"   Depth: {depth}")

    # Get AI service
    ai_service = get_ai_clarification_service()

    # Generate questions using AI based on project idea and depth
    try:
        questions = ai_service.generate_questions(
            project_idea=project_idea,
            depth=depth,
            previous_answers=None
        )
        print(f"✅ Generated {len(questions)} AI-powered questions")
    except Exception as e:
        print(f"❌ AI generation failed: {e}")
        # Fallback to basic questions
        questions = ai_service._get_fallback_questions(
            10 if depth == "minimal" else 20 if depth == "standard" else 40
        )
        print(f"⚠️ Using fallback questions: {len(questions)}")

    # Create clarification session in database
    session = models.ClarificationSession(
        id=session_id,
        project_idea=project_idea,
        depth=depth,
        current_question=0,
        questions=json.dumps(questions),
        answers=json.dumps({}),
        total_questions=len(questions),
        is_completed=False,
        project_id=None  # Will be set when project is created
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    # Return in the format frontend expects
    return {
        "session_id": session_id,
        "current_question": questions[0],
        "progress": {
            "answered": 0,
            "total": len(questions),
            "percentage": 0.0,
            "category_progress": {"basic": "0/2", "technical": "0/2", "quality": "0/1"},
            "estimated_time_remaining": len(questions) * 2
        },
        "can_skip": not questions[0]["required"],
        "can_finish_early": False,
        "next_available": len(questions) > 1,
        "previous_available": False
    }

@app.get("/api/v1/clarifications/{session_id}")
async def get_clarification_session(session_id: str, db: Session = Depends(get_db)):
    """Get clarification session details from database"""
    session = db.query(models.ClarificationSession).filter(
        models.ClarificationSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return session.to_dict()

@app.post("/api/v1/clarifications/{session_id}/answer")
async def submit_answer(session_id: str, request: Dict, db: Session = Depends(get_db)):
    """Submit an answer to clarification question in database"""
    session = db.query(models.ClarificationSession).filter(
        models.ClarificationSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Parse JSON fields
    questions = json.loads(session.questions) if isinstance(session.questions, str) else session.questions
    answers = json.loads(session.answers) if isinstance(session.answers, str) else session.answers or {}

    current_idx = session.current_question
    answer_value = request.get("answer")
    skip = request.get("skip", False)

    # Save answer if not skipping
    if not skip and current_idx < len(questions):
        current_q = questions[current_idx]
        answers[current_q["id"]] = answer_value

    # Move to next question
    session.current_question = min(current_idx + 1, len(questions))
    new_idx = session.current_question

    # Update answers in database
    session.answers = json.dumps(answers)
    session.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(session)

    # Calculate progress
    answered = len(answers)
    total = len(questions)

    # Get current question
    current_question = questions[new_idx] if new_idx < len(questions) else None

    # Return in the format frontend expects
    return {
        "session_id": session_id,
        "current_question": current_question,
        "progress": {
            "answered": answered,
            "total": total,
            "percentage": (answered / total * 100) if total > 0 else 0,
            "category_progress": {"basic": f"{answered}/2", "technical": "0/2", "quality": "0/1"},
            "estimated_time_remaining": max(0, (total - answered) * 2)
        },
        "can_skip": not current_question["required"] if current_question else False,
        "can_finish_early": answered >= int(total * 0.8),
        "next_available": new_idx < total - 1,
        "previous_available": new_idx > 0
    }

@app.get("/api/v1/clarifications/{session_id}/progress")
async def get_progress(session_id: str, db: Session = Depends(get_db)):
    """Get session progress from database"""
    session = db.query(models.ClarificationSession).filter(
        models.ClarificationSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    answers = json.loads(session.answers) if isinstance(session.answers, str) else session.answers or {}
    total_questions = session.total_questions
    answered = len(answers)

    return {
        "session_id": session_id,
        "answered": answered,
        "total": total_questions,
        "percentage": (answered / total_questions) * 100 if total_questions > 0 else 0
    }

@app.post("/api/v1/clarifications/{session_id}/complete")
async def complete_clarification(session_id: str, db: Session = Depends(get_db)):
    """Complete clarification session with AI-generated comprehensive brief in database"""
    session = db.query(models.ClarificationSession).filter(
        models.ClarificationSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Parse JSON fields
    answers = json.loads(session.answers) if isinstance(session.answers, str) else session.answers or {}
    questions = json.loads(session.questions) if isinstance(session.questions, str) else session.questions

    print(f"📝 Generating comprehensive brief for session: {session_id}")
    print(f"   Answered: {len(answers)}/{session.total_questions} questions")

    # Get AI service
    ai_service = get_ai_clarification_service()

    # Generate comprehensive brief using GPT-4
    try:
        brief = ai_service.generate_comprehensive_brief(
            project_idea=session.project_idea,
            all_answers=answers,
            questions=questions
        )
        print(f"✅ Generated comprehensive brief with {len(brief.keys())} sections")
    except Exception as e:
        print(f"❌ Brief generation failed: {e}")
        # Fallback to basic brief
        brief = ai_service._get_fallback_brief(
            session.project_idea,
            answers
        )
        print(f"⚠️ Using fallback brief")

    # Update session in database
    session.is_completed = True
    session.completed_at = datetime.utcnow()
    session.brief = json.dumps(brief)
    session.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(session)

    return {
        "status": "completed",
        "message": "Clarification completed successfully",
        "brief": brief
    }

@app.post("/api/v1/clarifications/{session_id}/navigate/{direction}")
async def navigate_clarification(session_id: str, direction: str, db: Session = Depends(get_db)):
    """Navigate to next/previous question in database"""
    session = db.query(models.ClarificationSession).filter(
        models.ClarificationSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if direction not in ["next", "previous"]:
        raise HTTPException(status_code=400, detail="Invalid direction")

    # Parse JSON fields
    questions = json.loads(session.questions) if isinstance(session.questions, str) else session.questions
    answers = json.loads(session.answers) if isinstance(session.answers, str) else session.answers or {}

    current = session.current_question
    total = len(questions)

    # Update current question index
    if direction == "next":
        session.current_question = min(current + 1, total - 1)
    elif direction == "previous":
        session.current_question = max(current - 1, 0)

    session.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(session)

    new_idx = session.current_question
    answered = len(answers)

    # Get current question
    current_question = questions[new_idx] if new_idx < len(questions) else None

    # Return in the format frontend expects
    return {
        "session_id": session_id,
        "current_question": current_question,
        "progress": {
            "answered": answered,
            "total": total,
            "percentage": (answered / total * 100) if total > 0 else 0,
            "category_progress": {"basic": f"{answered}/2", "technical": "0/2", "quality": "0/1"},
            "estimated_time_remaining": max(0, (total - answered) * 2)
        },
        "can_skip": not current_question["required"] if current_question else False,
        "can_finish_early": answered >= int(total * 0.8),
        "next_available": new_idx < total - 1,
        "previous_available": new_idx > 0
    }

@app.put("/api/v1/clarifications/{session_id}/draft")
async def update_draft(session_id: str, request: Dict, db: Session = Depends(get_db)):
    """Update draft answers (auto-save) in database"""
    session = db.query(models.ClarificationSession).filter(
        models.ClarificationSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Note: We don't have draft_answers field in the model yet
    # For now, we'll just update the updated_at timestamp
    session.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(session)

    return {
        "status": "saved",
        "timestamp": session.updated_at.isoformat()
    }

@app.websocket("/api/v1/clarifications/ws/{session_id}")
async def websocket_clarification(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time clarification"""
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()
            # Echo back for now
            await websocket.send_json({
                "type": "update",
                "session_id": session_id,
                "message": "Answer received",
                "data": data
            })
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for session {session_id}")

# Collaboration endpoints
@app.get("/api/v1/collaboration/health")
async def collaboration_health():
    return {"status": "healthy", "service": "collaboration"}

@app.post("/api/v1/collaboration/messages/send")
async def send_message(request: Dict):
    return {"status": "sent", "message_id": str(uuid.uuid4())}

# Cost tracking endpoints
@app.get("/api/v1/costs/health")
async def costs_health():
    return {"status": "healthy", "service": "costs"}

@app.get("/api/v1/costs/summary/{project_id}")
async def get_cost_summary(project_id: str):
    return {
        "project_id": project_id,
        "total_cost": 0.0,
        "cost_by_agent": {},
        "timestamp": datetime.utcnow().isoformat()
    }

# Benchmark endpoints
@app.get("/api/v1/benchmarks/health")
async def benchmarks_health():
    return {"status": "healthy", "service": "benchmarks"}

# AI Models endpoints
models_db = [
    {
        "id": "gpt-4-turbo",
        "name": "GPT-4 Turbo",
        "provider": "openai",
        "description": "Most capable GPT-4 model, optimized for speed and cost",
        "context_window": 128000,
        "max_tokens": 4096,
        "cost_per_1k_input": 0.01,
        "cost_per_1k_output": 0.03,
        "speed_score": 8,
        "quality_score": 10,
        "capabilities": ["chat", "code_generation", "analysis", "reasoning"],
        "status": "available",
        "enabled": True
    },
    {
        "id": "gpt-4",
        "name": "GPT-4",
        "provider": "openai",
        "description": "Original GPT-4 model with exceptional capabilities",
        "context_window": 8192,
        "max_tokens": 4096,
        "cost_per_1k_input": 0.03,
        "cost_per_1k_output": 0.06,
        "speed_score": 6,
        "quality_score": 10,
        "capabilities": ["chat", "code_generation", "analysis", "reasoning", "creative_writing"],
        "status": "available",
        "enabled": True
    },
    {
        "id": "gpt-3.5-turbo",
        "name": "GPT-3.5 Turbo",
        "provider": "openai",
        "description": "Fast and cost-effective model for most tasks",
        "context_window": 16385,
        "max_tokens": 4096,
        "cost_per_1k_input": 0.0005,
        "cost_per_1k_output": 0.0015,
        "speed_score": 10,
        "quality_score": 7,
        "capabilities": ["chat", "code_generation", "analysis"],
        "status": "available",
        "enabled": True
    },
    {
        "id": "claude-3-opus",
        "name": "Claude 3 Opus",
        "provider": "anthropic",
        "description": "Most capable Claude model for complex tasks",
        "context_window": 200000,
        "max_tokens": 4096,
        "cost_per_1k_input": 0.015,
        "cost_per_1k_output": 0.075,
        "speed_score": 7,
        "quality_score": 10,
        "capabilities": ["chat", "code_generation", "analysis", "reasoning", "long_context"],
        "status": "available",
        "enabled": True
    },
    {
        "id": "claude-3-sonnet",
        "name": "Claude 3 Sonnet",
        "provider": "anthropic",
        "description": "Balanced performance and cost",
        "context_window": 200000,
        "max_tokens": 4096,
        "cost_per_1k_input": 0.003,
        "cost_per_1k_output": 0.015,
        "speed_score": 9,
        "quality_score": 9,
        "capabilities": ["chat", "code_generation", "analysis", "long_context"],
        "status": "available",
        "enabled": True
    },
    {
        "id": "claude-3-haiku",
        "name": "Claude 3 Haiku",
        "provider": "anthropic",
        "description": "Fastest Claude model for simple tasks",
        "context_window": 200000,
        "max_tokens": 4096,
        "cost_per_1k_input": 0.00025,
        "cost_per_1k_output": 0.00125,
        "speed_score": 10,
        "quality_score": 7,
        "capabilities": ["chat", "analysis"],
        "status": "available",
        "enabled": True
    },
    {
        "id": "gemini-pro",
        "name": "Gemini Pro",
        "provider": "google",
        "description": "Google's most capable model",
        "context_window": 32768,
        "max_tokens": 8192,
        "cost_per_1k_input": 0.00025,
        "cost_per_1k_output": 0.0005,
        "speed_score": 9,
        "quality_score": 8,
        "capabilities": ["chat", "code_generation", "analysis", "multimodal"],
        "status": "available",
        "enabled": True
    },
    {
        "id": "cursor-small",
        "name": "Cursor Small",
        "provider": "cursor",
        "description": "Fast Cursor model for quick code generation",
        "context_window": 32768,
        "max_tokens": 4096,
        "cost_per_1k_input": 0.0003,
        "cost_per_1k_output": 0.0006,
        "speed_score": 10,
        "quality_score": 8,
        "capabilities": ["chat", "code_generation", "analysis", "code_completion"],
        "status": "available",
        "enabled": True
    },
    {
        "id": "cursor-large",
        "name": "Cursor Large",
        "provider": "cursor",
        "description": "Advanced Cursor model for complex code generation and analysis",
        "context_window": 100000,
        "max_tokens": 8192,
        "cost_per_1k_input": 0.001,
        "cost_per_1k_output": 0.002,
        "speed_score": 9,
        "quality_score": 9,
        "capabilities": ["chat", "code_generation", "analysis", "code_completion", "refactoring"],
        "status": "available",
        "enabled": True
    }
]

@app.get("/api/v1/models/list")
async def get_models(provider: Optional[str] = None, capability: Optional[str] = None):
    """Get list of available AI models"""
    filtered = models_db

    if provider:
        filtered = [m for m in filtered if m["provider"] == provider]
    if capability:
        filtered = [m for m in filtered if capability in m["capabilities"]]

    return {"models": filtered, "total": len(filtered)}

@app.get("/api/v1/models/{model_id}")
async def get_model(model_id: str):
    """Get specific model details"""
    model = next((m for m in models_db if m["id"] == model_id), None)
    if model:
        return model
    return {"error": "Model not found"}

@app.post("/api/v1/models/{model_id}/test")
async def test_model(model_id: str, request: Dict):
    """Test a model with a prompt"""
    model = next((m for m in models_db if m["id"] == model_id), None)
    if not model:
        return {"error": "Model not found"}

    prompt = request.get("prompt", "Hello, world!")

    # Simulate model response
    return {
        "model_id": model_id,
        "model_name": model["name"],
        "prompt": prompt,
        "response": f"This is a simulated response from {model['name']}. In production, this would call the actual API.",
        "tokens_used": len(prompt.split()) * 2,
        "cost": len(prompt.split()) * model["cost_per_1k_input"] / 1000,
        "latency_ms": 100 + (10 - model["speed_score"]) * 50
    }

@app.post("/api/v1/models/compare")
async def compare_models(request: Dict):
    """Compare multiple models"""
    model_ids = request.get("model_ids", [])
    comparison = []

    for model_id in model_ids:
        model = next((m for m in models_db if m["id"] == model_id), None)
        if model:
            comparison.append(model)

    return {
        "models": comparison,
        "total": len(comparison),
        "comparison_metrics": {
            "cheapest": min(comparison, key=lambda x: x["cost_per_1k_input"])["id"] if comparison else None,
            "fastest": max(comparison, key=lambda x: x["speed_score"])["id"] if comparison else None,
            "best_quality": max(comparison, key=lambda x: x["quality_score"])["id"] if comparison else None
        }
    }

@app.get("/api/v1/models/providers")
async def get_providers():
    """Get list of AI providers"""
    providers = {}
    for model in models_db:
        provider = model["provider"]
        if provider not in providers:
            providers[provider] = {"name": provider, "models": []}
        providers[provider]["models"].append(model["id"])

    return {"providers": list(providers.values())}

@app.get("/api/v1/providers/status")
async def check_providers_status():
    """Check availability status of all AI providers"""
    providers_status = {}

    # Check OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    providers_status["openai"] = {
        "available": bool(openai_key and len(openai_key) > 20),
        "name": "OpenAI",
        "models_count": len([m for m in models_db if m["provider"] == "openai"]),
        "api_configured": bool(openai_key),
        "status_code": 200 if openai_key else 401,
        "icon": "🟢"
    }

    # Check Anthropic
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    providers_status["anthropic"] = {
        "available": bool(anthropic_key and len(anthropic_key) > 20),
        "name": "Anthropic Claude",
        "models_count": len([m for m in models_db if m["provider"] == "anthropic"]),
        "api_configured": bool(anthropic_key),
        "status_code": 200 if anthropic_key else 401,
        "icon": "🔵"
    }

    # Check Google Gemini
    google_key = os.getenv("GOOGLE_API_KEY")
    providers_status["gemini"] = {
        "available": bool(google_key and len(google_key) > 20),
        "name": "Google Gemini",
        "models_count": len([m for m in models_db if m["provider"] == "google"]),
        "api_configured": bool(google_key),
        "status_code": 200 if google_key else 401,
        "icon": "🔴"
    }

    # Check Cursor
    cursor_key = os.getenv("CURSOR_API_KEY")
    providers_status["cursor"] = {
        "available": bool(cursor_key and len(cursor_key) > 20),
        "name": "Cursor AI",
        "models_count": len([m for m in models_db if m["provider"] == "cursor"]),
        "api_configured": bool(cursor_key),
        "status_code": 200 if cursor_key else 401,
        "icon": "⚡"
    }

    total_available = sum(1 for p in providers_status.values() if p["available"])

    return {
        "providers": providers_status,
        "total_providers": len(providers_status),
        "available_providers": total_available,
        "all_operational": total_available == len(providers_status),
        "timestamp": datetime.utcnow().isoformat()
    }

# Analytics endpoints
@app.get("/api/v1/analytics")
async def get_comprehensive_analytics(range: str = "30d", db: Session = Depends(get_db)):
    """
    Get comprehensive analytics with REAL database aggregation

    Supports query parameters:
    - range: 7d, 30d, all (default: 30d)
    """
    from sqlalchemy import func, desc
    from datetime import timedelta

    # Calculate date range
    now = datetime.utcnow()
    if range == "7d":
        start_date = now - timedelta(days=7)
    elif range == "30d":
        start_date = now - timedelta(days=30)
    else:  # "all"
        start_date = datetime(2020, 1, 1)  # Beginning of time

    # Query projects from database
    projects_query = db.query(models.Project).filter(
        models.Project.created_at >= start_date
    )

    all_projects = projects_query.all()

    # Overview stats
    total_projects = len(all_projects)
    completed = len([p for p in all_projects if p.status == "completed"])
    failed = len([p for p in all_projects if p.status == "failed"])
    in_progress = len([p for p in all_projects if p.status in ["in_progress", "executing"]])

    total_cost = sum(p.actual_cost or 0 for p in all_projects)
    total_files = sum(p.files_generated or 0 for p in all_projects)
    total_lines = sum(p.lines_of_code or 0 for p in all_projects)

    # Calculate average duration for completed projects
    completed_projects = [p for p in all_projects if p.status == "completed" and p.started_at and p.completed_at]
    if completed_projects:
        durations = [(p.completed_at - p.started_at).total_seconds() / 60 for p in completed_projects]
        avg_duration = sum(durations) / len(durations)
    else:
        avg_duration = 0

    # AI usage by model (from projects)
    model_usage = {}
    for project in all_projects:
        model = project.primary_model or "unknown"
        if model not in model_usage:
            model_usage[model] = {
                "model": model,
                "count": 0,
                "total_cost": 0,
                "total_lines": 0
            }
        model_usage[model]["count"] += 1
        model_usage[model]["total_cost"] += project.actual_cost or 0
        model_usage[model]["total_lines"] += project.lines_of_code or 0

    # AI usage by strategy
    strategy_usage = {}
    for project in all_projects:
        strategy = project.strategy or "balanced"
        if strategy not in strategy_usage:
            strategy_usage[strategy] = {
                "strategy": strategy,
                "count": 0,
                "success_rate": 0
            }
        strategy_usage[strategy]["count"] += 1
        if project.status == "completed":
            strategy_usage[strategy]["success_rate"] += 1

    # Calculate success rates for strategies
    for strategy in strategy_usage.values():
        if strategy["count"] > 0:
            strategy["success_rate"] = round((strategy["success_rate"] / strategy["count"]) * 100, 1)

    # Timeline data (last 30 days of activity)
    timeline_days = 30 if range != "7d" else 7
    timeline = []
    for i in range(timeline_days):
        day_start = now - timedelta(days=timeline_days - i - 1)
        day_end = day_start + timedelta(days=1)

        day_projects = [p for p in all_projects if day_start <= p.created_at < day_end]

        timeline.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "projects_created": len(day_projects),
            "projects_completed": len([p for p in day_projects if p.status == "completed"]),
            "cost": sum(p.actual_cost or 0 for p in day_projects),
            "lines_of_code": sum(p.lines_of_code or 0 for p in day_projects)
        })

    # Top 5 projects by lines of code
    top_projects = sorted(all_projects, key=lambda p: p.lines_of_code or 0, reverse=True)[:5]
    top_projects_data = [{
        "id": p.id,
        "name": p.name,
        "lines_of_code": p.lines_of_code or 0,
        "files_generated": p.files_generated or 0,
        "status": p.status,
        "cost": p.actual_cost or 0
    } for p in top_projects]

    # Query AI provider usage from database
    ai_usage_query = db.query(models.AIProviderUsage).filter(
        models.AIProviderUsage.created_at >= start_date
    )
    ai_usage_records = ai_usage_query.all()

    # Provider stats
    provider_stats = {}
    for record in ai_usage_records:
        provider = record.provider
        if provider not in provider_stats:
            provider_stats[provider] = {
                "provider": provider,
                "requests": 0,
                "total_tokens": 0,
                "total_cost": 0,
                "avg_latency": 0,
                "success_rate": 0
            }

        provider_stats[provider]["requests"] += 1
        provider_stats[provider]["total_tokens"] += record.total_tokens or 0
        provider_stats[provider]["total_cost"] += record.cost or 0
        if record.latency_ms:
            provider_stats[provider]["avg_latency"] += record.latency_ms
        if record.success:
            provider_stats[provider]["success_rate"] += 1

    # Calculate averages
    for provider in provider_stats.values():
        if provider["requests"] > 0:
            provider["avg_latency"] = round(provider["avg_latency"] / provider["requests"])
            provider["success_rate"] = round((provider["success_rate"] / provider["requests"]) * 100, 1)

    return {
        "overview": {
            "total_projects": total_projects,
            "completed": completed,
            "failed": failed,
            "in_progress": in_progress,
            "total_cost": round(total_cost, 2),
            "total_files": total_files,
            "total_lines": total_lines,
            "avg_duration_minutes": round(avg_duration, 1)
        },
        "ai_usage": {
            "by_model": list(model_usage.values()),
            "by_strategy": list(strategy_usage.values()),
            "by_provider": list(provider_stats.values())
        },
        "timeline": timeline,
        "top_projects": top_projects_data,
        "range": range,
        "timestamp": now.isoformat()
    }

@app.get("/api/v1/analytics/metrics")
async def get_analytics_metrics():
    """Get analytics metrics (legacy endpoint - redirects to new endpoint)"""
    import random
    return {
        "total_requests": random.randint(1000, 5000),
        "total_tokens": random.randint(100000, 500000),
        "total_cost": round(random.uniform(10, 100), 2),
        "avg_latency_ms": random.randint(100, 500),
        "success_rate": round(random.uniform(95, 99.9), 2),
        "active_users": random.randint(10, 50),
        "period": "last_30_days"
    }

@app.get("/api/v1/analytics/usage")
async def get_usage_stats():
    """Get usage statistics over time"""
    import random
    from datetime import datetime, timedelta

    data = []
    for i in range(30):
        date = (datetime.now() - timedelta(days=29-i)).strftime("%Y-%m-%d")
        data.append({
            "date": date,
            "requests": random.randint(50, 200),
            "tokens": random.randint(5000, 20000),
            "cost": round(random.uniform(0.5, 5), 2)
        })

    return {"usage": data, "total_days": 30}

@app.get("/api/v1/analytics/models-usage")
async def get_models_usage():
    """Get usage breakdown by model"""
    import random

    usage = []
    for model in models_db[:5]:
        usage.append({
            "model_id": model["id"],
            "model_name": model["name"],
            "requests": random.randint(100, 1000),
            "tokens": random.randint(10000, 100000),
            "cost": round(random.uniform(5, 50), 2),
            "percentage": round(random.uniform(10, 30), 1)
        })

    return {"models": usage}

# Marketplace endpoints
marketplace_items = [
    {
        "id": "plugin-slack",
        "name": "Slack Integration",
        "type": "plugin",
        "description": "Send AI responses to Slack channels",
        "author": "YAGO Team",
        "version": "1.2.0",
        "downloads": 1234,
        "rating": 4.8,
        "price": "free",
        "icon": "💬",
        "tags": ["communication", "integration", "slack"],
        "installed": False
    },
    {
        "id": "plugin-github",
        "name": "GitHub Integration",
        "type": "plugin",
        "description": "Auto-generate code reviews and PR summaries",
        "author": "YAGO Team",
        "version": "2.0.1",
        "downloads": 2456,
        "rating": 4.9,
        "price": "free",
        "icon": "🐙",
        "tags": ["dev-tools", "integration", "github"],
        "installed": False
    },
    {
        "id": "template-api",
        "name": "REST API Template",
        "type": "template",
        "description": "Production-ready REST API with authentication",
        "author": "Community",
        "version": "1.5.0",
        "downloads": 5678,
        "rating": 4.7,
        "price": "free",
        "icon": "🔌",
        "tags": ["template", "api", "backend"],
        "installed": False
    },
    {
        "id": "plugin-analytics",
        "name": "Advanced Analytics",
        "type": "plugin",
        "description": "Detailed analytics and custom dashboards",
        "author": "YAGO Pro",
        "version": "3.1.0",
        "downloads": 890,
        "rating": 4.6,
        "price": "$9.99/mo",
        "icon": "📊",
        "tags": ["analytics", "premium", "dashboards"],
        "installed": False
    },
    {
        "id": "integration-notion",
        "name": "Notion Integration",
        "type": "integration",
        "description": "Save AI conversations to Notion databases",
        "author": "Community",
        "version": "1.0.5",
        "downloads": 3421,
        "rating": 4.5,
        "price": "free",
        "icon": "📝",
        "tags": ["productivity", "integration", "notion"],
        "installed": False
    }
]

@app.get("/api/v1/marketplace/items")
async def get_marketplace_items(item_type: Optional[str] = None):
    """Get marketplace items"""
    filtered = marketplace_items
    if item_type:
        filtered = [item for item in filtered if item["type"] == item_type]

    return {"items": filtered, "total": len(filtered)}

@app.get("/api/v1/marketplace/items/{item_id}")
async def get_marketplace_item(item_id: str):
    """Get specific marketplace item"""
    item = next((i for i in marketplace_items if i["id"] == item_id), None)
    if item:
        return item
    return {"error": "Item not found"}

@app.post("/api/v1/marketplace/items/{item_id}/install")
async def install_marketplace_item(item_id: str):
    """Install a marketplace item"""
    item = next((i for i in marketplace_items if i["id"] == item_id), None)
    if not item:
        return {"error": "Item not found"}

    return {
        "item_id": item_id,
        "status": "installed",
        "message": f"{item['name']} installed successfully",
        "version": item["version"]
    }

# Projects database - MIGRATED TO DATABASE
# projects_db: Dict[str, Dict] = {}  # Old in-memory storage

@app.get("/api/v1/projects")
async def list_projects(
    status: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all projects from database"""
    # Query projects from database
    query = db.query(models.Project)

    # Filter by status if provided
    if status:
        query = query.filter(models.Project.status == status)

    # Sort by created_at descending (newest first)
    query = query.order_by(models.Project.created_at.desc())

    # Get total count before limit
    total = query.count()

    # Apply limit
    projects = query.limit(limit).all()

    # Convert to dict
    projects_list = [project.to_dict() for project in projects]

    return {
        "projects": projects_list,
        "total": total,
        "filtered": total
    }

@app.get("/api/v1/projects/{project_id}")
async def get_project(project_id: str, db: Session = Depends(get_db)):
    """Get specific project details from database"""
    project = db.query(models.Project).filter(models.Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project.to_dict()

@app.post("/api/v1/projects")
async def create_project(request: Dict, db: Session = Depends(get_db)):
    """Create a new project in database"""
    project_id = str(uuid.uuid4())

    # Extract project configuration
    brief = request.get("brief", {})
    config = request.get("config", {})

    # Create new project model
    project = models.Project(
        id=project_id,
        name=brief.get("project_idea", "Untitled Project"),
        description=brief.get("project_idea", "No description"),
        status="creating",
        progress=0,
        brief=json.dumps(brief) if isinstance(brief, dict) else brief,
        config=json.dumps(config) if isinstance(config, dict) else config,
        primary_model=config.get("primary_model", "unknown"),
        agent_role=config.get("agent_role", "unknown"),
        strategy=config.get("strategy", "balanced"),
        temperature=config.get("temperature", 0.7),
        max_tokens=config.get("max_tokens", 4000),
        cost_estimate=0.0,
        actual_cost=0.0,
        files_generated=0,
        lines_of_code=0,
        errors=json.dumps([]),
        logs=json.dumps([])
    )

    # Add to database
    db.add(project)
    db.commit()
    db.refresh(project)

    return {
        "project_id": project_id,
        "status": "created",
        "message": "Project created successfully",
        "project": project.to_dict()
    }

@app.put("/api/v1/projects/{project_id}")
async def update_project(project_id: str, request: Dict, db: Session = Depends(get_db)):
    """Update project status or details in database"""
    project = db.query(models.Project).filter(models.Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Update allowed fields
    if "status" in request:
        project.status = request["status"]
        if request["status"] == "in_progress" and not project.started_at:
            project.started_at = datetime.utcnow()
        elif request["status"] == "completed" and not project.completed_at:
            project.completed_at = datetime.utcnow()

    if "progress" in request:
        project.progress = request["progress"]

    if "actual_cost" in request:
        project.actual_cost = request["actual_cost"]

    if "files_generated" in request:
        project.files_generated = request["files_generated"]

    if "lines_of_code" in request:
        project.lines_of_code = request["lines_of_code"]

    if "error" in request:
        # Parse existing errors
        errors_list = json.loads(project.errors) if isinstance(project.errors, str) else project.errors or []
        errors_list.append({
            "timestamp": datetime.utcnow().isoformat(),
            "error": request["error"]
        })
        project.errors = json.dumps(errors_list)

    if "log" in request:
        # Parse existing logs
        logs_list = json.loads(project.logs) if isinstance(project.logs, str) else project.logs or []
        logs_list.append({
            "timestamp": datetime.utcnow().isoformat(),
            "log": request["log"]
        })
        project.logs = json.dumps(logs_list)

    project.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(project)

    return {
        "project_id": project_id,
        "status": "updated",
        "project": project.to_dict()
    }

@app.delete("/api/v1/projects/{project_id}")
async def delete_project(project_id: str, db: Session = Depends(get_db)):
    """Delete a project from database"""
    project = db.query(models.Project).filter(models.Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project_name = project.name

    db.delete(project)
    db.commit()

    return {
        "project_id": project_id,
        "status": "deleted",
        "message": f"Project '{project_name}' deleted successfully"
    }

@app.post("/api/v1/projects/{project_id}/start")
async def start_project(project_id: str, db: Session = Depends(get_db)):
    """Start project execution in database"""
    project = db.query(models.Project).filter(models.Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project.status = "in_progress"
    project.started_at = datetime.utcnow()
    project.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(project)

    return {
        "project_id": project_id,
        "status": "started",
        "message": "Project execution started"
    }

@app.post("/api/v1/projects/{project_id}/pause")
async def pause_project(project_id: str, db: Session = Depends(get_db)):
    """Pause project execution in database"""
    project = db.query(models.Project).filter(models.Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project.status = "paused"
    project.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(project)

    return {
        "project_id": project_id,
        "status": "paused",
        "message": "Project execution paused"
    }

@app.post("/api/v1/projects/{project_id}/resume")
async def resume_project(project_id: str, db: Session = Depends(get_db)):
    """Resume project execution in database"""
    project = db.query(models.Project).filter(models.Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project.status = "in_progress"
    project.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(project)

    return {
        "project_id": project_id,
        "status": "resumed",
        "message": "Project execution resumed"
    }

# Provider Analytics Endpoint
@app.get("/api/v1/analytics/providers-usage")
async def get_providers_usage():
    """Get usage analytics per provider"""
    import random
    providers = ["openai", "anthropic", "gemini", "cursor"]

    usage_data = []
    for provider in providers:
        usage_data.append({
            "provider": provider,
            "total_requests": random.randint(100, 5000),
            "total_tokens": random.randint(10000, 500000),
            "total_cost": round(random.uniform(5, 100), 2),
            "avg_latency_ms": random.randint(100, 800),
            "success_rate": round(random.uniform(95, 99.9), 2),
            "last_used": datetime.utcnow().isoformat()
        })

    return {
        "providers_usage": usage_data,
        "period": "last_30_days",
        "timestamp": datetime.utcnow().isoformat()
    }

# Cost Alerts System
@app.get("/api/v1/costs/alerts")
async def get_cost_alerts(db: Session = Depends(get_db)):
    """Get cost alerts and budget warnings from database"""
    alerts = []

    # Get all projects from database
    projects = db.query(models.Project).all()

    # Check if any project exceeds budget
    for project in projects:
        if project.actual_cost > project.cost_estimate * 1.2 and project.cost_estimate > 0:
            alerts.append({
                "id": str(uuid.uuid4()),
                "type": "budget_exceeded",
                "severity": "high",
                "project_id": project.id,
                "project_name": project.name,
                "message": f"Project budget exceeded by {((project.actual_cost / project.cost_estimate) - 1) * 100:.1f}%",
                "actual_cost": project.actual_cost,
                "estimated_cost": project.cost_estimate,
                "created_at": datetime.utcnow().isoformat()
            })

    # Weekly cost warning
    total_cost = sum(p.actual_cost or 0 for p in projects)
    if total_cost > 50:
        alerts.append({
            "id": str(uuid.uuid4()),
            "type": "weekly_limit_warning",
            "severity": "medium",
            "message": f"Weekly spending is ${total_cost:.2f}, approaching limit",
            "total_cost": total_cost,
            "limit": 100,
            "created_at": datetime.utcnow().isoformat()
        })

    return {
        "alerts": alerts,
        "total_alerts": len(alerts),
        "unread_count": len([a for a in alerts if a["severity"] == "high"]),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/v1/costs/alerts/{alert_id}/dismiss")
async def dismiss_alert(alert_id: str):
    """Dismiss a cost alert"""
    return {
        "alert_id": alert_id,
        "status": "dismissed",
        "dismissed_at": datetime.utcnow().isoformat()
    }

# Export Project Endpoint
@app.get("/api/v1/projects/{project_id}/export")
async def export_project(project_id: str, db: Session = Depends(get_db)):
    """Export project as JSON (ready for ZIP generation) from database"""
    try:
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Convert to dict
        project_dict = project.to_dict()

        # Create serializable copy of project
        project_copy = json.loads(json.dumps(project_dict, default=str))

        export_data = {
            "project": project_copy,
            "exported_at": datetime.utcnow().isoformat(),
            "export_version": "1.0",
            "files": [
                {"name": "README.md", "content": f"# {project.name}\n\n{project.description or 'No description'}"},
                {"name": "project.json", "content": json.dumps(project_copy, indent=2)},
                {"name": "brief.md", "content": f"# Project Brief\n\n{project.brief}"}
            ]
        }

        return export_data
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        return {
            "error": f"Export failed: {str(e)}",
            "traceback": traceback.format_exc()
        }

# ============================================================================
# AI CODE EXECUTION ENDPOINTS
# ============================================================================

@app.post("/api/v1/projects/{project_id}/execute")
async def execute_project_code_generation(project_id: str, db: Session = Depends(get_db)):
    """
    🚀 Execute AI agent to generate actual code for the project

    This is the main feature of YAGO - transforms user requirements into working code!

    Process:
    1. Analyze project brief
    2. Design architecture
    3. Generate code files
    4. Generate tests
    5. Save to filesystem
    """
    try:
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Parse brief and config from JSON strings if needed
        brief = json.loads(project.brief) if isinstance(project.brief, str) else project.brief
        config = json.loads(project.config) if isinstance(project.config, str) else project.config

        # Update project status
        project.status = "executing"
        project.started_at = datetime.utcnow()
        project.updated_at = datetime.utcnow()
        db.commit()

        # Get executor
        executor = get_code_executor()

        # Execute code generation
        result = await executor.execute_project(
            project_id,
            brief or {},
            config or {}
        )

        # Update project with results
        project.status = "completed"
        project.completed_at = datetime.utcnow()
        project.updated_at = datetime.utcnow()
        project.files_generated = result.get("files_generated", 0)
        project.lines_of_code = result.get("lines_of_code", 0)
        project.project_path = result.get("project_path", "")

        # Estimate cost (rough estimate)
        tokens_used = result.get("lines_of_code", 0) * 10  # ~10 tokens per line
        project.actual_cost = round((tokens_used / 1000) * 0.002, 2)  # GPT-4 pricing

        db.commit()
        db.refresh(project)

        return {
            "project_id": project_id,
            "status": "success",
            "message": "✅ Code generation completed!",
            "result": result
        }

    except HTTPException:
        raise
    except Exception as e:
        # Update project status to failed
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if project:
            project.status = "failed"
            project.updated_at = datetime.utcnow()

            # Parse errors and append
            errors_list = json.loads(project.errors) if isinstance(project.errors, str) else project.errors or []
            errors_list.append({
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
            project.errors = json.dumps(errors_list)

            db.commit()

        import traceback
        return {
            "error": f"Execution failed: {str(e)}",
            "traceback": traceback.format_exc()
        }

@app.get("/api/v1/projects/{project_id}/files")
async def list_project_files(project_id: str, db: Session = Depends(get_db)):
    """Get list of generated files for a project"""
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project_path = project.project_path
    if not project_path:
        return {"files": [], "message": "Project not executed yet"}

    try:
        from pathlib import Path
        path = Path(project_path)

        if not path.exists():
            return {"files": [], "message": "Project directory not found"}

        files = []
        for file in path.rglob("*"):
            if file.is_file():
                relative_path = file.relative_to(path)
                files.append({
                    "path": str(relative_path),
                    "size": file.stat().st_size,
                    "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                })

        return {
            "project_id": project_id,
            "project_path": str(path.absolute()),
            "files": files,
            "total_files": len(files)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

@app.get("/api/v1/projects/{project_id}/files/{file_path:path}")
async def get_project_file(project_id: str, file_path: str, db: Session = Depends(get_db)):
    """Get content of a specific generated file"""
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project_path = project.project_path
    if not project_path:
        raise HTTPException(status_code=400, detail="Project not executed yet")

    try:
        from pathlib import Path
        full_path = Path(project_path) / file_path

        if not full_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        # Security check - ensure file is within project directory
        if not str(full_path.resolve()).startswith(str(Path(project_path).resolve())):
            raise HTTPException(status_code=403, detail="Access denied")

        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return {
            "project_id": project_id,
            "file_path": file_path,
            "content": content,
            "size": len(content),
            "lines": len(content.split('\n'))
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")

@app.get("/api/v1/projects/{project_id}/download")
async def download_project_zip(project_id: str, db: Session = Depends(get_db)):
    """Download project as ZIP file"""
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project_path = project.project_path
    if not project_path:
        raise HTTPException(status_code=400, detail="Project not executed yet")

    try:
        from pathlib import Path
        import zipfile
        import tempfile

        path = Path(project_path)
        if not path.exists():
            raise HTTPException(status_code=404, detail="Project directory not found")

        # Create temporary ZIP file
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        zip_path = temp_zip.name
        temp_zip.close()

        # Create ZIP archive
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in path.rglob("*"):
                if file.is_file():
                    # Add file to ZIP with relative path
                    arcname = file.relative_to(path)
                    zipf.write(file, arcname=arcname)

        # Get project name for filename
        project_name = project.name or f"project_{project_id[:8]}"
        safe_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        zip_filename = f"{safe_name}.zip"

        # Return ZIP file
        return FileResponse(
            path=zip_path,
            media_type='application/zip',
            filename=zip_filename,
            headers={
                "Content-Disposition": f"attachment; filename={zip_filename}"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create ZIP: {str(e)}")

# ============================================================================
# ENTERPRISE FEATURES - Git Analysis, Refactoring, Documentation
# ============================================================================

# Import enterprise services
try:
    from .services.git_analyzer import GitProjectAnalyzer
    from .services.code_refactor import CodeRefactorService
    from .services.doc_compliance import DocComplianceService
    from .services.doc_generator import DocGeneratorService
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from services.git_analyzer import GitProjectAnalyzer
    from services.code_refactor import CodeRefactorService
    from services.doc_compliance import DocComplianceService
    from services.doc_generator import DocGeneratorService

@app.post("/api/v1/enterprise/analyze-git")
async def analyze_git_project(request: Dict):
    """Analyze a Git repository for completion opportunities"""
    git_url = request.get("git_url")
    if not git_url:
        raise HTTPException(status_code=400, detail="git_url is required")

    analyzer = GitProjectAnalyzer()
    try:
        report = analyzer.generate_completion_report(git_url)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    finally:
        analyzer.cleanup()

@app.post("/api/v1/enterprise/refactor-project")
async def refactor_project(request: Dict):
    """Analyze project for refactoring opportunities"""
    project_path = request.get("project_path")
    if not project_path:
        raise HTTPException(status_code=400, detail="project_path is required")

    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail="Project path not found")

    refactor = CodeRefactorService(project_path)
    try:
        report = refactor.analyze_project()
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refactoring analysis failed: {str(e)}")

@app.post("/api/v1/enterprise/check-compliance")
async def check_documentation_compliance(request: Dict):
    """Check if code matches technical documentation"""
    project_path = request.get("project_path")
    docs_path = request.get("docs_path")

    if not project_path:
        raise HTTPException(status_code=400, detail="project_path is required")

    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail="Project path not found")

    compliance = DocComplianceService(project_path, docs_path)
    try:
        report = compliance.analyze_compliance()
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compliance check failed: {str(e)}")

@app.post("/api/v1/enterprise/generate-docs")
async def generate_documentation(request: Dict):
    """Auto-generate documentation from code"""
    project_path = request.get("project_path")
    if not project_path:
        raise HTTPException(status_code=400, detail="project_path is required")

    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail="Project path not found")

    doc_gen = DocGeneratorService(project_path)
    try:
        result = doc_gen.generate_all_documentation()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Documentation generation failed: {str(e)}")

@app.get("/api/v1/enterprise/features")
async def list_enterprise_features():
    """List all available enterprise features"""
    return {
        "features": [
            {
                "id": "git_analysis",
                "name": "Git Project Analysis",
                "description": "Analyze existing Git projects to find TODOs, incomplete features, and improvement opportunities",
                "endpoint": "/api/v1/enterprise/analyze-git",
                "method": "POST",
                "parameters": ["git_url"]
            },
            {
                "id": "code_refactor",
                "name": "Code Refactoring",
                "description": "Detect dead code, duplicates, complexity issues, and get modernization suggestions",
                "endpoint": "/api/v1/enterprise/refactor-project",
                "method": "POST",
                "parameters": ["project_path"]
            },
            {
                "id": "doc_compliance",
                "name": "Documentation Compliance",
                "description": "Check if code implementation matches technical documentation",
                "endpoint": "/api/v1/enterprise/check-compliance",
                "method": "POST",
                "parameters": ["project_path", "docs_path"]
            },
            {
                "id": "auto_docs",
                "name": "Auto Documentation",
                "description": "Generate comprehensive documentation from code automatically",
                "endpoint": "/api/v1/enterprise/generate-docs",
                "method": "POST",
                "parameters": ["project_path"]
            }
        ],
        "total_features": 4,
        "version": "8.2.0"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
