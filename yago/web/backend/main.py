from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional
import uvicorn
import uuid
import json
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

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

# Clarification endpoints
sessions_db: Dict[str, Dict] = {}

@app.post("/api/v1/clarifications/start")
async def start_clarification(request: Dict):
    """Start a new clarification session with AI-generated questions"""
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

    sessions_db[session_id] = {
        "session_id": session_id,
        "project_idea": project_idea,
        "depth": depth,
        "user_id": request.get("user_id"),
        "created_at": datetime.utcnow().isoformat(),
        "current_question": 0,
        "questions": questions,
        "answers": {},
        "total_questions": len(questions),
        "followup_questions": []  # Store dynamic follow-ups
    }

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
async def get_clarification_session(session_id: str):
    """Get clarification session details"""
    session = sessions_db.get(session_id)
    if session:
        return session
    return {"error": "Session not found"}

@app.post("/api/v1/clarifications/{session_id}/answer")
async def submit_answer(session_id: str, request: Dict):
    """Submit an answer to clarification question"""
    session = sessions_db.get(session_id)
    if not session:
        return {"error": "Session not found"}

    questions = session.get("questions", [])
    current_idx = session["current_question"]
    answer_value = request.get("answer")
    skip = request.get("skip", False)

    # Save answer if not skipping
    if not skip and current_idx < len(questions):
        current_q = questions[current_idx]
        session["answers"][current_q["id"]] = answer_value

    # Move to next question
    session["current_question"] = min(current_idx + 1, len(questions))
    new_idx = session["current_question"]

    # Calculate progress
    answered = len(session["answers"])
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
async def get_progress(session_id: str):
    """Get session progress"""
    session = sessions_db.get(session_id)
    if not session:
        return {"error": "Session not found"}

    total_questions = 5
    answered = len(session.get("answers", {}))

    return {
        "session_id": session_id,
        "answered": answered,
        "total": total_questions,
        "percentage": (answered / total_questions) * 100
    }

@app.post("/api/v1/clarifications/{session_id}/complete")
async def complete_clarification(session_id: str):
    """Complete clarification session with AI-generated comprehensive brief"""
    session = sessions_db.get(session_id)
    if not session:
        return {"error": "Session not found"}

    print(f"📝 Generating comprehensive brief for session: {session_id}")
    print(f"   Answered: {len(session['answers'])}/{session['total_questions']} questions")

    # Get AI service
    ai_service = get_ai_clarification_service()

    # Generate comprehensive brief using GPT-4
    try:
        brief = ai_service.generate_comprehensive_brief(
            project_idea=session["project_idea"],
            all_answers=session["answers"],
            questions=session["questions"]
        )
        print(f"✅ Generated comprehensive brief with {len(brief.keys())} sections")
    except Exception as e:
        print(f"❌ Brief generation failed: {e}")
        # Fallback to basic brief
        brief = ai_service._get_fallback_brief(
            session["project_idea"],
            session["answers"]
        )
        print(f"⚠️ Using fallback brief")

    session["status"] = "completed"
    session["completed_at"] = datetime.utcnow().isoformat()
    session["brief"] = brief

    return {
        "status": "completed",
        "message": "Clarification completed successfully",
        "brief": brief
    }

