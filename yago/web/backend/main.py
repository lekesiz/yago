from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional
import uvicorn
import uuid
from datetime import datetime

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
    """Start a new clarification session"""
    session_id = str(uuid.uuid4())
    sessions_db[session_id] = {
        "session_id": session_id,
        "project_idea": request.get("project_idea"),
        "depth": request.get("depth", "standard"),
        "user_id": request.get("user_id"),
        "created_at": datetime.utcnow().isoformat(),
        "current_question": 0,
        "answers": {}
    }

    return {
        "session_id": session_id,
        "message": "Clarification session started",
        "first_question": {
            "id": "q1",
            "text": "What is the primary purpose of your project?",
            "type": "text",
            "required": True
        }
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

    question_id = request.get("question_id")
    answer = request.get("answer")

    session["answers"][question_id] = answer
    session["current_question"] += 1

    # Return next question or completion
    if session["current_question"] >= 5:  # Max 5 questions for demo
        return {
            "status": "completed",
            "message": "Clarification completed",
            "summary": session["answers"]
        }

    next_q = session["current_question"] + 1
    return {
        "status": "in_progress",
        "next_question": {
            "id": f"q{next_q}",
            "text": f"Question {next_q}: Tell us more about your requirements?",
            "type": "text",
            "required": False
        }
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
    """Complete clarification session"""
    session = sessions_db.get(session_id)
    if not session:
        return {"error": "Session not found"}

    session["status"] = "completed"
    session["completed_at"] = datetime.utcnow().isoformat()

    return {
        "status": "completed",
        "message": "Clarification completed successfully",
        "brief": {
            "session_id": session_id,
            "project_idea": session["project_idea"],
            "answers": session["answers"],
            "completed_at": session["completed_at"]
        }
    }

@app.post("/api/v1/clarifications/{session_id}/navigate/{direction}")
async def navigate_clarification(session_id: str, direction: str):
    """Navigate to next/previous question"""
    session = sessions_db.get(session_id)
    if not session:
        return {"error": "Session not found"}

    if direction not in ["next", "previous"]:
        return {"error": "Invalid direction"}

    current = session["current_question"]
    if direction == "next":
        session["current_question"] = min(current + 1, 4)  # Max 5 questions (0-4)
    elif direction == "previous":
        session["current_question"] = max(current - 1, 0)

    return {
        "session_id": session_id,
        "current_question": session["current_question"],
        "status": "ok"
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