@app.post("/api/v1/clarifications/{session_id}/navigate/{direction}")
async def navigate_clarification(session_id: str, direction: str):
    """Navigate to next/previous question"""
    session = sessions_db.get(session_id)
    if not session:
        return {"error": "Session not found"}

    if direction not in ["next", "previous"]:
        return {"error": "Invalid direction"}

    questions = session.get("questions", [])
    current = session["current_question"]
    total = len(questions)

    # Update current question index
    if direction == "next":
        session["current_question"] = min(current + 1, total - 1)
    elif direction == "previous":
        session["current_question"] = max(current - 1, 0)

    new_idx = session["current_question"]
    answered = len(session["answers"])

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
async def update_draft(session_id: str, request: Dict):
    """Update draft answers (auto-save)"""
    session = sessions_db.get(session_id)
    if not session:
        return {"error": "Session not found"}

    session["draft_answers"] = request.get("answers", {})
    session["updated_at"] = datetime.utcnow().isoformat()

    return {
        "status": "saved",
        "timestamp": session["updated_at"]
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
@app.get("/api/v1/analytics/metrics")
async def get_analytics_metrics():
    """Get analytics metrics"""
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

# Projects database
projects_db: Dict[str, Dict] = {}

@app.get("/api/v1/projects")
async def list_projects(status: Optional[str] = None, limit: int = 100):
    """List all projects"""
    projects = list(projects_db.values())

    # Filter by status if provided
    if status:
        projects = [p for p in projects if p.get("status") == status]

    # Sort by created_at descending (newest first)
    projects.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    return {
        "projects": projects[:limit],
        "total": len(projects),
        "filtered": len(projects) if status else len(projects_db)
    }

@app.get("/api/v1/projects/{project_id}")
async def get_project(project_id: str):
    """Get specific project details"""
    project = projects_db.get(project_id)
    if not project:
        return {"error": "Project not found"}

    return project

@app.post("/api/v1/projects")
async def create_project(request: Dict):
    """Create a new project"""
    project_id = str(uuid.uuid4())

    # Extract project configuration
    brief = request.get("brief", {})
    config = request.get("config", {})

    project = {
        "id": project_id,
        "name": brief.get("project_idea", "Untitled Project"),
        "description": brief.get("project_idea", "No description"),
        "status": "creating",  # creating, in_progress, paused, completed, failed
        "progress": 0,
        "brief": brief,
        "config": config,
        "primary_model": config.get("primary_model", "unknown"),
        "agent_role": config.get("agent_role", "unknown"),
        "strategy": config.get("strategy", "balanced"),
        "temperature": config.get("temperature", 0.7),
        "max_tokens": config.get("max_tokens", 4000),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "started_at": None,
        "completed_at": None,
        "cost_estimate": 0.0,
        "actual_cost": 0.0,
        "files_generated": 0,
        "lines_of_code": 0,
        "errors": [],
        "logs": []
    }

    projects_db[project_id] = project

    return {
        "project_id": project_id,
        "status": "created",
        "message": "Project created successfully",
        "project": project
    }

@app.put("/api/v1/projects/{project_id}")
async def update_project(project_id: str, request: Dict):
    """Update project status or details"""
    project = projects_db.get(project_id)
    if not project:
        return {"error": "Project not found"}

    # Update allowed fields
    if "status" in request:
        project["status"] = request["status"]
        if request["status"] == "in_progress" and not project.get("started_at"):
            project["started_at"] = datetime.utcnow().isoformat()
        elif request["status"] == "completed" and not project.get("completed_at"):
            project["completed_at"] = datetime.utcnow().isoformat()

    if "progress" in request:
        project["progress"] = request["progress"]

    if "actual_cost" in request:
        project["actual_cost"] = request["actual_cost"]

    if "files_generated" in request:
        project["files_generated"] = request["files_generated"]

    if "lines_of_code" in request:
        project["lines_of_code"] = request["lines_of_code"]

    if "error" in request:
        if "errors" not in project:
            project["errors"] = []
        project["errors"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "error": request["error"]
        })

    if "log" in request:
        if "logs" not in project:
            project["logs"] = []
        project["logs"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "log": request["log"]
        })

    project["updated_at"] = datetime.utcnow().isoformat()

    return {
        "project_id": project_id,
        "status": "updated",
        "project": project
    }

@app.delete("/api/v1/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete a project"""
    if project_id not in projects_db:
        return {"error": "Project not found"}

    deleted_project = projects_db.pop(project_id)

    return {
        "project_id": project_id,
        "status": "deleted",
        "message": f"Project '{deleted_project['name']}' deleted successfully"
    }

@app.post("/api/v1/projects/{project_id}/start")
async def start_project(project_id: str):
    """Start project execution"""
    project = projects_db.get(project_id)
    if not project:
        return {"error": "Project not found"}

    project["status"] = "in_progress"
    project["started_at"] = datetime.utcnow().isoformat()
    project["updated_at"] = datetime.utcnow().isoformat()

    return {
        "project_id": project_id,
        "status": "started",
        "message": "Project execution started"
    }

@app.post("/api/v1/projects/{project_id}/pause")
async def pause_project(project_id: str):
    """Pause project execution"""
    project = projects_db.get(project_id)
    if not project:
        return {"error": "Project not found"}

    project["status"] = "paused"
    project["updated_at"] = datetime.utcnow().isoformat()

    return {
        "project_id": project_id,
        "status": "paused",
        "message": "Project execution paused"
    }

@app.post("/api/v1/projects/{project_id}/resume")
async def resume_project(project_id: str):
    """Resume project execution"""
    project = projects_db.get(project_id)
    if not project:
        return {"error": "Project not found"}

    project["status"] = "in_progress"
    project["updated_at"] = datetime.utcnow().isoformat()

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
async def get_cost_alerts():
    """Get cost alerts and budget warnings"""
    import random

    alerts = []

    # Check if any project exceeds budget
    for project in projects_db.values():
        if project.get("actual_cost", 0) > project.get("cost_estimate", 0) * 1.2:
            alerts.append({
                "id": str(uuid.uuid4()),
                "type": "budget_exceeded",
                "severity": "high",
                "project_id": project["id"],
                "project_name": project["name"],
                "message": f"Project budget exceeded by {((project['actual_cost'] / project['cost_estimate']) - 1) * 100:.1f}%",
                "actual_cost": project["actual_cost"],
                "estimated_cost": project.get("cost_estimate", 0),
                "created_at": datetime.utcnow().isoformat()
            })

    # Weekly cost warning
    total_cost = sum(p.get("actual_cost", 0) for p in projects_db.values())
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
async def export_project(project_id: str):
    """Export project as JSON (ready for ZIP generation)"""
    try:
        project = projects_db.get(project_id)
        if not project:
            return {"error": "Project not found"}

        # Create serializable copy of project
        project_copy = json.loads(json.dumps(project, default=str))

        export_data = {
            "project": project_copy,
            "exported_at": datetime.utcnow().isoformat(),
            "export_version": "1.0",
            "files": [
                {"name": "README.md", "content": f"# {project['name']}\n\n{project.get('description', 'No description')}"},
                {"name": "project.json", "content": json.dumps(project_copy, indent=2)},
                {"name": "brief.md", "content": f"# Project Brief\n\n{json.dumps(project.get('brief', {}), indent=2)}"}
            ]
        }

        return export_data
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
async def execute_project_code_generation(project_id: str):
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
        project = projects_db.get(project_id)
        if not project:
            return {"error": "Project not found"}

        # Update project status
        project["status"] = "executing"
        project["started_at"] = datetime.utcnow().isoformat()
        project["updated_at"] = datetime.utcnow().isoformat()

        # Get executor
        executor = get_code_executor()

        # Execute code generation
        result = await executor.execute_project(
            project_id,
            project.get("brief", {}),
            project.get("config", {})
        )

        # Update project with results
        project["status"] = "completed"
        project["completed_at"] = datetime.utcnow().isoformat()
        project["updated_at"] = datetime.utcnow().isoformat()
        project["files_generated"] = result.get("files_generated", 0)
        project["lines_of_code"] = result.get("lines_of_code", 0)
        project["project_path"] = result.get("project_path", "")

        # Estimate cost (rough estimate)
        tokens_used = result.get("lines_of_code", 0) * 10  # ~10 tokens per line
        project["actual_cost"] = round((tokens_used / 1000) * 0.002, 2)  # GPT-4 pricing

        return {
            "project_id": project_id,
            "status": "success",
            "message": "✅ Code generation completed!",
            "result": result
        }

    except Exception as e:
        # Update project status to failed
        if project_id in projects_db:
            projects_db[project_id]["status"] = "failed"
            projects_db[project_id]["updated_at"] = datetime.utcnow().isoformat()
            projects_db[project_id]["errors"].append({
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })

        import traceback
        return {
            "error": f"Execution failed: {str(e)}",
            "traceback": traceback.format_exc()
        }

@app.get("/api/v1/projects/{project_id}/files")
async def list_project_files(project_id: str):
    """Get list of generated files for a project"""
    project = projects_db.get(project_id)
    if not project:
        return {"error": "Project not found"}

    project_path = project.get("project_path")
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
            "files": files,
            "total_files": len(files)
        }

    except Exception as e:
        return {"error": f"Failed to list files: {str(e)}"}

@app.get("/api/v1/projects/{project_id}/files/{file_path:path}")
async def get_project_file(project_id: str, file_path: str):
    """Get content of a specific generated file"""
    project = projects_db.get(project_id)
    if not project:
        return {"error": "Project not found"}

    project_path = project.get("project_path")
    if not project_path:
        return {"error": "Project not executed yet"}

    try:
        from pathlib import Path
        full_path = Path(project_path) / file_path

        if not full_path.exists():
            return {"error": "File not found"}

        # Security check - ensure file is within project directory
        if not str(full_path.resolve()).startswith(str(Path(project_path).resolve())):
            return {"error": "Access denied"}

        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return {
            "project_id": project_id,
            "file_path": file_path,
            "content": content,
            "size": len(content),
            "lines": len(content.split('\n'))
        }

    except Exception as e:
        return {"error": f"Failed to read file: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
